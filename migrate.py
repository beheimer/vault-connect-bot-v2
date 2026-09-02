import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.db import init_db, set_setting

init_db()

with open('db.json') as f:
    db = json.load(f)

settings = db.get('_settings', {})
for key, value in settings.items():
    set_setting(key, str(value))
    print(f"Migrated setting: {key} = {value}")

print("Migration complete.")
