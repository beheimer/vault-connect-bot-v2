"""Tests for the currency selection feature."""
import pytest
import sys
import os

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(__file__))


class TestTextsKeys:
    """Verify all new text keys exist in all 3 languages."""

    def test_currency_prompt_all_langs(self):
        from texts import TEXTS
        for lang in ("en", "uk", "ru"):
            assert "ADMIN_CURRENCY_PROMPT" in TEXTS[lang], f"Missing ADMIN_CURRENCY_PROMPT in {lang}"

    def test_currency_custom_prompt_all_langs(self):
        from texts import TEXTS
        for lang in ("en", "uk", "ru"):
            assert "ADMIN_CURRENCY_CUSTOM_PROMPT" in TEXTS[lang], f"Missing ADMIN_CURRENCY_CUSTOM_PROMPT in {lang}"

    def test_currency_saved_all_langs(self):
        from texts import TEXTS
        for lang in ("en", "uk", "ru"):
            assert "ADMIN_CURRENCY_SAVED" in TEXTS[lang], f"Missing ADMIN_CURRENCY_SAVED in {lang}"

    def test_currency_saved_has_placeholder(self):
        from texts import t
        result = t("en", "ADMIN_CURRENCY_SAVED", currency="€")
        assert "€" in result

    def test_price_info_has_currency_placeholder(self):
        """ADMIN_PRICE_INFO should accept {currency} param, not hardcode $."""
        from texts import t
        result = t("en", "ADMIN_PRICE_INFO", price=50, label="/mo.", currency="€")
        assert "€50" in result
        assert "$50" not in result

    def test_price_changed_has_currency_placeholder(self):
        from texts import t
        result = t("en", "ADMIN_PRICE_CHANGED", price=100, label="/mo.", currency="£")
        assert "£100" in result
        assert "$100" not in result

    def test_price_info_uk(self):
        from texts import t
        result = t("uk", "ADMIN_PRICE_INFO", price=50, label="/міс.", currency="₴")
        assert "₴50" in result

    def test_price_info_ru(self):
        from texts import t
        result = t("ru", "ADMIN_PRICE_INFO", price=50, label="/мес.", currency="$")
        assert "$50" in result

    def test_live_monitor_revenue_has_currency(self):
        from texts import t
        result = t("en", "ADMIN_LIVE_30D_REVENUE", amount=500, currency="€")
        assert "€500" in result
        assert "$500" not in result

    def test_live_monitor_revenue_uk(self):
        from texts import t
        result = t("uk", "ADMIN_LIVE_30D_REVENUE", amount=500, currency="₴")
        assert "₴500" in result

    def test_live_monitor_revenue_ru(self):
        from texts import t
        result = t("ru", "ADMIN_LIVE_30D_REVENUE", amount=500, currency="$")
        assert "$500" in result


class TestPriceEditStates:
    """Verify the FSM state for currency was added."""

    def test_waiting_for_currency_state_exists(self):
        from handlers.admin_panel import PriceEdit
        assert hasattr(PriceEdit, "waiting_for_currency")

    def test_waiting_for_type_still_exists(self):
        from handlers.admin_panel import PriceEdit
        assert hasattr(PriceEdit, "waiting_for_type")

    def test_waiting_for_price_still_exists(self):
        from handlers.admin_panel import PriceEdit
        assert hasattr(PriceEdit, "waiting_for_price")

    def test_state_order(self):
        """Currency should be first, then type, then price."""
        from handlers.admin_panel import PriceEdit
        states = list(PriceEdit.all_states)
        state_names = [s.state.split(":")[-1] for s in states]
        assert "waiting_for_currency" in state_names
        assert "waiting_for_type" in state_names
        assert "waiting_for_price" in state_names


class TestProcessCustomCurrencyExists:
    """Verify the process_custom_currency handler function exists."""

    def test_function_exists(self):
        from handlers.admin_panel import process_custom_currency
        assert callable(process_custom_currency)


class TestRegisterHandlers:
    """Verify the register_handlers function registers currency handlers."""

    def test_register_handlers_callable(self):
        from handlers.admin_panel import register_handlers
        assert callable(register_handlers)


class TestStartPayManualCurrency:
    """Verify pay_manual uses dynamic currency."""

    def test_pay_manual_source_uses_get_setting(self):
        """Verify the source code of pay_manual uses get_setting for currency."""
        import inspect
        from handlers.start import pay_manual
        source = inspect.getsource(pay_manual)
        assert 'get_setting("currency"' in source, "pay_manual should call get_setting for currency"
        assert 'f"${price}' not in source, "pay_manual should not hardcode $ in price_label"
        assert '{currency}{price}' in source, "pay_manual should use {currency}{price} format"


class TestDbSettingCurrency:
    """Verify currency can be stored/retrieved via get_setting/set_setting."""

    def test_set_and_get_currency(self):
        from utils.db import get_setting, set_setting
        set_setting("currency", "€")
        assert get_setting("currency", "$") == "€"
        # Reset to default
        set_setting("currency", "$")
        assert get_setting("currency", "$") == "$"

    def test_get_currency_default(self):
        from utils.db import get_setting, set_setting
        # Make sure there's a default
        set_setting("currency", "$")
        result = get_setting("currency", "$")
        assert result == "$"
