# texts.py — multilingual support (en, uk, ru)
import json

TEXTS = {
    "en": {
        # Welcome
        "WELCOME_TEXT": (
            "Hi, {name}! 👋\n\n"
            "Here you can explore our services\n"
            "and get access.\n\n"
            "Choose an action from the menu below."
        ),
        "POPUP_TEXT": (
            "🎯 What you get inside:\n\n"
            "● [item 1]\n"
            "● [item 2]\n"
            "● [item 3]\n\n"
            "💬 Community of active members\n"
            "🔐 Private access"
        ),
        # Payment
        "PAYMENT_TEXT": (
            "💳 Access payment\n\n"
            "💰 Price: {price}\n\n"
            "↳ Send payment to the address below\n"
            "↳ After payment press [Paid]\n"
            "↳ Enter the TXID of the transaction\n"
            "↳ Wait for confirmation\n\n"
            "Payment address: 👇"
        ),
        "CRYPTO_INFO": (
            "● Coin: Tether (USDT)\n"
            "● Network: TRON - TRC20\n\n"
            "`TEwnPR7daATh84DLFiTXJGaCge4NbYDbV8`\n"
            "↳ Tap the address to copy!\n\n"
        ),
        "CRYPTO_INFO_DYNAMIC": (
            "● Coin: Tether (USDT)\n"
            "● Network: TRON - TRC20\n\n"
            "`{address}`\n"
            "↳ Tap the address to copy!\n\n"
        ),
        "SHOW_QR": "Show QR code",
        "HIDE_QR": "Hide QR code",
        "PAID_BUTTON": "Paid",
        "TXID_PROMPT": "💳 Enter your TXID to verify the payment.",
        "TXID_SENT": (
            "💳 ↳ Data sent for verification.\n\n"
            "↳ Wait for confirmation from the administrator."
        ),
        "ALREADY_PAID": (
            "✅ ↳ Your access is already active.\n\n"
            "↳ Everything is working, you are in the channel."
        ),
        # Payment admin
        "PAYMENT_REQUEST": (
            "💳 Payment request\n\n"
            "👤 User: {identity}\n"
            "🕰 Date: {date}\n"
            "🔗 TXID: `{txid}`"
        ),
        "ADMIN_30_DAYS": "30 days",
        "ADMIN_90_DAYS": "90 days",
        "ADMIN_180_DAYS": "180 days",
        "ADMIN_FOREVER": "♾ Forever",
        "ADMIN_REJECT": "❌ Reject",
        "ADMIN_ACCEPTED": "\n\n✅ Accepted: @{admin} • {date}\nPeriod: {period}",
        "ADMIN_REJECTED": "\n\n❌ Rejected: @{admin} • {date}",
        "PERIOD_FOREVER": "forever ♾",
        "PERIOD_DAYS": "{days} days",
        "PAYMENT_APPROVED_LINK": "✅ Payment confirmed!\n\n🔗 Entry link:\n{link}",
        "PAYMENT_APPROVED_NO_LINK": "✅ Payment confirmed! You may already be in the channel.",
        "PAYMENT_REJECTED": (
            "❌ Payment not confirmed.\n\n"
            "↳ Check the TXID or contact the administrator."
        ),
        # Trial
        "TRIAL_ACTIVATED": (
            "✅ Trial access activated!\n\n"
            "↳ You have 120 hours of free access."
        ),
        "TRIAL_ALREADY_USED": (
            "⚠️ Trial access has already been used.\n\n"
            "To continue, get full access."
        ),
        "TRIAL_LINK": "Entry link:\n{link}",
        "TRIAL_FAILED": (
            "⚠️ Could not create an invite link.\n\n"
            "↳ You may already be in the channel."
        ),
        "TRIAL_LINK_ALREADY_MEMBER": "✅ Trial activated! You're already in the channel or the link will arrive shortly.",
        "PROMO_ALREADY_ACTIVE": "✅ You already have active access. No need to use this promo code.",
        # Referral
        "REF_INFO": (
            "🤝 Invite a friend\n\n"
            "🔗 Your referral link:\n{link}\n\n"
            "🧬 1 friend's payment = 1 point\n"
            "💠 3 points = 30 days of free access\n\n"
            "Share the link and earn bonuses."
        ),
        "REF_ENTERED": "🛰 Someone followed your referral link.\n",
        # Stats
        "STATS_TEXT": (
            "📋 My access\n"
            "─────────────\n"
            "Status: {mode}\n"
            "Remaining: {access_time}\n"
            "─────────────\n"
            "Invited: {invited}\n"
            "Points: {units} / 3\n"
        ),
        "STATS_TEXT_NO_REF": (
            "📋 My access\n"
            "─────────────\n"
            "Status: {mode}\n"
            "Remaining: {access_time}\n"
            "─────────────\n"
        ),
        # Access approval
        "APPROVED_USER": "✅ Access confirmed!\n\n🔗 Entry link:\n{link}",
        "APPROVED_FAILED": (
            "⚠️ Access confirmed, but the link was not created.\n"
            "↳ You may already be in the channel."
        ),
        "APPROVED_CONFIRM": "✅ User @{username} has been added to the channel.",
        "APPROVE_NOT_FOUND": "❌ User not found. Check @username or ID.",
        "APPROVE_USAGE": "⚙️ Format: /approve @username",
        # Bonus
        "BONUS_RECEIVED": "🎉 You earned +1 point!\n",
        "BONUS_REWARDED": "🎉 3 points collected!\n\nAccess extended by 30 days.",
        # Expiry reminders
        "TRIAL_ENDING": (
            "⏳ Less than an hour left of trial access.\n\n"
            "↳ Get full access to stay in the channel."
        ),
        "PAID_ENDING": (
            "⏳ Less than 24 hours of access remaining.\n\n"
            "↳ Renew access to stay in the channel."
        ),
        "TRIAL_EXPIRED": (
            "🔒 Your access has expired.\n\n"
            "↳ Get access to return to the channel."
        ),
        # Kick
        "KICKED_BY_ADMIN": "⛔️ Your access has been revoked by the administrator.",
        "KICK_SUCCESS": "🗑 User @{username} has been removed from the channel.",
        "KICK_NOT_FOUND": "🔍 User not found in the database.",
        "KICK_FAILED": "⚠️ Action failed: {error}",
        # Broadcast
        "BROADCAST_EMPTY": "📭 Provide text after /broadcast",
        "BROADCAST_RESULT": "📡 Broadcast complete. Sent: {ok}, Failed: {fail}",
        # Copy trading
        "COPY_ACCESS_ENABLED": (
            "🔓 Copy trading\n\n"
            "Your Bybit account automatically copies trades in real time.\n\n"
            "How to connect:\n"
            "Press the button below and send your Bybit UID\n"
            "After verification, you will be added to the system.\n\n"
            "Awaiting UID..."
        ),
        "COPY_USAGE": "⚙️ Enter your Bybit UID to connect copy trading.",
        "COPY_NOT_ACTIVATED": (
            "⚠️ Copy trading is available only with an active access.\n\n"
            "↳ Get access from the main menu."
        ),
        "COPY_UID_RECEIVED": (
            "✅ UID received.\n\n"
            "↳ Wait for confirmation from the administrator."
        ),
        # Menu buttons
        "BUTTON_ACTIVATE": "🔐 Activate access",
        "BUTTON_TRIAL": "🧪 Trial access",
        "BUTTON_INVITE": "🤝 Invite a friend",
        "BUTTON_MY_ACCESS": "📋 My access",
        "BUTTON_DETAILS": "🔍 Details",
        # Language
        "LANG_SELECT": "🌍 Choose your language:",
        "LANG_CHOOSE_FIRST": "🌍 Please choose your language first.",
        "MENU_HINT": "Use the menu below to navigate. 👇",
        # Access modes
        "MODE_ADMIN": "👑 ADMIN",
        "MODE_FULL": "💠 FULL ACCESS",
        "MODE_TRIAL": "🧪 TRIAL ACCESS",
        "MODE_GUEST": "🕶️ GUEST",
        # Boot animation
        "BOOT_1": "Connecting...",
        "BOOT_2": "Checking access...",
        "BOOT_3": "Loading...",
        "BOOT_4": "Almost ready...",
        "BOOT_5": "Welcome! ✅",
        "BOOT_LOADING": "Loading...",
        # Promo
        "PROMO_ACTIVATED_FULL_FOREVER": (
            "✅ Promo code activated!\n\n"
            "Your access is active: ♾️"
        ),
        "PROMO_ACTIVATED_FULL_DAYS": (
            "✅ Promo code activated!\n\n"
            "Your access is active for: {days} days."
        ),
        "PROMO_ACTIVATED_TRIAL": (
            "✅ Promo code activated!\n\n"
            "Trial access opened for {days} days."
        ),
        "PROMO_INVALID": "❌ Promo code is invalid or already used.",
        # Custom days
        "CUSTOM_DAYS_PROMPT": "✏️ Enter number of days for user {label}:",
        "CUSTOM_DAYS_CONFIRM": "✅ Approved — {days} days for {label}.",
        # Trial cancel
        "TRIAL_CANCEL": "Activation cancelled.",
        # Trial confirmation
        "TRIAL_CONFIRM_TITLE": "🧪 Trial Access",
        "TRIAL_CONFIRM_DURATION": "You will get access to the private channel for {duration}.",
        "TRIAL_CONFIRM_START": "📅 Start: now",
        "TRIAL_CONFIRM_END": "📅 Ends: {end_time}",
        "TRIAL_CONFIRM_NOTE": (
            "After expiration, access will be closed automatically.\n"
            "To stay — purchase full access from the menu."
        ),
        "BTN_ACTIVATE_TRIAL": "✅ Activate",
        # Duration
        "DURATION_DAYS_HOURS": "{days}d {rem}h",
        "DURATION_DAYS": "{days} days",
        "DURATION_HOURS": "{hours} hours",
        # Access time
        "ACCESS_TIME": "{days}d {hours}h",
        "ACCESS_TIME_ZERO": "0d 0h",
        # Errors
        "ERR_POSITIVE_INT": "❌ Enter a positive number.",
        # /msg command
        "MSG_FORMAT": "⚠️ Format: /msg @username message text",
        "MSG_NOT_FOUND": "❌ User with this @username not found.",
        "MSG_SENT": "✅ Message sent to @{username}",
        "MSG_FAILED": "❌ Error sending message: {error}",
        # Language set
        "LANG_SET": "✅ Language set: English",

        # ── Admin Panel ──
        "ADMIN_PANEL_TITLE": "🛠 Admin Panel",
        "ADMIN_USERS_LIST": "👥 All users:",
        "ADMIN_REFS_LIST": "🤝 Referral links:",
        "ADMIN_NO_REFS": "No referrals yet.",
        "ADMIN_REFS_INVITED": "{count} invited",
        "ADMIN_STATUS_LIST": "💼 Access statuses:",
        "ADMIN_STATUS_UNTIL": "Until: {date}",
        "ADMIN_STATS_TITLE": "📊 General statistics:",
        "ADMIN_STATS_TOTAL": "👥 Users: {total}",
        "ADMIN_STATS_TRIALS": "🆓 Used trial: {trials}",
        "ADMIN_STATS_ACTIVE": "✅ Active subscriptions: {active}",
        "ADMIN_TRIAL_DURATION_INFO": (
            "⏱ Current trial duration: {hours}h ({days}d {rem}h)\n\n"
            "Enter new value:\n"
            "/set_trial_duration <hours> or /set_trial_duration <days>d\n\n"
            "Examples:\n"
            "● /set_trial_duration 72 — 72 hours\n"
            "● /set_trial_duration 5d — 5 days"
        ),
        "ADMIN_RESET_TRIAL_PROMPT": "🔄 Reset user trial:\n\nEnter /reset_trial @username or ID",
        "ADMIN_RESET_USAGE": "⚙️ Format: /reset_trial @username or ID",
        "ADMIN_RESET_NOT_FOUND": "❌ User not found.",
        "ADMIN_RESET_DONE": "✅ Trial reset for @{username}.\n↳ User can activate trial again.",
        "ADMIN_TRIAL_USAGE": "⚙️ Format: /set_trial_duration 72 or /set_trial_duration 5d",
        "ADMIN_TRIAL_INVALID": "❌ Invalid format. Example: /set_trial_duration 72 or /set_trial_duration 5d",
        "ADMIN_TRIAL_CHANGED": "✅ Trial duration changed: {hours}h ({days}d {rem}h)",
        "ADMIN_MSG_PROMPT": "✉️ Enter @username or ID to message:",
        "ADMIN_MSG_TEXT_PROMPT": "✉️ Now enter the message text:",
        "ADMIN_MSG_SENT": "✅ Message sent to {target}.",
        "ADMIN_MSG_NOT_FOUND": "❌ User not found.",
        "ADMIN_MSG_FAILED": "⚠️ Could not send: {error}",
        "ADMIN_KICK_PROMPT": "🚫 Enter @username or ID to kick:",
        "ADMIN_KICK_NOT_FOUND": "❌ User not found.",
        "ADMIN_KICK_SUCCESS": "✅ User @{username} kicked from channel.",
        "ADMIN_KICK_FAILED": "⚠️ Could not kick: {error}",
        "ADMIN_PRICE_INFO": "⚙️ Current price: {currency}{price} {label}\n\nSelect payment type:",
        "ADMIN_PRICE_TYPE_PROMPT": "⚙️ Type: {label}\n\nEnter new price (number):",
        "ADMIN_PRICE_CHANGED": "✅ Access price updated: {currency}{price} {label}",
        "ADMIN_PRICE_INVALID": "❌ Invalid format. Enter a whole number greater than 0.",
        "ADMIN_PRICE_LABEL_MONTHLY": "/mo.",
        "ADMIN_PRICE_LABEL_FOREVER": "— forever",
        "ADMIN_BROADCAST_PROMPT": "📢 Send the message or photo to broadcast:",
        "ADMIN_PROMOS_TITLE": "🎟 Promo codes",
        "ADMIN_PROMOS_EMPTY": "🎟 Promo codes\n\nList is empty.",
        "ADMIN_PROMO_TYPE_PROMPT": "🎟 Select promo type:",
        "ADMIN_PROMO_DAYS_PROMPT": "🎟 Type: {label}\n\nEnter number of days:",
        "ADMIN_PROMO_DAYS_INVALID": "❌ Enter a whole number greater than 0.",
        "ADMIN_PROMO_CREATED": (
            "✅ Promo code created!\n\n"
            "🎟 Code: `{code}`\n"
            "📋 Type: {type}\n"
            "⏱ Duration: {days}\n\n"
            "Send this code to the user."
        ),
        "ADMIN_PROMO_ACTIVE": "⏳ Active",
        "ADMIN_PROMO_DELETED": "🗑 Promo code {code} deleted.",
        "ADMIN_PROMO_DEL_NOT_FOUND": "❌ Promo code not found.",
        "ADMIN_BACK": "⬅️ Back",
        # Admin panel buttons
        "ADMIN_BTN_DM": "✉️ Write DM",
        "ADMIN_BTN_KICK": "🚫 Kick",
        "ADMIN_BTN_BROADCAST": "📢 Broadcast",
        "ADMIN_BTN_RESET_TRIAL": "🔄 Reset trial",
        "ADMIN_BTN_TRIAL_DURATION": "⏱ Trial duration",
        "ADMIN_BTN_PRICE": "⚙️ Access price",
        "ADMIN_BTN_PROMOS": "🎟 Promo codes",
        "ADMIN_BTN_USERS": "👥 Users",
        "ADMIN_BTN_STATUS": "💼 Access statuses",
        "ADMIN_BTN_STATS": "📊 Statistics",
        "ADMIN_BTN_LIVE_MONITOR": "🧠 LIVE MONITOR",
        "ADMIN_BTN_REFS": "🤝 Referrals",
        "ADMIN_PRICE_BTN_MONTHLY": "📅 /mo.",
        "ADMIN_PRICE_BTN_FOREVER": "💎 Forever",
        "ADMIN_PROMO_BTN_FULL": "💠 Full (full access)",
        "ADMIN_PROMO_BTN_TRIAL": "🧪 Trial",
        "ADMIN_PROMO_BTN_FOREVER": "♾️ Forever",
        "ADMIN_PROMO_BTN_CREATE": "➕ Create new",
        "ADMIN_PROMO_BTN_LIST": "🎟 To promo list",
        # Live monitor
        "ADMIN_LIVE_TITLE": "🧠 LIVE MONITOR",
        "ADMIN_LIVE_TOTAL": "👥 Total users: {total}",
        "ADMIN_LIVE_ACTIVE": "🟢 Active: {active}",
        "ADMIN_LIVE_TRIAL": "🧪 Trial: {trial}",
        "ADMIN_LIVE_LOCKED": "🔒 No access: {locked}",
        "ADMIN_LIVE_30D_TITLE": "📊 Last 30 days:",
        "ADMIN_LIVE_30D_NEW": "• New: {count}",
        "ADMIN_LIVE_30D_TRIAL": "• Activated trial: {count} ({conv})",
        "ADMIN_LIVE_30D_PAID": "• Bought access: {count} ({conv})",
        "ADMIN_LIVE_30D_REVENUE": "• 💰 Revenue: {currency}{amount}",
        # Admin management
        "ADMIN_BTN_ADMINS": "👥 Admins",
        "ADMIN_ADMINS_TITLE": "👥 Administrators",
        "ADMIN_ADMINS_EMPTY": "👥 Administrators\n\nNo additional admins.",
        "ADMIN_ADMINS_ADDED": "Added: {date}",
        "ADMIN_ADD_BTN": "➕ Add admin",
        "PROMO_TYPE_FULL": "Full",
        "PROMO_TYPE_TRIAL": "Trial",
        "ADMIN_REFRESH": "🔄 Refresh",
        "DATA_ACTUAL": "✅ Data is up to date",
        "NAV_PREV": "◀️ Back",
        "NAV_NEXT": "▶️ Next",
        "CUSTOM_DAYS_BTN": "✏️ Custom days",
        "BTN_CONFIRM": "✅ Confirm",
        "BTN_CANCEL": "❌ Cancel",
        "BTN_YES": "✅ Yes",
        "BTN_NO": "❌ No",
        "CURRENCY_EUR": "€ EUR",
        "CURRENCY_USD": "$ USD",
        "CURRENCY_GBP": "£ GBP",
        "CURRENCY_CUSTOM": "✏️ Custom",
        "ADMIN_ADD_PROMPT": "➕ Enter @username or ID of the new admin:",
        "ADMIN_ADD_NOT_FOUND": "❌ User not found in the database.",
        "ADMIN_ADD_ALREADY": "⚠️ This user is already an admin.",
        "ADMIN_ADD_SUCCESS": "👑 @{username} is now an administrator.",
        "ADMIN_REMOVE_CONFIRM": "⚠️ Remove admin rights from @{username}?",
        "ADMIN_REMOVE_SUCCESS": "✅ Admin rights removed from @{username}.",
        "ADMIN_REMOVE_NOT_FOUND": "❌ Admin not found.",
        "ADMIN_NEW_ADMIN_NOTIFY": "👑 Congratulations. You have been granted administrator rights.\nThe control panel is now at your disposal — /admin",
        "ADMIN_ONLY_OWNER": "⚠️ Only the main administrator can manage admins.",
        "CONFIRM_KICK": "⚠️ Kick user @{username}?",
        "ACTION_CANCELLED": "❌ Action cancelled.",
        "CONFIRM_PROMO_DEL": "⚠️ Delete promo code {code}?",
        # Currency selection
        "ADMIN_CURRENCY_PROMPT": "Choose currency or enter custom:",
        "ADMIN_CURRENCY_CUSTOM_PROMPT": "Enter currency symbol (e.g.: ₴, USDT, CHF):",
        "ADMIN_CURRENCY_SAVED": "✅ Currency saved: {currency}",
        # User detail view
        "USER_DETAIL_TITLE": "👤 User Info",
        "USER_JOINED": "📅 Joined: {date}",
        "USER_STATUS": "🔰 Status: {mode}",
        "USER_ACCESS_UNTIL": "⏳ Expires: {date}",
        "BTN_DM": "✉️ DM",
        "BTN_RESET_TRIAL": "🔄 Reset trial",
        "BTN_KICK": "🚫 Kick",
        "CONFIRM_RESET_TRIAL": "🔄 Reset trial for @{username}?",
        "RESET_TRIAL_DONE": "✅ Trial reset for @{username}",
        "DM_PROMPT": "✉️ Enter message text:",
        "DM_SENT": "✅ Message sent",
        "DM_FAILED": "❌ Could not send: {error}",
        "ADMIN_REVOKED": "🔒 Your administrator rights have been revoked.",
        # Price suffixes & hardcoded button labels (i18n cleanup)
        "PRICE_SUFFIX_MONTHLY": "/month",
        "PRICE_SUFFIX_FOREVER": "— forever",
        "BTN_CUSTOM_DAYS": "✏️ Custom days",
        "BTN_ADMIN_PANEL": "🛠 Admin Panel",
        # Crypto address management
        "ADMIN_BTN_ADDRESS": "💳 Crypto address",
        "ADMIN_ADDRESS_PROMPT": "Enter the new USDT TRC-20 wallet address:",
        "ADMIN_ADDRESS_SET": "✅ Address updated: `{address}`",
        "ADMIN_ADDRESS_INVALID": "❌ Invalid address. Must start with T and be 34 characters.",
        "ADMIN_ADDRESS_PROMPT_FLOW": "💳 Enter USDT TRC-20 wallet address (or send /skip to keep current):",
        "ADMIN_ADDRESS_SKIPPED": "⏭ Crypto address unchanged.",
    },
    "uk": {
        # Welcome
        "WELCOME_TEXT": (
            "Привіт, {name}! 👋\n\n"
            "Тут ти можеш ознайомитись з нашими послугами\n"
            "та оформити доступ.\n\n"
            "Обери дію в меню нижче."
        ),
        "POPUP_TEXT": (
            "🎯 Що ти отримуєш всередині:\n\n"
            "● [пункт 1]\n"
            "● [пункт 2]\n"
            "● [пункт 3]\n\n"
            "💬 Спільнота активних учасників\n"
            "🔐 Закритий доступ"
        ),
        # Payment
        "PAYMENT_TEXT": (
            "💳 Оплата доступу\n\n"
            "💰 Вартість: {price}\n\n"
            "↳ Перерахуй оплату на адресу нижче\n"
            "↳ Після оплати натисни [Оплачено]\n"
            "↳ Введи TXID транзакції\n"
            "↳ Очікуй підтвердження\n\n"
            "Адреса для оплати: 👇"
        ),
        "CRYPTO_INFO": (
            "● Монета: Tether (USDT)\n"
            "● Мережа: TRON - TRC20\n\n"
            "`TEwnPR7daATh84DLFiTXJGaCge4NbYDbV8`\n"
            "↳ Натисни на адресу, щоб скопіювати!\n\n"
        ),
        "CRYPTO_INFO_DYNAMIC": (
            "● Монета: Tether (USDT)\n"
            "● Мережа: TRON - TRC20\n\n"
            "`{address}`\n"
            "↳ Натисніть адресу щоб скопіювати!\n\n"
        ),
        "SHOW_QR": "Показати QR-код",
        "HIDE_QR": "Сховати QR-код",
        "PAID_BUTTON": "Оплачено",
        "TXID_PROMPT": "💳 Введи TXID для підтвердження оплати.",
        "TXID_SENT": (
            "💳 ↳ Дані передано на верифікацію.\n\n"
            "↳ Очікуй підтвердження від адміністратора."
        ),
        "ALREADY_PAID": (
            "✅ ↳ Твій доступ вже активний.\n\n"
            "↳ Все працює, ти в каналі."
        ),
        # Payment admin
        "PAYMENT_REQUEST": (
            "💳 Заявка на оплату\n\n"
            "👤 Користувач: {identity}\n"
            "🕰 Дата: {date}\n"
            "🔗 TXID: `{txid}`"
        ),
        "ADMIN_30_DAYS": "30 днів",
        "ADMIN_90_DAYS": "90 днів",
        "ADMIN_180_DAYS": "180 днів",
        "ADMIN_FOREVER": "♾ Назавжди",
        "ADMIN_REJECT": "❌ Відхилити",
        "ADMIN_ACCEPTED": "\n\n✅ Підтверджено: @{admin} • {date}\nПеріод: {period}",
        "ADMIN_REJECTED": "\n\n❌ Відхилено: @{admin} • {date}",
        "PERIOD_FOREVER": "назавжди ♾",
        "PERIOD_DAYS": "{days} днів",
        "PAYMENT_APPROVED_LINK": "✅ Оплату підтверджено!\n\n🔗 Посилання для входу:\n{link}",
        "PAYMENT_APPROVED_NO_LINK": "✅ Оплату підтверджено! Можливо ти вже є в каналі.",
        "PAYMENT_REJECTED": (
            "❌ Оплату не підтверджено.\n\n"
            "↳ Перевір TXID або зверніться до адміністратора."
        ),
        # Trial
        "TRIAL_ACTIVATED": (
            "✅ Пробний доступ активовано!\n\n"
            "↳ У тебе є 120 годин безкоштовного доступу."
        ),
        "TRIAL_ALREADY_USED": (
            "⚠️ Пробний доступ вже було використано.\n\n"
            "Для продовження — оформи повний доступ."
        ),
        "TRIAL_LINK": "Посилання для входу:\n{link}",
        "TRIAL_FAILED": (
            "⚠️ Не вдалось створити посилання.\n\n"
            "↳ Можливо ти вже є в каналі."
        ),
        "TRIAL_LINK_ALREADY_MEMBER": "✅ Тріал активовано! Ти вже є учасником каналу або посилання надійде невдовзі.",
        "PROMO_ALREADY_ACTIVE": "✅ У тебе вже є активний доступ. Цей промокод не потрібен.",
        # Referral
        "REF_INFO": (
            "🤝 Запроси друга\n\n"
            "🔗 Твоє реферальне посилання:\n{link}\n\n"
            "🧬 1 оплата друга = 1 бал\n"
            "💠 3 бали = 30 днів доступу безкоштовно\n\n"
            "Поділись посиланням і отримуй бонуси."
        ),
        "REF_ENTERED": "🛰 Хтось перейшов за твоїм посиланням.\n",
        # Stats
        "STATS_TEXT": (
            "📋 Мій доступ\n"
            "─────────────\n"
            "Статус: {mode}\n"
            "Діє ще: {access_time}\n"
            "─────────────\n"
            "Запрошено: {invited}\n"
            "Балів: {units} / 3\n"
        ),
        "STATS_TEXT_NO_REF": (
            "📋 Мій доступ\n"
            "─────────────\n"
            "Статус: {mode}\n"
            "Діє ще: {access_time}\n"
            "─────────────\n"
        ),
        # Access approval
        "APPROVED_USER": "✅ Доступ підтверджено!\n\n🔗 Посилання для входу:\n{link}",
        "APPROVED_FAILED": (
            "⚠️ Доступ підтверджено, але посилання не створилось.\n"
            "↳ Можливо ти вже є в каналі."
        ),
        "APPROVED_CONFIRM": "✅ Користувача @{username} додано до каналу.",
        "APPROVE_NOT_FOUND": "❌ Користувача не знайдено. Перевір @username або ID.",
        "APPROVE_USAGE": "⚙️ Формат: /approve @username",
        # Bonus
        "BONUS_RECEIVED": "🎉 Тобі нараховано +1 бал!\n",
        "BONUS_REWARDED": "🎉 Зібрано 3 бали!\n\nДоступ продовжено на 30 днів.",
        # Expiry reminders
        "TRIAL_ENDING": (
            "⏳ До кінця пробного доступу залишилась менше години.\n\n"
            "↳ Оформи доступ щоб залишитись у каналі."
        ),
        "PAID_ENDING": (
            "⏳ До кінця доступу залишилось менше 24 годин.\n\n"
            "↳ Продовж доступ щоб не випасти з каналу."
        ),
        "TRIAL_EXPIRED": (
            "🔒 Твій доступ завершився.\n\n"
            "↳ Оформи доступ щоб повернутись у канал."
        ),
        # Kick
        "KICKED_BY_ADMIN": "⛔️ Твій доступ було анульовано адміністратором.",
        "KICK_SUCCESS": "🗑 Користувача @{username} видалено з каналу.",
        "KICK_NOT_FOUND": "🔍 Користувача не знайдено в базі.",
        "KICK_FAILED": "⚠️ Не вдалось виконати дію: {error}",
        # Broadcast
        "BROADCAST_EMPTY": "📭 Вкажи текст після /broadcast",
        "BROADCAST_RESULT": "📡 Розсилку завершено. Надіслано: {ok}, Помилок: {fail}",
        # Copy trading
        "COPY_ACCESS_ENABLED": (
            "🔓 Копітрейдинг\n\n"
            "Твій акаунт Bybit автоматично повторює угоди в реальному часі.\n\n"
            "Як підключитись:\n"
            "Натисни кнопку нижче і надішли свій Bybit UID\n"
            "Після перевірки тебе додадуть до системи.\n\n"
            "Очікується UID..."
        ),
        "COPY_USAGE": "⚙️ Введи свій Bybit UID для підключення копітрейдингу.",
        "COPY_NOT_ACTIVATED": (
            "⚠️ Копітрейдинг доступний лише з активним доступом.\n\n"
            "↳ Оформи доступ через головне меню."
        ),
        "COPY_UID_RECEIVED": (
            "✅ UID отримано.\n\n"
            "↳ Очікуй підтвердження від адміністратора."
        ),
        # Menu buttons
        "BUTTON_ACTIVATE": "🔐 Активувати доступ",
        "BUTTON_TRIAL": "🧪 Пробний доступ",
        "BUTTON_INVITE": "🤝 Запросити друга",
        "BUTTON_MY_ACCESS": "📋 Мій доступ",
        "BUTTON_DETAILS": "🔍 Детальніше",
        # Language
        "LANG_SELECT": "🌍 Обери мову:",
        "LANG_CHOOSE_FIRST": "🌍 Спочатку обери мову.",
        "MENU_HINT": "Використай меню нижче для навігації. 👇",
        # Access modes
        "MODE_ADMIN": "👑 ADMIN",
        "MODE_FULL": "💠 FULL ACCESS",
        "MODE_TRIAL": "🧪 TRIAL ACCESS",
        "MODE_GUEST": "🕶️ GUEST",
        # Boot animation
        "BOOT_1": "Підключення...",
        "BOOT_2": "Перевірка доступу...",
        "BOOT_3": "Завантаження...",
        "BOOT_4": "Майже готово...",
        "BOOT_5": "Вітаємо! ✅",
        "BOOT_LOADING": "Завантаження...",
        # Promo
        "PROMO_ACTIVATED_FULL_FOREVER": (
            "✅ Промокод активовано!\n\n"
            "Твій доступ активний на: ♾️"
        ),
        "PROMO_ACTIVATED_FULL_DAYS": (
            "✅ Промокод активовано!\n\n"
            "Твій доступ активний на: {days} днів."
        ),
        "PROMO_ACTIVATED_TRIAL": (
            "✅ Промокод активовано!\n\n"
            "Пробний доступ відкрито на {days} днів."
        ),
        "PROMO_INVALID": "❌ Промокод недійсний або вже активований.",
        # Custom days
        "CUSTOM_DAYS_PROMPT": "✏️ Введи кількість днів для користувача {label}:",
        "CUSTOM_DAYS_CONFIRM": "✅ Прийнято — {days} днів для {label}.",
        # Trial cancel
        "TRIAL_CANCEL": "Активацію скасовано.",
        # Trial confirmation
        "TRIAL_CONFIRM_TITLE": "🧪 Пробний доступ",
        "TRIAL_CONFIRM_DURATION": "Ти отримаєш доступ до закритого каналу на {duration}.",
        "TRIAL_CONFIRM_START": "📅 Початок: зараз",
        "TRIAL_CONFIRM_END": "📅 Закінчення: {end_time}",
        "TRIAL_CONFIRM_NOTE": (
            "Після закінчення доступ буде автоматично закрито.\n"
            "Щоб залишитись — оформи повний доступ через меню."
        ),
        "BTN_ACTIVATE_TRIAL": "✅ Активувати",
        # Duration
        "DURATION_DAYS_HOURS": "{days} дн. {rem} год.",
        "DURATION_DAYS": "{days} дн.",
        "DURATION_HOURS": "{hours} год.",
        # Access time
        "ACCESS_TIME": "{days}д {hours}г",
        "ACCESS_TIME_ZERO": "0д 0г",
        # Errors
        "ERR_POSITIVE_INT": "❌ Введи ціле число більше 0.",
        # /msg command
        "MSG_FORMAT": "⚠️ Формат: /msg @username текст повідомлення",
        "MSG_NOT_FOUND": "❌ Користувача з таким @username не знайдено.",
        "MSG_SENT": "✅ Повідомлення надіслано користувачу @{username}",
        "MSG_FAILED": "❌ Помилка надсилання повідомлення: {error}",
        # Language set
        "LANG_SET": "✅ Мову обрано: Українська",

        # ── Адмін-панель ──
        "ADMIN_PANEL_TITLE": "🛠 Адмін-панель",
        "ADMIN_USERS_LIST": "👥 Усі користувачі:",
        "ADMIN_REFS_LIST": "🤝 Реферальні зв\'язки:",
        "ADMIN_NO_REFS": "Немає рефералів.",
        "ADMIN_REFS_INVITED": "{count} запрошено",
        "ADMIN_STATUS_LIST": "💼 Статуси доступу:",
        "ADMIN_STATUS_UNTIL": "До: {date}",
        "ADMIN_STATS_TITLE": "📊 Загальна статистика:",
        "ADMIN_STATS_TOTAL": "👥 Користувачів: {total}",
        "ADMIN_STATS_TRIALS": "🆓 Використали тріал: {trials}",
        "ADMIN_STATS_ACTIVE": "✅ Активні підписки: {active}",
        "ADMIN_TRIAL_DURATION_INFO": (
            "⏱ Поточна тривалість тріалу: {hours}г ({days}д {rem}г)\n\n"
            "Введи нове значення командою:\n"
            "/set_trial_duration <години> або /set_trial_duration <дні>д\n\n"
            "Приклади:\n"
            "● /set_trial_duration 72 — 72 години\n"
            "● /set_trial_duration 5д — 5 днів"
        ),
        "ADMIN_RESET_TRIAL_PROMPT": "🔄 Скинути тріал користувачу:\n\nВведи /reset_trial @username або ID",
        "ADMIN_RESET_USAGE": "⚙️ Формат: /reset_trial @username або ID",
        "ADMIN_RESET_NOT_FOUND": "❌ Користувача не знайдено.",
        "ADMIN_RESET_DONE": "✅ Тріал скинуто для @{username}.\n↳ Користувач може знову активувати пробний доступ.",
        "ADMIN_TRIAL_USAGE": "⚙️ Формат: /set_trial_duration 72 або /set_trial_duration 5д",
        "ADMIN_TRIAL_INVALID": "❌ Невірний формат. Приклад: /set_trial_duration 72 або /set_trial_duration 5д",
        "ADMIN_TRIAL_CHANGED": "✅ Тривалість тріалу змінено: {hours}г ({days}д {rem}г)",
        "ADMIN_MSG_PROMPT": "✉️ Введи @username або ID користувача якому хочеш написати:",
        "ADMIN_MSG_TEXT_PROMPT": "✉️ Тепер введи текст повідомлення:",
        "ADMIN_MSG_SENT": "✅ Повідомлення надіслано користувачу {target}.",
        "ADMIN_MSG_NOT_FOUND": "❌ Користувача не знайдено.",
        "ADMIN_MSG_FAILED": "⚠️ Не вдалось надіслати: {error}",
        "ADMIN_KICK_PROMPT": "🚫 Введи @username або ID користувача якого хочеш кікнути:",
        "ADMIN_KICK_NOT_FOUND": "❌ Користувача не знайдено.",
        "ADMIN_KICK_SUCCESS": "✅ Користувача @{username} кікнуто з каналу.",
        "ADMIN_KICK_FAILED": "⚠️ Не вдалось кікнути: {error}",
        "ADMIN_PRICE_INFO": "⚙️ Поточна ціна: {currency}{price} {label}\n\nОбери тип оплати:",
        "ADMIN_PRICE_TYPE_PROMPT": "⚙️ Тип: {label}\n\nВведи нову ціну (число):",
        "ADMIN_PRICE_CHANGED": "✅ Ціну доступу змінено: {currency}{price} {label}",
        "ADMIN_PRICE_INVALID": "❌ Невірний формат. Введи ціле число більше 0.",
        "ADMIN_PRICE_LABEL_MONTHLY": "/міс.",
        "ADMIN_PRICE_LABEL_FOREVER": "— назавжди",
        "ADMIN_BROADCAST_PROMPT": "📢 Надішли текст або фото з підписом для розсилки:",
        "ADMIN_PROMOS_TITLE": "🎟 Промокоди",
        "ADMIN_PROMOS_EMPTY": "🎟 Промокоди\n\nСписок порожній.",
        "ADMIN_PROMO_TYPE_PROMPT": "🎟 Оберіть тип промокоду:",
        "ADMIN_PROMO_DAYS_PROMPT": "🎟 Тип: {label}\n\nВведи кількість днів числом:",
        "ADMIN_PROMO_DAYS_INVALID": "❌ Введи ціле число більше 0.",
        "ADMIN_PROMO_CREATED": (
            "✅ Промокод створено!\n\n"
            "🎟 Код: `{code}`\n"
            "📋 Тип: {type}\n"
            "⏱ Тривалість: {days}\n\n"
            "Надішліть цей код користувачу."
        ),
        "ADMIN_PROMO_ACTIVE": "⏳ Активний",
        "ADMIN_PROMO_DELETED": "🗑 Промокод {code} видалено.",
        "ADMIN_PROMO_DEL_NOT_FOUND": "❌ Промокод не знайдено.",
        "ADMIN_BACK": "⬅️ Назад",
        # Кнопки адмін-панелі
        "ADMIN_BTN_DM": "✉️ Написати в DM",
        "ADMIN_BTN_KICK": "🚫 Кікнути",
        "ADMIN_BTN_BROADCAST": "📢 Розсилка",
        "ADMIN_BTN_RESET_TRIAL": "🔄 Скинути тріал",
        "ADMIN_BTN_TRIAL_DURATION": "⏱ Тривалість тріалу",
        "ADMIN_BTN_PRICE": "⚙️ Ціна доступу",
        "ADMIN_BTN_PROMOS": "🎟 Промокоди",
        "ADMIN_BTN_USERS": "👥 Користувачі",
        "ADMIN_BTN_STATUS": "💼 Статуси доступу",
        "ADMIN_BTN_STATS": "📊 Статистика",
        "ADMIN_BTN_LIVE_MONITOR": "🧠 LIVE MONITOR",
        "ADMIN_BTN_REFS": "🤝 Реферали",
        "ADMIN_PRICE_BTN_MONTHLY": "📅 /міс.",
        "ADMIN_PRICE_BTN_FOREVER": "💎 Назавжди",
        "ADMIN_PROMO_BTN_FULL": "💠 Full (повний доступ)",
        "ADMIN_PROMO_BTN_TRIAL": "🧪 Trial (пробний)",
        "ADMIN_PROMO_BTN_FOREVER": "♾️ Назавжди",
        "ADMIN_PROMO_BTN_CREATE": "➕ Створити новий",
        "ADMIN_PROMO_BTN_LIST": "🎟 До списку промокодів",
        # Live monitor
        "ADMIN_LIVE_TITLE": "🧠 LIVE MONITOR",
        "ADMIN_LIVE_TOTAL": "👥 Всього юзерів: {total}",
        "ADMIN_LIVE_ACTIVE": "🟢 Активних: {active}",
        "ADMIN_LIVE_TRIAL": "🧪 Тріал: {trial}",
        "ADMIN_LIVE_LOCKED": "🔒 Без доступу: {locked}",
        "ADMIN_LIVE_30D_TITLE": "📊 За останні 30 днів:",
        "ADMIN_LIVE_30D_NEW": "• Нових: {count}",
        "ADMIN_LIVE_30D_TRIAL": "• Активували тріал: {count} ({conv})",
        "ADMIN_LIVE_30D_PAID": "• Купили доступ: {count} ({conv})",
        "ADMIN_LIVE_30D_REVENUE": "• 💰 Прибуток: {currency}{amount}",
        # Управління адмінами
        "ADMIN_BTN_ADMINS": "👥 Адміни",
        "ADMIN_ADMINS_TITLE": "👥 Адміністратори",
        "ADMIN_ADMINS_EMPTY": "👥 Адміністратори\n\nДодаткових адмінів немає.",
        "ADMIN_ADMINS_ADDED": "Доданий: {date}",
        "ADMIN_ADD_BTN": "➕ Додати адміна",
        "PROMO_TYPE_FULL": "Повний",
        "PROMO_TYPE_TRIAL": "Пробний",
        "ADMIN_REFRESH": "🔄 Оновити",
        "DATA_ACTUAL": "✅ Дані актуальні",
        "NAV_PREV": "◀️ Назад",
        "NAV_NEXT": "▶️ Далі",
        "CUSTOM_DAYS_BTN": "✏️ Вказати дні",
        "BTN_CONFIRM": "✅ Підтвердити",
        "BTN_CANCEL": "❌ Скасувати",
        "BTN_YES": "✅ Так",
        "BTN_NO": "❌ Ні",
        "CURRENCY_EUR": "€ EUR",
        "CURRENCY_USD": "$ USD",
        "CURRENCY_GBP": "£ GBP",
        "CURRENCY_CUSTOM": "✏️ Своя",
        "ADMIN_ADD_PROMPT": "➕ Введи @username або ID нового адміна:",
        "ADMIN_ADD_NOT_FOUND": "❌ Користувача не знайдено в базі.",
        "ADMIN_ADD_ALREADY": "⚠️ Цей користувач вже є адміном.",
        "ADMIN_ADD_SUCCESS": "👑 @{username} тепер серед адміністраторів.",
        "ADMIN_REMOVE_CONFIRM": "⚠️ Зняти права адміна у @{username}?",
        "ADMIN_REMOVE_SUCCESS": "✅ Права адміна знято у @{username}.",
        "ADMIN_REMOVE_NOT_FOUND": "❌ Адміна не знайдено.",
        "ADMIN_NEW_ADMIN_NOTIFY": "👑 Вітаємо. Ви отримали права адміністратора.\nПанель керування тепер у вашому розпорядженні — /admin",
        "ADMIN_ONLY_OWNER": "⚠️ Тільки головний адміністратор може керувати адмінами.",
        "CONFIRM_KICK": "⚠️ Кікнути користувача @{username}?",
        "ACTION_CANCELLED": "❌ Дію скасовано.",
        "CONFIRM_PROMO_DEL": "⚠️ Видалити промокод {code}?",
        # Вибір валюти
        "ADMIN_CURRENCY_PROMPT": "Оберіть валюту або введіть свою:",
        "ADMIN_CURRENCY_CUSTOM_PROMPT": "Введіть символ валюти (наприклад: ₴, USDT, CHF):",
        "ADMIN_CURRENCY_SAVED": "✅ Валюту збережено: {currency}",
        # Деталі користувача
        "USER_DETAIL_TITLE": "👤 Інформація про користувача",
        "USER_JOINED": "📅 Приєднався: {date}",
        "USER_STATUS": "🔰 Статус: {mode}",
        "USER_ACCESS_UNTIL": "⏳ Закінчується: {date}",
        "BTN_DM": "✉️ Написати",
        "BTN_RESET_TRIAL": "🔄 Скинути тріал",
        "BTN_KICK": "🚫 Кікнути",
        "CONFIRM_RESET_TRIAL": "🔄 Скинути тріал для @{username}?",
        "RESET_TRIAL_DONE": "✅ Тріал скинуто для @{username}",
        "DM_PROMPT": "✉️ Введіть текст повідомлення:",
        "DM_SENT": "✅ Повідомлення надіслано",
        "DM_FAILED": "❌ Не вдалось надіслати: {error}",
        "ADMIN_REVOKED": "🔒 Ваші права адміністратора були скасовані.",
        # Price suffixes & hardcoded button labels (i18n cleanup)
        "PRICE_SUFFIX_MONTHLY": "/міс.",
        "PRICE_SUFFIX_FOREVER": "— назавжди",
        "BTN_CUSTOM_DAYS": "✏️ Вказати дні",
        "BTN_ADMIN_PANEL": "🛠 Адмін панель",
        # Управління крипто адресою
        "ADMIN_BTN_ADDRESS": "💳 Крипто адреса",
        "ADMIN_ADDRESS_PROMPT": "Введіть нову адресу USDT TRC-20 гаманця:",
        "ADMIN_ADDRESS_SET": "✅ Адресу оновлено: `{address}`",
        "ADMIN_ADDRESS_INVALID": "❌ Невірна адреса. Має починатись з T та містити 34 символи.",
        "ADMIN_ADDRESS_PROMPT_FLOW": "💳 Введіть адресу USDT TRC-20 гаманця (або надішліть /skip щоб залишити поточну):",
        "ADMIN_ADDRESS_SKIPPED": "⏭ Крипто адресу не змінено.",
    },
    "ru": {
        # Welcome
        "WELCOME_TEXT": (
            "Привет, {name}! 👋\n\n"
            "Здесь ты можешь ознакомиться с нашими услугами\n"
            "и оформить доступ.\n\n"
            "Выбери действие в меню ниже."
        ),
        "POPUP_TEXT": (
            "🎯 Что ты получаешь внутри:\n\n"
            "● [пункт 1]\n"
            "● [пункт 2]\n"
            "● [пункт 3]\n\n"
            "💬 Сообщество активных участников\n"
            "🔐 Закрытый доступ"
        ),
        # Payment
        "PAYMENT_TEXT": (
            "💳 Оплата доступа\n\n"
            "💰 Стоимость: {price}\n\n"
            "↳ Переведи оплату на адрес ниже\n"
            "↳ После оплаты нажми [Оплачено]\n"
            "↳ Введи TXID транзакции\n"
            "Ожидай подтверждение\n\n"
            "Адрес для оплаты: 👇"
        ),
        "CRYPTO_INFO": (
            "● Монета: Tether (USDT)\n"
            "● Сеть: TRON - TRC20\n\n"
            "`TEwnPR7daATh84DLFiTXJGaCge4NbYDbV8`\n"
            "↳ Нажми на адрес, чтобы скопировать!\n\n"
        ),
        "CRYPTO_INFO_DYNAMIC": (
            "● Монета: Tether (USDT)\n"
            "● Сеть: TRON - TRC20\n\n"
            "`{address}`\n"
            "↳ Нажмите адрес чтобы скопировать!\n\n"
        ),
        "SHOW_QR": "Показать QR-код",
        "HIDE_QR": "Скрыть QR-код",
        "PAID_BUTTON": "Оплачено",
        "TXID_PROMPT": "💳 Введи TXID для подтверждения оплаты.",
        "TXID_SENT": (
            "💳 ↳ Данные переданы на верификацию.\n\n"
            "↳ Ожидай подтверждения от администратора."
        ),
        "ALREADY_PAID": (
            "✅ ↳ Твой доступ уже активен.\n\n"
            "↳ Всё работает, ты в канале."
        ),
        # Payment admin
        "PAYMENT_REQUEST": (
            "💳 Заявка на оплату\n\n"
            "👤 Пользователь: {identity}\n"
            "🕰 Дата: {date}\n"
            "🔗 TXID: `{txid}`"
        ),
        "ADMIN_30_DAYS": "30 дней",
        "ADMIN_90_DAYS": "90 дней",
        "ADMIN_180_DAYS": "180 дней",
        "ADMIN_FOREVER": "♾ Навсегда",
        "ADMIN_REJECT": "❌ Отклонить",
        "ADMIN_ACCEPTED": "\n\n✅ Подтверждено: @{admin} • {date}\nПериод: {period}",
        "ADMIN_REJECTED": "\n\n❌ Отклонено: @{admin} • {date}",
        "PERIOD_FOREVER": "навсегда ♾",
        "PERIOD_DAYS": "{days} дней",
        "PAYMENT_APPROVED_LINK": "✅ Оплата подтверждена!\n\n🔗 Ссылка для входа:\n{link}",
        "PAYMENT_APPROVED_NO_LINK": "✅ Оплата подтверждена! Возможно ты уже в канале.",
        "PAYMENT_REJECTED": (
            "❌ Оплата не подтверждена.\n\n"
            "↳ Проверь TXID или обратись к администратору."
        ),
        # Trial
        "TRIAL_ACTIVATED": (
            "✅ Пробный доступ активирован!\n\n"
            "↳ У тебя есть 120 часов бесплатного доступа."
        ),
        "TRIAL_ALREADY_USED": (
            "⚠️ Пробный доступ уже был использован.\n\n"
            "Для продолжения — оформи полный доступ."
        ),
        "TRIAL_LINK": "Ссылка для входа:\n{link}",
        "TRIAL_FAILED": (
            "⚠️ Не удалось создать ссылку.\n\n"
            "↳ Возможно ты уже в канале."
        ),
        "TRIAL_LINK_ALREADY_MEMBER": "✅ Триал активирован! Ты уже участник канала или ссылка придёт чуть позже.",
        "PROMO_ALREADY_ACTIVE": "✅ У тебя уже есть активный доступ. Этот промокод не нужен.",
        # Referral
        "REF_INFO": (
            "🤝 Пригласи друга\n\n"
            "🔗 Твоя реферальная ссылка:\n{link}\n\n"
            "🧬 1 оплата друга = 1 балл\n"
            "💠 3 балла = 30 дней доступа бесплатно\n\n"
            "Поделись ссылкой и получай бонусы."
        ),
        "REF_ENTERED": "🛰 Кто-то перешёл по твоей ссылке.\n",
        # Stats
        "STATS_TEXT": (
            "📋 Мой доступ\n"
            "─────────────\n"
            "Статус: {mode}\n"
            "Осталось: {access_time}\n"
            "─────────────\n"
            "Приглашено: {invited}\n"
            "Баллов: {units} / 3\n"
        ),
        "STATS_TEXT_NO_REF": (
            "📋 Мой доступ\n"
            "─────────────\n"
            "Статус: {mode}\n"
            "Осталось: {access_time}\n"
            "─────────────\n"
        ),
        # Access approval
        "APPROVED_USER": "✅ Доступ подтверждён!\n\n🔗 Ссылка для входа:\n{link}",
        "APPROVED_FAILED": (
            "⚠️ Доступ подтверждён, но ссылка не создалась.\n"
            "↳ Возможно ты уже в канале."
        ),
        "APPROVED_CONFIRM": "✅ Пользователь @{username} добавлен в канал.",
        "APPROVE_NOT_FOUND": "❌ Пользователь не найден. Проверь @username или ID.",
        "APPROVE_USAGE": "⚙️ Формат: /approve @username",
        # Bonus
        "BONUS_RECEIVED": "🎉 Тебе начислен +1 балл!\n",
        "BONUS_REWARDED": "🎉 Собрано 3 балла!\n\nДоступ продлён на 30 дней.",
        # Expiry reminders
        "TRIAL_ENDING": (
            "⏳ До конца пробного доступа осталось меньше часа.\n\n"
            "↳ Оформи доступ чтобы остаться в канале."
        ),
        "PAID_ENDING": (
            "⏳ До конца доступа осталось меньше 24 часов.\n\n"
            "↳ Продли доступ чтобы не выпасть из канала."
        ),
        "TRIAL_EXPIRED": (
            "🔒 Твой доступ завершился.\n\n"
            "↳ Оформи доступ чтобы вернуться в канал."
        ),
        # Kick
        "KICKED_BY_ADMIN": "⛔️ Твой доступ был аннулирован администратором.",
        "KICK_SUCCESS": "🗑 Пользователь @{username} удалён из канала.",
        "KICK_NOT_FOUND": "🔍 Пользователь не найден в базе.",
        "KICK_FAILED": "⚠️ Не удалось выполнить действие: {error}",
        # Broadcast
        "BROADCAST_EMPTY": "📭 Укажи текст после /broadcast",
        "BROADCAST_RESULT": "📡 Рассылка завершена. Отправлено: {ok}, Ошибок: {fail}",
        # Copy trading
        "COPY_ACCESS_ENABLED": (
            "🔓 Копитрейдинг\n\n"
            "Твой аккаунт Bybit автоматически повторяет сделки в реальном времени.\n\n"
            "Как подключиться:\n"
            "Нажми кнопку ниже и отправь свой Bybit UID\n"
            "После проверки тебя добавят в систему.\n\n"
            "Ожидается UID..."
        ),
        "COPY_USAGE": "⚙️ Введи свой Bybit UID для подключения копитрейдинга.",
        "COPY_NOT_ACTIVATED": (
            "⚠️ Копитрейдинг доступен только с активным доступом.\n\n"
            "↳ Оформи доступ через главное меню."
        ),
        "COPY_UID_RECEIVED": (
            "✅ UID получен.\n\n"
            "↳ Ожидай подтверждения от администратора."
        ),
        # Menu buttons
        "BUTTON_ACTIVATE": "🔐 Активировать доступ",
        "BUTTON_TRIAL": "🧪 Пробный доступ",
        "BUTTON_INVITE": "🤝 Пригласить друга",
        "BUTTON_MY_ACCESS": "📋 Мой доступ",
        "BUTTON_DETAILS": "🔍 Подробнее",
        # Language
        "LANG_SELECT": "🌍 Выбери язык:",
        "LANG_CHOOSE_FIRST": "🌍 Сначала выбери язык.",
        "MENU_HINT": "Используй меню ниже для навигации. 👇",
        # Access modes
        "MODE_ADMIN": "👑 ADMIN",
        "MODE_FULL": "💠 FULL ACCESS",
        "MODE_TRIAL": "🧪 TRIAL ACCESS",
        "MODE_GUEST": "🕶️ GUEST",
        # Boot animation
        "BOOT_1": "Подключение...",
        "BOOT_2": "Проверка доступа...",
        "BOOT_3": "Загрузка...",
        "BOOT_4": "Почти готово...",
        "BOOT_5": "Добро пожаловать! ✅",
        "BOOT_LOADING": "Загрузка...",
        # Promo
        "PROMO_ACTIVATED_FULL_FOREVER": (
            "✅ Промокод активирован!\n\n"
            "Твой доступ активен на: ♾️"
        ),
        "PROMO_ACTIVATED_FULL_DAYS": (
            "✅ Промокод активирован!\n\n"
            "Твой доступ активен на: {days} дней."
        ),
        "PROMO_ACTIVATED_TRIAL": (
            "✅ Промокод активирован!\n\n"
            "Пробный доступ открыт на {days} дней."
        ),
        "PROMO_INVALID": "❌ Промокод недействителен или уже активирован.",
        # Custom days
        "CUSTOM_DAYS_PROMPT": "✏️ Введи количество дней для пользователя {label}:",
        "CUSTOM_DAYS_CONFIRM": "✅ Принято — {days} дней для {label}.",
        # Trial cancel
        "TRIAL_CANCEL": "Активация отменена.",
        # Trial confirmation
        "TRIAL_CONFIRM_TITLE": "🧪 Пробный доступ",
        "TRIAL_CONFIRM_DURATION": "Ты получишь доступ к закрытому каналу на {duration}.",
        "TRIAL_CONFIRM_START": "📅 Начало: сейчас",
        "TRIAL_CONFIRM_END": "📅 Окончание: {end_time}",
        "TRIAL_CONFIRM_NOTE": (
            "После окончания доступ будет автоматически закрыт.\n"
            "Чтобы остаться — оформи полный доступ через меню."
        ),
        "BTN_ACTIVATE_TRIAL": "✅ Активировать",
        # Duration
        "DURATION_DAYS_HOURS": "{days} дн. {rem} ч.",
        "DURATION_DAYS": "{days} дн.",
        "DURATION_HOURS": "{hours} ч.",
        # Access time
        "ACCESS_TIME": "{days}д {hours}г",
        "ACCESS_TIME_ZERO": "0д 0г",
        # Errors
        "ERR_POSITIVE_INT": "❌ Введи целое число больше 0.",
        # /msg command
        "MSG_FORMAT": "⚠️ Формат: /msg @username текст сообщения",
        "MSG_NOT_FOUND": "❌ Пользователь с таким @username не найден.",
        "MSG_SENT": "✅ Сообщение отправлено пользователю @{username}",
        "MSG_FAILED": "❌ Ошибка отправки сообщения: {error}",
        # Language set
        "LANG_SET": "✅ Язык выбран: Русский",

        # ── Админ-панель ──
        "ADMIN_PANEL_TITLE": "🛠 Админ-панель",
        "ADMIN_USERS_LIST": "👥 Все пользователи:",
        "ADMIN_REFS_LIST": "🤝 Реферальные связи:",
        "ADMIN_NO_REFS": "Нет рефералов.",
        "ADMIN_REFS_INVITED": "{count} приглашено",
        "ADMIN_STATUS_LIST": "💼 Статусы доступа:",
        "ADMIN_STATUS_UNTIL": "До: {date}",
        "ADMIN_STATS_TITLE": "📊 Общая статистика:",
        "ADMIN_STATS_TOTAL": "👥 Пользователей: {total}",
        "ADMIN_STATS_TRIALS": "🆓 Использовали триал: {trials}",
        "ADMIN_STATS_ACTIVE": "✅ Активные подписки: {active}",
        "ADMIN_TRIAL_DURATION_INFO": (
            "⏱ Текущая длительность триала: {hours}ч ({days}д {rem}ч)\n\n"
            "Введи новое значение командой:\n"
            "/set_trial_duration <часы> или /set_trial_duration <дни>д\n\n"
            "Примеры:\n"
            "● /set_trial_duration 72 — 72 часа\n"
            "● /set_trial_duration 5д — 5 дней"
        ),
        "ADMIN_RESET_TRIAL_PROMPT": "🔄 Сбросить триал пользователю:\n\nВведи /reset_trial @username или ID",
        "ADMIN_RESET_USAGE": "⚙️ Формат: /reset_trial @username или ID",
        "ADMIN_RESET_NOT_FOUND": "❌ Пользователь не найден.",
        "ADMIN_RESET_DONE": "✅ Триал сброшен для @{username}.\n↳ Пользователь может снова активировать пробный доступ.",
        "ADMIN_TRIAL_USAGE": "⚙️ Формат: /set_trial_duration 72 или /set_trial_duration 5д",
        "ADMIN_TRIAL_INVALID": "❌ Неверный формат. Пример: /set_trial_duration 72 или /set_trial_duration 5д",
        "ADMIN_TRIAL_CHANGED": "✅ Длительность триала изменена: {hours}ч ({days}д {rem}ч)",
        "ADMIN_MSG_PROMPT": "✉️ Введи @username или ID пользователя которому хочешь написать:",
        "ADMIN_MSG_TEXT_PROMPT": "✉️ Теперь введи текст сообщения:",
        "ADMIN_MSG_SENT": "✅ Сообщение отправлено пользователю {target}.",
        "ADMIN_MSG_NOT_FOUND": "❌ Пользователь не найден.",
        "ADMIN_MSG_FAILED": "⚠️ Не удалось отправить: {error}",
        "ADMIN_KICK_PROMPT": "🚫 Введи @username или ID пользователя которого хочешь кикнуть:",
        "ADMIN_KICK_NOT_FOUND": "❌ Пользователь не найден.",
        "ADMIN_KICK_SUCCESS": "✅ Пользователь @{username} кикнут из канала.",
        "ADMIN_KICK_FAILED": "⚠️ Не удалось кикнуть: {error}",
        "ADMIN_PRICE_INFO": "⚙️ Текущая цена: {currency}{price} {label}\n\nВыбери тип оплаты:",
        "ADMIN_PRICE_TYPE_PROMPT": "⚙️ Тип: {label}\n\nВведи новую цену (число):",
        "ADMIN_PRICE_CHANGED": "✅ Цена доступа изменена: {currency}{price} {label}",
        "ADMIN_PRICE_INVALID": "❌ Неверный формат. Введи целое число больше 0.",
        "ADMIN_PRICE_LABEL_MONTHLY": "/мес.",
        "ADMIN_PRICE_LABEL_FOREVER": "— навсегда",
        "ADMIN_BROADCAST_PROMPT": "📢 Отправь текст или фото с подписью для рассылки:",
        "ADMIN_PROMOS_TITLE": "🎟 Промокоды",
        "ADMIN_PROMOS_EMPTY": "🎟 Промокоды\n\nСписок пуст.",
        "ADMIN_PROMO_TYPE_PROMPT": "🎟 Выберите тип промокода:",
        "ADMIN_PROMO_DAYS_PROMPT": "🎟 Тип: {label}\n\nВведи количество дней числом:",
        "ADMIN_PROMO_DAYS_INVALID": "❌ Введи целое число больше 0.",
        "ADMIN_PROMO_CREATED": (
            "✅ Промокод создан!\n\n"
            "🎟 Код: `{code}`\n"
            "📋 Тип: {type}\n"
            "⏱ Длительность: {days}\n\n"
            "Отправьте этот код пользователю."
        ),
        "ADMIN_PROMO_ACTIVE": "⏳ Активный",
        "ADMIN_PROMO_DELETED": "🗑 Промокод {code} удалён.",
        "ADMIN_PROMO_DEL_NOT_FOUND": "❌ Промокод не найден.",
        "ADMIN_BACK": "⬅️ Назад",
        # Кнопки админ-панели
        "ADMIN_BTN_DM": "✉️ Написать в DM",
        "ADMIN_BTN_KICK": "🚫 Кикнуть",
        "ADMIN_BTN_BROADCAST": "📢 Рассылка",
        "ADMIN_BTN_RESET_TRIAL": "🔄 Сбросить триал",
        "ADMIN_BTN_TRIAL_DURATION": "⏱ Длительность триала",
        "ADMIN_BTN_PRICE": "⚙️ Цена доступа",
        "ADMIN_BTN_PROMOS": "🎟 Промокоды",
        "ADMIN_BTN_USERS": "👥 Пользователи",
        "ADMIN_BTN_STATUS": "💼 Статусы доступа",
        "ADMIN_BTN_STATS": "📊 Статистика",
        "ADMIN_BTN_LIVE_MONITOR": "🧠 LIVE MONITOR",
        "ADMIN_BTN_REFS": "🤝 Рефералы",
        "ADMIN_PRICE_BTN_MONTHLY": "📅 /мес.",
        "ADMIN_PRICE_BTN_FOREVER": "💎 Навсегда",
        "ADMIN_PROMO_BTN_FULL": "💠 Full (полный доступ)",
        "ADMIN_PROMO_BTN_TRIAL": "🧪 Trial (пробный)",
        "ADMIN_PROMO_BTN_FOREVER": "♾️ Навсегда",
        "ADMIN_PROMO_BTN_CREATE": "➕ Создать новый",
        "ADMIN_PROMO_BTN_LIST": "🎟 К списку промокодов",
        # Live monitor
        "ADMIN_LIVE_TITLE": "🧠 LIVE MONITOR",
        "ADMIN_LIVE_TOTAL": "👥 Всего пользователей: {total}",
        "ADMIN_LIVE_ACTIVE": "🟢 Активных: {active}",
        "ADMIN_LIVE_TRIAL": "🧪 Триал: {trial}",
        "ADMIN_LIVE_LOCKED": "🔒 Без доступа: {locked}",
        "ADMIN_LIVE_30D_TITLE": "📊 За последние 30 дней:",
        "ADMIN_LIVE_30D_NEW": "• Новых: {count}",
        "ADMIN_LIVE_30D_TRIAL": "• Активировали триал: {count} ({conv})",
        "ADMIN_LIVE_30D_PAID": "• Купили доступ: {count} ({conv})",
        "ADMIN_LIVE_30D_REVENUE": "• 💰 Доход: {currency}{amount}",
        # Управление админами
        "ADMIN_BTN_ADMINS": "👥 Админы",
        "ADMIN_ADMINS_TITLE": "👥 Администраторы",
        "ADMIN_ADMINS_EMPTY": "👥 Администраторы\n\nДополнительных админов нет.",
        "ADMIN_ADMINS_ADDED": "Добавлен: {date}",
        "ADMIN_ADD_BTN": "➕ Добавить админа",
        "PROMO_TYPE_FULL": "Полный",
        "PROMO_TYPE_TRIAL": "Пробный",
        "ADMIN_REFRESH": "🔄 Обновить",
        "DATA_ACTUAL": "✅ Данные актуальны",
        "NAV_PREV": "◀️ Назад",
        "NAV_NEXT": "▶️ Далее",
        "CUSTOM_DAYS_BTN": "✏️ Указать дни",
        "BTN_CONFIRM": "✅ Подтвердить",
        "BTN_CANCEL": "❌ Отмена",
        "BTN_YES": "✅ Да",
        "BTN_NO": "❌ Нет",
        "CURRENCY_EUR": "€ EUR",
        "CURRENCY_USD": "$ USD",
        "CURRENCY_GBP": "£ GBP",
        "CURRENCY_CUSTOM": "✏️ Своя",
        "ADMIN_ADD_PROMPT": "➕ Введи @username или ID нового админа:",
        "ADMIN_ADD_NOT_FOUND": "❌ Пользователь не найден в базе.",
        "ADMIN_ADD_ALREADY": "⚠️ Этот пользователь уже является админом.",
        "ADMIN_ADD_SUCCESS": "👑 @{username} теперь среди администраторов.",
        "ADMIN_REMOVE_CONFIRM": "⚠️ Снять права админа у @{username}?",
        "ADMIN_REMOVE_SUCCESS": "✅ Права админа сняты у @{username}.",
        "ADMIN_REMOVE_NOT_FOUND": "❌ Админ не найден.",
        "ADMIN_NEW_ADMIN_NOTIFY": "👑 Поздравляем. Вы получили права администратора.\nПанель управления теперь в вашем распоряжении — /admin",
        "ADMIN_ONLY_OWNER": "⚠️ Только главный администратор может управлять админами.",
        "CONFIRM_KICK": "⚠️ Кикнуть пользователя @{username}?",
        "ACTION_CANCELLED": "❌ Действие отменено.",
        "CONFIRM_PROMO_DEL": "⚠️ Удалить промокод {code}?",
        # Выбор валюты
        "ADMIN_CURRENCY_PROMPT": "Выберите валюту или введите свою:",
        "ADMIN_CURRENCY_CUSTOM_PROMPT": "Введите символ валюты (например: ₴, USDT, CHF):",
        "ADMIN_CURRENCY_SAVED": "✅ Валюта сохранена: {currency}",
        # Детали пользователя
        "USER_DETAIL_TITLE": "👤 Информация о пользователе",
        "USER_JOINED": "📅 Присоединился: {date}",
        "USER_STATUS": "🔰 Статус: {mode}",
        "USER_ACCESS_UNTIL": "⏳ Закінчується: {date}",
        "BTN_DM": "✉️ Написать",
        "BTN_RESET_TRIAL": "🔄 Сбросить триал",
        "BTN_KICK": "🚫 Кикнуть",
        "CONFIRM_RESET_TRIAL": "🔄 Сбросить триал для @{username}?",
        "RESET_TRIAL_DONE": "✅ Триал сброшен для @{username}",
        "DM_PROMPT": "✉️ Введите текст сообщения:",
        "DM_SENT": "✅ Сообщение отправлено",
        "DM_FAILED": "❌ Не удалось отправить: {error}",
        "ADMIN_REVOKED": "🔒 Ваши права администратора были отозваны.",
        # Price suffixes & hardcoded button labels (i18n cleanup)
        "PRICE_SUFFIX_MONTHLY": "/мес.",
        "PRICE_SUFFIX_FOREVER": "— навсегда",
        "BTN_CUSTOM_DAYS": "✏️ Указать дни",
        "BTN_ADMIN_PANEL": "🛠 Админ панель",
        # Управление крипто адресом
        "ADMIN_BTN_ADDRESS": "💳 Крипто адрес",
        "ADMIN_ADDRESS_PROMPT": "Введите новый адрес USDT TRC-20 кошелька:",
        "ADMIN_ADDRESS_SET": "✅ Адрес обновлён: `{address}`",
        "ADMIN_ADDRESS_INVALID": "❌ Неверный адрес. Должен начинаться с T и содержать 34 символа.",
        "ADMIN_ADDRESS_PROMPT_FLOW": "💳 Введите адрес USDT TRC-20 кошелька (или отправьте /skip чтобы оставить текущий):",
        "ADMIN_ADDRESS_SKIPPED": "⏭ Крипто адрес не изменён.",
    },
}


def t(lang, key, **kwargs):
    """Get translated text by language and key."""
    text = TEXTS.get(lang, TEXTS["en"]).get(key, TEXTS["en"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text


# All 3 variants of each button text for handler matching
ALL_ACTIVATE = [TEXTS[l]["BUTTON_ACTIVATE"] for l in ("en", "uk", "ru")]
ALL_TRIAL = [TEXTS[l]["BUTTON_TRIAL"] for l in ("en", "uk", "ru")]
ALL_INVITE = [TEXTS[l]["BUTTON_INVITE"] for l in ("en", "uk", "ru")]
ALL_MY_ACCESS = [TEXTS[l]["BUTTON_MY_ACCESS"] for l in ("en", "uk", "ru")]
ALL_ADMIN_PANEL = [TEXTS[l]["BTN_ADMIN_PANEL"] for l in ("en", "uk", "ru")]
