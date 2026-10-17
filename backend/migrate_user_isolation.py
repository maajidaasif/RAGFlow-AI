"""
migrate_user_isolation.py
=========================
One-time migration: adds user_id column to the
'papers' and 'analysis_history' tables.

Safe strategy:
  - Adds columns as nullable (no NOT NULL constraint).
  - Existing rows keep user_id = NULL and will NOT
    appear in any authenticated user's queries.
  - No data is deleted or arbitrarily reassigned.

Run from the backend/ folder with venv active:
    python migrate_user_isolation.py

This script is idempotent — safe to run multiple times.
"""

import sqlite3
import os
import sys

# ------------------------------------
# Locate the database file
# ------------------------------------

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "database", "researchmind.db")
)

if not os.path.exists(DB_PATH):
    print(f"ERROR: Database not found at: {DB_PATH}")
    print("Start the app once to create the database, then re-run this script.")
    sys.exit(1)

print(f"\nDatabase found: {DB_PATH}")


def column_exists(cursor, table_name, column_name):
    """Return True if column_name already exists in table_name."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

migrations_applied = 0

# ------------------------------------
# 1. Add user_id to papers
# ------------------------------------

if not column_exists(cursor, "papers", "user_id"):
    print("\n[1/2] Adding user_id to 'papers' table...")
    cursor.execute(
        "ALTER TABLE papers ADD COLUMN user_id INTEGER REFERENCES users(id)"
    )
    conn.commit()
    print("      [OK] user_id added to papers (existing rows set to NULL)")
    migrations_applied += 1
else:
    print("\n[1/2] user_id already exists in 'papers' — skipped.")

# ------------------------------------
# 2. Add user_id to analysis_history
# ------------------------------------

if not column_exists(cursor, "analysis_history", "user_id"):
    print("\n[2/2] Adding user_id to 'analysis_history' table...")
    cursor.execute(
        "ALTER TABLE analysis_history ADD COLUMN user_id INTEGER REFERENCES users(id)"
    )
    conn.commit()
    print("      [OK] user_id added to analysis_history (existing rows set to NULL)")
    migrations_applied += 1
else:
    print("\n[2/2] user_id already exists in 'analysis_history' — skipped.")

conn.close()

# ------------------------------------
# Summary
# ------------------------------------

print("\n" + "=" * 50)
if migrations_applied > 0:
    print(f"Migration complete. {migrations_applied} column(s) added.")
    print("\nIMPORTANT: Existing records have user_id = NULL.")
    print("They will not appear in any user's queries.")
    print("They can be safely deleted from the DB if needed.")
else:
    print("No migrations needed. Database is already up to date.")
print("=" * 50 + "\n")
