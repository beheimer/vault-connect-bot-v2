from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault
from config.settings import BOT_TOKEN, ADMIN_ID
from handlers import register_all_handlers
import asyncio
from utils.database import kick_expired_users
from utils.db import init_db

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

register_all_handlers(dp)

def run_migration():
    import os, json
    db_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.json')
    if os.path.exists(db_json_path):
        try:
            from utils.db import set_setting
            with open(db_json_path) as f:
                db = json.load(f)
            for key, value in db.get('_settings', {}).items():
                set_setting(key, str(value))
            os.rename(db_json_path, db_json_path + '.migrated')
        except Exception as e:
            print(f"Migration warning: {e}")


COMMANDS = {
    "en": {
        "user": [
            BotCommand("start",    "🚀 Start the bot"),
            BotCommand("language", "🌐 Change language"),
        ],
        "admin_extra": [
            BotCommand("admin",              "🛠 Admin panel"),
                BotCommand("kick",               "🚫 Remove user"),
            BotCommand("reset_trial",        "🔄 Reset user trial"),
            BotCommand("broadcast",          "📢 Send message to all users"),
            BotCommand("msg",                "✉️ Send message to specific user"),
            BotCommand("set_trial_duration", "⏱ Set trial duration"),
        ],
    },
    "uk": {
        "user": [
            BotCommand("start",    "🚀 Запустити бота"),
            BotCommand("language", "🌐 Змінити мову"),
        ],
        "admin_extra": [
            BotCommand("admin",              "🛠 Адмін панель"),
                BotCommand("kick",               "🚫 Видалити користувача"),
            BotCommand("reset_trial",        "🔄 Скинути тріал"),
            BotCommand("broadcast",          "📢 Розсилка всім"),
            BotCommand("msg",                "✉️ Написати конкретному юзеру"),
            BotCommand("set_trial_duration", "⏱ Тривалість тріалу"),
        ],
    },
    "ru": {
        "user": [
            BotCommand("start",    "🚀 Запустить бота"),
            BotCommand("language", "🌐 Изменить язык"),
        ],
        "admin_extra": [
            BotCommand("admin",              "🛠 Панель администратора"),
                BotCommand("kick",               "🚫 Удалить пользователя"),
            BotCommand("reset_trial",        "🔄 Сбросить триал"),
            BotCommand("broadcast",          "📢 Рассылка всем"),
            BotCommand("msg",                "✉️ Написать конкретному юзеру"),
            BotCommand("set_trial_duration", "⏱ Длительность триала"),
        ],
    },
}


async def set_commands():
    from utils.db import get_admins

    # Set user commands for each language
    for lang_code, data in COMMANDS.items():
        await bot.set_my_commands(
            data["user"],
            scope=BotCommandScopeDefault(),
            language_code=lang_code
        )

    # Fallback default (English) for unknown languages
    await bot.set_my_commands(COMMANDS["en"]["user"])

    # Collect all admin IDs (primary + DB admins)
    admin_ids = [ADMIN_ID]
    try:
        db_admins = get_admins()
        for a in db_admins:
            aid = a.get("user_id")
            if aid and aid not in admin_ids:
                admin_ids.append(aid)
    except Exception:
        pass

    # Set admin commands for all admins
    for admin_id in admin_ids:
        for lang_code, data in COMMANDS.items():
            try:
                await bot.set_my_commands(
                    data["user"] + data["admin_extra"],
                    scope=BotCommandScopeChat(chat_id=admin_id),
                    language_code=lang_code
                )
            except Exception as e:
                print(f"[COMMANDS] Admin {admin_id} {lang_code} error: {e}")

        # Admin fallback (English)
        try:
            await bot.set_my_commands(
                COMMANDS["en"]["user"] + COMMANDS["en"]["admin_extra"],
                scope=BotCommandScopeChat(chat_id=admin_id)
            )
        except Exception as e:
            print(f"[COMMANDS] Admin {admin_id} fallback error: {e}")

    print("[COMMANDS] All commands set successfully")


async def on_startup(dp):
    init_db()
    run_migration()
    await set_commands()
    asyncio.get_event_loop().create_task(kick_expired_users(bot))


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
