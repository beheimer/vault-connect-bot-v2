import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'connect.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        full_name TEXT,
        username TEXT,
        lang TEXT DEFAULT 'en',
        joined_at TEXT,
        invited_by INTEGER,
        trial_used INTEGER DEFAULT 0,
        trial_at TEXT,
        access_paid INTEGER DEFAULT 0,
        access_until TEXT,
        paid_at TEXT,
        reminder_sent INTEGER DEFAULT 0,
        paid_refs INTEGER DEFAULT 0,
        referral_bonus_given INTEGER DEFAULT 0,
        mode TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS promos (
        code TEXT PRIMARY KEY,
        type TEXT,
        days INTEGER,
        used INTEGER DEFAULT 0,
        used_by INTEGER
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        added_by INTEGER,
        added_at TEXT
    )''')
    # Add columns that may be missing from earlier schema version
    for col, coltype in [
        ('referral_bonus_given', 'INTEGER DEFAULT 0'),
        ('mode', 'TEXT'),
    ]:
        try:
            c.execute(f'ALTER TABLE users ADD COLUMN {col} {coltype}')
        except Exception:
            pass
    conn.commit()
    conn.close()

def get_user(user_id: int) -> dict:
    conn = get_conn()
    row = conn.execute('SELECT * FROM users WHERE id=?', (int(user_id),)).fetchone()
    conn.close()
    return dict(row) if row else {}

def get_user_by_username(username: str) -> dict:
    conn = get_conn()
    row = conn.execute('SELECT * FROM users WHERE LOWER(username)=LOWER(?)', (username,)).fetchone()
    conn.close()
    return dict(row) if row else {}

def save_user(user_id: int, data: dict):
    conn = get_conn()
    existing = conn.execute('SELECT id FROM users WHERE id=?', (int(user_id),)).fetchone()
    if existing:
        if data:
            fields = ', '.join(f'{k}=?' for k in data)
            conn.execute(f'UPDATE users SET {fields} WHERE id=?', (*data.values(), int(user_id)))
    else:
        data = dict(data)
        data['id'] = int(user_id)
        fields = ', '.join(data.keys())
        placeholders = ', '.join('?' * len(data))
        conn.execute(f'INSERT INTO users ({fields}) VALUES ({placeholders})', list(data.values()))
    conn.commit()
    conn.close()

def update_user_field(user_id: int, field: str, value):
    conn = get_conn()
    conn.execute(f'UPDATE users SET {field}=? WHERE id=?', (value, int(user_id)))
    conn.commit()
    conn.close()

def get_all_users() -> list:
    conn = get_conn()
    rows = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_referral_counts() -> dict:
    """Returns {user_id: count_of_invited_users}."""
    conn = get_conn()
    rows = conn.execute(
        'SELECT invited_by, COUNT(*) as cnt FROM users WHERE invited_by IS NOT NULL GROUP BY invited_by'
    ).fetchall()
    conn.close()
    return {row['invited_by']: row['cnt'] for row in rows}

def get_setting(key: str, default=None):
    conn = get_conn()
    row = conn.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
    conn.close()
    return row['value'] if row else default

def set_setting(key: str, value):
    conn = get_conn()
    conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
    conn.commit()
    conn.close()

def get_promo(code: str) -> dict:
    conn = get_conn()
    row = conn.execute('SELECT * FROM promos WHERE code=?', (code,)).fetchone()
    conn.close()
    return dict(row) if row else {}

def get_all_promos() -> list:
    conn = get_conn()
    rows = conn.execute('SELECT * FROM promos').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_promo(code: str, ptype: str, days: int):
    conn = get_conn()
    conn.execute('INSERT OR IGNORE INTO promos (code, type, days) VALUES (?, ?, ?)', (code, ptype, days))
    conn.commit()
    conn.close()

def use_promo(code: str, user_id: int):
    conn = get_conn()
    conn.execute('UPDATE promos SET used=1, used_by=? WHERE code=?', (int(user_id), code))
    conn.commit()
    conn.close()

def delete_promo_by_code(code: str):
    conn = get_conn()
    conn.execute('DELETE FROM promos WHERE code=?', (code,))
    conn.commit()
    conn.close()


def get_admins() -> list:
    conn = get_conn()
    rows = conn.execute('SELECT * FROM admins').fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_admin(user_id, username, added_by) -> None:
    import datetime
    conn = get_conn()
    conn.execute(
        'INSERT OR REPLACE INTO admins (user_id, username, added_by, added_at) VALUES (?, ?, ?, ?)',
        (int(user_id), username, int(added_by), datetime.datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def remove_admin(user_id) -> None:
    conn = get_conn()
    conn.execute('DELETE FROM admins WHERE user_id=?', (int(user_id),))
    conn.commit()
    conn.close()


def is_admin(user_id: int) -> bool:
    from config.settings import ADMIN_ID
    if int(user_id) == int(ADMIN_ID):
        return True
    conn = get_conn()
    row = conn.execute('SELECT user_id FROM admins WHERE user_id=?', (int(user_id),)).fetchone()
    conn.close()
    return row is not None

def get_admin_panel_msg_id(admin_id: int) -> int:
    val = get_setting(f"panel_msg_{admin_id}", "")
    try:
        return int(val)
    except Exception:
        return 0

def set_admin_panel_msg_id(admin_id: int, msg_id: int):
    set_setting(f"panel_msg_{admin_id}", str(msg_id))
