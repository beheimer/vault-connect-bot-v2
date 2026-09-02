import datetime
import time
from utils.db import get_user, save_user, update_user_field, get_setting


def activate_trial_for_user(user_id):
    """Activate trial. Returns 'activated' or 'already_used'."""
    user = get_user(user_id)
    if user.get("trial_used"):
        return "already_used"

    _hours = int(get_setting("trial_duration_hours", 120))
    access_until = (datetime.datetime.now() + datetime.timedelta(hours=_hours)).isoformat()

    if user:
        update_user_field(int(user_id), 'trial_used', 1)
        update_user_field(int(user_id), 'access_until', access_until)
        update_user_field(int(user_id), 'access_paid', 0)
        update_user_field(int(user_id), 'trial_at', datetime.datetime.now().isoformat())
    else:
        save_user(int(user_id), {
            'trial_used': 1,
            'access_until': access_until,
            'access_paid': 0,
            'trial_at': datetime.datetime.now().isoformat()
        })
    return "activated"


async def generate_personal_invite(bot, user_id):
    from config.settings import CHANNEL_LINK
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_LINK, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return None

        expire = int(time.time()) + 600
        invite = await bot.create_chat_invite_link(
            chat_id=CHANNEL_LINK,
            name=f"user_{user_id}",
            member_limit=1,
            expire_date=expire,
            creates_join_request=False
        )
        return invite.invite_link
    except Exception as e:
        print("Error creating invite link:", e)
        return None



def get_access_mode(user):
    """Returns a text key: 'MODE_FULL', 'MODE_TRIAL', or 'MODE_GUEST'."""
    now = datetime.datetime.now()

    access_until = user.get("access_until")
    access_paid = user.get("access_paid", False)

    if access_until:
        try:
            until = datetime.datetime.fromisoformat(access_until)
            if until > now:
                if access_paid:
                    return "MODE_FULL"
                else:
                    return "MODE_TRIAL"
        except Exception:
            pass

    return "MODE_GUEST"
