from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config.settings import CHANNEL_ID, ADMIN_ID
from utils.admin_check import is_admin as check_admin
from utils.access import get_access_mode
from texts import t
from utils.lang import get_lang
from utils.db import (
    get_user, get_all_users, update_user_field, get_user_by_username,
    get_setting, set_setting, get_referral_counts,
    get_admins, add_admin, remove_admin
)
from utils.promo import make_promo, get_promos, delete_promo
import datetime
import re


class Broadcast(StatesGroup):
    waiting_for_content = State()


class TrialEdit(StatesGroup):
    waiting_for_duration = State()


class MsgUser(StatesGroup):
    waiting_for_target = State()
    waiting_for_text = State()


class PromoCreate(StatesGroup):
    waiting_for_days = State()

class KickUser(StatesGroup):
    waiting_for_target = State()


class DmUser(StatesGroup):
    waiting_for_text = State()


class AdminAdd(StatesGroup):
    waiting_for_target = State()


class ResetTrial(StatesGroup):
    waiting_for_target = State()


class PriceEdit(StatesGroup):
    waiting_for_currency = State()
    waiting_for_type = State()
    waiting_for_price = State()
    waiting_for_address = State()


ITEMS_PER_PAGE = 8


def paginate(items, page, per_page=ITEMS_PER_PAGE):
    """Return (page_items, total_pages) for the given page."""
    total_pages = max(1, (len(items) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    start = page * per_page
    return items[start:start + per_page], total_pages


def _parse_page(data, prefix):
    """Extract page number from callback_data like 'prefix_p3'. Default 0."""
    m = re.search(r'_p(\d+)$', data)
    if m:
        return int(m.group(1))
    return 0


def _nav_buttons(prefix, page, total_pages, lang=None):
    """Return a list of navigation InlineKeyboardButtons (◀️ / ▶️)."""
    if lang is None:
        lang = _admin_lang()
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton(t(lang, "NAV_PREV"), callback_data=f"{prefix}_p{page - 1}"))
    if page < total_pages - 1:
        buttons.append(InlineKeyboardButton(t(lang, "NAV_NEXT"), callback_data=f"{prefix}_p{page + 1}"))
    return buttons


def _admin_lang():
    """Get admin's language via ADMIN_ID."""
    return get_lang(ADMIN_ID)


def get_admin_keyboard(lang=None):
    from config.settings import REFERRAL_ENABLED
    if lang is None:
        lang = _admin_lang()
    kb = InlineKeyboardMarkup(row_width=2)

    # Block 1 — User actions
    kb.add(
        InlineKeyboardButton(t(lang, "ADMIN_BTN_DM"), callback_data="admin_msg_user"),
        InlineKeyboardButton(t(lang, "ADMIN_BTN_KICK"), callback_data="admin_kick_user")
    )
    kb.add(
        InlineKeyboardButton(t(lang, "ADMIN_BTN_BROADCAST"), callback_data="admin_broadcast"),
        InlineKeyboardButton(t(lang, "ADMIN_BTN_RESET_TRIAL"), callback_data="admin_reset_trial")
    )

    # Block 2 — Settings
    kb.add(
        InlineKeyboardButton(t(lang, "ADMIN_BTN_TRIAL_DURATION"), callback_data="admin_trial_duration"),
        InlineKeyboardButton(t(lang, "ADMIN_BTN_PRICE"), callback_data="admin_set_price")
    )
    kb.add(
        InlineKeyboardButton(t(lang, "ADMIN_BTN_PROMOS"), callback_data="admin_promos"),
        InlineKeyboardButton(t(lang, "ADMIN_BTN_USERS"), callback_data="admin_users")
    )

    # Block 3 — Monitoring + Admin
    kb.add(
        InlineKeyboardButton(t(lang, "ADMIN_BTN_LIVE_MONITOR"), callback_data="admin_live_monitor"),
        InlineKeyboardButton(t(lang, "ADMIN_BTN_ADMINS"), callback_data="admin_admins")
    )

    # Block 4 — Referrals (only if enabled)
    if REFERRAL_ENABLED:
        kb.add(
            InlineKeyboardButton(t(lang, "ADMIN_BTN_REFS"), callback_data="admin_refs")
        )

    return kb


def _back_kb(lang):
    """Inline keyboard with a single Back button."""
    return InlineKeyboardMarkup().add(
        InlineKeyboardButton(t(lang, "ADMIN_BACK"), callback_data="admin_back")
    )


def _safe_dt(s):
    try:
        return datetime.datetime.fromisoformat(s) if s else datetime.datetime(2000, 1, 1)
    except Exception:
        return datetime.datetime(2000, 1, 1)


async def admin_panel(message: types.Message):
    from utils.db import get_admin_panel_msg_id, set_admin_panel_msg_id
    if not check_admin(message.from_user.id):
        return
    admin_id = message.from_user.id
    admin_lang = get_lang(admin_id)

    old_msg_id = get_admin_panel_msg_id(admin_id)
    if old_msg_id:
        try:
            await message.bot.delete_message(chat_id=admin_id, message_id=old_msg_id)
        except Exception:
            pass

    sent = await message.answer(t(admin_lang, "ADMIN_PANEL_TITLE"), reply_markup=get_admin_keyboard(admin_lang))

    set_admin_panel_msg_id(admin_id, sent.message_id)
    return sent


async def admin_callbacks(call: types.CallbackQuery, state: FSMContext):
    admin_lang = _admin_lang()

    users = get_all_users()

    if call.data.startswith("admin_users") and not call.data.startswith("admin_user_"):
        page = _parse_page(call.data, "admin_users")
        all_users = list(users)
        page_users, total_pages = paginate(all_users, page)

        msg = t(admin_lang, "ADMIN_USERS_LIST") + f"  (Page {page + 1}/{total_pages})\n\n"
        for user in page_users:
            uid = user.get('id')
            name = user.get('full_name') or '—'
            uname = user.get('username')
            identity = f"@{uname}" if uname else f"ID: {uid}"
            mode_key = "MODE_ADMIN" if check_admin(user.get("id", 0)) else get_access_mode(user)
            mode = t(admin_lang, mode_key)
            msg += f"• {name} | {identity} | {mode}\n"

        kb = InlineKeyboardMarkup(row_width=2)
        for user in page_users:
            uid = user.get('id')
            uname = user.get('username')
            btn_label = f"👤 @{uname}" if uname else f"👤 ID:{uid}"
            kb.add(InlineKeyboardButton(btn_label, callback_data=f"admin_user_{uid}_p{page}"))
        nav = _nav_buttons("admin_users", page, total_pages)
        if nav:
            kb.row(*nav)
        kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="admin_back"))
        await call.message.edit_text(msg, reply_markup=kb)

    elif call.data.startswith("admin_user_"):
        # Parse admin_user_{uid}_p{page}
        m_user = re.match(r'admin_user_(\d+)_p(\d+)', call.data)
        if m_user:
            uid = int(m_user.group(1))
            page = int(m_user.group(2))
            target_user = get_user(uid)
            if not target_user:
                await call.answer("User not found", show_alert=True)
                return
            name = target_user.get('full_name') or '—'
            uname = target_user.get('username')
            identity = f"@{uname}" if uname else f"ID: {uid}"
            joined_raw = target_user.get('joined_at')
            try:
                joined = datetime.datetime.fromisoformat(joined_raw).strftime("%d.%m.%Y %H:%M") if joined_raw else "—"
            except Exception:
                joined = "—"
            mode_key = "MODE_ADMIN" if check_admin(target_user.get("id", 0)) else get_access_mode(target_user)
            mode = t(admin_lang, mode_key)
            access_raw = target_user.get('access_until')
            try:
                access_until_fmt = datetime.datetime.fromisoformat(access_raw).strftime("%d.%m.%Y %H:%M") if access_raw else "—"
            except Exception:
                access_until_fmt = "—"

            msg = (
                t(admin_lang, "USER_DETAIL_TITLE") + "\n\n"
                + f"👤 {name}\n"
                + f"{identity} | ID: {uid}\n"
                + t(admin_lang, "USER_JOINED", date=joined) + "\n"
                + t(admin_lang, "USER_STATUS", mode=mode) + "\n"
                + t(admin_lang, "USER_ACCESS_UNTIL", date=access_until_fmt)
            )

            kb = InlineKeyboardMarkup(row_width=2)
            kb.add(
                InlineKeyboardButton(t(admin_lang, "BTN_KICK"), callback_data=f"confirm_kick_{uid}"),
                InlineKeyboardButton(t(admin_lang, "BTN_DM"), callback_data=f"admin_dm_{uid}_p{page}")
            )
            kb.add(
                InlineKeyboardButton(t(admin_lang, "BTN_RESET_TRIAL"), callback_data=f"confirm_reset_trial_{uid}_p{page}")
            )
            kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data=f"admin_users_p{page}"))
            await call.message.edit_text(msg, reply_markup=kb)

    elif call.data.startswith("admin_dm_"):
        # admin_dm_{uid}_p{page}
        m_dm = re.match(r'admin_dm_(\d+)_p(\d+)', call.data)
        if m_dm:
            uid = int(m_dm.group(1))
            page = int(m_dm.group(2))
            await state.update_data(dm_target_uid=uid, dm_return_page=page)
            await call.message.edit_text(
                t(admin_lang, "DM_PROMPT"),
                reply_markup=_back_kb(admin_lang)
            )
            await DmUser.waiting_for_text.set()

    elif call.data.startswith("admin_refs"):
        page = _parse_page(call.data, "admin_refs")
        ref_counts = get_referral_counts()
        active_refs = [(uid_ref, count) for uid_ref, count in ref_counts.items() if count > 0]

        if not active_refs:
            msg = t(admin_lang, "ADMIN_REFS_LIST") + "\n\n" + t(admin_lang, "ADMIN_NO_REFS")
            await call.message.edit_text(msg, reply_markup=_back_kb(admin_lang))
        else:
            page_refs, total_pages = paginate(active_refs, page)
            msg = t(admin_lang, "ADMIN_REFS_LIST") + f"  (Page {page + 1}/{total_pages})\n\n"
            for uid_ref, count in page_refs:
                ref_user = get_user(int(uid_ref))
                uname = ref_user.get('username', str(uid_ref)) if ref_user else str(uid_ref)
                msg += f"@{uname} → {t(admin_lang, 'ADMIN_REFS_INVITED', count=count)}\n"

            kb = InlineKeyboardMarkup(row_width=2)
            nav = _nav_buttons("admin_refs", page, total_pages)
            if nav:
                kb.row(*nav)
            kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="admin_back"))
            await call.message.edit_text(msg, reply_markup=kb)

    elif call.data.startswith("admin_status"):
        page = _parse_page(call.data, "admin_status")
        all_users = list(users)
        page_users, total_pages = paginate(all_users, page)

        msg = t(admin_lang, "ADMIN_STATUS_LIST") + f"  (Page {page + 1}/{total_pages})\n\n"
        for user in page_users:
            uid = user.get('id')
            mode_key = "MODE_ADMIN" if check_admin(user.get("id", 0)) else get_access_mode(user)
            mode = t(admin_lang, mode_key)
            raw = user.get("access_until")
            try:
                formatted = datetime.datetime.fromisoformat(raw).strftime("%d.%m.%Y %H:%M:%S")
            except Exception:
                formatted = "—"
            uname2 = user.get('username')
            identity2 = f"@{uname2}" if uname2 else f"ID: {uid}"
            msg += f"{identity2} — {mode}\n{t(admin_lang, 'ADMIN_STATUS_UNTIL', date=formatted)}\n\n"

        kb = InlineKeyboardMarkup(row_width=2)
        nav = _nav_buttons("admin_status", page, total_pages)
        if nav:
            kb.row(*nav)
        kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="admin_back"))
        await call.message.edit_text(msg, reply_markup=kb)

    elif call.data == "admin_stats":
        total = len(users)
        trials = sum(1 for u in users if u.get("trial_used"))
        active = sum(1 for u in users if u.get("access_until"))
        msg = (
            t(admin_lang, "ADMIN_STATS_TITLE") + "\n"
            + t(admin_lang, "ADMIN_STATS_TOTAL", total=total) + "\n"
            + t(admin_lang, "ADMIN_STATS_TRIALS", trials=trials) + "\n"
            + t(admin_lang, "ADMIN_STATS_ACTIVE", active=active) + "\n"
        )
        await call.message.edit_text(msg, reply_markup=_back_kb(admin_lang))

    elif call.data == "admin_live_monitor":
        now = datetime.datetime.now()
        cutoff = now - datetime.timedelta(days=30)

        total = len(users)
        active = sum(1 for u in users if _safe_dt(u.get("access_until")) > now)
        trial = sum(1 for u in users if u.get("trial_at") and not u.get("access_paid"))
        locked = total - active

        new_30 = sum(1 for u in users if _safe_dt(u.get("joined_at")) > cutoff)
        trial_30 = sum(1 for u in users if _safe_dt(u.get("trial_at")) > cutoff)
        paid_30 = sum(1 for u in users if _safe_dt(u.get("paid_at")) > cutoff)

        trial_conv = f"{round(trial_30/new_30*100)}%" if new_30 > 0 else "—"
        paid_conv = f"{round(paid_30/trial_30*100)}%" if trial_30 > 0 else "—"

        price = int(get_setting("access_price", 50))
        revenue = paid_30 * price

        msg = (
            t(admin_lang, "ADMIN_LIVE_TITLE") + "\n\n"
            + t(admin_lang, "ADMIN_LIVE_TOTAL", total=total) + "\n"
            + t(admin_lang, "ADMIN_LIVE_ACTIVE", active=active) + "\n"
            + t(admin_lang, "ADMIN_LIVE_TRIAL", trial=trial) + "\n"
            + t(admin_lang, "ADMIN_LIVE_LOCKED", locked=locked) + "\n\n"
            + t(admin_lang, "ADMIN_LIVE_30D_TITLE") + "\n"
            + t(admin_lang, "ADMIN_LIVE_30D_NEW", count=new_30) + "\n"
            + t(admin_lang, "ADMIN_LIVE_30D_TRIAL", count=trial_30, conv=trial_conv) + "\n"
            + t(admin_lang, "ADMIN_LIVE_30D_PAID", count=paid_30, conv=paid_conv) + "\n"
            + t(admin_lang, "ADMIN_LIVE_30D_REVENUE", amount=revenue, currency=get_setting("currency", "$"))
        )
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(t(admin_lang, "ADMIN_REFRESH"), callback_data="admin_live_monitor"),
            InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="admin_back")
        )
        try:
            await call.message.edit_text(msg, reply_markup=kb)
        except Exception:
            await call.answer(t(admin_lang, "DATA_ACTUAL"), show_alert=False)

    elif call.data == "admin_broadcast":
        await call.message.answer(t(admin_lang, "ADMIN_BROADCAST_PROMPT"))
        await Broadcast.waiting_for_content.set()

    elif call.data == "admin_reset_trial":
        await call.message.edit_text(
            t(admin_lang, "ADMIN_RESET_TRIAL_PROMPT"),
            reply_markup=_back_kb(admin_lang)
        )
        await ResetTrial.waiting_for_target.set()

    elif call.data == "admin_trial_duration":
        current = int(get_setting("trial_duration_hours", 120))
        days = current // 24
        hours = current % 24
        await call.message.edit_text(
            t(admin_lang, "ADMIN_TRIAL_DURATION_INFO", hours=current, days=days, rem=hours),
            reply_markup=_back_kb(admin_lang)
        )
        await TrialEdit.waiting_for_duration.set()

    elif call.data == "admin_msg_user":
        await call.message.edit_text(
            t(admin_lang, "ADMIN_MSG_PROMPT"),
            reply_markup=_back_kb(admin_lang)
        )
        await MsgUser.waiting_for_target.set()

    elif call.data == "admin_kick_user":
        await call.message.edit_text(
            t(admin_lang, "ADMIN_KICK_PROMPT"),
            reply_markup=_back_kb(admin_lang)
        )
        await KickUser.waiting_for_target.set()

    elif call.data == "admin_set_price":
        current_price = int(get_setting("access_price", 50))
        current_type = get_setting("price_type", "monthly")
        currency = get_setting("currency", "$")
        type_label = t(admin_lang, "ADMIN_PRICE_LABEL_MONTHLY") if current_type == "monthly" else t(admin_lang, "ADMIN_PRICE_LABEL_FOREVER")
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(t(admin_lang, "CURRENCY_EUR"), callback_data="currency_eur"),
            InlineKeyboardButton(t(admin_lang, "CURRENCY_USD"), callback_data="currency_usd")
        )
        kb.add(
            InlineKeyboardButton(t(admin_lang, "CURRENCY_GBP"), callback_data="currency_gbp"),
            InlineKeyboardButton(t(admin_lang, "CURRENCY_CUSTOM"), callback_data="currency_custom")
        )
        kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="admin_back"))
        await call.message.edit_text(
            t(admin_lang, "ADMIN_PRICE_INFO", price=current_price, label=type_label, currency=currency)
            + "\n\n" + t(admin_lang, "ADMIN_CURRENCY_PROMPT"),
            reply_markup=kb
        )
        await PriceEdit.waiting_for_currency.set()

    elif call.data in ("price_type_monthly", "price_type_forever"):
        price_type = "monthly" if call.data == "price_type_monthly" else "forever"
        await state.update_data(price_type=price_type)
        label = t(admin_lang, "ADMIN_PRICE_LABEL_MONTHLY") if price_type == "monthly" else t(admin_lang, "ADMIN_PRICE_LABEL_FOREVER")
        await call.message.edit_text(
            t(admin_lang, "ADMIN_PRICE_TYPE_PROMPT", label=label),
            reply_markup=_back_kb(admin_lang)
        )
        await PriceEdit.waiting_for_price.set()
        await call.answer()

    elif call.data.startswith("currency_") and call.data != "currency_custom":
        currency_map = {
            "currency_eur": "€",
            "currency_usd": "$",
            "currency_gbp": "£",
        }
        symbol = currency_map.get(call.data, "$")
        await state.update_data(currency=symbol)
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(t(admin_lang, "ADMIN_PRICE_BTN_MONTHLY"), callback_data="price_type_monthly"),
            InlineKeyboardButton(t(admin_lang, "ADMIN_PRICE_BTN_FOREVER"), callback_data="price_type_forever")
        )
        kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="admin_back"))
        await call.message.edit_text(
            t(admin_lang, "ADMIN_CURRENCY_SAVED", currency=symbol)
            + "\n\n" + t(admin_lang, "ADMIN_PRICE_INFO", price=int(get_setting("access_price", 50)),
                          label=t(admin_lang, "ADMIN_PRICE_LABEL_MONTHLY") if get_setting("price_type", "monthly") == "monthly" else t(admin_lang, "ADMIN_PRICE_LABEL_FOREVER"),
                          currency=symbol),
            reply_markup=kb
        )
        await PriceEdit.waiting_for_type.set()
        await call.answer()

    elif call.data == "currency_custom":
        await call.message.edit_text(
            t(admin_lang, "ADMIN_CURRENCY_CUSTOM_PROMPT"),
            reply_markup=_back_kb(admin_lang)
        )
        await call.answer()

    elif call.data.startswith("admin_promos"):
        page = _parse_page(call.data, "admin_promos")
        promos = get_promos()
        if not promos:
            msg = t(admin_lang, "ADMIN_PROMOS_EMPTY")
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_PROMO_BTN_CREATE"), callback_data="promo_create"))
            kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="admin_back"))
            await call.message.edit_text(msg, reply_markup=kb)
        else:
            all_promos = list(promos.items())
            page_promos, total_pages = paginate(all_promos, page)

            msg = t(admin_lang, "ADMIN_PROMOS_TITLE") + f"  (Page {page + 1}/{total_pages})\n\n"
            for code, p in page_promos:
                ptype = t(admin_lang, "PROMO_TYPE_FULL") if p["type"] == "full" else t(admin_lang, "PROMO_TYPE_TRIAL")
                pdays = "♾️" if p["days"] == 0 else f"{p['days']}d"
                if p["used"]:
                    used_by = p.get("used_by", "?")
                    udata = get_user(int(used_by)) if used_by else {}
                    uname = udata.get("username") if udata else None
                    ident = f"@{uname}" if uname else str(used_by)
                    status = f"✅ {ident}"
                else:
                    status = t(admin_lang, "ADMIN_PROMO_ACTIVE")
                msg += f"{code} | {ptype} {pdays} | {status}\n"

            kb = InlineKeyboardMarkup()
            for code, p in page_promos:
                if not p["used"]:
                    kb.add(InlineKeyboardButton(f"🗑 {code}", callback_data=f"promo_del_{code}_p{page}"))
            nav = _nav_buttons("admin_promos", page, total_pages)
            if nav:
                kb.row(*nav)
            kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_PROMO_BTN_CREATE"), callback_data="promo_create"))
            kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="admin_back"))
            await call.message.edit_text(msg, reply_markup=kb)

    elif call.data.startswith("admin_admins"):
        page = _parse_page(call.data, "admin_admins")
        admins_list = get_admins()
        admin_lang_local = get_lang(call.from_user.id)

        if not admins_list:
            kb = InlineKeyboardMarkup()
            if call.from_user.id == ADMIN_ID:
                kb.add(InlineKeyboardButton(t(admin_lang_local, "ADMIN_ADD_BTN"), callback_data="admin_add_admin"))
            kb.add(InlineKeyboardButton(t(admin_lang_local, "ADMIN_BACK"), callback_data="admin_back"))
            await call.message.edit_text(t(admin_lang_local, "ADMIN_ADMINS_EMPTY"), reply_markup=kb)
        else:
            page_admins, total_pages = paginate(admins_list, page)
            msg = t(admin_lang_local, "ADMIN_ADMINS_TITLE") + f"  (Page {page + 1}/{total_pages})\n\n"
            for a in page_admins:
                uname = a.get("username") or str(a["user_id"])
                added_at = a.get("added_at", "—")
                try:
                    added_at = datetime.datetime.fromisoformat(added_at).strftime("%d.%m.%Y")
                except Exception:
                    pass
                msg += f"@{uname} | ID: {a['user_id']} | {t(admin_lang_local, 'ADMIN_ADMINS_ADDED', date=added_at)}\n"

            kb = InlineKeyboardMarkup()
            if call.from_user.id == ADMIN_ID:
                for a in page_admins:
                    uname = a.get("username") or str(a["user_id"])
                    kb.add(InlineKeyboardButton(f"🗑 @{uname}", callback_data=f"admin_remove_{a['user_id']}"))
            nav = _nav_buttons("admin_admins", page, total_pages)
            if nav:
                kb.row(*nav)
            if call.from_user.id == ADMIN_ID:
                kb.add(InlineKeyboardButton(t(admin_lang_local, "ADMIN_ADD_BTN"), callback_data="admin_add_admin"))
            kb.add(InlineKeyboardButton(t(admin_lang_local, "ADMIN_BACK"), callback_data="admin_back"))
            await call.message.edit_text(msg, reply_markup=kb)

    elif call.data == "admin_add_admin":
        if call.from_user.id != ADMIN_ID:
            await call.answer(t(get_lang(call.from_user.id), "ADMIN_ONLY_OWNER"), show_alert=True)
            return
        admin_lang_local = get_lang(call.from_user.id)
        await call.message.edit_text(
            t(admin_lang_local, "ADMIN_ADD_PROMPT"),
            reply_markup=_back_kb(admin_lang_local)
        )
        await AdminAdd.waiting_for_target.set()

    elif call.data.startswith("admin_remove_"):
        if call.from_user.id != ADMIN_ID:
            await call.answer(t(get_lang(call.from_user.id), "ADMIN_ONLY_OWNER"), show_alert=True)
            return
        target_id = int(call.data.replace("admin_remove_", ""))
        target_user = get_user(target_id)
        uname = target_user.get("username", str(target_id)) if target_user else str(target_id)
        admin_lang_local = get_lang(call.from_user.id)
        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(t(admin_lang_local, "BTN_YES"), callback_data=f"confirm_remove_admin_{target_id}"),
            InlineKeyboardButton(t(admin_lang_local, "BTN_NO"), callback_data="cancel_action")
        )
        await call.message.edit_text(
            t(admin_lang_local, "ADMIN_REMOVE_CONFIRM", username=uname),
            reply_markup=kb
        )

    elif call.data == "admin_back":
        await state.finish()
        await call.message.edit_text(
            t(admin_lang, "ADMIN_PANEL_TITLE"),
            reply_markup=get_admin_keyboard(admin_lang)
        )


