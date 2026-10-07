"""
backend/recommendation_model.py
--------------------------------
Content-Based Movie Recommendation Model for CineVault.

Uses:
    - MongoDB
    - TF-IDF Vectorization
    - Cosine Similarity

Movie features:
    - Genres
    - Director
    - Cast
    - Description
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.database.connection import get_collection


class MovieRecommendationModel:

    def __init__(self):
        self.movies = []
        self.movie_vectors = None
        self.similarity_matrix = None

        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

    # --------------------------------------------------
    # 1. LOAD MOVIES FROM MONGODB
    # --------------------------------------------------

    def load_movies(self):
        """Load movies from the CineVault MongoDB collection."""

        collection = get_collection("movies")

        self.movies = list(
            collection.find(
                {},
                {
                    "_id": 1,
                    "title": 1,
                    "genres": 1,
                    "director": 1,
                    "cast": 1,
                    "description": 1,
                    "year": 1,
                    "rating": 1,
                    "poster_url": 1
                }
            )
        )

        return self.movies

    # --------------------------------------------------
    # 2. PREPARE MOVIE TEXT
    # --------------------------------------------------

    def _movie_text(self, movie):
        """
        Combine important movie features into one text string.
        """

        genres = movie.get("genres", [])
        cast = movie.get("cast", [])

        # Convert genres into text
        if isinstance(genres, list):
            genres = " ".join(
                str(item) for item in genres
            )
        else:
            genres = str(genres)

        # Convert cast into text
        if isinstance(cast, list):
            cast = " ".join(
                str(item) for item in cast
            )
        else:
            cast = str(cast)

        director = str(
            movie.get("director", "") or ""
        )

        description = str(
            movie.get("description", "") or ""
        )

        # Combine all recommendation features
        combined_text = " ".join([
            genres,
            director,
            cast,
            description
        ])

        return combined_text

    # --------------------------------------------------
    # 3. BUILD TF-IDF + COSINE SIMILARITY MODEL
    # --------------------------------------------------

    def build_model(self):
        """Build the TF-IDF vectors and similarity matrix."""

        if not self.movies:
            self.load_movies()

        if not self.movies:
            raise ValueError(
                "No movies found in MongoDB."
            )

        movie_texts = [
            self._movie_text(movie)
            for movie in self.movies
        ]

        # Convert movie text into TF-IDF vectors
        self.movie_vectors = (
            self.vectorizer.fit_transform(movie_texts)
        )

        # Calculate movie-to-movie similarity
        self.similarity_matrix = cosine_similarity(
            self.movie_vectors
        )

        return self.similarity_matrix

    # --------------------------------------------------
    # 4. RECOMMEND MOVIES
    # --------------------------------------------------

    def recommend_movies(self, movie_title, n=10):
        """
        Recommend movies similar to a given movie.

        Parameters:
            movie_title: Title of the input movie.
            n: Number of recommendations.

        Returns:
            List of recommended movie documents.
        """

        # Build model if it hasn't been built yet
        if self.similarity_matrix is None:
            self.build_model()

        movie_title = str(
            movie_title
        ).strip().lower()

        movie_index = None

        # Find the requested movie
        for index, movie in enumerate(self.movies):

            title = str(
                movie.get("title", "")
            ).strip().lower()

            if title == movie_title:
                movie_index = index
                break

        # Movie not found
        if movie_index is None:
            return []

        # Get similarity scores
        similarity_scores = list(
            enumerate(
                self.similarity_matrix[movie_index]
            )
        )

        # Highest similarity first
        similarity_scores.sort(
            key=lambda x: x[1],
            reverse=True
        )

        recommendations = []

        for index, score in similarity_scores:

            # Don't recommend the same movie
            if index == movie_index:
                continue

            movie = self.movies[index].copy()

            movie["similarity_score"] = round(
                float(score),
                4
            )

            recommendations.append(movie)

            if len(recommendations) >= n:
                break

        return recommendations


# --------------------------------------------------
# REUSABLE MODEL INSTANCE
# --------------------------------------------------

_recommendation_model = None


def recommend_movies(movie_title, n=10):
    """
    Public function that other CineVault modules can use.

    Example:

        recommendations = recommend_movies("Leo", 5)
    """

    global _recommendation_model

    if _recommendation_model is None:
        _recommendation_model = (
            MovieRecommendationModel()
        )

    return _recommendation_model.recommend_movies(
        movie_title,
        n
    )