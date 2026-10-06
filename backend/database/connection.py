"""
database/connection.py
-------------------------
Single, reusable MongoDB connection for the whole application.

Everything else (models/controllers) imports get_db() from here
instead of creating its own MongoClient, so there's exactly one
connection pool for the app's lifetime.

Reads the connection string from the MONGO_URI environment variable
if present, otherwise falls back to the local default. This makes it
easy to point the app at a different Mongo instance (or a mock, for
testing) without touching any other file.
"""

import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure


DEFAULT_URI = "mongodb://localhost:27017/"
DATABASE_NAME = "movie_recommendation_db"

# Module-level singletons, created lazily on first use.
_client = None
_db = None
_connection_error = None


class DatabaseConnectionError(Exception):
    """Raised when the app cannot reach MongoDB. Views catch this and
    show a friendly dialog instead of letting the app crash."""
    pass


def _create_client():
    uri = os.environ.get("MONGO_URI", DEFAULT_URI)
    client = MongoClient(uri, serverSelectionTimeoutMS=4000)
    # Force a round-trip so connection errors surface immediately
    # instead of on the first real query somewhere deep in the GUI.
    client.admin.command("ping")
    return client


def get_client() -> MongoClient:
    """Returns the shared MongoClient, creating it on first call."""
    global _client, _connection_error
    if _client is not None:
        return _client
    try:
        _client = _create_client()
        _connection_error = None
        return _client
    except (ServerSelectionTimeoutError, ConnectionFailure) as e:
        _connection_error = str(e)
        raise DatabaseConnectionError(
            "Could not connect to MongoDB at "
            f"{os.environ.get('MONGO_URI', DEFAULT_URI)}.\n\n"
            "Make sure MongoDB Community Server is running locally, "
            "then restart CineVault.\n\n"
            f"Details: {e}"
        ) from e


def get_db():
    """Returns the movie_recommendation_db database handle."""
    global _db
    if _db is not None:
        return _db
    client = get_client()
    _db = client[DATABASE_NAME]
    return _db


def get_collection(name: str):
    """Convenience helper: get_collection('movies') -> Collection."""
    return get_db()[name]


def is_connected() -> bool:
    """Non-throwing check, useful for a splash-screen connectivity test."""
    try:
        get_client()
        return True
    except DatabaseConnectionError:
        return False


def reset_connection_for_testing(client=None, db=None):
    """
    Test-only hook: lets tests (or this project's own smoke tests)
    inject a mongomock client/db instead of a real MongoDB instance.
    Not used anywhere in normal application flow.
    """
    global _client, _db
    _client = client
    _db = db
