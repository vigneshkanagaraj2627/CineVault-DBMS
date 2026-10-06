import os
import sys

# Add CineVault project root to Python path
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.database.connection import get_collection


def reset_watchlists():
    users = get_collection("users")

    result = users.update_many(
        {},
        {"$set": {"watchlist": []}}
    )

    print("Watchlists reset successfully.")
    print("Users matched:", result.matched_count)
    print("Users updated:", result.modified_count)


if __name__ == "__main__":
    reset_watchlists()