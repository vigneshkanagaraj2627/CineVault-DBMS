"""
scripts/init_database.py
----------------------------
One-time (or safely re-runnable) setup script for CineVault's
MongoDB database. Run this AFTER MongoDB is installed and running,
and AFTER your existing ~1500-movie dataset has been imported into
the `movies` collection.

What this script does:
    1. Verifies the connection to MongoDB.
    2. Creates the `users` collection if it doesn't exist yet.
    3. Creates a UNIQUE index on users.email (prevents duplicate
       accounts at the database level, as a safety net on top of
       the application-level check in AuthController).
    4. Creates a helpful index on movies.name (case-insensitive
       search) and movies.rating (fast top-rated sorting) — this
       does NOT touch or overwrite your existing movie documents.
    5. Optionally creates a default admin account, ONLY if no admin
       account exists yet, so you have a way to log into the Admin
       Dashboard immediately.

This script never deletes or modifies the existing `movies`
collection's documents — it only adds indexes.

Run with:
    python scripts/init_database.py
"""

import sys
import os

# Allow running this script directly (python scripts/init_database.py)
# by making sure the project root is on sys.path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

from backend.database.connection import get_db, DatabaseConnectionError

DEFAULT_ADMIN_EMAIL = "admin@cinevault.com"
DEFAULT_ADMIN_PASSWORD = "Admin@123"
DEFAULT_ADMIN_NAME = "CineVault Admin"


def main():
    print("=" * 60)
    print(" CineVault — Database Initialization")
    print("=" * 60)

    # ---- Step 1: verify connection ----
    print("\n[1/4] Connecting to MongoDB...")
    try:
        db = get_db()
        db.command("ping")
    except DatabaseConnectionError as e:
        print("\n❌ Could not connect to MongoDB.")
        print(str(e))
        sys.exit(1)
    print("      ✅ Connected to database:", db.name)

    # ---- Step 2: users collection + unique email index ----
    print("\n[2/4] Setting up 'users' collection...")
    users = db["users"]
    users.create_index("email", unique=True, name="unique_email_idx")
    print("      ✅ Unique index on users.email ready.")

    # ---- Step 3: movies collection indexes (non-destructive) ----
    print("\n[3/4] Setting up indexes on existing 'movies' collection...")
    movies = db["movies"]
    existing_count = movies.count_documents({})
    print(f"      Found {existing_count} existing movie document(s) — left untouched.")

    movies.create_index("name", name="name_idx")
    movies.create_index([("rating", -1)], name="rating_desc_idx")
    movies.create_index("year", name="year_idx")
    print("      ✅ Indexes on movies.name / movies.rating / movies.year ready.")

    # ---- Step 4: default admin account ----
    print("\n[4/4] Checking for an existing admin account...")
    existing_admin = users.find_one({"role": "admin"})
    if existing_admin:
        print(f"      ℹ️  An admin account already exists ({existing_admin.get('email')}). Skipping creation.")
    else:
        hashed = bcrypt.hashpw(DEFAULT_ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt())
        admin_doc = {
            "name": DEFAULT_ADMIN_NAME,
            "email": DEFAULT_ADMIN_EMAIL,
            "password": hashed.decode("utf-8"),
            "role": "admin",
            "watchlist": [],
            "created_at": datetime.now(timezone.utc),
        }
        try:
            users.insert_one(admin_doc)
            print("      ✅ Default admin account created:")
            print(f"         Email:    {DEFAULT_ADMIN_EMAIL}")
            print(f"         Password: {DEFAULT_ADMIN_PASSWORD}")
            print("         ⚠️  Please change this password after your first login.")
        except DuplicateKeyError:
            print("      ℹ️  An account with this email already exists. Skipping creation.")

    print("\n" + "=" * 60)
    print(" Database initialization complete. You can now run CineVault:")
    print("     python main.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
