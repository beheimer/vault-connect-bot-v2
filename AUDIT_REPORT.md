# 🔍 Code Audit Report — `vault-connect-bot`

> **Generated:** 2026-09-01  
> **Scope:** Full codebase static analysis  
> **Purpose:** Identify dead code, unused imports, disabled features, duplicate logic, and production hygiene issues

---

## 📊 Summary

| # | Category | Severity | Items Found |
|---|----------|----------|-------------|
| 1 | [Dead Code / Unused Functions](#1-dead-code--unused-functions) | 🟡 Medium | 5 |
| 2 | [Unused Imports & Constants](#2-unused-imports--constants) | 🟢 Low | 5 |
| 3 | [Feature-Gated Dead Code (Config Flags)](#3-feature-gated-dead-code-config-flags) | 🟡 Medium | 1 flag / ~120 LOC |
| 4 | [Stub / Placeholder Attributes](#4-stub--placeholder-attributes) | 🟢 Low | 1 |
| 5 | [Duplicated Logic](#5-duplicated-logic) | 🔴 High | 1 module |
| 6 | [Files Not Needed in Production](#6-files-not-needed-in-production) | 🟡 Medium | 6 |
| 7 | [Unfilled Text Placeholders](#7-unfilled-text-placeholders) | 🔴 High | 2 strings × 3 locales |

**Total findings:** 21 individual items across 7 categories

---

## 1. Dead Code / Unused Functions

**Severity:** 🟡 Medium — unreachable code increases maintenance burden and misleads future developers

| Function | File | Issue |
|----------|------|-------|
| `activate_promo()` | `utils/promo.py` | Defined but never called. The active call-site uses `redeem_promo()` instead. |
| `has_active_access()` | `utils/access.py` | Defined but never called anywhere in the codebase. |
| `has_paid_access()` | `utils/access.py` | Imported in `handlers/start.py` but never invoked — dead import and dead function. |
| `update_access()` | `utils/access.py` | Defined but no call-sites found. |
| `save_uid_to_whitelist()` | `utils/database.py` | Defined but never called. |

**Recommended fix:** Remove all five functions. If any are intended for future use, move them to a clearly labeled `utils/_deprecated.py` or open a ticket and delete them from the main flow.

---

## 2. Unused Imports & Constants

**Severity:** 🟢 Low — minimal runtime impact, but adds noise and confuses linters / new developers

| Symbol | Defined / Imported In | Issue |
|--------|-----------------------|-------|
| `PAYMENT_CONTACT` | `handlers/start.py` (imported from config) | Imported but never referenced in the module. |
| `has_paid_access` | `handlers/start.py` (imported from `utils/access`) | Imported but never called (see §1). |
| `itertools` | `handlers/start.py` | Used only inside `boot_animation()` via `itertools.cycle`. Valid, but could be a local import to limit module-level side-effects. |
| `ReplyKeyboardMarkup` | `handlers/start.py` | Used in `main_menu()` — **valid import**, included here for completeness only. |
| `COPY_UID_TARGET = "@arkai_ai"` | `config/settings.py` | Defined as a module constant but referenced nowhere in the codebase. |

**Recommended fix:** Remove `PAYMENT_CONTACT`, `has_paid_access`, and `COPY_UID_TARGET`. Optionally localise the `itertools` import inside `boot_animation()`.

---

## 3. Feature-Gated Dead Code (Config Flags)

**Severity:** 🟡 Medium — ~120 lines of code are permanently unreachable at runtime until the flag is changed

| Flag | File | Current Value | Impact |
|------|------|---------------|--------|
| `REFERRAL_ENABLED` | `config/settings.py` | `False` | The entire referral subsystem is disabled. |

**Affected areas while `REFERRAL_ENABLED = False`:**

| File | Dead Section |
|------|-------------|
| `utils/referral.py` | Everything except `add_user()` — all referral tracking, reward, and lookup logic |
| `handlers/start.py` | All `if REFERRAL_ENABLED:` branches |
| `handlers/admin_panel.py` | All `if REFERRAL_ENABLED:` branches |

**Estimated dead lines:** ~120 LOC

**Recommended fix:** Make a decision — either:
- **Enable the feature** (set `REFERRAL_ENABLED = True` and test end-to-end), or  
- **Remove the dead code** entirely and delete `utils/referral.py`, cleaning up the conditional branches.

Leaving permanently-disabled feature code in production increases the diff surface for every future change.

---

## 4. Stub / Placeholder Attributes

**Severity:** 🟢 Low — does not affect runtime behavior, but creates false expectations about the FSM state structure

| Symbol | File | Issue |
|--------|------|-------|
| `CustomDaysState.user_id = None` | `handlers/start.py` | Declared as a class-level attribute on an FSM state group, but never read or set by any handler. Actual data is passed via `state.update_data(...)`. |

**Recommended fix:** Remove the `user_id = None` class attribute from `CustomDaysState`. If user identification is genuinely needed within this state, pass it via `state.update_data` consistently.

---

## 5. Duplicated Logic

**Severity:** 🔴 High — two separate code paths handle the same operations, making bugs and maintenance twice as costly

| Module | Description |
|--------|-------------|
| `handlers/admin.py` | Implements `/broadcast` and `/msg` as **text commands** |
| `handlers/admin_panel.py` | Implements the **same broadcast/message logic** via inline keyboard buttons |

`handlers/admin.py` is effectively **superseded** by `handlers/admin_panel.py`. Any bug fix or change to the broadcast logic must currently be applied in two places, which will inevitably lead to divergence.

**Recommended fix:**
1. Confirm that the inline-panel flow in `handlers/admin_panel.py` is fully functional and covers all edge cases.
2. **Delete `handlers/admin.py`** and remove its router registration from `bot.py` / `main.py`.
3. If text-command aliases are still desired, add thin wrappers in `admin_panel.py` that delegate to the existing inline handlers — do not duplicate the logic.

---

## 6. Files Not Needed in Production

**Severity:** 🟡 Medium — these files should not be committed to or deployed on a production server; they increase attack surface, cause confusion, and clutter the repository

| File | Reason |
|------|--------|
| `migrate.py` | One-time migration script from `db.json`. Migration logic is already embedded as `run_migration()` in `bot.py`. This standalone file is no longer needed post-migration. |
| `script.bat` | Windows batch launcher (`python.exe bot.py`). Irrelevant on Linux / VPS deployments. |
| `requirements.txt.txt` | Duplicate of `requirements.txt` with a double extension — likely a copy/paste artifact. Will confuse `pip install -r` if the wrong filename is used. |
| `test_*.py` (×6 files) | Six test files in the project root that are not connected to any test runner (no `pytest.ini`, `setup.cfg`, or CI pipeline configuration). |

**Recommended fix:**

| File | Action |
|------|--------|
| `migrate.py` | Archive or delete after confirming migration is complete |
| `script.bat` | Delete; add to `.gitignore` for future |
| `requirements.txt.txt` | Delete immediately — keep only `requirements.txt` |
| `test_*.py` (6 files) | Either wire them into a proper test suite (`pytest`) or delete if stale |

---

## 7. Unfilled Text Placeholders

**Severity:** 🔴 High — users will see raw template markers (`[item 1]`, `[item 2]`, `[item 3]`) instead of actual content

| Constant | File | Affected Locales | Placeholder Pattern |
|----------|------|------------------|---------------------|
| `WELCOME_TEXT` | `texts.py` | 🇬🇧 EN / 🇺🇦 UK / 🇷🇺 RU | `[item 1]`, `[item 2]`, `[item 3]` |
| `POPUP_TEXT` | `texts.py` | 🇬🇧 EN / 🇺🇦 UK / 🇷🇺 RU | `[item 1]`, `[item 2]`, `[item 3]` |

**Total unfilled placeholder instances:** 6 (2 strings × 3 locales)

**Impact:** These strings are shown directly to end users on bot start and in popups. Shipping placeholder text to production is a visible product quality failure.

**Recommended fix:** Fill in the actual content for all six locale variants before the next deployment. Use a content review step in the release checklist to prevent regression.

---

## ✅ Recommended Actions (Prioritized by Impact)

| Priority | Action | Category | Effort | Risk |
|----------|--------|----------|--------|------|
| 🔴 **P1** | Fill all placeholder text in `WELCOME_TEXT` and `POPUP_TEXT` for EN/UK/RU | §7 | Low | None |
| 🔴 **P2** | Delete `handlers/admin.py` — it is fully superseded by `admin_panel.py` | §5 | Low | Low — test inline panel first |
| 🟡 **P3** | Decide on `REFERRAL_ENABLED`: enable + test, or remove ~120 LOC entirely | §3 | Medium | Medium |
| 🟡 **P4** | Delete production-irrelevant files: `migrate.py`, `script.bat`, `requirements.txt.txt` | §6 | Low | None |
| 🟡 **P5** | Wire `test_*.py` into a pytest suite or delete stale tests | §6 | Medium | Low |
| 🟡 **P6** | Remove the five dead functions in `utils/access.py`, `utils/promo.py`, `utils/database.py` | §1 | Low | Low — verify no dynamic calls |
| 🟢 **P7** | Remove unused imports/constants: `PAYMENT_CONTACT`, `has_paid_access`, `COPY_UID_TARGET` | §2 | Low | None |
| 🟢 **P8** | Remove stub `CustomDaysState.user_id = None` class attribute | §4 | Low | None |
| 🟢 **P9** | Optionally localise `itertools` import inside `boot_animation()` | §2 | Trivial | None |

---

*This report was generated from static analysis. Dynamic call-path analysis (e.g. via `vulture` or manual tracing) is recommended before removing any function marked as dead code, to guard against reflection-based or dynamically constructed call-sites.*