async def process_broadcast(message: types.Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        return

    admin_lang = _admin_lang()

    if not (message.text or message.caption or message.photo):
        await message.answer(t(admin_lang, "BROADCAST_EMPTY"))
        return

    users = get_all_users()

    sent, failed = 0, 0
    for user in users:
        uid = user.get('id')
        if not uid:
            continue
        try:
            if message.photo:
                await message.bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption or "")
            else:
                await message.bot.send_message(uid, message.text)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(t(admin_lang, "BROADCAST_RESULT", ok=sent, fail=failed))
    await state.finish()
    await admin_panel(message)


async def kick_user(message: types.Message):
    if not check_admin(message.from_user.id):
        return

    admin_lang = _admin_lang()
    args = message.get_args()
    if not args:
        await message.answer(t(admin_lang, "KICK_NOT_FOUND"))
        return

    identifier = args.strip()
    user_id_to_kick = None
    username_to_kick = None

    if identifier.startswith('@'):
        user = get_user_by_username(identifier[1:])
        if user:
            user_id_to_kick = user['id']
            username_to_kick = user.get('username')
    else:
        try:
            user = get_user(int(identifier))
            if user:
                user_id_to_kick = user['id']
                username_to_kick = user.get('username')
        except (ValueError, TypeError):
            pass

    if not user_id_to_kick:
        await message.answer(t(admin_lang, "KICK_NOT_FOUND"))
        return

    kicked_lang = get_lang(user_id_to_kick)

    try:
        await message.bot.ban_chat_member(CHANNEL_ID, user_id_to_kick)
        await message.bot.unban_chat_member(CHANNEL_ID, user_id_to_kick)

        update_user_field(user_id_to_kick, 'access_until', None)
        update_user_field(user_id_to_kick, 'access_paid', 0)
        update_user_field(user_id_to_kick, 'reminder_sent', 0)

        try:
            await message.bot.send_message(user_id_to_kick, t(kicked_lang, "KICKED_BY_ADMIN"))
        except Exception:
            pass

        await message.answer(t(admin_lang, "KICK_SUCCESS", username=username_to_kick or user_id_to_kick))

    except Exception as e:
        await message.answer(t(admin_lang, "KICK_FAILED", error=str(e)))


