import os
import sqlite3

db_path = "neps.db"

if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Removed {db_path}")

from app.core.database import init_db

print("Initializing database...")
init_db()
print("Done!")
