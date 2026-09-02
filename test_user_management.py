"""Tests for user management improvements in admin_panel.py"""
import sys
import os
import re
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from texts import t, TEXTS
from handlers.admin_panel import (
    DmUser, KickUser, AdminAdd, ResetTrial,
    paginate, _parse_page, _nav_buttons, ITEMS_PER_PAGE
)


class TestTextKeys:
    """Verify all new text keys exist in all 3 languages."""

    REQUIRED_KEYS = [
        'USER_DETAIL_TITLE', 'USER_JOINED', 'USER_STATUS', 'USER_ACCESS_UNTIL',
        'BTN_DM', 'BTN_RESET_TRIAL', 'BTN_KICK',
        'CONFIRM_RESET_TRIAL', 'RESET_TRIAL_DONE',
        'DM_PROMPT', 'DM_SENT', 'DM_FAILED',
        'ADMIN_REVOKED',
    ]

    def test_all_keys_exist_in_all_languages(self):
        for lang in ['en', 'uk', 'ru']:
            for key in self.REQUIRED_KEYS:
                assert key in TEXTS[lang], f"Missing key '{key}' in lang '{lang}'"

    def test_keys_are_not_empty(self):
        for lang in ['en', 'uk', 'ru']:
            for key in self.REQUIRED_KEYS:
                assert TEXTS[lang][key].strip(), f"Empty value for '{key}' in '{lang}'"

    def test_format_placeholders_work(self):
        for lang in ['en', 'uk', 'ru']:
            assert '{date}' not in t(lang, 'USER_JOINED', date='2025-01-01')
            assert '{mode}' not in t(lang, 'USER_STATUS', mode='FULL')
            assert '{date}' not in t(lang, 'USER_ACCESS_UNTIL', date='2025-12-31')
            assert '{username}' not in t(lang, 'CONFIRM_RESET_TRIAL', username='testuser')
            assert '{username}' not in t(lang, 'RESET_TRIAL_DONE', username='testuser')
            assert '{error}' not in t(lang, 'DM_FAILED', error='timeout')

    def test_admin_revoked_all_languages(self):
        assert '🔒' in t('en', 'ADMIN_REVOKED')
        assert '🔒' in t('uk', 'ADMIN_REVOKED')
        assert '🔒' in t('ru', 'ADMIN_REVOKED')
        assert 'revoked' in t('en', 'ADMIN_REVOKED').lower()
        assert 'скасовані' in t('uk', 'ADMIN_REVOKED').lower()
        assert 'отозваны' in t('ru', 'ADMIN_REVOKED').lower()

    def test_user_detail_title_languages(self):
        assert 'User Info' in t('en', 'USER_DETAIL_TITLE')
        assert 'Інформація про користувача' in t('uk', 'USER_DETAIL_TITLE')
        assert 'Информация о пользователе' in t('ru', 'USER_DETAIL_TITLE')


class TestDmUserFSM:
    """Verify DmUser FSM state is properly defined."""

    def test_dm_user_state_exists(self):
        assert hasattr(DmUser, 'waiting_for_text')

    def test_dm_user_state_name(self):
        assert 'DmUser:waiting_for_text' in str(DmUser.waiting_for_text)


class TestPagination:
    """Verify pagination works correctly for user list."""

    def test_paginate_basic(self):
        items = list(range(20))
        page_items, total = paginate(items, 0)
        assert len(page_items) == ITEMS_PER_PAGE
        assert total == 3  # ceil(20/8) = 3

    def test_paginate_last_page(self):
        items = list(range(20))
        page_items, total = paginate(items, 2)
        assert len(page_items) == 4  # 20 - 16 = 4
        assert total == 3

    def test_paginate_empty(self):
        page_items, total = paginate([], 0)
        assert len(page_items) == 0
        assert total == 1

    def test_paginate_single_page(self):
        items = list(range(5))
        page_items, total = paginate(items, 0)
        assert len(page_items) == 5
        assert total == 1


