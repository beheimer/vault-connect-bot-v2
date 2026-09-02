import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN     = os.environ.get("BOT_TOKEN", "")  # Token from @BotFather
ADMIN_USERNAME = ""        # Your Telegram username (without @)
ADMIN_ID       = 0         # Your Telegram user ID (integer)
CHANNEL_ID     = 0         # Your channel ID (e.g. -1001234567890)
CHANNEL_LINK   = 0         # Same as CHANNEL_ID
REFERRAL_ENABLED = False   # Enable/disable referral system
PROMO_ENABLED    = True    # Enable/disable promo code system
