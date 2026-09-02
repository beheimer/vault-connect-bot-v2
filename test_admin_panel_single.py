"""Tests for single admin panel message feature."""
import os
import sys
import sqlite3
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.db import (
    get_admin_panel_msg_id,
    set_admin_panel_msg_id,
    get_setting,
    set_setting,
    init_db,
    DB_PATH,
)


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Use a temp DB for each test."""
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr("utils.db.DB_PATH", db_path)
    init_db()
    yield db_path


# --- DB helper tests ---

class TestAdminPanelMsgId:
    def test_default_returns_zero(self):
        assert get_admin_panel_msg_id(111) == 0

    def test_set_and_get(self):
        set_admin_panel_msg_id(111, 42)
        assert get_admin_panel_msg_id(111) == 42

    def test_overwrite(self):
        set_admin_panel_msg_id(111, 42)
        set_admin_panel_msg_id(111, 99)
        assert get_admin_panel_msg_id(111) == 99

    def test_different_admins(self):
        set_admin_panel_msg_id(111, 42)
        set_admin_panel_msg_id(222, 77)
        assert get_admin_panel_msg_id(111) == 42
        assert get_admin_panel_msg_id(222) == 77

    def test_corrupt_value_returns_zero(self):
        set_setting("panel_msg_111", "not_a_number")
        assert get_admin_panel_msg_id(111) == 0

    def test_empty_value_returns_zero(self):
        set_setting("panel_msg_111", "")
        assert get_admin_panel_msg_id(111) == 0


# --- admin_panel() function tests ---

def _make_message(user_id=100):
    """Create a mock Message for admin_panel()."""
    msg = AsyncMock()
    msg.from_user = MagicMock()
    msg.from_user.id = user_id
    msg.bot = AsyncMock()

    sent = AsyncMock()
    sent.message_id = 999
    msg.answer = AsyncMock(return_value=sent)
    return msg


@pytest.mark.asyncio
async def test_admin_panel_stores_msg_id():
    """admin_panel() should store the sent message_id."""
    with patch("handlers.admin_panel.check_admin", return_value=True), \
         patch("handlers.admin_panel.get_lang", return_value="en"):
        from handlers.admin_panel import admin_panel

        msg = _make_message(user_id=100)
        result = await admin_panel(msg)

        assert result is not None
        assert result.message_id == 999
        assert get_admin_panel_msg_id(100) == 999


@pytest.mark.asyncio
async def test_admin_panel_deletes_old_message():
    """admin_panel() should try to delete the previously stored message."""
    set_admin_panel_msg_id(100, 555)

    with patch("handlers.admin_panel.check_admin", return_value=True), \
         patch("handlers.admin_panel.get_lang", return_value="en"):
        from handlers.admin_panel import admin_panel

        msg = _make_message(user_id=100)
        await admin_panel(msg)

        msg.bot.delete_message.assert_awaited_once_with(chat_id=100, message_id=555)
        assert get_admin_panel_msg_id(100) == 999


@pytest.mark.asyncio
async def test_admin_panel_delete_failure_ignored():
    """If deleting old message fails, it should be silently ignored."""
    set_admin_panel_msg_id(100, 555)

    with patch("handlers.admin_panel.check_admin", return_value=True), \
         patch("handlers.admin_panel.get_lang", return_value="en"):
        from handlers.admin_panel import admin_panel

        msg = _make_message(user_id=100)
        msg.bot.delete_message = AsyncMock(side_effect=Exception("Message not found"))

        result = await admin_panel(msg)
        assert result is not None
        assert get_admin_panel_msg_id(100) == 999


@pytest.mark.asyncio
async def test_admin_panel_no_delete_when_no_stored():
    """If no old message stored, delete should NOT be called."""
    with patch("handlers.admin_panel.check_admin", return_value=True), \
         patch("handlers.admin_panel.get_lang", return_value="en"):
        from handlers.admin_panel import admin_panel

        msg = _make_message(user_id=100)
        await admin_panel(msg)

        msg.bot.delete_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_admin_panel_non_admin_returns_none():
    """Non-admin users should get None and no message stored."""
    with patch("handlers.admin_panel.check_admin", return_value=False):
        from handlers.admin_panel import admin_panel

        msg = _make_message(user_id=100)
        result = await admin_panel(msg)

        assert result is None
        assert get_admin_panel_msg_id(100) == 0


@pytest.mark.asyncio
async def test_admin_panel_trigger_calls_admin_panel():
    """admin_panel_trigger in start.py should call admin_panel."""
    with patch("handlers.admin_panel.check_admin", return_value=True), \
         patch("handlers.admin_panel.get_lang", return_value="en"):
        from handlers.start import admin_panel_trigger

        msg = _make_message(user_id=100)
        await admin_panel_trigger(msg)

        msg.answer.assert_awaited_once()
        assert get_admin_panel_msg_id(100) == 999