async def reset_trial(message: types.Message):
    if not check_admin(message.from_user.id):
        return

    admin_lang = _admin_lang()
    args = message.get_args()
    if not args:
        await message.answer(t(admin_lang, "ADMIN_RESET_USAGE"))
        return

    identifier = args.strip()

    user = None
    if identifier.startswith("@"):
        user = get_user_by_username(identifier[1:])
    else:
        try:
            user = get_user(int(identifier))
        except (ValueError, TypeError):
            pass

    if not user:
        await message.answer(t(admin_lang, "ADMIN_RESET_NOT_FOUND"))
        return

    uid = user['id']
    update_user_field(uid, 'trial_used', 0)
    update_user_field(uid, 'access_until', None)
    update_user_field(uid, 'access_paid', 0)
    update_user_field(uid, 'reminder_sent', 0)

    username = user.get("username", str(uid))
    await message.answer(t(admin_lang, "ADMIN_RESET_DONE", username=username))


async def set_trial_duration(message: types.Message):
    if not check_admin(message.from_user.id):
        return

    admin_lang = _admin_lang()
    args = message.get_args().strip()
    if not args:
        await message.answer(t(admin_lang, "ADMIN_TRIAL_USAGE"))
        return

    try:
        if args.endswith("д") or args.endswith("d"):
            hours = int(args[:-1]) * 24
        else:
            hours = int(args)
    except ValueError:
        await message.answer(t(admin_lang, "ADMIN_TRIAL_INVALID"))
        return

    set_setting("trial_duration_hours", hours)

    days = hours // 24
    rem = hours % 24
    await message.answer(t(admin_lang, "ADMIN_TRIAL_CHANGED", hours=hours, days=days, rem=rem))


