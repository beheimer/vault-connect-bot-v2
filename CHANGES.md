# CHANGES — Dynamic Crypto Address Management

## Summary
Added dynamic crypto address management to the Telegram bot. Admins can now configure the USDT TRC-20 wallet address from within the bot, and QR codes are generated dynamically in memory.

## Changes

### 1. Database (`settings` table)
- `crypto_address` key stored in the `settings` table (default: `""`).

### 2. `handlers/start.py`
- `pay_manual()` reads `crypto_address` from DB via `get_setting()`, uses `CRYPTO_INFO_DYNAMIC` text key.
- `show_qr()` generates QR code in memory using `qrcode.make()` + `io.BytesIO` from the dynamic address.
- `hide_qr()` reads dynamic address from DB for display text.

### 3. `texts.py`
- Added `CRYPTO_INFO_DYNAMIC` (en/uk/ru) with `{address}` placeholder.
- Added `ADMIN_ADDRESS_PROMPT`, `ADMIN_ADDRESS_SET`, `ADMIN_ADDRESS_INVALID` (en/uk/ru).
- Added `ADMIN_ADDRESS_PROMPT_FLOW` (en/uk/ru) — prompt within the PriceEdit FSM flow.
- Added `ADMIN_ADDRESS_SKIPPED` (en/uk/ru) — shown when admin sends `/skip`.

### 4. `handlers/admin_panel.py`
- **Removed** standalone `AddressEdit` FSM class.
- **Removed** "💳 Crypto Address" button from admin keyboard.
- **Added** `waiting_for_address` state to `PriceEdit` FSM.
- Modified `process_new_price()`: after saving price, prompts for crypto address (step 4 of PriceEdit flow).
- Modified `process_new_address()`: accepts valid TRC-20 address (starts with `T`, 34 chars) or `/skip` to keep current.
- Updated handler registration to use `PriceEdit.waiting_for_address`.

### 5. Dependencies
- Added `qrcode[pil]` to `requirements.txt`.

## PriceEdit FSM Flow (Updated)
1. Currency → 2. Type (monthly/forever) → 3. Price → **4. Crypto Address (or /skip)**

---

# CHANGES — Single Admin Panel Message (2026-09-02)

## Problem
Every time an admin opened the panel, a new message was sent, cluttering the chat.

## Solution
Store the panel `message_id` per admin in the DB `settings` table. Before sending a new panel, delete the previous one.

### 1. `utils/db.py`
- Added `get_admin_panel_msg_id(admin_id)` — reads `panel_msg_{admin_id}` from settings.
- Added `set_admin_panel_msg_id(admin_id, msg_id)` — writes it.

### 2. `handlers/admin_panel.py`
- `admin_panel()` now:
  1. Deletes the previously stored panel message (ignores errors).
  2. Sends the new panel.
  3. Stores the new `message_id` via `set_admin_panel_msg_id`.
  4. Returns the sent `Message` object.
- The `/admin` command handler and all internal callers (`process_broadcast`, `process_new_address`) automatically use the new logic.

### 3. `handlers/start.py`
- `admin_panel_trigger()` unchanged — it delegates to `admin_panel()` which now handles everything.

### 4. Tests
- Added `test_admin_panel_single.py` with 12 tests covering DB helpers, delete/store logic, error handling, and the trigger path.
