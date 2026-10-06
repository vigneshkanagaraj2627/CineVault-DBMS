"""
backend/controllers/movie_controller.py
---------------------------------------
Movie operations for the FINAL CineVault MongoDB movie schema.

Final fields:
    title, year, certificate, duration, genres, rating,
    metascore, director, cast, votes, description,
    review_count, review_title, review, poster_url

All read methods return dictionaries prepared for the GUI through
Movie.to_gui_dict().
"""

import re

from bson import ObjectId
from bson.errors import InvalidId

from backend.database.connection import (
    get_collection,
    DatabaseConnectionError
)
from backend.models.movie_model import Movie, parse_genres


class MovieError(Exception):
    """Expected movie-operation error shown safely in the GUI."""
    pass


class MovieController:

    # =========================================================
    # COLLECTION
    # =========================================================

    @staticmethod
    def _collection():
        try:
            return get_collection("movies")
        except DatabaseConnectionError as e:
            raise MovieError(str(e)) from e

    # =========================================================
    # READ
    # =========================================================

    @staticmethod
    def get_all_movies(limit: int = 100) -> list:
        """
        Return a limited number of movies.

        We intentionally do NOT load all ~10,000 movies into
        CustomTkinter at once because that would make the GUI slow.
        """
        col = MovieController._collection()

        cursor = (
            col.find()
            .sort([("rating", -1), ("votes", -1)])
            .limit(limit)
        )

        return [
            Movie.from_doc(doc).to_gui_dict()
            for doc in cursor
        ]

    @staticmethod
    def get_movie_by_id(movie_id) -> dict:
        """Return one movie by MongoDB ObjectId."""

        col = MovieController._collection()

        try:
            oid = ObjectId(movie_id)
        except (InvalidId, TypeError):
            raise MovieError("Invalid movie ID.")

        doc = col.find_one({"_id": oid})

        if not doc:
            raise MovieError("Movie not found.")

        return Movie.from_doc(doc).to_gui_dict()

    # =========================================================
    # SEARCH
    # =========================================================

    @staticmethod
    def search_movies(query: str, limit: int = 100) -> list:
        """
        Case-insensitive partial title search.
        """

        print(f"Search Clicked -> query='{query}'")

        query = (query or "").strip()

        if not query:
            return MovieController.get_all_movies(limit)

        col = MovieController._collection()

        # Escape special regex characters entered by the user.
        pattern = re.compile(
            re.escape(query),
            re.IGNORECASE
        )

        cursor = (
            col.find({
                "title": {
                    "$regex": pattern
                }
            })
            .sort([("rating", -1), ("votes", -1)])
            .limit(limit)
        )

        return [
            Movie.from_doc(doc).to_gui_dict()
            for doc in cursor
        ]

    # =========================================================
    # FILTER
    # =========================================================

    @staticmethod
    def filter_movies(
        genre: str = None,
        min_rating: float = None,
        year: int = None,
        limit: int = 100
    ) -> list:

        print(
            "Filter Applied -> "
            f"genre={genre}, "
            f"min_rating={min_rating}, "
            f"year={year}"
        )

        col = MovieController._collection()

        mongo_query = {}

        # Genres are now stored as MongoDB arrays:
        #
        # genres: ["Action", "Adventure", "Sci-Fi"]
        #
        # MongoDB naturally matches an array containing this value.
        if genre and genre != "All":
            mongo_query["genres"] = genre

        if min_rating is not None:
            try:
                mongo_query["rating"] = {
                    "$gte": float(min_rating)
                }
            except (TypeError, ValueError):
                raise MovieError(
                    "Minimum rating must be a number."
                )

        if year is not None:
            try:
                mongo_query["year"] = int(year)
            except (TypeError, ValueError):
                raise MovieError(
                    "Year must be a whole number."
                )

        cursor = (
            col.find(mongo_query)
            .sort([("rating", -1), ("votes", -1)])
            .limit(limit)
        )

        return [
            Movie.from_doc(doc).to_gui_dict()
            for doc in cursor
        ]

    @staticmethod
    def filter_by_genre(genre: str) -> list:
        return MovieController.filter_movies(
            genre=genre
        )

    @staticmethod
    def filter_by_rating(min_rating: float) -> list:
        return MovieController.filter_movies(
            min_rating=min_rating
        )

    @staticmethod
    def filter_by_year(year: int) -> list:
        return MovieController.filter_movies(
            year=year
        )

    # =========================================================
    # TOP RATED
    # =========================================================

    @staticmethod
    def get_top_rated(limit: int = 20) -> list:
        """
        Return highest-rated movies.

        votes is used as a secondary sort so movies with the
        same rating are ordered by popularity.
        """

        col = MovieController._collection()

        cursor = (
            col.find({
                "rating": {
                    "$ne": None
                }
            })
            .sort([
                ("rating", -1),
                ("votes", -1)
            ])
            .limit(limit)
        )

        return [
            Movie.from_doc(doc).to_gui_dict()
            for doc in cursor
        ]

    # =========================================================
    # GENRES
    # =========================================================

    @staticmethod
    def get_all_genres() -> list:
        """
        Return all unique genres.

        Because genres are MongoDB arrays, distinct() automatically
        returns the individual genre values.
        """

        col = MovieController._collection()

        genres = col.distinct("genres")

        cleaned = {
            str(genre).strip()
            for genre in genres
            if genre and str(genre).strip()
        }

        return ["All"] + sorted(cleaned)

    # =========================================================
    # STATISTICS
    # =========================================================

    @staticmethod
    def count_movies() -> int:
        col = MovieController._collection()

        return col.count_documents({})

    @staticmethod
    def get_stats() -> dict:
        """
        Statistics used by the Admin Dashboard.
        """

        col = MovieController._collection()

        total_movies = col.count_documents({})

        genres = col.distinct("genres")

        total_genres = len([
            genre
            for genre in genres
            if genre
        ])

        avg_result = list(
            col.aggregate([
                {
                    "$match": {
                        "rating": {
                            "$ne": None
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "avg_rating": {
                            "$avg": "$rating"
                        }
                    }
                }
            ])
        )

        if avg_result:
            avg_rating = (
                avg_result[0].get("avg_rating") or 0.0
            )
        else:
            avg_rating = 0.0

        return {
            "total_movies": total_movies,
            "total_genres": total_genres,
            "avg_rating": round(avg_rating, 1)
        }

    # =========================================================
    # CREATE
    # =========================================================

    @staticmethod
    def add_movie(movie_data: dict) -> dict:

        print(
            f"Add Movie Clicked -> {movie_data}"
        )

        title = str(
            movie_data.get("title")
            or movie_data.get("name")
            or ""
        ).strip()

        if not title:
            raise MovieError(
                "Movie title is required."
            )

        year = _validate_year(
            movie_data.get("year"),
            required=True
        )

        rating = _validate_rating(
            movie_data.get("rating")
        )

        duration = _safe_optional_int(
            movie_data.get("duration")
        )

        metascore = _safe_optional_int(
            movie_data.get("metascore")
        )

        votes = _safe_optional_int(
            movie_data.get("votes")
            or movie_data.get("num_raters")
        )

        review_count = _safe_optional_int(
            movie_data.get("review_count")
            or movie_data.get("num_reviews")
        )

        genres = parse_genres(
            movie_data.get("genres")
            or movie_data.get("genre")
            or []
        )

        cast = _parse_list(
            movie_data.get("cast")
        )

        doc = {
            "title": title,
            "year": year,

            "certificate": str(
                movie_data.get("certificate")
                or movie_data.get("movie_rated")
                or ""
            ).strip(),

            "duration": duration,

            "genres": genres,

            "rating": rating,

            "metascore": metascore,

            "director": str(
                movie_data.get("director")
                or ""
            ).strip(),

            "cast": cast,

            "votes": votes,

            "description": str(
                movie_data.get("description")
                or ""
            ).strip(),

            "review_count": review_count,

            "review_title": str(
                movie_data.get("review_title")
                or ""
            ).strip(),

            "review": str(
                movie_data.get("review")
                or ""
            ).strip(),

            "poster_url": str(
                movie_data.get("poster_url")
                or ""
            ).strip()
        }

        col = MovieController._collection()

        result = col.insert_one(doc)

        doc["_id"] = result.inserted_id

        return Movie.from_doc(
            doc
        ).to_gui_dict()

    # =========================================================
    # UPDATE
    # =========================================================

    @staticmethod
    def update_movie(
        movie_id,
        updated_data: dict
    ) -> dict:

        print(
            "Update Movie Clicked -> "
            f"id={movie_id}, "
            f"data={updated_data}"
        )

        col = MovieController._collection()

        try:
            oid = ObjectId(movie_id)

        except (InvalidId, TypeError):
            raise MovieError(
                "Invalid movie ID."
            )

        existing = col.find_one({
            "_id": oid
        })

        if not existing:
            raise MovieError(
                "Movie not found."
            )

        # Start from existing values.
        # This prevents unspecified fields from being erased.
        set_doc = {}

        if "title" in updated_data or "name" in updated_data:

            title = str(
                updated_data.get("title")
                or updated_data.get("name")
                or ""
            ).strip()

            if not title:
                raise MovieError(
                    "Movie title is required."
                )

            set_doc["title"] = title

        if "year" in updated_data:

            set_doc["year"] = _validate_year(
                updated_data.get("year"),
                required=True
            )

        if (
            "certificate" in updated_data
            or "movie_rated" in updated_data
        ):

            set_doc["certificate"] = str(
                updated_data.get("certificate")
                or updated_data.get("movie_rated")
                or ""
            ).strip()

        if "duration" in updated_data:

            set_doc["duration"] = (
                _safe_optional_int(
                    updated_data.get("duration")
                )
            )

        if (
            "genres" in updated_data
            or "genre" in updated_data
        ):

            set_doc["genres"] = parse_genres(
                updated_data.get("genres")
                or updated_data.get("genre")
                or []
            )

        if "rating" in updated_data:

            set_doc["rating"] = (
                _validate_rating(
                    updated_data.get("rating")
                )
            )

        if "metascore" in updated_data:

            set_doc["metascore"] = (
                _safe_optional_int(
                    updated_data.get("metascore")
                )
            )

        if "director" in updated_data:

            set_doc["director"] = str(
                updated_data.get("director")
                or ""
            ).strip()

        if "cast" in updated_data:

            set_doc["cast"] = _parse_list(
                updated_data.get("cast")
            )

        if (
            "votes" in updated_data
            or "num_raters" in updated_data
        ):

            set_doc["votes"] = (
                _safe_optional_int(
                    updated_data.get("votes")
                    or updated_data.get(
                        "num_raters"
                    )
                )
            )

        if "description" in updated_data:

            set_doc["description"] = str(
                updated_data.get("description")
                or ""
            ).strip()

        if (
            "review_count" in updated_data
            or "num_reviews" in updated_data
        ):

            set_doc["review_count"] = (
                _safe_optional_int(
                    updated_data.get(
                        "review_count"
                    )
                    or updated_data.get(
                        "num_reviews"
                    )
                )
            )

        if "review_title" in updated_data:

            set_doc["review_title"] = str(
                updated_data.get(
                    "review_title"
                )
                or ""
            ).strip()

        if "review" in updated_data:

            set_doc["review"] = str(
                updated_data.get("review")
                or ""
            ).strip()

        if "poster_url" in updated_data:

            set_doc["poster_url"] = str(
                updated_data.get("poster_url")
                or ""
            ).strip()

        if not set_doc:
            raise MovieError(
                "No movie fields were provided."
            )

        col.update_one(
            {"_id": oid},
            {"$set": set_doc}
        )

        return MovieController.get_movie_by_id(
            movie_id
        )

    # =========================================================
    # DELETE
    # =========================================================

    @staticmethod
    def delete_movie(movie_id) -> bool:

        print(
            f"Delete Movie Clicked -> "
            f"id={movie_id}"
        )

        col = MovieController._collection()

        try:
            oid = ObjectId(movie_id)

        except (InvalidId, TypeError):
            raise MovieError(
                "Invalid movie ID."
            )

        result = col.delete_one({
            "_id": oid
        })

        if result.deleted_count == 0:
            raise MovieError(
                "Movie not found."
            )

        return True


# =============================================================
# VALIDATION HELPERS
# =============================================================

def _validate_year(
    value,
    required=False
):

    if value in (None, ""):

        if required:
            raise MovieError(
                "Release year is required."
            )

        return None

    try:
        year = int(float(value))

    except (TypeError, ValueError):
        raise MovieError(
            "Release year must be a whole number, "
            "for example 2010."
        )

    if year < 1888 or year > 2100:

        raise MovieError(
            "Please enter a realistic release year."
        )

    return year


def _validate_rating(value):

    if value in (None, ""):
        return None

    try:
        rating = float(value)

    except (TypeError, ValueError):
        raise MovieError(
            "Rating must be a number between "
            "0 and 10."
        )

    if rating < 0 or rating > 10:

        raise MovieError(
            "Rating must be between 0 and 10."
        )

    return round(rating, 1)


def _safe_optional_int(value):

    if value in (None, ""):
        return None

    try:
        return int(float(value))

    except (TypeError, ValueError):
        return None


def _parse_list(value):
    """
    Convert comma/semicolon-separated values into a list.
    Used mainly for cast.
    """

    if not value:
        return []

    if isinstance(value, list):

        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    text = str(value)

    separator = ";" if ";" in text else ","

    return [
        item.strip()
        for item in text.split(separator)
        if item.strip()
    ]