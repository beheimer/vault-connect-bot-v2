import re
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config.settings import ADMIN_ID, REFERRAL_ENABLED, PROMO_ENABLED
from utils.admin_check import is_admin as check_admin
from utils.referral import generate_ref_link, add_user, get_user_stats, check_referral
from utils.promo import redeem_promo
from utils.access import (
    activate_trial_for_user,
    generate_personal_invite,
    get_access_mode
)
from texts import t, ALL_ACTIVATE, ALL_TRIAL, ALL_INVITE, ALL_MY_ACCESS, ALL_ADMIN_PANEL
from utils.lang import get_lang, set_lang
from utils.db import get_user, save_user, update_user_field, get_setting, set_setting, get_admins

from datetime import datetime
import asyncio
import itertools

QR_IMAGE_URL = "https://i.ibb.co/5gMGHD0J/qr-gradient-neon.png"


class PaymentState(StatesGroup):
    waiting_for_txid = State()

class CustomDaysState(StatesGroup):
    waiting_for_days = State()


def escape_markdown(text: str) -> str:
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def main_menu(user_id=None):
    lang = get_lang(user_id) if user_id else "en"
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    has_paid = False
    if user_id:
        try:
            _user = get_user(int(user_id))
            has_paid = _user.get("access_paid", False)
        except:
            pass

    is_admin_user = user_id and check_admin(int(user_id))
    if not has_paid and not is_admin_user:
        kb.add(t(lang, "BUTTON_ACTIVATE"), t(lang, "BUTTON_TRIAL"))

    if not is_admin_user:
        if REFERRAL_ENABLED:
            kb.add(t(lang, "BUTTON_INVITE"), t(lang, "BUTTON_MY_ACCESS"))
        else:
            kb.add(t(lang, "BUTTON_MY_ACCESS"))

    if user_id and check_admin(int(user_id)):
        _al = get_lang(ADMIN_ID)
        _btn = t(_al, "BTN_ADMIN_PANEL")
        kb.add(_btn)
    return kb


def popup_button(lang="en"):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(t(lang, "BUTTON_DETAILS"), callback_data="explain_how_it_works"))
    return kb


def lang_picker_keyboard():
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
        InlineKeyboardButton("🇺🇦 Українська", callback_data="set_lang_uk"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
    )
    return kb


async def boot_animation(message_or_msg, lang):
    frames = [
        t(lang, "BOOT_1"),
        t(lang, "BOOT_2"),
        t(lang, "BOOT_3"),
        t(lang, "BOOT_4"),
        t(lang, "BOOT_5"),
    ]
    loader = itertools.cycle(["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"])
    msg = await message_or_msg.answer("⣾ " + t(lang, "BOOT_LOADING"))
    for frame in frames:
        emoji = next(loader)
        await asyncio.sleep(0.3)
        await msg.edit_text(f"{emoji} {frame}")


# --- /start ---
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    payload = message.get_args()

    if REFERRAL_ENABLED:
        await check_referral(message.bot, user_id, payload)
    add_user(user_id, full_name, message.from_user.username)

    # Check if user already has a language set
    lang = get_lang(user_id)

    # If no lang record yet (new user), show language picker
    user_data = get_user(int(user_id))
    has_lang = bool(user_data.get("lang"))

    if not has_lang:
        await message.answer(
            "🇬🇧 Choose your language\n🇺🇦 Обери мову\n🇷🇺 Выбери язык",
            reply_markup=lang_picker_keyboard()
        )
        return

    # User has a language, proceed normally
    await _show_welcome(message, user_id, full_name, lang)


async def _show_welcome(message, user_id, full_name, lang):
    user = get_user(int(user_id))
    mode_key = get_access_mode(user)

    mode = t(lang, mode_key)

    await boot_animation(message, lang)

    await message.answer(
        t(lang, "WELCOME_TEXT", name=full_name),
        reply_markup=popup_button(lang)
    )

    await message.answer(
        t(lang, "MENU_HINT"),
        reply_markup=main_menu(user_id=user_id)
    )


# --- Language selection callback ---
async def lang_selected(call: types.CallbackQuery):
    user_id = call.from_user.id
    lang_code = call.data.replace("set_lang_", "")  # en / uk / ru
    set_lang(user_id, lang_code)

    await call.message.edit_text(
        t(lang_code, "LANG_SET"),
        reply_markup=None
    )
    await call.answer()

    full_name = call.from_user.full_name
    await _show_welcome(call.message, user_id, full_name, lang_code)


