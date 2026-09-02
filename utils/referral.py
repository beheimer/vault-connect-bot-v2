import datetime
from texts import t
from utils.lang import get_lang
from utils.db import get_user, save_user, update_user_field


def generate_ref_link(user_id):
    return f"https://t.me/Vault_connectBot?start={user_id}"


async def check_referral(bot, user_id, ref_id):
    if not ref_id or str(user_id) == str(ref_id):
        return

    # If user already exists, skip
    existing = get_user(int(user_id))
    if existing:
        return

    # Save new user with invited_by (don't set full_name/username — add_user will fill those)
    save_user(int(user_id), {
        'invited_by': int(ref_id),
        'paid_refs': 0
    })

    # Note: 'invited' list is not stored in SQLite (referral count is derived)
    # We only track invited_by per user

    try:
        ref_lang = get_lang(ref_id)
        await bot.send_message(ref_id, t(ref_lang, "REF_ENTERED"))
    except:
        pass


def add_user(user_id, full_name, username):
    user = get_user(int(user_id))
    data = {}
    data['full_name'] = full_name
    data['username'] = username or (user.get('username', 'unknown') if user else 'unknown')
    if not user or not user.get('joined_at'):
        data['joined_at'] = datetime.datetime.now().isoformat()
    if not user:
        data['paid_refs'] = 0
    save_user(int(user_id), data)


def get_user_stats(user_id):
    user = get_user(int(user_id))
    paid = user.get('paid_refs', 0) if user else 0
    # Count how many users have invited_by = user_id
    from utils.db import get_conn
    conn = get_conn()
    row = conn.execute('SELECT COUNT(*) as cnt FROM users WHERE invited_by=?', (int(user_id),)).fetchone()
    conn.close()
    invited = row['cnt'] if row else 0
    return invited, paid