async def process_msg_target(message: types.Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        return
    admin_lang = _admin_lang()
    await state.update_data(target=message.text.strip())
    await message.answer(t(admin_lang, "ADMIN_MSG_TEXT_PROMPT"))
    await MsgUser.waiting_for_text.set()


async def process_msg_text(message: types.Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        return

    admin_lang = _admin_lang()
    data = await state.get_data()
    identifier = data.get("target", "").replace("@", "")

    target_user = get_user_by_username(identifier)
    if not target_user:
        try:
            target_user = get_user(int(identifier))
        except (ValueError, TypeError):
            target_user = {}

    if not target_user:
        await message.answer(t(admin_lang, "ADMIN_MSG_NOT_FOUND"))
        await state.finish()
        return

    target_id = target_user['id']
    try:
        await message.bot.send_message(int(target_id), message.text)
        await message.answer(t(admin_lang, "ADMIN_MSG_SENT", target=data.get('target')))
    except Exception as e:
        await message.answer(t(admin_lang, "ADMIN_MSG_FAILED", error=str(e)))

    await state.finish()


async def process_kick_target(message: types.Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        return

    admin_lang = get_lang(message.from_user.id)
    identifier = message.text.strip().replace("@", "")

    target_user = get_user_by_username(identifier)
    if not target_user:
        try:
            target_user = get_user(int(identifier))
        except (ValueError, TypeError):
            target_user = {}

    if not target_user:
        await message.answer(t(admin_lang, "ADMIN_KICK_NOT_FOUND"))
        await state.finish()
        return

    user_id_to_kick = target_user['id']
    username_to_kick = target_user.get("username", str(user_id_to_kick))

    await state.finish()
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(t(get_lang(message.from_user.id), "BTN_CONFIRM"), callback_data=f"confirm_kick_{user_id_to_kick}"),
        InlineKeyboardButton(t(get_lang(message.from_user.id), "BTN_CANCEL"), callback_data="cancel_action")
    )
    await message.answer(t(admin_lang, "CONFIRM_KICK", username=username_to_kick), reply_markup=kb)


async def process_new_price(message: types.Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        return

    admin_lang = _admin_lang()

    try:
        price = int(message.text.strip())
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t(admin_lang, "ADMIN_PRICE_INVALID"))
        return

    data = await state.get_data()
    price_type = data.get("price_type", "monthly")
    currency = data.get("currency", get_setting("currency", "$"))
    set_setting("access_price", price)
    set_setting("price_type", price_type)
    set_setting("currency", currency)

    label = t(admin_lang, "ADMIN_PRICE_LABEL_MONTHLY") if price_type == "monthly" else t(admin_lang, "ADMIN_PRICE_LABEL_FOREVER")
    await message.answer(t(admin_lang, "ADMIN_PRICE_CHANGED", price=price, label=label, currency=currency))

    current_address = get_setting("crypto_address", "")
    display = f"\n\nCurrent: `{current_address}`" if current_address else ""
    await message.answer(
        t(admin_lang, "ADMIN_ADDRESS_PROMPT_FLOW") + display,
        parse_mode="Markdown"
    )
    await PriceEdit.waiting_for_address.set()


async def process_new_address(message: types.Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        return

    admin_lang = _admin_lang()
    text = message.text.strip()

    if text == "/skip":
        await message.answer(t(admin_lang, "ADMIN_ADDRESS_SKIPPED"))
        await state.finish()
        await admin_panel(message)
        return

    if not text.startswith("T") or len(text) != 34:
        await message.answer(t(admin_lang, "ADMIN_ADDRESS_INVALID"))
        return

    set_setting("crypto_address", text)
    await message.answer(
        t(admin_lang, "ADMIN_ADDRESS_SET", address=text),
        parse_mode="Markdown"
    )
    await state.finish()
    await admin_panel(message)


async def promo_callbacks(call: types.CallbackQuery, state: FSMContext):
    if not check_admin(call.from_user.id):
        return

    admin_lang = _admin_lang()

    if call.data == "promo_create":
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton(t(admin_lang, "ADMIN_PROMO_BTN_FULL"), callback_data="promo_t_full"),
            InlineKeyboardButton(t(admin_lang, "ADMIN_PROMO_BTN_TRIAL"), callback_data="promo_t_trial")
        )
        kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="admin_promos"))
        await call.message.edit_text(t(admin_lang, "ADMIN_PROMO_TYPE_PROMPT"), reply_markup=kb)

    elif call.data in ("promo_t_full", "promo_t_trial"):
        ptype = "full" if call.data == "promo_t_full" else "trial"
        await state.update_data(promo_type=ptype)
        kb = InlineKeyboardMarkup()
        if ptype == "full":
            kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_PROMO_BTN_FOREVER"), callback_data="promo_d_0_full"))
        kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="promo_create"))
        label = t(admin_lang, "PROMO_TYPE_FULL") if ptype == "full" else t(admin_lang, "PROMO_TYPE_TRIAL")
        await call.message.edit_text(
            t(admin_lang, "ADMIN_PROMO_DAYS_PROMPT", label=label),
            reply_markup=kb
        )
        await PromoCreate.waiting_for_days.set()

    elif call.data.startswith("promo_d_0_full"):
        await state.finish()
        code = make_promo("full", 0)
        msg = t(admin_lang, "ADMIN_PROMO_CREATED", code=code, type="Full", days="♾️")
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_PROMO_BTN_LIST"), callback_data="admin_promos"))
        await call.message.edit_text(msg, reply_markup=kb, parse_mode="Markdown")

    elif call.data.startswith("promo_del_") and not call.data.startswith("promo_del_confirmed_"):
        # Parse page from callback: promo_del_{code}_p{n}
        suffix = call.data[len("promo_del_"):]
        page = 0
        m = re.search(r'_p(\d+)$', suffix)
        if m:
            page = int(m.group(1))
            code = suffix[:m.start()]
        else:
            code = suffix

        # Show confirmation instead of deleting immediately
        kb_confirm = InlineKeyboardMarkup(row_width=2)
        kb_confirm.add(
            InlineKeyboardButton("✅ Yes", callback_data=f"confirm_promo_del_{code}_p{page}"),
            InlineKeyboardButton("❌ No", callback_data=f"cancel_promo_del_p{page}")
        )
        await call.message.edit_text(
            t(admin_lang, "CONFIRM_PROMO_DEL", code=code),
            reply_markup=kb_confirm
        )
        await call.answer()
        return

    elif call.data.startswith("promo_del_confirmed_"):
        # This branch won't be hit — confirm_promo_del handles it
        pass

    elif call.data.startswith("old_promo_del_"):
        suffix = call.data[len("old_promo_del_"):]
        page = 0
        m = re.search(r'_p(\d+)$', suffix)
        if m:
            page = int(m.group(1))
            code = suffix[:m.start()]
        else:
            code = suffix

        deleted = delete_promo(code)
        if deleted:
            await call.answer(t(admin_lang, "ADMIN_PROMO_DELETED", code=code), show_alert=True)
        else:
            await call.answer(t(admin_lang, "ADMIN_PROMO_DEL_NOT_FOUND"), show_alert=True)

        # Refresh the promo list at the same page
        promos = get_promos()
        if not promos:
            msg = t(admin_lang, "ADMIN_PROMOS_EMPTY")
            kb2 = InlineKeyboardMarkup()
            kb2.add(InlineKeyboardButton(t(admin_lang, "ADMIN_PROMO_BTN_CREATE"), callback_data="promo_create"))
            kb2.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="admin_back"))
            await call.message.edit_text(msg, reply_markup=kb2)
        else:
            all_promos = list(promos.items())
            page_promos, total_pages = paginate(all_promos, page)

            # If current page is now empty (all items deleted), go back one page
            if not page_promos and page > 0:
                page = total_pages - 1
                page_promos, total_pages = paginate(all_promos, page)

            msg = t(admin_lang, "ADMIN_PROMOS_TITLE") + f"  (Page {page + 1}/{total_pages})\n\n"
            for c, p in page_promos:
                pt = t(admin_lang_local, "PROMO_TYPE_FULL") if p["type"] == "full" else t(admin_lang_local, "PROMO_TYPE_TRIAL")
                pd = "♾️" if p["days"] == 0 else f"{p['days']}d"
                if p["used"]:
                    ub = p.get("used_by", "?")
                    ud = get_user(int(ub)) if ub else {}
                    un = ud.get("username") if ud else None
                    ident = f"@{un}" if un else str(ub)
                    st = f"✅ {ident}"
                else:
                    st = t(admin_lang, "ADMIN_PROMO_ACTIVE")
                msg += f"{c} | {pt} {pd} | {st}\n"

            kb2 = InlineKeyboardMarkup()
            for c, p in page_promos:
                if not p["used"]:
                    kb2.add(InlineKeyboardButton(f"🗑 {c}", callback_data=f"promo_del_{c}_p{page}"))
            nav = _nav_buttons("admin_promos", page, total_pages)
            if nav:
                kb2.row(*nav)
            kb2.add(InlineKeyboardButton(t(admin_lang, "ADMIN_PROMO_BTN_CREATE"), callback_data="promo_create"))
            kb2.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="admin_back"))
            await call.message.edit_text(msg, reply_markup=kb2)

    await call.answer()

