from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import datetime
import asyncio
from config.settings import CHANNEL_LINK
from texts import t
from utils.lang import get_lang
from utils.db import get_all_users, update_user_field


async def kick_expired_users(bot):
    while True:
        try:
            users = get_all_users()
            now = datetime.datetime.now()

            for data in users:
                uid = data.get('id')
                if not uid:
                    continue
                access_until = data.get("access_until")
                if access_until:
                    try:
                        end_time = datetime.datetime.fromisoformat(access_until)
                        time_left = (end_time - now).total_seconds()
                        lang = data.get("lang", "en") or "en"

                        # Reminder 1 hour before expiry
                        if 86100 <= time_left <= 86400 and not data.get("reminder_sent"):
                            if data.get("access_paid"):
                                renew_kb2 = InlineKeyboardMarkup()
                                renew_kb2.add(InlineKeyboardButton(
                                    t(lang, "BUTTON_ACTIVATE"),
                                    callback_data="renew_access"
                                ))
                                await bot.send_message(uid, t(lang, "PAID_ENDING"), reply_markup=renew_kb2)
                            else:
                                renew_kb3 = InlineKeyboardMarkup()
                                renew_kb3.add(InlineKeyboardButton(
                                    t(lang, "BUTTON_ACTIVATE"),
                                    callback_data="renew_access"
                                ))
                                await bot.send_message(uid, t(lang, "TRIAL_ENDING"), reply_markup=renew_kb3)
                            update_user_field(uid, 'reminder_sent', 1)

                        # Access expired
                        if time_left <= 0:
                            renew_kb = InlineKeyboardMarkup()
                            renew_kb.add(InlineKeyboardButton(
                                t(lang, "BUTTON_ACTIVATE"),
                                callback_data="renew_access"
                            ))
                            await bot.send_message(uid, t(lang, "TRIAL_EXPIRED"), reply_markup=renew_kb)
                            try:
                                await bot.ban_chat_member(CHANNEL_LINK, int(uid))
                                await bot.unban_chat_member(CHANNEL_LINK, int(uid))
                            except Exception as e:
                                print(f"[KICK ERROR] {uid}: {e}")
                            update_user_field(uid, 'access_until', None)
                            update_user_field(uid, 'access_paid', 0)
                            update_user_field(uid, 'reminder_sent', 0)

                    except Exception as e:
                        print(f"[TIME PARSE ERROR] {uid}: {e}")

        except Exception as e:
            print(f"[DB ERROR] {e}")

        await asyncio.sleep(60)

