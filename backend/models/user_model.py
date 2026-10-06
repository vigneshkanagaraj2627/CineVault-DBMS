"""
models/user_model.py
-----------------------
Data representation of a User matching the MongoDB users collection:

    _id, name, email, password (hashed), role, watchlist, created_at

role is either "user" or "admin".
watchlist is a list of movie _id strings.

to_gui_dict() maps these onto the keys the existing views/widgets
already use (full_name, username, is_admin, watchlist_count, joined)
so Sidebar/Profile/etc. don't need to change their field names.
"""

from datetime import datetime, timezone


class User:
    def __init__(self, id=None, name="", email="", password="",
                 role="user", watchlist=None, created_at=None):
        self.id = id
        self.name = name
        self.email = email
        self.password = password  # hashed, never plaintext past the controller
        self.role = role
        self.watchlist = watchlist if watchlist is not None else []
        self.created_at = created_at or datetime.now(timezone.utc)

    @classmethod
    def from_doc(cls, doc: dict) -> "User":
        if doc is None:
            return None
        return cls(
            id=doc.get("_id"),
            name=doc.get("name", ""),
            email=doc.get("email", ""),
            password=doc.get("password", ""),
            role=doc.get("role", "user"),
            watchlist=doc.get("watchlist", []),
            created_at=doc.get("created_at"),
        )

    def to_doc(self) -> dict:
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role,
            "watchlist": self.watchlist,
            "created_at": self.created_at,
        }

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def to_gui_dict(self) -> dict:
        """Compatibility layer so existing views (Sidebar, Profile,
        Dashboard headers) keep working with the same key names they
        were written against, but now backed by real data."""
        joined_str = "—"
        if isinstance(self.created_at, datetime):
            joined_str = self.created_at.strftime("%B %Y")

        return {
            "id": str(self.id) if self.id is not None else None,
            "username": self.email.split("@")[0] if self.email else "user",
            "full_name": self.name or "Unnamed User",
            "name": self.name or "Unnamed User",
            "email": self.email,
            "role": self.role,
            "is_admin": self.is_admin,
            "watchlist": [str(mid) for mid in self.watchlist],
            "watchlist_count": len(self.watchlist),
            "joined": joined_str,
        }

    def __repr__(self):
        return f"<User {self.email!r} role={self.role!r}>"
