"""
backend/controllers/recommendation_controller.py
------------------------------------------------
Simple content-based recommendation system for CineVault.

Recommendation logic:

1. Read movies from the user's watchlist.
2. Count the genres appearing in those movies.
3. Use those genres as the user's preference profile.
4. Find highly-rated movies sharing those genres.
5. Exclude movies already in the watchlist.
6. Rank recommendations using genre preference + rating.

This approach is intentionally simple and explainable for the
DBMS Mini Project viva.
"""

from collections import Counter

from bson import ObjectId
from bson.errors import InvalidId

from backend.database.connection import (
    get_collection,
    DatabaseConnectionError
)

from backend.models.movie_model import Movie, parse_genres


class RecommendationError(Exception):
    """Raised when recommendation generation fails."""
    pass


class RecommendationController:

    MIN_RATING_FOR_RECOMMENDATION = 7.0

    # Limit the candidate pool so we don't process thousands
    # of movies in Python every time the dashboard opens.
    CANDIDATE_LIMIT = 300

    # =========================================================
    # COLLECTIONS
    # =========================================================

    @staticmethod
    def _movies_collection():

        try:
            return get_collection("movies")

        except DatabaseConnectionError as e:
            raise RecommendationError(str(e)) from e

    @staticmethod
    def _users_collection():

        try:
            return get_collection("users")

        except DatabaseConnectionError as e:
            raise RecommendationError(str(e)) from e

    # =========================================================
    # RECOMMENDATIONS
    # =========================================================

    @staticmethod
    def get_recommendations(
        user_id,
        limit: int = 12
    ) -> list:

        movies_col = (
            RecommendationController._movies_collection()
        )

        users_col = (
            RecommendationController._users_collection()
        )

        # -----------------------------------------------------
        # Validate user ID
        # -----------------------------------------------------

        try:
            user_oid = ObjectId(user_id)

        except (InvalidId, TypeError):
            raise RecommendationError(
                "Invalid user ID."
            )

        user_doc = users_col.find_one({
            "_id": user_oid
        })

        if not user_doc:
            raise RecommendationError(
                "User not found."
            )

        watchlist_ids = user_doc.get(
            "watchlist",
            []
        )

        # -----------------------------------------------------
        # Empty watchlist
        # -----------------------------------------------------

        if not watchlist_ids:

            return (
                RecommendationController
                ._get_top_rated(
                    movies_col,
                    limit
                )
            )

        # -----------------------------------------------------
        # Convert watchlist IDs safely
        # -----------------------------------------------------

        watchlist_object_ids = []

        for movie_id in watchlist_ids:

            try:

                if isinstance(movie_id, ObjectId):
                    oid = movie_id

                else:
                    oid = ObjectId(movie_id)

                watchlist_object_ids.append(
                    oid
                )

            except (InvalidId, TypeError):
                continue

        if not watchlist_object_ids:

            return (
                RecommendationController
                ._get_top_rated(
                    movies_col,
                    limit
                )
            )

        # -----------------------------------------------------
        # Build genre preference profile
        # -----------------------------------------------------

        watchlist_docs = movies_col.find(
            {
                "_id": {
                    "$in": watchlist_object_ids
                }
            },
            {
                "genres": 1
            }
        )

        genre_counter = Counter()

        for doc in watchlist_docs:

            genres = parse_genres(
                doc.get("genres", [])
            )

            for genre in genres:
                genre_counter[genre] += 1

        # If watchlist movies disappeared after dataset replacement,
        # there may be no valid genres.
        if not genre_counter:

            return (
                RecommendationController
                ._get_top_rated(
                    movies_col,
                    limit
                )
            )

        favorite_genres = list(
            genre_counter.keys()
        )

        # -----------------------------------------------------
        # Candidate query
        # -----------------------------------------------------
        #
        # MongoDB now stores:
        #
        # genres: ["Action", "Sci-Fi"]
        #
        # $in therefore finds movies containing at least one
        # preferred genre.

        candidate_query = {

            "_id": {
                "$nin": watchlist_object_ids
            },

            "genres": {
                "$in": favorite_genres
            },

            "rating": {
                "$gte":
                RecommendationController
                .MIN_RATING_FOR_RECOMMENDATION
            }
        }

        # First let MongoDB reduce the candidate pool.
        # Then Python performs the personalized scoring.

        candidates = (
            movies_col
            .find(candidate_query)
            .sort([
                ("rating", -1),
                ("votes", -1)
            ])
            .limit(
                RecommendationController
                .CANDIDATE_LIMIT
            )
        )

        # -----------------------------------------------------
        # Score candidates
        # -----------------------------------------------------

        scored_movies = []

        for doc in candidates:

            movie_genres = set(
                parse_genres(
                    doc.get("genres", [])
                )
            )

            genre_score = sum(
                genre_counter[genre]
                for genre in movie_genres
                if genre in genre_counter
            )

            if genre_score <= 0:
                continue

            try:
                rating = float(
                    doc.get("rating") or 0
                )

            except (TypeError, ValueError):
                rating = 0.0

            try:
                votes = int(
                    doc.get("votes") or 0
                )

            except (TypeError, ValueError):
                votes = 0

            scored_movies.append(
                (
                    genre_score,
                    rating,
                    votes,
                    doc
                )
            )

        # Highest genre preference first.
        # Rating and votes act as tie-breakers.

        scored_movies.sort(
            key=lambda item: (
                item[0],
                item[1],
                item[2]
            ),
            reverse=True
        )

        top_docs = [
            item[3]
            for item in scored_movies[:limit]
        ]

        # -----------------------------------------------------
        # Fill remaining spaces
        # -----------------------------------------------------

        if len(top_docs) < limit:

            seen_ids = (
                {doc["_id"] for doc in top_docs}
                | set(watchlist_object_ids)
            )

            remaining = (
                limit - len(top_docs)
            )

            extra_cursor = (
                movies_col
                .find({
                    "_id": {
                        "$nin": list(
                            seen_ids
                        )
                    },
                    "rating": {
                        "$ne": None
                    }
                })
                .sort([
                    ("rating", -1),
                    ("votes", -1)
                ])
                .limit(remaining)
            )

            top_docs.extend(
                list(extra_cursor)
            )

        return [
            Movie.from_doc(doc).to_gui_dict()
            for doc in top_docs
        ]

    # =========================================================
    # TOP-RATED FALLBACK
    # =========================================================

    @staticmethod
    def _get_top_rated(
        movies_col,
        limit
    ):

        cursor = (
            movies_col
            .find({
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
    # EXPLAIN USER PROFILE
    # =========================================================

    @staticmethod
    def explain_profile(
        user_id
    ) -> list:
        """
        Return the user's top three genres.

        Example:
            ["Action", "Sci-Fi", "Thriller"]

        The GUI can display:
            Because you like Action, Sci-Fi and Thriller
        """

        users_col = (
            RecommendationController
            ._users_collection()
        )

        movies_col = (
            RecommendationController
            ._movies_collection()
        )

        try:
            user_oid = ObjectId(user_id)

        except (InvalidId, TypeError):
            return []

        user_doc = users_col.find_one({
            "_id": user_oid
        })

        if (
            not user_doc
            or not user_doc.get("watchlist")
        ):
            return []

        object_ids = []

        for movie_id in user_doc["watchlist"]:

            try:

                if isinstance(
                    movie_id,
                    ObjectId
                ):
                    oid = movie_id

                else:
                    oid = ObjectId(
                        movie_id
                    )

                object_ids.append(oid)

            except (InvalidId, TypeError):
                continue

        if not object_ids:
            return []

        genre_counter = Counter()

        cursor = movies_col.find(
            {
                "_id": {
                    "$in": object_ids
                }
            },
            {
                "genres": 1
            }
        )

        for doc in cursor:

            genres = parse_genres(
                doc.get("genres", [])
            )

            for genre in genres:
                genre_counter[genre] += 1

        return [
            genre
            for genre, _
            in genre_counter.most_common(3)
        ]