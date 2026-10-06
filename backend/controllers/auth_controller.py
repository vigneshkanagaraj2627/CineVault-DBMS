"""
controllers/auth_controller.py
---------------------------------
Real authentication against the MongoDB `users` collection.

- Passwords are hashed with bcrypt; plaintext passwords are never
  stored or compared directly.
- Raises AuthError with a human-readable message on any failure
  (duplicate email, wrong password, missing fields, DB down) so
  views can show it directly in a dialog/label.
"""

import re
from datetime import datetime, timezone

import bcrypt
from pymongo.errors import DuplicateKeyError

from backend.database.connection import get_collection, DatabaseConnectionError
from backend.models.user_model import User

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AuthError(Exception):
    """Raised for any expected auth failure (bad input, duplicate
    email, wrong credentials). Views should catch this and show the
    message to the user; anything else is an unexpected bug."""
    pass


class AuthController:

    @staticmethod
    def _users_collection():
        try:
            return get_collection("users")
        except DatabaseConnectionError as e:
            raise AuthError(str(e)) from e

    # ---------------- Registration ----------------

    @staticmethod
    def register(full_name: str, email: str, password: str, confirm_password: str, role: str = "user") -> dict:
        full_name = (full_name or "").strip()
        email = (email or "").strip().lower()
        password = password or ""

        if not full_name or not email or not password or not confirm_password:
            raise AuthError("Please fill in all fields.")

        if not EMAIL_REGEX.match(email):
            raise AuthError("Please enter a valid email address.")

        if len(password) < 6:
            raise AuthError("Password must be at least 6 characters long.")

        if password != confirm_password:
            raise AuthError("Passwords do not match.")

        users = AuthController._users_collection()

        if users.find_one({"email": email}):
            raise AuthError("An account with this email already exists.")

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        new_user = User(
            name=full_name,
            email=email,
            password=hashed.decode("utf-8"),
            role=role,
            watchlist=[],
            created_at=datetime.now(timezone.utc),
        )

        try:
            result = users.insert_one(new_user.to_doc())
        except DuplicateKeyError:
            raise AuthError("An account with this email already exists.")

        new_user.id = result.inserted_id
        print(f"Register Clicked -> email='{email}' (account created)")
        return new_user.to_gui_dict()

    # ---------------- Login ----------------

    @staticmethod
    def login(email: str, password: str) -> dict:
        email = (email or "").strip().lower()
        password = password or ""

        if not email or not password:
            raise AuthError("Please enter both email and password.")

        users = AuthController._users_collection()
        doc = users.find_one({"email": email})

        print(f"Login Clicked -> email='{email}'")

        if not doc:
            raise AuthError("No account found with this email.")

        stored_hash = doc.get("password", "").encode("utf-8")
        if not bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            raise AuthError("Incorrect password.")

        user = User.from_doc(doc)
        return user.to_gui_dict()

    # ---------------- Misc ----------------

    @staticmethod
    def count_admins() -> int:
        users = AuthController._users_collection()
        return users.count_documents({"role": "admin"})

    @staticmethod
    def logout():
        print("Logout Clicked")
        return True

    @staticmethod
    def get_user_by_id(user_id) -> dict:
        from bson import ObjectId
        users = AuthController._users_collection()
        try:
            doc = users.find_one({"_id": ObjectId(user_id)})
        except Exception:
            doc = None
        user = User.from_doc(doc)
        return user.to_gui_dict() if user else None
