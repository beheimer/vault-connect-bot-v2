import random
import string
import datetime
from utils.db import get_promo, get_all_promos, create_promo, use_promo, delete_promo_by_code, update_user_field, get_user

def generate_promo_code() -> str:
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=4)) + '-' + ''.join(random.choices(chars, k=4))

def make_promo(ptype: str, days: int) -> str:
    code = generate_promo_code()
    create_promo(code, ptype, days)
    return code

def get_promos() -> dict:
    promos = get_all_promos()
    return {p['code']: p for p in promos}

def redeem_promo(code: str, user_id: int):
    """Returns (status, promo) where status is 'not_found', 'already_used', 'already_active', 'trial_already_used', or 'success'."""
    promo = get_promo(code)
    if not promo:
        return "not_found", None
    if promo.get('used'):
        return "already_used", promo

    days = promo.get('days', 0)
    ptype = promo.get('type', 'full')
    now = datetime.datetime.now()

    if ptype == "trial":
        user = get_user(int(user_id))
        if user:
            access_until = user.get("access_until")
            if access_until:
                try:
                    if datetime.datetime.fromisoformat(access_until) > now:
                        return "already_active", promo
                except Exception:
                    pass
            if user.get("trial_used"):
                return "trial_already_used", promo

    use_promo(code, user_id)

    if ptype == "full":
        update_user_field(int(user_id), 'access_paid', 1)
        if days == 0:
            update_user_field(int(user_id), 'access_until', "2099-12-31T23:59:59")
        else:
            update_user_field(int(user_id), 'access_until', (now + datetime.timedelta(days=days)).isoformat())
        update_user_field(int(user_id), 'paid_at', now.isoformat())
    elif ptype == "trial":
        update_user_field(int(user_id), 'trial_used', 1)
        update_user_field(int(user_id), 'access_until', (now + datetime.timedelta(days=days)).isoformat())
        update_user_field(int(user_id), 'trial_at', now.isoformat())

    return "success", promo

def delete_promo(code: str):
    delete_promo_by_code(code)
    return True
