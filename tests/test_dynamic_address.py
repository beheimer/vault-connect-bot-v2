"""Tests for dynamic crypto address management feature."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from texts import t, TEXTS


# ── Text key tests ──

class TestTextKeys:
    """Verify all required text keys exist in all 3 languages."""

    REQUIRED_KEYS = [
        "CRYPTO_INFO_DYNAMIC",
        "ADMIN_ADDRESS_PROMPT",
        "ADMIN_ADDRESS_SET",
        "ADMIN_ADDRESS_INVALID",
        "ADMIN_ADDRESS_PROMPT_FLOW",
        "ADMIN_ADDRESS_SKIPPED",
        "SHOW_QR",
        "HIDE_QR",
    ]

    @pytest.mark.parametrize("lang", ["en", "uk", "ru"])
    def test_keys_present(self, lang):
        for key in self.REQUIRED_KEYS:
            assert key in TEXTS[lang], f"Missing key '{key}' in lang '{lang}'"

    @pytest.mark.parametrize("lang", ["en", "uk", "ru"])
    def test_crypto_info_dynamic_has_address_placeholder(self, lang):
        text = TEXTS[lang]["CRYPTO_INFO_DYNAMIC"]
        assert "{address}" in text

    @pytest.mark.parametrize("lang", ["en", "uk", "ru"])
    def test_address_set_has_address_placeholder(self, lang):
        text = TEXTS[lang]["ADMIN_ADDRESS_SET"]
        assert "{address}" in text

    def test_t_function_formats_address(self):
        result = t("en", "CRYPTO_INFO_DYNAMIC", address="T1234567890abcdefghijklmnopqrstuvw")
        assert "T1234567890abcdefghijklmnopqrstuvw" in result

    def test_t_function_fallback_to_en(self):
        result = t("xx", "ADMIN_ADDRESS_PROMPT_FLOW")
        assert result == TEXTS["en"]["ADMIN_ADDRESS_PROMPT_FLOW"]


# ── FSM structure tests ──

class TestFSMStructure:
    """Verify PriceEdit FSM has the correct states."""

    def test_price_edit_has_waiting_for_address(self):
        from handlers.admin_panel import PriceEdit
        states = [s.state for s in PriceEdit.states]
        assert "PriceEdit:waiting_for_address" in states

    def test_price_edit_has_all_states(self):
        from handlers.admin_panel import PriceEdit
        state_names = [s.state.split(":")[-1] for s in PriceEdit.states]
        assert "waiting_for_currency" in state_names
        assert "waiting_for_type" in state_names
        assert "waiting_for_price" in state_names
        assert "waiting_for_address" in state_names

    def test_no_standalone_address_edit(self):
        """AddressEdit class should NOT exist anymore."""
        import handlers.admin_panel as ap
        assert not hasattr(ap, "AddressEdit"), "AddressEdit should be removed"


# ── Admin keyboard tests ──

class TestAdminKeyboard:
    """Verify the admin keyboard no longer has a standalone Crypto Address button."""

    def test_no_address_button_in_keyboard(self):
        from handlers.admin_panel import get_admin_keyboard
        kb = get_admin_keyboard("en")
        all_callbacks = []
        for row in kb.inline_keyboard:
            for btn in row:
                all_callbacks.append(btn.callback_data)
        assert "admin_set_address" not in all_callbacks

    def test_price_button_still_exists(self):
        from handlers.admin_panel import get_admin_keyboard
        kb = get_admin_keyboard("en")
        all_callbacks = []
        for row in kb.inline_keyboard:
            for btn in row:
                all_callbacks.append(btn.callback_data)
        assert "admin_set_price" in all_callbacks


# ── Address validation tests ──

class TestAddressValidation:
    VALID_ADDRESSES = [
        "TEwnPR7daATh84DLFiTXJGaCge4NbYDbV8",
        "T1234567890abcdefghijklmnopqrstuvw",
        "TABCDEFGHIJKLMNOPQRSTUVWXYZ1234567",
    ]

    INVALID_ADDRESSES = [
        "0x1234567890abcdefghijklmnopqrstu",
        "T1234",
        "T" + "a" * 40,
        "",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ12345678",
    ]

    def _validate(self, addr):
        return addr.startswith("T") and len(addr) == 34

    @pytest.mark.parametrize("addr", [
        "TEwnPR7daATh84DLFiTXJGaCge4NbYDbV8",
        "T1234567890abcdefghijklmnopqrstuvw",
        "TABCDEFGHIJKLMNOPQRSTUVWXYZ1234567",
    ])
    def test_valid_addresses(self, addr):
        assert self._validate(addr)

    @pytest.mark.parametrize("addr", [
        "0x1234567890abcdefghijklmnopqrstu",
        "T1234",
        "T" + "a" * 40,
        "",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ12345678",
    ])
    def test_invalid_addresses(self, addr):
        assert not self._validate(addr)


# ── DB settings tests ──

class TestDBSettings:
    def test_crypto_address_default(self):
        from utils.db import get_setting, init_db
        init_db()
        val = get_setting("crypto_address", "")
        assert isinstance(val, str)

    def test_set_and_get_crypto_address(self):
        from utils.db import get_setting, set_setting, init_db
        init_db()
        test_addr = "TEwnPR7daATh84DLFiTXJGaCge4NbYDbV8"
        set_setting("crypto_address", test_addr)
        assert get_setting("crypto_address", "") == test_addr

    def test_overwrite_crypto_address(self):
        from utils.db import get_setting, set_setting, init_db
        init_db()
        set_setting("crypto_address", "T1111111111111111111111111111111111")
        set_setting("crypto_address", "T2222222222222222222222222222222222")
        assert get_setting("crypto_address", "") == "T2222222222222222222222222222222222"


# ── QR code generation test ──

class TestQRGeneration:
    def test_qr_generation_in_memory(self):
        import qrcode
        import io
        addr = "TEwnPR7daATh84DLFiTXJGaCge4NbYDbV8"
        qr = qrcode.make(addr)
        buf = io.BytesIO()
        qr.save(buf, format='PNG')
        buf.seek(0)
        data = buf.read()
        assert data[:4] == b'\x89PNG'
        assert len(data) > 100

    def test_qr_generation_with_dynamic_address(self):
        import qrcode
        import io
        addr = "T9876543210zyxwvutsrqponmlkjihgfe"
        qr = qrcode.make(addr)
        buf = io.BytesIO()
        qr.save(buf, format='PNG')
        buf.seek(0)
        assert buf.read(4) == b'\x89PNG'


# ── Handler registration tests ──

class TestHandlerRegistration:
    def test_process_new_address_exists(self):
        from handlers.admin_panel import process_new_address
        assert callable(process_new_address)

    def test_process_new_price_exists(self):
        from handlers.admin_panel import process_new_price
        assert callable(process_new_price)

    def test_register_handlers_callable(self):
        from handlers.admin_panel import register_handlers
        assert callable(register_handlers)