# --- Activate access ---
async def pay_manual(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)

    def needs_renewal(user: dict) -> bool:
        try:
            access_until = datetime.fromisoformat(user.get("access_until"))
            return (access_until - datetime.now()).total_seconds() < 86400
        except:
            return True

    user = get_user(int(user_id))

    if not user.get("access_paid") or needs_renewal(user):
        price = int(get_setting("access_price", 50))
        price_type = get_setting("price_type", "monthly")
        if price_type == "monthly":
            price_suffix = t(lang, "PRICE_SUFFIX_MONTHLY")
        else:
            price_suffix = t(lang, "PRICE_SUFFIX_FOREVER")
        currency = get_setting("currency", "$")
        price_label = f"{currency}{price} {price_suffix}"
        await message.answer(t(lang, "PAYMENT_TEXT", price=price_label))

        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton(t(lang, "SHOW_QR"), callback_data="show_qr"),
            InlineKeyboardButton(t(lang, "PAID_BUTTON"), callback_data="paid_confirm")
        )
        await message.answer(
            t(lang, "CRYPTO_INFO"),
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    else:
        await message.answer(t(lang, "ALREADY_PAID"))


# --- Show QR ---
async def show_qr(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = get_lang(user_id)

    text = t(lang, "CRYPTO_INFO") + f"[👾]({QR_IMAGE_URL})"

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(t(lang, "HIDE_QR"), callback_data="hide_qr"),
        InlineKeyboardButton(t(lang, "PAID_BUTTON"), callback_data="paid_confirm")
    )
    await callback_query.message.edit_text(text, reply_markup=keyboard, parse_mode="Markdown")
    await callback_query.answer()


# --- Hide QR ---
async def hide_qr(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = get_lang(user_id)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(t(lang, "SHOW_QR"), callback_data="show_qr"),
        InlineKeyboardButton(t(lang, "PAID_BUTTON"), callback_data="paid_confirm")
    )
    await callback_query.message.edit_text(
        t(lang, "CRYPTO_INFO"),
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await callback_query.answer()


# --- Paid confirm ---
async def paid_confirm(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    lang = get_lang(user_id)
    await callback_query.message.answer(t(lang, "TXID_PROMPT"))
    await PaymentState.waiting_for_txid.set()
    await callback_query.answer()


# --- Receive TXID ---
async def receive_txid(message: types.Message, state: FSMContext):
    txid = message.text.strip()
    user = message.from_user
    user_id = user.id
    lang = get_lang(user_id)

    safe_txid = escape_markdown(txid)
    username = escape_markdown(user.username) if user.username else str(user.id)

    identity = f"@{username}" if user.username else f"ID: {user.id}"

    # Admin notification in admin's language
    admin_lang = get_lang(ADMIN_ID)
    text = t(admin_lang, "PAYMENT_REQUEST",
             identity=identity,
             date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
             txid=safe_txid)

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(t(admin_lang, "ADMIN_30_DAYS"), callback_data=f"approve_pay_{user.id}_30"),
        InlineKeyboardButton(t(admin_lang, "ADMIN_90_DAYS"), callback_data=f"approve_pay_{user.id}_90")
    )
    kb.add(
        InlineKeyboardButton(t(admin_lang, "ADMIN_180_DAYS"), callback_data=f"approve_pay_{user.id}_180"),
        InlineKeyboardButton(t(admin_lang, "ADMIN_FOREVER"), callback_data=f"approve_pay_{user.id}_0")
    )
    kb.add(
        InlineKeyboardButton(
            t(get_lang(ADMIN_ID), "BTN_CUSTOM_DAYS"),
            callback_data=f"approve_custom_{user.id}"
        )
    )
    kb.add(
        InlineKeyboardButton(t(admin_lang, "ADMIN_REJECT"), callback_data=f"reject_pay_{user.id}_0")
    )

    all_admin_ids = [ADMIN_ID] + [a['user_id'] for a in get_admins()]
    for _aid in all_admin_ids:
        try:
            sent = await message.bot.send_message(_aid, text, reply_markup=kb, parse_mode="Markdown")
            try:
                await message.bot.pin_chat_message(_aid, sent.message_id, disable_notification=True)
            except:
                pass
        except Exception as e:
            print(f"[PAYMENT NOTIFY] Could not notify admin {_aid}: {e}")

    await message.answer(t(lang, "TXID_SENT"))
    await state.finish()


# --- Payment decision (admin approves/rejects) ---
async def handle_payment_decision(call: types.CallbackQuery):
    data = call.data
    parts = data.split("_")
    action = parts[0]       # approve / reject
    user_id = parts[2]
    days = int(parts[3]) if len(parts) > 3 else 30

    lang = get_lang(int(user_id))
    admin_lang = get_lang(ADMIN_ID)

    user_data = get_user(int(user_id))

    if action == "approve":
        from datetime import timedelta
        now = datetime.now()

        update_user_field(int(user_id), 'access_paid', 1)
        update_user_field(int(user_id), 'paid_at', datetime.now().isoformat())
        update_user_field(int(user_id), 'reminder_sent', 0)

        if days == 0:
            update_user_field(int(user_id), 'access_until', "2099-12-31T23:59:59")
            period_text = t(lang, "PERIOD_FOREVER")
        else:
            update_user_field(int(user_id), 'access_until', (now + timedelta(days=days)).isoformat())
            period_text = t(lang, "PERIOD_DAYS", days=days)

        link = await generate_personal_invite(call.bot, int(user_id))
        if link:
            await call.bot.send_message(
                int(user_id),
                t(lang, "PAYMENT_APPROVED_LINK", link=link),
                reply_markup=main_menu(user_id=int(user_id))
            )
        else:
            await call.bot.send_message(
                int(user_id),
                t(lang, "PAYMENT_APPROVED_NO_LINK"),
                reply_markup=main_menu(user_id=int(user_id))
            )

        admin_username = call.from_user.username or str(call.from_user.id)
        decision_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        await call.message.edit_text(
            call.message.text + t(admin_lang, "ADMIN_ACCEPTED", period=period_text, admin=admin_username, date=decision_date),
            reply_markup=None, parse_mode="Markdown"
        )

    elif action == "reject":
        await call.bot.send_message(int(user_id), t(lang, "PAYMENT_REJECTED"))
        admin_username = call.from_user.username or str(call.from_user.id)
        decision_date = datetime.now().strftime("%d.%m.%Y %H:%M")
        await call.message.edit_text(
            call.message.text + t(admin_lang, "ADMIN_REJECTED", admin=admin_username, date=decision_date),
            reply_markup=None, parse_mode="Markdown"
        )

    await call.answer()


# --- Trial ---
async def activate_trial(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)

    # Check if trial has already been used
    user_data = get_user(int(user_id))
    if user_data.get("trial_used"):
        await message.answer(t(lang, "TRIAL_ALREADY_USED"))
        return

    # Read trial duration from settings
    hours = int(get_setting("trial_duration_hours", 120))
    days = hours // 24
    rem = hours % 24

    if days > 0 and rem > 0:
        duration_text = t(lang, "DURATION_DAYS_HOURS", days=days, rem=rem)
    elif days > 0:
        duration_text = t(lang, "DURATION_DAYS", days=days)
    else:
        duration_text = t(lang, "DURATION_HOURS", hours=hours)

    from datetime import timedelta
    end_time = (datetime.now() + timedelta(hours=hours)).strftime("%d.%m.%Y %H:%M")

    confirm_text = "\n\n".join([
        t(lang, "TRIAL_CONFIRM_TITLE"),
        t(lang, "TRIAL_CONFIRM_DURATION", duration=duration_text),
        t(lang, "TRIAL_CONFIRM_START") + "\n" + t(lang, "TRIAL_CONFIRM_END", end_time=end_time),
        t(lang, "TRIAL_CONFIRM_NOTE"),
    ])

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(t(lang, "BTN_ACTIVATE_TRIAL"), callback_data="trial_confirm"),
        InlineKeyboardButton(t(lang, "BTN_CANCEL"), callback_data="trial_cancel")
    )
    await message.answer(confirm_text, reply_markup=kb)


async def trial_confirm(call: types.CallbackQuery):
    user_id = call.from_user.id
    lang = get_lang(user_id)
    result = activate_trial_for_user(user_id)
    if result == "activated":
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer(t(lang, "TRIAL_ACTIVATED"))
        link = await generate_personal_invite(call.bot, user_id)
        if link:
            await call.message.answer(t(lang, "TRIAL_LINK", link=link))
        else:
            await call.message.answer(t(lang, "TRIAL_LINK_ALREADY_MEMBER"))
    else:
        await call.message.answer(t(lang, "TRIAL_ALREADY_USED"))
    await call.answer()


async def trial_cancel(call: types.CallbackQuery):
    lang = get_lang(call.from_user.id)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t(lang, "TRIAL_CANCEL"))
    await call.answer()


