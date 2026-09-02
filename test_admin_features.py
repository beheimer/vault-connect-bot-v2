"""Tests for 4 admin features: multi-admin, confirmations, payment edit, refresh button."""
import os
import sys
import sqlite3
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up env
os.environ.setdefault("BOT_TOKEN", "123:TEST")

from utils.db import (
    init_db, get_conn, DB_PATH,
    is_admin, add_admin, remove_admin, get_admins,
    get_user, save_user
)
from config.settings import ADMIN_ID


def setup():
    """Reset database for each test."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()


# ===== FEATURE 1: Multi-admin support =====

class TestMultiAdmin:

    def test_admins_table_exists(self):
        setup()
        conn = get_conn()
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='admins'"
        ).fetchone()
        conn.close()
        assert row is not None, "admins table should exist"

    def test_is_admin_primary(self):
        setup()
        assert is_admin(ADMIN_ID) is True

    def test_is_admin_unknown(self):
        setup()
        assert is_admin(999999) is False

    def test_add_and_check_admin(self):
        setup()
        add_admin(12345, "testuser", ADMIN_ID)
        assert is_admin(12345) is True

    def test_get_admins(self):
        setup()
        add_admin(12345, "testuser1", ADMIN_ID)
        add_admin(67890, "testuser2", ADMIN_ID)
        admins = get_admins()
        assert len(admins) == 2
        ids = [a["user_id"] for a in admins]
        assert 12345 in ids
        assert 67890 in ids

    def test_remove_admin(self):
        setup()
        add_admin(12345, "testuser", ADMIN_ID)
        assert is_admin(12345) is True
        remove_admin(12345)
        assert is_admin(12345) is False

    def test_add_admin_stored_fields(self):
        setup()
        add_admin(12345, "testuser", ADMIN_ID)
        admins = get_admins()
        a = admins[0]
        assert a["user_id"] == 12345
        assert a["username"] == "testuser"
        assert a["added_by"] == ADMIN_ID
        assert a["added_at"] is not None

    def test_add_admin_idempotent(self):
        setup()
        add_admin(12345, "testuser", ADMIN_ID)
        add_admin(12345, "testuser_updated", ADMIN_ID)
        admins = get_admins()
        assert len(admins) == 1
        assert admins[0]["username"] == "testuser_updated"


class TestAdminCheck:

    def test_admin_check_module(self):
        setup()
        from utils.admin_check import is_admin as check_admin
        assert check_admin(ADMIN_ID) is True
        assert check_admin(999999) is False
        add_admin(111, "x", ADMIN_ID)
        assert check_admin(111) is True


# ===== FEATURE 1 continued: verify admin checks are replaced =====

class TestAdminChecksReplaced:

    def test_admin_panel_uses_check_admin(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        assert 'from utils.admin_check import is_admin as check_admin' in content
        assert 'not check_admin(message.from_user.id)' in content or 'not check_admin(call.from_user.id)' in content
        # Old pattern for general admin checks should NOT be present
        # But owner-only checks (ADMIN_ID != for add/remove admin) are intentional
        lines = content.split('\n')
        general_old_checks = []
        for i, l in enumerate(lines):
            if ('message.from_user.id != ADMIN_ID' in l or 'call.from_user.id != ADMIN_ID' in l) and 'import' not in l:
                # Check context: owner-only operations are OK
                context = '\n'.join(lines[max(0,i-3):i+3])
                if 'ADMIN_ONLY_OWNER' not in context:
                    general_old_checks.append(l.strip())
        assert len(general_old_checks) == 0, f"Found old admin check: {general_old_checks}"

    def test_admin_panel_has_admins_button(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        assert 'ADMIN_BTN_ADMINS' in content
        assert 'admin_admins' in content

    def test_admin_panel_has_admin_add_state(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        assert 'class AdminAdd(StatesGroup):' in content
        assert 'waiting_for_target = State()' in content

    def test_admin_panel_has_add_admin_handler(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        assert 'admin_add_admin' in content
        assert 'process_admin_add_target' in content

    def test_admin_panel_has_remove_admin_handler(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        assert 'admin_remove_' in content
        assert 'confirm_remove_admin_' in content


# ===== FEATURE 2: Confirmation for dangerous actions =====

class TestConfirmation:

    def test_kick_shows_confirmation(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        assert 'confirm_kick_' in content
        assert 'cancel_action' in content

    def test_promo_delete_shows_confirmation(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        assert 'confirm_promo_del_' in content
        assert 'cancel_promo_del_p' in content
        assert 'CONFIRM_PROMO_DEL' in content

    def test_admin_remove_shows_confirmation(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        assert 'ADMIN_REMOVE_CONFIRM' in content
        assert 'confirm_remove_admin_' in content

    def test_confirm_handlers_registered(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        assert 'confirm_callbacks' in content
        assert 'lambda call: call.data.startswith("confirm_")' in content

    def test_cancel_action_handler(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        assert 'ACTION_CANCELLED' in content


# ===== FEATURE 3: Auto-edit payment with admin identity =====

class TestPaymentEdit:

    def test_texts_have_admin_param(self):
        from texts import TEXTS
        for lang in ("en", "uk", "ru"):
            text = TEXTS[lang]["ADMIN_ACCEPTED"]
            assert "{admin}" in text, f"ADMIN_ACCEPTED in {lang} missing admin param"
            assert "{date}" in text, f"ADMIN_ACCEPTED in {lang} missing date param"

    def test_texts_rejected_have_admin_param(self):
        from texts import TEXTS
        for lang in ("en", "uk", "ru"):
            text = TEXTS[lang]["ADMIN_REJECTED"]
            assert "{admin}" in text, f"ADMIN_REJECTED in {lang} missing admin param"
            assert "{date}" in text, f"ADMIN_REJECTED in {lang} missing date param"

    def test_start_handler_passes_admin_and_date(self):
        with open('handlers/start.py') as f:
            content = f.read()
        assert 'admin_username = call.from_user.username or str(call.from_user.id)' in content
        assert 'decision_date = datetime.now().strftime("%d.%m.%Y %H:%M")' in content
        # Check both approve and reject pass the params
        assert 'admin=admin_username, date=decision_date' in content

    def test_text_format_works(self):
        from texts import t
        result = t("en", "ADMIN_ACCEPTED", period="30 days", admin="testadmin", date="01.09.2026 16:00")
        assert "@testadmin" in result
        assert "01.09.2026 16:00" in result
        assert "30 days" in result

    def test_text_rejected_format_works(self):
        from texts import t
        result = t("uk", "ADMIN_REJECTED", admin="testadmin", date="01.09.2026 16:00")
        assert "@testadmin" in result
        assert "01.09.2026 16:00" in result


# ===== FEATURE 4: Refresh button in live monitor =====

class TestRefreshButton:

    def test_live_monitor_has_refresh(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        assert 'ADMIN_REFRESH' in content
        assert 'callback_data="admin_live_monitor"' in content

    def test_live_monitor_keyboard_row_width(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        # Check that we have a 2-button row for the live monitor
        assert 'InlineKeyboardMarkup(row_width=2)' in content


# ===== FEATURE 1 continued: bot.py admin commands =====

class TestBotCommands:

    def test_bot_sets_commands_for_db_admins(self):
        with open('bot.py') as f:
            content = f.read()
        assert 'from utils.db import get_admins' in content
        assert 'db_admins = get_admins()' in content
        assert 'for admin_id in admin_ids:' in content


# ===== Text keys for all languages =====

class TestTextKeys:

    def test_all_new_text_keys_exist(self):
        from texts import TEXTS
        new_keys = [
            "ADMIN_BTN_ADMINS", "ADMIN_ADMINS_TITLE", "ADMIN_ADMINS_EMPTY",
            "ADMIN_ADMINS_ADDED", "ADMIN_ADD_PROMPT", "ADMIN_ADD_NOT_FOUND",
            "ADMIN_ADD_ALREADY", "ADMIN_ADD_SUCCESS", "ADMIN_REMOVE_CONFIRM",
            "ADMIN_REMOVE_SUCCESS", "ADMIN_REMOVE_NOT_FOUND",
            "ADMIN_NEW_ADMIN_NOTIFY", "ADMIN_ONLY_OWNER",
            "CONFIRM_KICK", "ACTION_CANCELLED", "CONFIRM_PROMO_DEL"
        ]
        for lang in ("en", "uk", "ru"):
            for key in new_keys:
                assert key in TEXTS[lang], f"Missing text key {key} for language {lang}"

    def test_admin_notification_messages(self):
        from texts import TEXTS
        # English
        assert "control panel" in TEXTS["en"]["ADMIN_NEW_ADMIN_NOTIFY"].lower()
        # Ukrainian
        assert "панель керування" in TEXTS["uk"]["ADMIN_NEW_ADMIN_NOTIFY"].lower()
        # Russian
        assert "панель управления" in TEXTS["ru"]["ADMIN_NEW_ADMIN_NOTIFY"].lower()


# ===== Start.py admin check =====

class TestStartAdminCheck:

    def test_start_uses_check_admin(self):
        with open('handlers/start.py') as f:
            content = f.read()
        assert 'from utils.admin_check import is_admin as check_admin' in content
        assert 'check_admin(int(user_id))' in content


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-x", "-q"])
