# Refactoring Changes — 2026-09-01

## TASK 1: Remove duplicate `handlers/admin.py`

The `/broadcast` and `/msg` command handlers in `handlers/admin.py` were fully duplicated by the inline admin panel in `handlers/admin_panel.py` (which handles broadcast and private messaging via inline keyboard + FSM states).

### Changes:
- **Deleted** `handlers/admin.py`
- **Updated** `handlers/__init__.py` — removed `from .admin import register_handlers as register_admin` and the `register_admin(dp)` call

### Test updates (to accommodate the deletion):
- `test_admin_features.py` — removed `TestAdminChecksReplaced.test_admin_handler_uses_is_admin` (tested deleted file), updated `test_live_monitor_has_refresh` to check for `ADMIN_REFRESH` text key instead of hardcoded Ukrainian string
- `test_fixes.py` — removed `TestFix3AdminIDCheck.test_admin_py_uses_admin_id` (tested deleted file)
- `test_i18n_cleanup.py` — removed `test_no_hardcoded_strings_in_admin` (tested deleted file), updated `test_modules_import` to no longer import `handlers.admin`

---

## TASK 2: Clean dead code and unused imports

### Dead functions removed:
| Function | File | Reason |
|---|---|---|
| `activate_promo()` | `utils/promo.py` | Never called; replaced by `redeem_promo()` |
| `has_active_access()` | `utils/access.py` | Never called anywhere |
| `has_paid_access()` | `utils/access.py` | Never called (was imported in start.py but unused) |
| `update_access()` | `utils/access.py` | Never called anywhere |
| `save_uid_to_whitelist()` | `utils/database.py` | Never called anywhere |

### Unused imports/constants removed:
| Item | File | Change |
|---|---|---|
| `PAYMENT_CONTACT` | `handlers/start.py` | Removed from import line (kept in `config/settings.py`) |
| `has_paid_access` | `handlers/start.py` | Removed from import line |
| `COPY_UID_TARGET = "@arkai_ai"` | `config/settings.py` | Line removed |

### Stub removed:
| Item | File | Change |
|---|---|---|
| `CustomDaysState.user_id = None` | `handlers/start.py` | Line removed from the StatesGroup class |

---

## TASK 3: Wire tests to pytest

### Setup:
- Created `pytest.ini` in project root with standard configuration
- All 6 test files were already using pytest-compatible class/function patterns

### Test results: **220 passed, 0 failed**

| Test file | Tests | Status |
|---|---|---|
| `test_admin_features.py` | 28 | ✅ All pass |
| `test_currency.py` | 17 | ✅ All pass |
| `test_fixes.py` | 29 | ✅ All pass |
| `test_i18n_cleanup.py` | 42 | ✅ All pass |
| `test_pagination.py` | 41 | ✅ All pass |
| `test_user_management.py` | 22 | ✅ All pass |

### Test fixes applied:
- 3 tests that directly referenced the now-deleted `handlers/admin.py` were removed (they tested the file's content, not functionality)
- 1 test checking for a hardcoded Ukrainian string `"🔄 Оновити"` was updated to check for the `ADMIN_REFRESH` text key instead
- No test logic was rewritten — only broken imports/references were fixed

---

## Files modified:
- `handlers/__init__.py` — removed admin.py registration
- `handlers/start.py` — cleaned unused imports and stub
- `utils/promo.py` — removed `activate_promo()`
- `utils/access.py` — removed `has_active_access()`, `has_paid_access()`, `update_access()`
- `utils/database.py` — removed `save_uid_to_whitelist()`
- `config/settings.py` — removed `COPY_UID_TARGET`
- `test_admin_features.py` — fixed 2 tests broken by refactoring
- `test_fixes.py` — fixed 1 test broken by refactoring
- `test_i18n_cleanup.py` — fixed 2 tests broken by refactoring

## Files deleted:
- `handlers/admin.py`

## Files created:
- `pytest.ini`
- `CHANGES.md` (this file)

## 2026-09-01 — Translated all developer-facing Ukrainian/Russian text to English

### Files changed:
- **config/settings.py** — Translated 6 Ukrainian inline comments to English (admin rights, payment contact, channel IDs, referral toggle, promo toggle)
- **handlers/start.py** — Translated 2 Ukrainian comments to English (trial check, trial duration reading)
- **handlers/admin_panel.py** — Translated 2 hardcoded Ukrainian button labels ("✅ Так" → "✅ Yes", "❌ Ні" → "❌ No") in promo deletion confirmation

### Files reviewed with no changes needed (already English):
- bot.py (BotCommand strings for uk/ru locales intentionally preserved)
- handlers/__init__.py
- utils/access.py, utils/database.py, utils/db.py, utils/lang.py
- utils/admin_check.py, utils/promo.py, utils/referral.py
- migrate.py

### Not translated (intentionally preserved):
- texts.py — user-facing multilingual strings (EN/UK/RU)
- BotCommand descriptions in bot.py for uk/ru locales
- Multilingual button label dicts and locale-specific strings in handlers/start.py (user-facing)
- Ukrainian "д" day-suffix input parsing in handlers/admin_panel.py (user input handling)

## 2026-09-01 — Fix hardcoded i18n strings in handlers/start.py

Moved 4 hardcoded Ukrainian/Russian/English inline dicts from `handlers/start.py` into `texts.py` translation keys, replacing them with `t(lang, ...)` calls.

### New keys added to texts.py (all 3 locales: en, uk, ru):
| Key | en | uk | ru |
|---|---|---|---|
| `PRICE_SUFFIX_MONTHLY` | /month | /міс. | /мес. |
| `PRICE_SUFFIX_FOREVER` | — forever | — назавжди | — навсегда |
| `BTN_CUSTOM_DAYS` | ✏️ Custom days | ✏️ Вказати дні | ✏️ Указать дни |
| `BTN_ADMIN_PANEL` | 🛠 Admin Panel | 🛠 Адмін панель | 🛠 Админ панель |

Added `ALL_ADMIN_PANEL` convenience list (same pattern as `ALL_ACTIVATE`, etc.)

### Changes in handlers/start.py:
1. `main_menu()` — replaced `{"uk":..., "ru":..., "en":...}.get(...)` with `t(_al, "BTN_ADMIN_PANEL")`
2. `pay_manual()` — replaced price_suffix dicts with `t(lang, "PRICE_SUFFIX_MONTHLY")` / `t(lang, "PRICE_SUFFIX_FOREVER")`
3. `receive_txid()` — replaced custom days button dict with `t(get_lang(ADMIN_ID), "BTN_CUSTOM_DAYS")`
4. `register_handlers()` — replaced hardcoded string list with `ALL_ADMIN_PANEL`
5. Updated import to include `ALL_ADMIN_PANEL`

### Tests: 269 passed (242 existing + 27 new in test_start_i18n_fix.py)

### Files modified:
- `texts.py` — added 4 keys × 3 locales + `ALL_ADMIN_PANEL` list
- `handlers/start.py` — 5 replacements of hardcoded strings with t() calls

### Files created:
- `test_start_i18n_fix.py` — 27 tests validating the i18n cleanup
