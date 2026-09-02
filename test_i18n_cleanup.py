"""Tests for i18n cleanup — verify all hardcoded strings replaced with t() keys."""
import pytest
from texts import t, TEXTS


# ── Verify all new keys exist in all 3 languages ──
NEW_KEYS = [
    "TRIAL_CONFIRM_TITLE",
    "TRIAL_CONFIRM_DURATION",
    "TRIAL_CONFIRM_START",
    "TRIAL_CONFIRM_END",
    "TRIAL_CONFIRM_NOTE",
    "BTN_ACTIVATE_TRIAL",
    "DURATION_DAYS_HOURS",
    "DURATION_DAYS",
    "DURATION_HOURS",
    "ACCESS_TIME",
    "ACCESS_TIME_ZERO",
    "ERR_POSITIVE_INT",
    "MSG_FORMAT",
    "MSG_NOT_FOUND",
    "MSG_SENT",
    "MSG_FAILED",
    "LANG_SET",
]


@pytest.mark.parametrize("lang", ["uk", "ru", "en"])
@pytest.mark.parametrize("key", NEW_KEYS)
def test_key_exists_in_all_langs(lang, key):
    """Every new key must be present in uk, ru, and en."""
    assert key in TEXTS[lang], f"Key {key!r} missing in {lang!r}"


# ── Verify keys are different across languages (not copy-paste) ──
def test_trial_confirm_title_differs():
    assert TEXTS["uk"]["TRIAL_CONFIRM_TITLE"] != TEXTS["en"]["TRIAL_CONFIRM_TITLE"]
    assert TEXTS["ru"]["TRIAL_CONFIRM_TITLE"] != TEXTS["en"]["TRIAL_CONFIRM_TITLE"]


def test_btn_activate_trial_differs():
    assert TEXTS["uk"]["BTN_ACTIVATE_TRIAL"] != TEXTS["en"]["BTN_ACTIVATE_TRIAL"]
    assert TEXTS["ru"]["BTN_ACTIVATE_TRIAL"] != TEXTS["en"]["BTN_ACTIVATE_TRIAL"]


def test_lang_set_differs():
    assert TEXTS["uk"]["LANG_SET"] != TEXTS["en"]["LANG_SET"]
    assert TEXTS["ru"]["LANG_SET"] != TEXTS["en"]["LANG_SET"]
    assert TEXTS["uk"]["LANG_SET"] != TEXTS["ru"]["LANG_SET"]


def test_err_positive_int_differs():
    assert TEXTS["uk"]["ERR_POSITIVE_INT"] != TEXTS["en"]["ERR_POSITIVE_INT"]
    assert TEXTS["ru"]["ERR_POSITIVE_INT"] != TEXTS["en"]["ERR_POSITIVE_INT"]


def test_msg_format_differs():
    assert TEXTS["uk"]["MSG_FORMAT"] != TEXTS["en"]["MSG_FORMAT"]
    assert TEXTS["ru"]["MSG_FORMAT"] != TEXTS["en"]["MSG_FORMAT"]


# ── Verify format placeholders work ──
def test_duration_days_hours_format():
    assert "5" in t("uk", "DURATION_DAYS_HOURS", days=5, rem=3)
    assert "3" in t("uk", "DURATION_DAYS_HOURS", days=5, rem=3)
    assert "5d 3h" == t("en", "DURATION_DAYS_HOURS", days=5, rem=3)


def test_duration_days_format():
    assert t("en", "DURATION_DAYS", days=7) == "7 days"
    assert t("uk", "DURATION_DAYS", days=7) == "7 дн."


def test_duration_hours_format():
    assert t("en", "DURATION_HOURS", hours=12) == "12 hours"
    assert t("uk", "DURATION_HOURS", hours=12) == "12 год."
    assert t("ru", "DURATION_HOURS", hours=12) == "12 ч."


def test_access_time_format():
    assert t("en", "ACCESS_TIME", days=3, hours=5) == "3d 5h"
    assert t("uk", "ACCESS_TIME", days=3, hours=5) == "3д 5г"


def test_access_time_zero():
    assert t("en", "ACCESS_TIME_ZERO") == "0d 0h"
    assert t("uk", "ACCESS_TIME_ZERO") == "0д 0г"


def test_trial_confirm_duration_format():
    result = t("uk", "TRIAL_CONFIRM_DURATION", duration="5 дн.")
    assert "5 дн." in result


def test_trial_confirm_end_format():
    result = t("en", "TRIAL_CONFIRM_END", end_time="01.09.2026 17:00")
    assert "01.09.2026 17:00" in result


def test_msg_sent_format():
    assert "@testuser" in t("en", "MSG_SENT", username="testuser")
    assert "@testuser" in t("uk", "MSG_SENT", username="testuser")


def test_msg_failed_format():
    assert "timeout" in t("en", "MSG_FAILED", error="timeout")


# ── Verify no hardcoded strings remain in handler sources ──
def test_no_hardcoded_strings_in_start():
    import inspect
    from handlers import start
    source = inspect.getsource(start)
    
    # Trial confirm text should not be inline
    assert "Пробний доступ\\n\\n" not in source
    assert "Пробный доступ\\n\\n" not in source
    assert "Trial Access\\n\\n" not in source
    
    # Buttons should use t()
    assert '"✅ Активувати"' not in source
    assert '"✅ Активировать"' not in source
    assert '"❌ Скасувати"' not in source
    
    # Duration text should use t()
    assert 'f"{days} дн. {rem} год."' not in source
    assert 'f"{days}d {rem}h"' not in source
    
    # Access time
    assert '"0d 0h"' not in source
    assert '"0д 0г"' not in source
    
    # Custom days error
    assert '"❌ Введи ціле число більше 0."' not in source
    
    # Lang set
    assert '"✅ Language set: English"' not in source
    assert '"✅ Мову обрано: Українська"' not in source


# ── Verify modules import cleanly ──
def test_modules_import():
    from handlers.start import register_handlers
    from handlers.admin_panel import register_handlers
