from utils.db import get_user, update_user_field, save_user

def get_lang(user_id) -> str:
    if not user_id:
        return 'en'
    try:
        user = get_user(int(user_id))
        return user.get('lang', 'en') or 'en'
    except:
        return 'en'

def set_lang(user_id: int, lang: str):
    try:
        user = get_user(int(user_id))
        if user:
            update_user_field(int(user_id), 'lang', lang)
        else:
            save_user(int(user_id), {'lang': lang})
    except Exception as e:
        print(f"[LANG ERROR] {e}")
