"""
controllers/user_controller.py
---------------------------------
Real per-user operations against the MongoDB `users` collection:
watchlist management, profile updates, and password changes.

Every method takes the current user's id (a string, as stored in
the GUI's user dict under 'id') so the watchlist is scoped to the
logged-in user and persists across app restarts.
"""

import bcrypt
from bson import ObjectId
from bson.errors import InvalidId

from backend.database.connection import get_collection, DatabaseConnectionError
from backend.models.user_model import User
from backend.models.movie_model import Movie


class UserError(Exception):
    """Raised for expected user-operation failures (validation,
    not-found, DB down) so views can show a friendly dialog."""
    pass


class UserController:

    @staticmethod
    def _users_collection():
        try:
            return get_collection("users")
        except DatabaseConnectionError as e:
            raise UserError(str(e)) from e

    @staticmethod
    def _movies_collection():
        try:
            return get_collection("movies")
        except DatabaseConnectionError as e:
            raise UserError(str(e)) from e

    @staticmethod
    def _to_oid(id_value, label="ID"):
        try:
            return ObjectId(id_value)
        except (InvalidId, TypeError):
            raise UserError(f"Invalid {label}.")

    # ---------------- Watchlist ----------------

    @staticmethod
    def get_watchlist(user_id) -> list:
        users = UserController._users_collection()
        user_oid = UserController._to_oid(user_id, "user ID")
        user_doc = users.find_one({"_id": user_oid})
        if not user_doc:
            raise UserError("User not found.")

        watchlist_ids = user_doc.get("watchlist", [])
        if not watchlist_ids:
            return []

        movies_col = UserController._movies_collection()
        object_ids = []
        for mid in watchlist_ids:
            try:
                object_ids.append(mid if isinstance(mid, ObjectId) else ObjectId(mid))
            except (InvalidId, TypeError):
                continue

        cursor = movies_col.find({"_id": {"$in": object_ids}})
        return [Movie.from_doc(doc).to_gui_dict() for doc in cursor]

    @staticmethod
    def is_in_watchlist(user_id, movie_id) -> bool:
        users = UserController._users_collection()
        user_oid = UserController._to_oid(user_id, "user ID")
        user_doc = users.find_one({"_id": user_oid}, {"watchlist": 1})
        if not user_doc:
            return False
        watchlist = [str(mid) for mid in user_doc.get("watchlist", [])]
        return str(movie_id) in watchlist

    @staticmethod
    def add_to_watchlist(user_id, movie_id) -> bool:
        print(f"Add to Watchlist -> user={user_id}, movie={movie_id}")
        users = UserController._users_collection()
        user_oid = UserController._to_oid(user_id, "user ID")
        movie_oid = UserController._to_oid(movie_id, "movie ID")

        result = users.update_one(
            {"_id": user_oid},
            {"$addToSet": {"watchlist": movie_oid}}
        )
        if result.matched_count == 0:
            raise UserError("User not found.")
        return True

    @staticmethod
    def remove_from_watchlist(user_id, movie_id) -> bool:
        print(f"Remove from Watchlist -> user={user_id}, movie={movie_id}")
        users = UserController._users_collection()
        user_oid = UserController._to_oid(user_id, "user ID")
        movie_oid = UserController._to_oid(movie_id, "movie ID")

        result = users.update_one(
            {"_id": user_oid},
            {"$pull": {"watchlist": movie_oid}}
        )
        if result.matched_count == 0:
            raise UserError("User not found.")
        return True

    # ---------------- Profile & Settings ----------------

    @staticmethod
    def update_profile(user_id, user_data: dict) -> dict:
        print(f"Update Profile Clicked -> {user_data}")
        users = UserController._users_collection()
        user_oid = UserController._to_oid(user_id, "user ID")

        name = (user_data.get("full_name") or user_data.get("name") or "").strip()
        email = (user_data.get("email") or "").strip().lower()

        if not name or not email:
            raise UserError("Name and email cannot be empty.")

        # Prevent taking over someone else's email
        existing = users.find_one({"email": email, "_id": {"$ne": user_oid}})
        if existing:
            raise UserError("That email is already used by another account.")

        users.update_one({"_id": user_oid}, {"$set": {"name": name, "email": email}})
        updated_doc = users.find_one({"_id": user_oid})
        return User.from_doc(updated_doc).to_gui_dict()

    @staticmethod
    def change_password(user_id, current_password: str, new_password: str) -> bool:
        users = UserController._users_collection()
        user_oid = UserController._to_oid(user_id, "user ID")
        user_doc = users.find_one({"_id": user_oid})
        if not user_doc:
            raise UserError("User not found.")

        if not current_password or not new_password:
            raise UserError("Please fill in both password fields.")

        stored_hash = user_doc.get("password", "").encode("utf-8")
        if not bcrypt.checkpw(current_password.encode("utf-8"), stored_hash):
            raise UserError("Current password is incorrect.")

        if len(new_password) < 6:
            raise UserError("New password must be at least 6 characters long.")

        new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        users.update_one({"_id": user_oid}, {"$set": {"password": new_hash.decode("utf-8")}})
        print("Save Settings Clicked -> password updated")
        return True

    @staticmethod
    def update_settings(user_id, settings_data: dict) -> bool:
        """Handles the Settings screen's 'Change Password' form. Other
        toggles (dark mode, notifications) are cosmetic-only in this
        mini-project scope and aren't persisted server-side."""
        current_password = settings_data.get("current_password", "")
        new_password = settings_data.get("new_password", "")
        if not current_password and not new_password:
            # Nothing to change (e.g. only cosmetic toggles were touched)
            print("Save Settings Clicked -> no password change requested")
            return True
        return UserController.change_password(user_id, current_password, new_password)
