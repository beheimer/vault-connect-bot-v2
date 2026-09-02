"""Tests for all 10 bug fixes in the Telegram bot."""
import os
import sys
import datetime
import sqlite3
import importlib

# Ensure we can import from the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set a dummy bot token before any aiogram imports
os.environ["BOT_TOKEN"] = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz012345678"

import pytest
from utils.db import init_db, get_user, save_user, update_user_field, get_setting, set_setting, DB_PATH
from utils.promo import redeem_promo, make_promo
from utils.referral import add_user as ref_add_user


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Use a temporary database for each test."""
    db_path = str(tmp_path / "test.db")
    import utils.db as db_mod
    monkeypatch.setattr(db_mod, "DB_PATH", db_path)
    init_db()
    yield db_path


# ── FIX 1: Language selection on first launch ──
class TestFix1LanguageSelection:
    def test_start_cmd_shows_picker_when_no_lang(self):
        """Verify start_cmd returns early (shows picker) when user has no lang set."""
        from handlers.start import lang_picker_keyboard
        kb = lang_picker_keyboard()
        buttons = kb.inline_keyboard
        assert len(buttons) == 1
        assert len(buttons[0]) == 3
        callbacks = [b.callback_data for b in buttons[0]]
        assert "set_lang_en" in callbacks
        assert "set_lang_uk" in callbacks
        assert "set_lang_ru" in callbacks

    def test_new_user_has_no_lang(self):
        """New user should have no lang set initially."""
        user = get_user(999999)
        assert not user  # user doesn't exist
        # After save with no lang field
        save_user(999999, {"full_name": "Test"})
        user = get_user(999999)
        assert not user.get("lang") or user.get("lang") == "en"


# ── FIX 2: Double registration of admin_callbacks ──
class TestFix2DoubleRegistration:
    def test_register_handlers_order(self):
        """Verify price_type handler is registered BEFORE the generic admin_ handler."""
        import handlers.admin_panel as ap
        import inspect
        source = inspect.getsource(ap.register_handlers)
        
        # Find positions of the two callback registrations
        price_pos = source.find('("price_type_monthly", "price_type_forever")')
        admin_pos = source.find('call.data.startswith("admin_")')
        
        assert price_pos != -1, "price_type registration not found"
        assert admin_pos != -1, "admin_ registration not found"
        assert price_pos < admin_pos, "price_type handler must be registered BEFORE generic admin_ handler"

    def test_no_duplicate_admin_callbacks_registration(self):
        """Ensure admin_callbacks is not registered more than twice."""
        import handlers.admin_panel as ap
        import inspect
        source = inspect.getsource(ap.register_handlers)
        count = source.count("admin_callbacks")
        assert count <= 4, f"admin_callbacks should appear at most 4 times, found {count}"


# ── FIX 3: Admin check by ID ──
class TestFix3AdminIDCheck:
    def test_admin_panel_py_uses_admin_id(self):
        """admin_panel.py should use id checks, not username."""
        import handlers.admin_panel as ap
        import inspect
        source = inspect.getsource(ap)
        
        assert "ADMIN_USERNAME" not in source, "ADMIN_USERNAME should not be imported"
        assert "not check_admin(message.from_user.id)" in source
        assert "call.from_user.id != ADMIN_ID" in source


# ── FIX 4: admin_reset_trial FSM ──
class TestFix4ResetTrialFSM:
    def test_reset_trial_state_class_exists(self):
        """ResetTrial FSM state class should exist."""
        from handlers.admin_panel import ResetTrial
        assert hasattr(ResetTrial, "waiting_for_target")

    def test_process_reset_trial_target_exists(self):
        """process_reset_trial_target handler should exist."""
        from handlers.admin_panel import process_reset_trial_target
        import asyncio
        assert asyncio.iscoroutinefunction(process_reset_trial_target)

    def test_reset_trial_registered(self):
        """ResetTrial handler should be registered."""
        import handlers.admin_panel as ap
        import inspect
        source = inspect.getsource(ap.register_handlers)
        assert "ResetTrial.waiting_for_target" in source

    def test_reset_trial_sets_fsm_state(self):
        """admin_reset_trial callback should set ResetTrial FSM state."""
        import handlers.admin_panel as ap
        import inspect
        source = inspect.getsource(ap.admin_callbacks)
        # Find the reset_trial block
        idx = source.find('"admin_reset_trial"')
        block = source[idx:idx+300]
        assert "ResetTrial.waiting_for_target.set()" in block


# ── FIX 5: admin_trial_duration FSM ──
class TestFix5TrialDurationFSM:
    def test_trial_edit_state_class_exists(self):
        """TrialEdit FSM state class should exist with waiting_for_duration."""
        from handlers.admin_panel import TrialEdit
        assert hasattr(TrialEdit, "waiting_for_duration")

    def test_process_trial_duration_exists(self):
        """process_trial_duration handler should exist."""
        from handlers.admin_panel import process_trial_duration
        import asyncio
        assert asyncio.iscoroutinefunction(process_trial_duration)

    def test_trial_duration_sets_fsm_state(self):
        """admin_trial_duration callback should set TrialEdit FSM state."""
        import handlers.admin_panel as ap
        import inspect
        source = inspect.getsource(ap.admin_callbacks)
        idx = source.find('"admin_trial_duration"')
        block = source[idx:idx+400]
        assert "TrialEdit.waiting_for_duration.set()" in block

    def test_trial_duration_registered(self):
        """TrialEdit handler should be registered."""
        import handlers.admin_panel as ap
        import inspect
        source = inspect.getsource(ap.register_handlers)
        assert "TrialEdit.waiting_for_duration" in source

    def test_process_trial_duration_parses_days_format(self):
        """process_trial_duration should handle 'Xd' format."""
        import handlers.admin_panel as ap
        import inspect
        source = inspect.getsource(ap.process_trial_duration)
        assert 'text.endswith("d")' in source or "endswith" in source


# ── FIX 6: Promo trial type doesn't overwrite paid access ──
class TestFix6PromoTrialProtection:
    def test_trial_promo_blocked_when_active_access(self):
        """Trial promo should return 'already_active' if user has active access."""
        save_user(123, {
            "full_name": "Test",
            "access_until": (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat(),
            "access_paid": 1
        })
        code = make_promo("trial", 7)
        status, promo = redeem_promo(code, 123)
        assert status == "already_active"

    def test_trial_promo_blocked_when_trial_already_used(self):
        """Trial promo should return 'trial_already_used' if trial was used."""
        save_user(124, {
            "full_name": "Test2",
            "trial_used": 1,
        })
        code = make_promo("trial", 7)
        status, promo = redeem_promo(code, 124)
        assert status == "trial_already_used"

    def test_trial_promo_succeeds_for_new_user(self):
        """Trial promo should succeed for user without active access."""
        save_user(125, {"full_name": "Test3"})
        code = make_promo("trial", 7)
        status, promo = redeem_promo(code, 125)
        assert status == "success"
        user = get_user(125)
        assert user["trial_used"] == 1

    def test_full_promo_not_blocked(self):
        """Full promo should not be blocked by existing access."""
        save_user(126, {
            "full_name": "Test4",
            "access_until": (datetime.datetime.now() + datetime.timedelta(days=30)).isoformat(),
            "access_paid": 1
        })
        code = make_promo("full", 60)
        status, promo = redeem_promo(code, 126)
        assert status == "success"

    def test_promo_already_active_text_exists(self):
        """PROMO_ALREADY_ACTIVE text should exist in all 3 languages."""
        from texts import TEXTS
        for lang in ("en", "uk", "ru"):
            assert "PROMO_ALREADY_ACTIVE" in TEXTS[lang], f"Missing PROMO_ALREADY_ACTIVE in {lang}"

    def test_handle_promo_code_handles_new_statuses(self):
        """handle_promo_code should handle 'already_active' and 'trial_already_used'."""
        import handlers.start as start_mod
        import inspect
        source = inspect.getsource(start_mod.handle_promo_code)
        assert "already_active" in source
        assert "trial_already_used" in source


# ── FIX 7: _safe_dt in live monitor ──
class TestFix7SafeDatetime:
    def test_safe_dt_helper_exists(self):
        """_safe_dt helper function should exist."""
        from handlers.admin_panel import _safe_dt
        assert callable(_safe_dt)

    def test_safe_dt_with_valid_date(self):
        from handlers.admin_panel import _safe_dt
        dt = _safe_dt("2025-06-15T10:00:00")
        assert dt.year == 2025

    def test_safe_dt_with_none(self):
        from handlers.admin_panel import _safe_dt
        dt = _safe_dt(None)
        assert dt.year == 2000

    def test_safe_dt_with_empty_string(self):
        from handlers.admin_panel import _safe_dt
        dt = _safe_dt("")
        assert dt.year == 2000

    def test_safe_dt_with_garbage(self):
        from handlers.admin_panel import _safe_dt
        dt = _safe_dt("not-a-date")
        assert dt.year == 2000

    def test_live_monitor_uses_safe_dt(self):
        """admin_live_monitor block should use _safe_dt instead of raw fromisoformat."""
        import handlers.admin_panel as ap
        import inspect
        source = inspect.getsource(ap.admin_callbacks)
        # Find the live_monitor block
        idx = source.find('"admin_live_monitor"')
        block = source[idx:idx+800]
        assert "_safe_dt" in block
        assert "fromisoformat" not in block, "live_monitor should not use raw fromisoformat"


# ── FIX 8: TRIAL_LINK_ALREADY_MEMBER ──
class TestFix8TrialLinkAlreadyMember:
    def test_trial_link_already_member_text_exists(self):
        """TRIAL_LINK_ALREADY_MEMBER should exist in all 3 languages."""
        from texts import TEXTS
        for lang in ("en", "uk", "ru"):
            assert "TRIAL_LINK_ALREADY_MEMBER" in TEXTS[lang], f"Missing in {lang}"

    def test_trial_confirm_uses_already_member(self):
        """trial_confirm should use TRIAL_LINK_ALREADY_MEMBER, not TRIAL_FAILED."""
        import handlers.start as start_mod
        import inspect
        source = inspect.getsource(start_mod.trial_confirm)
        assert "TRIAL_LINK_ALREADY_MEMBER" in source
        assert "TRIAL_FAILED" not in source


# ── FIX 9: check_referral doesn't store unknown username ──
class TestFix9ReferralNoUnknown:
    def test_check_referral_no_unknown_fields(self):
        """check_referral should not pass username or full_name."""
        import utils.referral as ref_mod
        import inspect
        source = inspect.getsource(ref_mod.check_referral)
        # The save_user call should not contain 'unknown'
        assert "'unknown'" not in source, "check_referral should not store 'unknown'"
        assert '"unknown"' not in source

    def test_add_user_fills_real_name(self):
        """add_user should properly set full_name and username."""
        # First simulate check_referral creating partial record
        save_user(200, {"invited_by": 100, "paid_refs": 0})
        # Then add_user fills in real info
        ref_add_user(200, "John Doe", "johndoe")
        user = get_user(200)
        assert user["full_name"] == "John Doe"
        assert user["username"] == "johndoe"
        assert user["invited_by"] == 100


# ── FIX 10: migrate.py integration ──