class TestCallbackParsing:
    """Test callback data parsing for user detail view."""

    def test_parse_page_from_admin_users(self):
        assert _parse_page("admin_users_p3", "admin_users") == 3
        assert _parse_page("admin_users_p0", "admin_users") == 0
        assert _parse_page("admin_users", "admin_users") == 0

    def test_admin_user_callback_pattern(self):
        """Verify admin_user_{uid}_p{page} regex matches."""
        pattern = r'admin_user_(\d+)_p(\d+)'
        m = re.match(pattern, 'admin_user_123456_p2')
        assert m is not None
        assert m.group(1) == '123456'
        assert m.group(2) == '2'

    def test_admin_dm_callback_pattern(self):
        pattern = r'admin_dm_(\d+)_p(\d+)'
        m = re.match(pattern, 'admin_dm_789_p1')
        assert m is not None
        assert m.group(1) == '789'
        assert m.group(2) == '1'

    def test_confirm_reset_trial_callback_pattern(self):
        pattern = r'confirm_reset_trial_(\d+)_p(\d+)'
        m = re.match(pattern, 'confirm_reset_trial_456_p0')
        assert m is not None
        assert m.group(1) == '456'
        assert m.group(2) == '0'

    def test_do_reset_trial_callback_pattern(self):
        pattern = r'do_reset_trial_(\d+)_p(\d+)'
        m = re.match(pattern, 'do_reset_trial_456_p0')
        assert m is not None
        assert m.group(1) == '456'
        assert m.group(2) == '0'


class TestRegisterHandlers:
    """Verify that new handlers are registered."""

    def test_source_has_dm_user_registration(self):
        with open(os.path.join(os.path.dirname(__file__), 'handlers', 'admin_panel.py')) as f:
            src = f.read()
        assert 'DmUser.waiting_for_text' in src
        assert 'process_dm_text' in src

    def test_source_has_confirm_reset_trial(self):
        with open(os.path.join(os.path.dirname(__file__), 'handlers', 'admin_panel.py')) as f:
            src = f.read()
        assert 'confirm_reset_trial_' in src
        assert 'do_reset_trial_' in src

    def test_source_has_admin_revoked_notification(self):
        with open(os.path.join(os.path.dirname(__file__), 'handlers', 'admin_panel.py')) as f:
            src = f.read()
        assert 'ADMIN_REVOKED' in src

    def test_confirm_callbacks_matches_do_reset_trial(self):
        with open(os.path.join(os.path.dirname(__file__), 'handlers', 'admin_panel.py')) as f:
            src = f.read()
        assert 'do_reset_trial_' in src
        # Check it's in the lambda for confirm_callbacks registration
        assert "call.data.startswith(\"do_reset_trial_\")" in src

    def test_user_detail_view_has_kick_dm_reset(self):
        with open(os.path.join(os.path.dirname(__file__), 'handlers', 'admin_panel.py')) as f:
            src = f.read()
        assert 'BTN_KICK' in src
        assert 'BTN_DM' in src
        assert 'BTN_RESET_TRIAL' in src

    def test_admin_user_callback_handler_exists(self):
        with open(os.path.join(os.path.dirname(__file__), 'handlers', 'admin_panel.py')) as f:
            src = f.read()
        assert 'call.data.startswith("admin_user_")' in src

    def test_admin_dm_callback_handler_exists(self):
        with open(os.path.join(os.path.dirname(__file__), 'handlers', 'admin_panel.py')) as f:
            src = f.read()
        assert 'call.data.startswith("admin_dm_")' in src

    def test_admin_users_excludes_user_detail(self):
        """admin_users handler should NOT match admin_user_ (detail view)."""
        with open(os.path.join(os.path.dirname(__file__), 'handlers', 'admin_panel.py')) as f:
            src = f.read()
        assert 'call.data.startswith("admin_users") and not call.data.startswith("admin_user_")' in src


class TestImportIntegrity:
    """Verify the module can be fully imported without errors."""

    def test_full_import(self):
        from handlers.admin_panel import (
            register_handlers, admin_callbacks, confirm_callbacks,
            process_dm_text, DmUser
        )
        assert callable(register_handlers)
        assert callable(admin_callbacks)
        assert callable(confirm_callbacks)
        assert callable(process_dm_text)

    def test_start_import(self):
        from handlers.start import register_handlers
        assert callable(register_handlers)
