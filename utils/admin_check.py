from config.settings import ADMIN_ID
from utils.db import is_admin as db_is_admin


def is_admin(user_id) -> bool:
    if int(user_id) == int(ADMIN_ID):
        return True
    return db_is_admin(int(user_id))
