#!/usr/bin/env python3
"""
Emergency database reset script.
This will delete the old database and reinitialize from scratch.
"""
import os
import sys

# Get absolute path to the database
script_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_dir, "neps.db")

print(f"[*] Database path: {db_path}")

# Step 1: Delete the database
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"[✓] Deleted old database")
    except Exception as e:
        print(f"[✗] Failed to delete database: {e}")
        sys.exit(1)
else:
    print(f"[*] Database does not exist, will create new one")

# Step 2: Import and initialize
try:
    os.chdir(script_dir)
    sys.path.insert(0, script_dir)
    
    # Import models FIRST to register with Base.metadata
    from app.core.models import *  # noqa: F401, F403
    from app.core.database import init_db, engine
    from sqlalchemy import text
    
    print("[*] Initializing database...")
    init_db()
    print("[✓] Database initialized")
    
    # Step 3: Verify
    print("[*] Verifying schema...")
    with engine.begin() as conn:
        # Verify internships table
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM internships"))
            print("[✓] internships table accessible")
        except Exception as e:
            print(f"[✗] internships table error: {e}")
        
        # Verify students table
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM students"))
            print("[✓] students table accessible")
        except Exception as e:
            print(f"[✗] students table error: {e}")
    
    print("[✓] Database reset complete!")
    
except Exception as e:
    print(f"[✗] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