async def process_promo_days(message: types.Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        return

    admin_lang = _admin_lang()

    try:
        days = int(message.text.strip())
        if days <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t(admin_lang, "ADMIN_PROMO_DAYS_INVALID"))
        return

    data = await state.get_data()
    ptype = data.get("promo_type", "full")
    await state.finish()

    code = make_promo(ptype, days)
    label = t(admin_lang, "PROMO_TYPE_FULL") if ptype == "full" else t(admin_lang, "PROMO_TYPE_TRIAL")
    days_label = f"{days}d"
    msg = t(admin_lang, "ADMIN_PROMO_CREATED", code=code, type=label, days=days_label)
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_PROMO_BTN_LIST"), callback_data="admin_promos"))
    await message.answer(msg, reply_markup=kb, parse_mode="Markdown")


async def process_reset_trial_target(message: types.Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        return

    admin_lang = _admin_lang()
    identifier = message.text.strip().replace("@", "")

    user = get_user_by_username(identifier)
    if not user:
        try:
            user = get_user(int(identifier))
        except (ValueError, TypeError):
            user = {}

    if not user:
        await message.answer(t(admin_lang, "ADMIN_RESET_NOT_FOUND"))
        await state.finish()
        return

    uid = user['id']
    update_user_field(uid, 'trial_used', 0)
    update_user_field(uid, 'access_until', None)
    update_user_field(uid, 'access_paid', 0)
    update_user_field(uid, 'reminder_sent', 0)

    username = user.get("username", str(uid))
    await message.answer(t(admin_lang, "ADMIN_RESET_DONE", username=username))
    await state.finish()


async def process_trial_duration(message: types.Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        return

    admin_lang = _admin_lang()
    text = message.text.strip()

    try:
        if text.endswith("d") or text.endswith("д"):
            hours = int(text[:-1]) * 24
        else:
            hours = int(text)
        if hours <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t(admin_lang, "ADMIN_TRIAL_INVALID"))
        return

    set_setting("trial_duration_hours", hours)

    days = hours // 24
    rem = hours % 24
    await message.answer(t(admin_lang, "ADMIN_TRIAL_CHANGED", hours=hours, days=days, rem=rem))
    await state.finish()


async def process_custom_currency(message: types.Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        return

    admin_lang = _admin_lang()
    symbol = message.text.strip()[:6]
    if not symbol:
        await message.answer(t(admin_lang, "ADMIN_CURRENCY_CUSTOM_PROMPT"))
        return

    await state.update_data(currency=symbol)
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(t(admin_lang, "ADMIN_PRICE_BTN_MONTHLY"), callback_data="price_type_monthly"),
        InlineKeyboardButton(t(admin_lang, "ADMIN_PRICE_BTN_FOREVER"), callback_data="price_type_forever")
    )
    kb.add(InlineKeyboardButton(t(admin_lang, "ADMIN_BACK"), callback_data="admin_back"))
    await message.answer(
        t(admin_lang, "ADMIN_CURRENCY_SAVED", currency=symbol)
        + "\n\n" + t(admin_lang, "ADMIN_PRICE_INFO", price=int(get_setting("access_price", 50)),
                      label=t(admin_lang, "ADMIN_PRICE_LABEL_MONTHLY") if get_setting("price_type", "monthly") == "monthly" else t(admin_lang, "ADMIN_PRICE_LABEL_FOREVER"),
                      currency=symbol),
        reply_markup=kb
    )
    await PriceEdit.waiting_for_type.set()


async def process_admin_add_target(message: types.Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        return
    if message.from_user.id != ADMIN_ID:
        admin_lang_local = get_lang(message.from_user.id)
        await message.answer(t(admin_lang_local, "ADMIN_ONLY_OWNER"))
        await state.finish()
        return

    admin_lang_local = get_lang(message.from_user.id)
    identifier = message.text.strip().replace("@", "")

    target_user = get_user_by_username(identifier)
    if not target_user:
        try:
            target_user = get_user(int(identifier))
        except (ValueError, TypeError):
            target_user = {}

    if not target_user:
        await message.answer(t(admin_lang_local, "ADMIN_ADD_NOT_FOUND"))
        await state.finish()
        return

    target_id = target_user['id']
    target_uname = target_user.get("username", str(target_id))

    from utils.db import is_admin as db_is_admin
    if db_is_admin(target_id) or int(target_id) == int(ADMIN_ID):
        await message.answer(t(admin_lang_local, "ADMIN_ADD_ALREADY"))
        await state.finish()
        return

    add_admin(target_id, target_uname, message.from_user.id)

    # Notify the appointer
    await message.answer(t(admin_lang_local, "ADMIN_ADD_SUCCESS", username=target_uname))

    # Notify the new admin in their language
    new_admin_lang = get_lang(target_id)
    try:
        await message.bot.send_message(target_id, t(new_admin_lang, "ADMIN_NEW_ADMIN_NOTIFY"))
    except Exception:
        pass

    # Set admin commands for the new admin
    try:
        from bot import COMMANDS
        from aiogram.types import BotCommandScopeChat
        for lang_code, data in COMMANDS.items():
            try:
                await message.bot.set_my_commands(
                    data["user"] + data["admin_extra"],
                    scope=BotCommandScopeChat(chat_id=target_id),
                    language_code=lang_code
                )
            except Exception:
                pass
        await message.bot.set_my_commands(
            COMMANDS["en"]["user"] + COMMANDS["en"]["admin_extra"],
            scope=BotCommandScopeChat(chat_id=target_id)
        )
    except Exception:
        pass

    await state.finish()


async def confirm_callbacks(call: types.CallbackQuery, state: FSMContext):
    if not check_admin(call.from_user.id):
        return

    admin_lang_local = get_lang(call.from_user.id)

    if call.data == "cancel_action":
        await call.message.edit_text(t(admin_lang_local, "ACTION_CANCELLED"))
        await state.finish()
        await call.answer()
        return

    if call.data.startswith("cancel_promo_del_p"):
        page = _parse_page(call.data, "cancel_promo_del")
        # Return to promo list
        await state.finish()
        call.data = f"admin_promos_p{page}"
        await admin_callbacks(call, state)
        return

    if call.data.startswith("confirm_kick_"):
        user_id_to_kick = int(call.data.replace("confirm_kick_", ""))
        target_user = get_user(user_id_to_kick)
        username_to_kick = target_user.get("username", str(user_id_to_kick)) if target_user else str(user_id_to_kick)
        kicked_lang = get_lang(user_id_to_kick)

        try:
            await call.bot.ban_chat_member(CHANNEL_ID, user_id_to_kick)
            await call.bot.unban_chat_member(CHANNEL_ID, user_id_to_kick)

            update_user_field(user_id_to_kick, 'access_until', None)
            update_user_field(user_id_to_kick, 'access_paid', 0)
            update_user_field(user_id_to_kick, 'reminder_sent', 0)

            try:
                await call.bot.send_message(user_id_to_kick, t(kicked_lang, "KICKED_BY_ADMIN"))
            except Exception:
                pass

            await call.message.edit_text(t(admin_lang_local, "ADMIN_KICK_SUCCESS", username=username_to_kick))
        except Exception as e:
            await call.message.edit_text(t(admin_lang_local, "ADMIN_KICK_FAILED", error=str(e)))
        await call.answer()
        return

    if call.data.startswith("confirm_promo_del_"):
        suffix = call.data[len("confirm_promo_del_"):]
        page = 0
        m = re.search(r'_p(\d+)$', suffix)
        if m:
            page = int(m.group(1))
            code = suffix[:m.start()]
        else:
            code = suffix

        deleted = delete_promo(code)
        if deleted:
            await call.answer(t(admin_lang_local, "ADMIN_PROMO_DELETED", code=code), show_alert=True)
        else:
            await call.answer(t(admin_lang_local, "ADMIN_PROMO_DEL_NOT_FOUND"), show_alert=True)

        # Refresh promo list at same page
        promos = get_promos()
        if not promos:
            msg = t(admin_lang_local, "ADMIN_PROMOS_EMPTY")
            kb2 = InlineKeyboardMarkup()
            kb2.add(InlineKeyboardButton(t(admin_lang_local, "ADMIN_PROMO_BTN_CREATE"), callback_data="promo_create"))
            kb2.add(InlineKeyboardButton(t(admin_lang_local, "ADMIN_BACK"), callback_data="admin_back"))
            await call.message.edit_text(msg, reply_markup=kb2)
        else:
            all_promos = list(promos.items())
            page_promos, total_pages = paginate(all_promos, page)
            if not page_promos and page > 0:
                page = total_pages - 1
                page_promos, total_pages = paginate(all_promos, page)

            msg = t(admin_lang_local, "ADMIN_PROMOS_TITLE") + f"  (Page {page + 1}/{total_pages})\n\n"
            for c, p in page_promos:
                pt = t(admin_lang_local, "PROMO_TYPE_FULL") if p["type"] == "full" else t(admin_lang_local, "PROMO_TYPE_TRIAL")
                pd = "♾️" if p["days"] == 0 else f"{p['days']}d"
                if p["used"]:
                    ub = p.get("used_by", "?")
                    ud = get_user(int(ub)) if ub else {}
                    un = ud.get("username") if ud else None
                    ident = f"@{un}" if un else str(ub)
                    st = f"✅ {ident}"
                else:
                    st = t(admin_lang_local, "ADMIN_PROMO_ACTIVE")
                msg += f"{c} | {pt} {pd} | {st}\n"

            kb2 = InlineKeyboardMarkup()
            for c, p in page_promos:
                if not p["used"]:
                    kb2.add(InlineKeyboardButton(f"🗑 {c}", callback_data=f"promo_del_{c}_p{page}"))
            nav = _nav_buttons("admin_promos", page, total_pages)
            if nav:
                kb2.row(*nav)
            kb2.add(InlineKeyboardButton(t(admin_lang_local, "ADMIN_PROMO_BTN_CREATE"), callback_data="promo_create"))
            kb2.add(InlineKeyboardButton(t(admin_lang_local, "ADMIN_BACK"), callback_data="admin_back"))
            await call.message.edit_text(msg, reply_markup=kb2)
        return

    if call.data.startswith("confirm_remove_admin_"):
        if call.from_user.id != ADMIN_ID:
            await call.answer(t(admin_lang_local, "ADMIN_ONLY_OWNER"), show_alert=True)
            return
        target_id = int(call.data.replace("confirm_remove_admin_", ""))
        target_user = get_user(target_id)
        uname = target_user.get("username", str(target_id)) if target_user else str(target_id)

        remove_admin(target_id)

        # Notify the removed admin in their language
        try:
            removed_lang = get_lang(target_id)
            await call.bot.send_message(target_id, t(removed_lang, "ADMIN_REVOKED"))
        except Exception:
            pass

        # Remove admin commands for removed admin
        try:
            from aiogram.types import BotCommandScopeChat
            from bot import COMMANDS
            for lang_code, data in COMMANDS.items():
                try:
                    await call.bot.set_my_commands(
                        data["user"],
                        scope=BotCommandScopeChat(chat_id=target_id),
                        language_code=lang_code
                    )
                except Exception:
                    pass
            await call.bot.set_my_commands(
                COMMANDS["en"]["user"],
                scope=BotCommandScopeChat(chat_id=target_id)
            )
        except Exception:
            pass

        await call.message.edit_text(t(admin_lang_local, "ADMIN_REMOVE_SUCCESS", username=uname))
        await call.answer()
        # Return to admins list
        call.data = "admin_admins"
        await admin_callbacks(call, state)
        return

    if call.data.startswith("confirm_reset_trial_"):
        # confirm_reset_trial_{uid}_p{page}
        m_rt = re.match(r'confirm_reset_trial_(\d+)_p(\d+)', call.data)
        if m_rt:
            uid = int(m_rt.group(1))
            page = int(m_rt.group(2))
        else:
            uid = int(call.data.replace("confirm_reset_trial_", ""))
            page = 0
        target_user = get_user(uid)
        uname = target_user.get("username", str(uid)) if target_user else str(uid)

        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton(t(admin_lang_local, "BTN_YES"), callback_data=f"do_reset_trial_{uid}_p{page}"),
            InlineKeyboardButton(t(admin_lang_local, "BTN_NO"), callback_data=f"admin_user_{uid}_p{page}")
        )
        await call.message.edit_text(
            t(admin_lang_local, "CONFIRM_RESET_TRIAL", username=uname),
            reply_markup=kb
        )
        await call.answer()
        return

    if call.data.startswith("do_reset_trial_"):
        m_drt = re.match(r'do_reset_trial_(\d+)_p(\d+)', call.data)
        if m_drt:
            uid = int(m_drt.group(1))
            page = int(m_drt.group(2))
        else:
            uid = int(call.data.replace("do_reset_trial_", ""))
            page = 0
        target_user = get_user(uid)
        uname = target_user.get("username", str(uid)) if target_user else str(uid)

        update_user_field(uid, 'trial_used', 0)
        update_user_field(uid, 'access_until', None)
        update_user_field(uid, 'access_paid', 0)
        update_user_field(uid, 'reminder_sent', 0)

        await call.message.edit_text(t(admin_lang_local, "RESET_TRIAL_DONE", username=uname))
        await call.answer()
        # Return to user detail
        call.data = f"admin_user_{uid}_p{page}"
        await admin_callbacks(call, state)
        return

    await call.answer()


async def process_dm_text(message: types.Message, state: FSMContext):
    if not check_admin(message.from_user.id):
        return
    admin_lang = get_lang(message.from_user.id)
    data = await state.get_data()
    uid = data.get("dm_target_uid")
    page = data.get("dm_return_page", 0)
    await state.finish()

    if not uid:
        await message.answer(t(admin_lang, "DM_FAILED", error="no target"))
        return

    try:
        await message.bot.send_message(int(uid), message.text)
        await message.answer(t(admin_lang, "DM_SENT"))
    except Exception as e:
        await message.answer(t(admin_lang, "DM_FAILED", error=str(e)))


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_panel, commands=["admin"])
    dp.register_callback_query_handler(admin_callbacks, lambda c: c.data.startswith("currency_"), state=PriceEdit.waiting_for_currency)
    dp.register_message_handler(process_custom_currency, state=PriceEdit.waiting_for_currency, content_types=["text"])
    dp.register_callback_query_handler(admin_callbacks, lambda c: c.data in ("price_type_monthly", "price_type_forever"), state=PriceEdit.waiting_for_type)
    dp.register_callback_query_handler(confirm_callbacks, lambda call: call.data.startswith("confirm_") or call.data == "cancel_action" or call.data.startswith("cancel_promo_del_") or call.data.startswith("do_reset_trial_"), state="*")
    dp.register_message_handler(process_admin_add_target, state=AdminAdd.waiting_for_target, content_types=["text"])
    dp.register_message_handler(process_dm_text, state=DmUser.waiting_for_text, content_types=["text"])
    dp.register_callback_query_handler(admin_callbacks, lambda call: call.data.startswith("admin_"), state="*")
    dp.register_message_handler(process_broadcast, content_types=["text", "photo"], state=Broadcast.waiting_for_content)
    dp.register_message_handler(kick_user, commands=["kick"])
    dp.register_message_handler(reset_trial, commands=["reset_trial"])
    dp.register_message_handler(set_trial_duration, commands=["set_trial_duration"])
    dp.register_message_handler(process_msg_target, state=MsgUser.waiting_for_target, content_types=["text"])
    dp.register_message_handler(process_msg_text, state=MsgUser.waiting_for_text, content_types=["text"])
    dp.register_message_handler(process_kick_target, state=KickUser.waiting_for_target, content_types=["text"])
    dp.register_message_handler(process_reset_trial_target, state=ResetTrial.waiting_for_target, content_types=["text"])
    dp.register_message_handler(process_trial_duration, state=TrialEdit.waiting_for_duration, content_types=["text"])
    dp.register_message_handler(process_promo_days, state=PromoCreate.waiting_for_days, content_types=["text"])
    dp.register_message_handler(process_new_price, state=PriceEdit.waiting_for_price, content_types=["text"])
    dp.register_message_handler(process_new_address, state=PriceEdit.waiting_for_address, content_types=["text"])
    dp.register_callback_query_handler(promo_callbacks, lambda call: call.data.startswith("promo_"), state="*")