# --- Referral info ---
async def refer_info(message: types.Message):
    if not REFERRAL_ENABLED:
        return
    user_id = message.from_user.id
    lang = get_lang(user_id)
    ref_link = generate_ref_link(user_id)
    await message.answer(
        t(lang, "REF_INFO", link=f"`{ref_link}`"),
        parse_mode="Markdown"
    )


# --- Stats ---
async def stats(message: types.Message):
    user_id = message.from_user.id
    lang = get_lang(user_id)
    invited, paid = get_user_stats(user_id)
    ark_units = paid % 3

    user = get_user(int(user_id))
    access_until = user.get("access_until")
    if access_until:
        if access_until.startswith("2099"):
            access_time_text = "∞"
        else:
            delta = datetime.fromisoformat(access_until) - datetime.now()
            total_seconds = delta.total_seconds()
            days_left = max(int(total_seconds // 86400), 0)
            hours_left = max(int((total_seconds % 86400) // 3600), 0)
            access_time_text = t(lang, "ACCESS_TIME", days=days_left, hours=hours_left)
    else:
        access_time_text = t(lang, "ACCESS_TIME_ZERO")

    mode_key = get_access_mode(user)
    mode = t(lang, mode_key)

    if REFERRAL_ENABLED:
        await message.answer(t(lang, "STATS_TEXT",
            invited=invited,
            units=ark_units,
            access_time=access_time_text,
            mode=mode
        ), reply_markup=main_menu(user_id=user_id))
    else:
        await message.answer(t(lang, "STATS_TEXT_NO_REF",
            access_time=access_time_text,
            mode=mode
        ), reply_markup=main_menu(user_id=user_id))


# --- Popup (details) ---
async def explain_popup(call: types.CallbackQuery):
    lang = get_lang(call.from_user.id)
    await call.answer(t(lang, "POPUP_TEXT"), show_alert=True)


# --- Register handlers ---
async def renew_access(call: types.CallbackQuery):
    lang = get_lang(call.from_user.id)
    await pay_manual(call.message)
    await call.answer()


async def change_language(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
        InlineKeyboardButton("🇺🇦 Українська", callback_data="set_lang_uk"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
    )
    await message.answer("🌐 Please select your language", reply_markup=kb)



# --- Promo code ---
async def handle_promo_code(message: types.Message):
    if not PROMO_ENABLED:
        return
    code = message.text.strip()
    user_id = message.from_user.id
    lang = get_lang(user_id)

    status, promo = redeem_promo(code, user_id)

    if status == "not_found":
        return  # silently ignore

    if status == "already_used":
        await message.answer(t(lang, "PROMO_INVALID"))
        return

    if status == "already_active":
        await message.answer(t(lang, "PROMO_ALREADY_ACTIVE"))
        return

    if status == "trial_already_used":
        await message.answer(t(lang, "TRIAL_ALREADY_USED"))
        return

    # success
    days = promo["days"]
    if promo["type"] == "full":
        if days == 0:
            await message.answer(t(lang, "PROMO_ACTIVATED_FULL_FOREVER"))
        else:
            await message.answer(t(lang, "PROMO_ACTIVATED_FULL_DAYS", days=days))
    elif promo["type"] == "trial":
        await message.answer(t(lang, "PROMO_ACTIVATED_TRIAL", days=days))

    # Generate invite and send
    link = await generate_personal_invite(message.bot, user_id)
    if link:
        await message.answer(t(lang, "TRIAL_LINK", link=link))

    # Update menu
    await message.answer(t(lang, "MENU_HINT"), reply_markup=main_menu(user_id=user_id))


async def admin_panel_trigger(message: types.Message):
    from handlers.admin_panel import admin_panel
    await admin_panel(message)


async def approve_custom(call: types.CallbackQuery, state: FSMContext):
    user_id = call.data.replace("approve_custom_", "")
    await state.update_data(target_user_id=user_id, original_message=call.message.message_id)
    # Get username if exists
    _udata = get_user(int(user_id))
    _uname = _udata.get("username")
    _label = f"@{_uname}" if _uname else f"ID {user_id}"
    admin_lang = get_lang(ADMIN_ID)
    await call.message.answer(t(admin_lang, "CUSTOM_DAYS_PROMPT", label=_label))
    await CustomDaysState.waiting_for_days.set()
    await call.answer()


async def process_custom_days(message: types.Message, state: FSMContext):
    from config.settings import ADMIN_ID
    if message.from_user.id != ADMIN_ID:
        return
    try:
        days = int(message.text.strip())
        if days <= 0:
            raise ValueError
    except ValueError:
        await message.answer(t(get_lang(message.from_user.id), "ERR_POSITIVE_INT"))
        return

    data = await state.get_data()
    user_id = data.get("target_user_id")
    await state.finish()

    from datetime import timedelta
    from utils.access import generate_personal_invite

    now = datetime.now()
    update_user_field(int(user_id), 'access_paid', 1)
    update_user_field(int(user_id), 'access_until', (now + timedelta(days=days)).isoformat())
    update_user_field(int(user_id), 'paid_at', now.isoformat())
    update_user_field(int(user_id), 'reminder_sent', 0)

    link = await generate_personal_invite(message.bot, int(user_id))
    lang = get_lang(int(user_id))
    if link:
        await message.bot.send_message(int(user_id),
            t(lang, "PAYMENT_APPROVED_LINK", link=link),
            reply_markup=main_menu(user_id=int(user_id))
        )
    else:
        await message.bot.send_message(int(user_id),
            t(lang, "PAYMENT_APPROVED_NO_LINK"),
            reply_markup=main_menu(user_id=int(user_id))
        )
    # Edit and unpin original payment request message
    try:
        orig_msg_id = data.get("original_message")
        if orig_msg_id:
            await message.bot.edit_message_reply_markup(ADMIN_ID, orig_msg_id, reply_markup=None)
            await message.bot.unpin_chat_message(ADMIN_ID, orig_msg_id)
    except:
        pass
    _udata2 = get_user(int(user_id))
    _uname2 = _udata2.get("username")
    _label2 = f"@{_uname2}" if _uname2 else f"ID {user_id}"
    admin_lang = get_lang(ADMIN_ID)
    await message.answer(t(admin_lang, "CUSTOM_DAYS_CONFIRM", days=days, label=_label2))


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=["start"])
    dp.register_message_handler(lambda msg: admin_panel_trigger(msg), lambda msg: msg.text in ALL_ADMIN_PANEL)
    dp.register_message_handler(change_language, commands=["language"])
    dp.register_callback_query_handler(lang_selected, lambda c: c.data.startswith("set_lang_"))
    dp.register_callback_query_handler(explain_popup, lambda c: c.data == "explain_how_it_works")
    dp.register_message_handler(pay_manual, lambda msg: msg.text in ALL_ACTIVATE)
    dp.register_message_handler(activate_trial, lambda msg: msg.text in ALL_TRIAL)
    dp.register_callback_query_handler(trial_confirm, lambda c: c.data == 'trial_confirm')
    dp.register_callback_query_handler(trial_cancel, lambda c: c.data == 'trial_cancel')
    dp.register_callback_query_handler(renew_access, lambda c: c.data == 'renew_access')
    dp.register_message_handler(refer_info, lambda msg: msg.text in ALL_INVITE)
    dp.register_message_handler(stats, lambda msg: msg.text in ALL_MY_ACCESS)
    dp.register_callback_query_handler(show_qr, lambda c: c.data == "show_qr")
    dp.register_callback_query_handler(hide_qr, lambda c: c.data == "hide_qr")
    dp.register_callback_query_handler(paid_confirm, lambda c: c.data == "paid_confirm", state="*")
    dp.register_message_handler(receive_txid, state=PaymentState.waiting_for_txid)
    dp.register_callback_query_handler(
        handle_payment_decision,
        lambda c: c.data.startswith('approve_pay_') or c.data.startswith('reject_pay_')
    )
    dp.register_callback_query_handler(approve_custom, lambda c: c.data.startswith('approve_custom_'))
    dp.register_message_handler(process_custom_days, state=CustomDaysState.waiting_for_days, content_types=["text"])
    dp.register_message_handler(
        handle_promo_code,
        lambda msg: msg.text and re.match(r'^[A-Z0-9]{4}-[A-Z0-9]{4}$', msg.text.strip())
    )
