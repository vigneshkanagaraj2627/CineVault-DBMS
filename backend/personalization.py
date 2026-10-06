"""
CineVault - Personalized Movie Recommendation
Member 3: Personalization Logic

This module creates a user preference profile from existing
CineVault user activity and passes that information to the
recommendation system.

It does NOT modify the MongoDB database.
"""

from collections import Counter


class PersonalizationEngine:
    """
    Handles user preference extraction and personalization.

    Expected movie format:

    {
        "title": "Interstellar",
        "genre": ["Sci-Fi", "Drama"],
        "rating": 5
    }

    The exact field names can be adjusted to match CineVault.
    """

    def __init__(self):
        self.user_profile = {}

    # ---------------------------------------------------------
    # 1. Create user preference profile
    # ---------------------------------------------------------

    def create_user_profile(
        self,
        favorite_genres=None,
        rated_movies=None,
        watchlist=None,
        selected_movies=None
    ):
        """
        Creates a preference profile for the current user.

        Parameters:
            favorite_genres: genres explicitly selected by user
            rated_movies: movies rated by the user
            watchlist: movies added to watchlist
            selected_movies: movies the user has viewed/selected

        Returns:
            Dictionary containing the user's preferences.
        """

        favorite_genres = favorite_genres or []
        rated_movies = rated_movies or []
        watchlist = watchlist or []
        selected_movies = selected_movies or []

        # Find genres from highly rated movies
        rated_genres = self._extract_rated_genres(rated_movies)

        # Find genres from watchlist
        watchlist_genres = self._extract_movie_genres(watchlist)

        # Combine all genre signals
        all_genres = (
            favorite_genres
            + rated_genres
            + watchlist_genres
        )

        genre_preferences = self._calculate_genre_preferences(
            all_genres
        )

        # Store profile
        self.user_profile = {
            "favorite_genres": list(
                dict.fromkeys(favorite_genres)
            ),
            "genre_preferences": genre_preferences,
            "rated_movies": rated_movies,
            "watchlist": watchlist,
            "selected_movies": selected_movies
        }

        return self.user_profile

    # ---------------------------------------------------------
    # 2. Extract genres from highly rated movies
    # ---------------------------------------------------------

    def _extract_rated_genres(self, rated_movies):
        """
        Extract genres only from movies that the user rated
        positively.

        Ratings:
            5 -> Very strong preference
            4 -> Strong preference
            3 -> Neutral
            1-2 -> Weak/negative preference
        """

        genres = []

        for movie in rated_movies:

            rating = movie.get("rating", 0)

            if rating >= 4:

                movie_genres = movie.get("genre", [])

                if isinstance(movie_genres, str):
                    movie_genres = movie_genres.split(",")

                for genre in movie_genres:
                    genre = genre.strip()

                    if genre:
                        genres.append(genre)

        return genres

    # ---------------------------------------------------------
    # 3. Extract genres from watchlist
    # ---------------------------------------------------------

    def _extract_movie_genres(self, movies):
        """
        Extract genres from movies in the user's watchlist.
        """

        genres = []

        for movie in movies:

            movie_genres = movie.get("genre", [])

            if isinstance(movie_genres, str):
                movie_genres = movie_genres.split(",")

            for genre in movie_genres:

                genre = genre.strip()

                if genre:
                    genres.append(genre)

        return genres

    # ---------------------------------------------------------
    # 4. Calculate genre preference strength
    # ---------------------------------------------------------

    def _calculate_genre_preferences(self, genres):
        """
        Counts how frequently each genre appears.

        Example:

            Sci-Fi: 5
            Drama: 3
            Action: 2
        """

        counter = Counter(genres)

        return dict(
            sorted(
                counter.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )

    # ---------------------------------------------------------
    # 5. Get top preferred genres
    # ---------------------------------------------------------

    def get_top_genres(self, limit=5):
        """
        Returns the user's strongest genre preferences.
        """

        preferences = self.user_profile.get(
            "genre_preferences",
            {}
        )

        return list(preferences.keys())[:limit]

    # ---------------------------------------------------------
    # 6. Check whether a movie matches user preferences
    # ---------------------------------------------------------

    def movie_matches_preferences(self, movie):
        """
        Calculates a simple personalization score for a movie.

        Higher score = better match with user's preferences.
        """

        movie_genres = movie.get("genre", [])

        if isinstance(movie_genres, str):
            movie_genres = movie_genres.split(",")

        movie_genres = [
            genre.strip().lower()
            for genre in movie_genres
        ]

        preferences = self.user_profile.get(
            "genre_preferences",
            {}
        )

        score = 0

        for genre, weight in preferences.items():

            if genre.lower() in movie_genres:
                score += weight

        return score

    # ---------------------------------------------------------
    # 7. Personalize movie list
    # ---------------------------------------------------------

    def personalize_movies(self, movies, limit=10):
        """
        Sorts movies according to the user's preferences.

        This can be used as an additional personalization
        layer on top of the AI recommendation model.
        """

        scored_movies = []

        for movie in movies:

            score = self.movie_matches_preferences(movie)

            scored_movies.append(
                (score, movie)
            )

        # Highest preference score first
        scored_movies.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return [
            movie
            for score, movie in scored_movies[:limit]
        ]

    # ---------------------------------------------------------
    # 8. Return profile for AI recommendation model
    # ---------------------------------------------------------

    def get_ai_profile(self):
        """
        Returns only the information needed by the
        recommendation model.
        """

        return {
            "favorite_genres": self.user_profile.get(
                "favorite_genres",
                []
            ),

            "top_genres": self.get_top_genres(),

            "rated_movies": self.user_profile.get(
                "rated_movies",
                []
            ),

            "watchlist": self.user_profile.get(
                "watchlist",
                []
            ),

            "selected_movies": self.user_profile.get(
                "selected_movies",
                []
            )
        }


# =============================================================
# Example usage
# =============================================================

if __name__ == "__main__":

    # Example data coming from the existing CineVault system.
    # In the real project, this data should come from MongoDB
    # using your existing database functions.

    rated_movies = [
        {
            "title": "Interstellar",
            "genre": ["Sci-Fi", "Drama"],
            "rating": 5
        },
        {
            "title": "Inception",
            "genre": ["Sci-Fi", "Thriller"],
            "rating": 5
        },
        {
            "title": "The Martian",
            "genre": ["Sci-Fi", "Drama"],
            "rating": 4
        }
    ]

    watchlist = [
        {
            "title": "Arrival",
            "genre": ["Sci-Fi", "Drama"]
        },
        {
            "title": "Gravity",
            "genre": ["Sci-Fi", "Thriller"]
        }
    ]

    favorite_genres = ["Sci-Fi"]

    engine = PersonalizationEngine()

    profile = engine.create_user_profile(
        favorite_genres=favorite_genres,
        rated_movies=rated_movies,
        watchlist=watchlist
    )

    print("\nUSER PREFERENCE PROFILE")
    print("-----------------------")

    print("Top Genres:")
    print(engine.get_top_genres())

    print("\nAI Profile:")
    print(engine.get_ai_profile())
