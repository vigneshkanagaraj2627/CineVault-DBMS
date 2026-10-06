"""
backend/ai/data_preparation.py
--------------------------------

Member 1 - AI Data Preparation

This module prepares CineVault movie data for the
AI recommendation system.

It reads the existing movies collection from MongoDB
and creates a clean feature representation for each movie.

Important:
    - This module DOES NOT modify MongoDB.
    - It only reads existing movie data.
    - The prepared data will be used by Member 2
      to build the TF-IDF + Cosine Similarity model.

Main AI fields:
    - genres
    - director
    - cast
    - description
"""

from backend.database.connection import get_collection
from backend.models.movie_model import parse_list


# --------------------------------------------------
# Text Cleaning
# --------------------------------------------------

def clean_text(value):
    """
    Convert a value into clean lowercase text.

    Examples:

        "Christopher Nolan"
        -> "christopher nolan"

        None
        -> ""

        ["Action", "Drama"]
        -> "action drama"
    """

    if value is None:
        return ""

    # Handle lists such as genres and cast
    if isinstance(value, list):
        value = " ".join(
            str(item).strip()
            for item in value
            if item is not None and str(item).strip()
        )

    value = str(value).strip().lower()

    # Replace repeated spaces
    value = " ".join(value.split())

    return value


# --------------------------------------------------
# Prepare Genres
# --------------------------------------------------

def prepare_genres(genres):
    """
    Convert movie genres into clean text.

    Example:

        ["Action", "Adventure", "Sci-Fi"]

    becomes:

        "action adventure sci-fi"
    """

    genre_list = parse_list(genres)

    return clean_text(genre_list)


# --------------------------------------------------
# Prepare Cast
# --------------------------------------------------

def prepare_cast(cast):
    """
    Convert movie cast into clean text.

    Example:

        ["Tom Hanks", "Robin Wright"]

    becomes:

        "tom hanks robin wright"
    """

    cast_list = parse_list(cast)

    return clean_text(cast_list)


# --------------------------------------------------
# Prepare Single Movie
# --------------------------------------------------

def prepare_movie(movie):
    """
    Prepare one MongoDB movie document for AI processing.

    Returns a dictionary containing:

        movie_id
        title
        genres
        director
        cast
        description
        combined_features

    The 'combined_features' field is the main field that
    Member 2 will use for TF-IDF.
    """

    if not movie:
        return None

    movie_id = movie.get("_id")

    title = clean_text(movie.get("title", ""))

    genres = prepare_genres(
        movie.get("genres", [])
    )

    director = clean_text(
        movie.get("director", "")
    )

    cast = prepare_cast(
        movie.get("cast", [])
    )

    description = clean_text(
        movie.get("description", "")
    )

    # ----------------------------------------------
    # Combine important AI features
    # ----------------------------------------------

    combined_features = " ".join(
        part
        for part in [
            genres,
            director,
            cast,
            description
        ]
        if part
    )

    return {
        "movie_id": str(movie_id) if movie_id is not None else "",
        "title": movie.get("title", "Untitled"),
        "genres": genres,
        "director": director,
        "cast": cast,
        "description": description,
        "combined_features": combined_features
    }


# --------------------------------------------------
# Get Movies From MongoDB
# --------------------------------------------------

def get_movies_from_database():
    """
    Read all movies from the existing MongoDB movies collection.

    Returns:
        list[dict]

    No data is inserted, updated, or deleted.
    """

    collection = get_collection("movies")

    movies = list(
        collection.find({})
    )

    return movies


# --------------------------------------------------
# Prepare All Movies
# --------------------------------------------------

def prepare_movie_dataset():
    """
    Read all movies from MongoDB and prepare them
    for the AI recommendation model.

    Movies without a title or useful features are skipped.
    """

    movies = get_movies_from_database()

    prepared_movies = []

    for movie in movies:

        prepared_movie = prepare_movie(movie)

        if prepared_movie is None:
            continue

        # Movie must have a title
        if not prepared_movie["title"]:
            continue

        # Movie should have at least one AI feature
        if not prepared_movie["combined_features"]:
            continue

        prepared_movies.append(
            prepared_movie
        )

    return prepared_movies


# --------------------------------------------------
# Get Feature Text
# --------------------------------------------------

def get_feature_texts(prepared_movies):
    """
    Extract combined feature text from prepared movies.

    This list is directly useful for TF-IDF.

    Example:

        [
            "action adventure christopher nolan ...",
            "comedy drama tom hanks ..."
        ]
    """

    return [
        movie["combined_features"]
        for movie in prepared_movies
    ]


# --------------------------------------------------
# Display Dataset Information
# --------------------------------------------------

def print_dataset_summary(prepared_movies):
    """
    Print a simple summary for testing.

    Useful for Member 1 to verify that the data
    preparation is working correctly.
    """

    print("\n" + "=" * 60)
    print("CINEVAULT AI DATA PREPARATION")
    print("=" * 60)

    print(
        f"Total prepared movies: {len(prepared_movies)}"
    )

    print("-" * 60)

    for index, movie in enumerate(
        prepared_movies[:5],
        start=1
    ):

        print(f"\nMovie {index}")
        print(f"Title: {movie['title']}")
        print(f"Genres: {movie['genres']}")
        print(f"Director: {movie['director']}")
        print(f"Cast: {movie['cast']}")
        print(
            f"Description: "
            f"{movie['description'][:150]}"
        )
        print(
            f"Combined Features: "
            f"{movie['combined_features'][:250]}"
        )

    print("\n" + "=" * 60)


# --------------------------------------------------
# Test / Run Directly
# --------------------------------------------------

if __name__ == "__main__":

    print("Loading movies from MongoDB...")

    try:

        prepared_movies = prepare_movie_dataset()

        print_dataset_summary(
            prepared_movies
        )

    except Exception as error:

        print("\nError while preparing movie data:")
        print(error)