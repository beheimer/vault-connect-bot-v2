import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN      = os.environ.get("BOT_TOKEN", "")  # Token from @BotFather
ADMIN_USERNAME = ""        # Your Telegram username (without @)
ADMIN_ID       = 0         # Your Telegram user ID (integer)
CHANNEL_ID     = 0         # Your channel ID — replace with your real channel ID (e.g. -1001234567890)
CHANNEL_LINK   = 0         # channel chat_id as a number without quotes — same as CHANNEL_ID
REFERRAL_ENABLED = False   # completely disables the referral system when False
PROMO_ENABLED    = True    # enables/disables the promo code system
