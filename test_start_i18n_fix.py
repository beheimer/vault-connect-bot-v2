"""Tests for start.py i18n fix — hardcoded strings moved to texts.py."""
import pytest
import inspect
from texts import t, TEXTS, ALL_ADMIN_PANEL


# ── New keys exist in all 3 locales ──
NEW_KEYS = [
    "PRICE_SUFFIX_MONTHLY",
    "PRICE_SUFFIX_FOREVER",
    "BTN_CUSTOM_DAYS",
    "BTN_ADMIN_PANEL",
]


@pytest.mark.parametrize("lang", ["en", "uk", "ru"])
@pytest.mark.parametrize("key", NEW_KEYS)
def test_key_exists_in_all_langs(lang, key):
    assert key in TEXTS[lang], f"Key {key!r} missing in {lang!r}"


# ── Values are correct per locale ──
def test_price_suffix_monthly_values():
    assert TEXTS["en"]["PRICE_SUFFIX_MONTHLY"] == "/month"
    assert TEXTS["uk"]["PRICE_SUFFIX_MONTHLY"] == "/міс."
    assert TEXTS["ru"]["PRICE_SUFFIX_MONTHLY"] == "/мес."


def test_price_suffix_forever_values():
    assert TEXTS["en"]["PRICE_SUFFIX_FOREVER"] == "— forever"
    assert TEXTS["uk"]["PRICE_SUFFIX_FOREVER"] == "— назавжди"
    assert TEXTS["ru"]["PRICE_SUFFIX_FOREVER"] == "— навсегда"


def test_btn_custom_days_values():
    assert TEXTS["en"]["BTN_CUSTOM_DAYS"] == "✏️ Custom days"
    assert TEXTS["uk"]["BTN_CUSTOM_DAYS"] == "✏️ Вказати дні"
    assert TEXTS["ru"]["BTN_CUSTOM_DAYS"] == "✏️ Указать дни"


def test_btn_admin_panel_values():
    assert TEXTS["en"]["BTN_ADMIN_PANEL"] == "🛠 Admin Panel"
    assert TEXTS["uk"]["BTN_ADMIN_PANEL"] == "🛠 Адмін панель"
    assert TEXTS["ru"]["BTN_ADMIN_PANEL"] == "🛠 Админ панель"


# ── ALL_ADMIN_PANEL convenience list ──
def test_all_admin_panel_list():
    assert len(ALL_ADMIN_PANEL) == 3
    assert "🛠 Admin Panel" in ALL_ADMIN_PANEL
    assert "🛠 Адмін панель" in ALL_ADMIN_PANEL
    assert "🛠 Админ панель" in ALL_ADMIN_PANEL


# ── t() returns correct values ──
def test_t_returns_price_suffix():
    assert t("en", "PRICE_SUFFIX_MONTHLY") == "/month"
    assert t("uk", "PRICE_SUFFIX_FOREVER") == "— назавжди"
    assert t("ru", "BTN_CUSTOM_DAYS") == "✏️ Указать дни"


# ── No hardcoded strings remain in start.py ──
def test_no_hardcoded_admin_panel_dict():
    from handlers import start
    source = inspect.getsource(start)
    # The old inline dict pattern must be gone
    assert '"uk": "🛠 Адмін панель"' not in source
    assert '"ru": "🛠 Админ панель"' not in source


def test_no_hardcoded_price_suffix_dict():
    from handlers import start
    source = inspect.getsource(start)
    assert '"uk": "/міс."' not in source
    assert '"ru": "/мес."' not in source
    assert '"uk": "— назавжди"' not in source
    assert '"ru": "— навсегда"' not in source


def test_no_hardcoded_custom_days_dict():
    from handlers import start
    source = inspect.getsource(start)
    assert '"uk": "✏️ Вказати дні"' not in source
    assert '"ru": "✏️ Указать дни"' not in source


def test_no_hardcoded_admin_panel_in_register():
    from handlers import start
    source = inspect.getsource(start)
    assert '["🛠 Адмін панель"' not in source
    assert '"🛠 Admin Panel"]' not in source


# ── Verify start.py uses t() and ALL_ADMIN_PANEL ──
def test_start_uses_t_for_btn_admin_panel():
    from handlers import start
    source = inspect.getsource(start)
    assert 't(_al, "BTN_ADMIN_PANEL")' in source


def test_start_uses_t_for_price_suffix():
    from handlers import start
    source = inspect.getsource(start)
    assert 't(lang, "PRICE_SUFFIX_MONTHLY")' in source
    assert 't(lang, "PRICE_SUFFIX_FOREVER")' in source


def test_start_uses_t_for_btn_custom_days():
    from handlers import start
    source = inspect.getsource(start)
    assert 't(get_lang(ADMIN_ID), "BTN_CUSTOM_DAYS")' in source


def test_start_uses_all_admin_panel():
    from handlers import start
    source = inspect.getsource(start)
    assert 'ALL_ADMIN_PANEL' in source


# ── Module imports cleanly ──
def test_modules_import():
    from handlers.start import register_handlers
    from texts import ALL_ADMIN_PANEL
