"""
backend/models/movie_model.py
-----------------------------
Movie model for the FINAL CineVault MongoDB dataset.

Final MongoDB movie schema:

    title
    year
    certificate
    duration
    genres
    rating
    metascore
    director
    cast
    votes
    description
    review_count
    review_title
    review
    poster_url

The model converts MongoDB movie documents into a consistent
format used by the CustomTkinter frontend.
"""


class Movie:

    def __init__(
        self,
        id=None,
        title="Untitled",
        year=None,
        certificate="",
        duration=None,
        genres=None,
        rating=None,
        metascore=None,
        director="",
        cast=None,
        votes=None,
        description="",
        review_count=None,
        review_title="",
        review="",
        poster_url=""
    ):

        self.id = id

        # Always keep title as text.
        # This also prevents the previous:
        # TypeError: 'int' object is not iterable
        self.title = str(title).strip() if title is not None else "Untitled"

        self.year = year
        self.certificate = certificate or ""
        self.duration = duration

        self.genres = parse_list(genres)

        self.rating = _safe_float(rating)
        self.metascore = _safe_int(metascore)

        self.director = director or ""

        self.cast = parse_list(cast)

        self.votes = _safe_int(votes)

        self.description = description or ""

        self.review_count = _safe_int(review_count)
        self.review_title = review_title or ""
        self.review = review or ""

        self.poster_url = poster_url or ""

    # --------------------------------------------------
    # MongoDB -> Movie Object
    # --------------------------------------------------

    @classmethod
    def from_doc(cls, doc: dict):
        """Create a Movie object from a MongoDB document."""

        if not doc:
            return None

        return cls(
            id=doc.get("_id"),

            title=doc.get("title", "Untitled"),

            year=doc.get("year"),

            certificate=doc.get("certificate", ""),

            duration=doc.get("duration"),

            genres=doc.get("genres", []),

            rating=doc.get("rating"),

            metascore=doc.get("metascore"),

            director=doc.get("director", ""),

            cast=doc.get("cast", []),

            votes=doc.get("votes"),

            description=doc.get("description", ""),

            review_count=doc.get("review_count"),

            review_title=doc.get("review_title", ""),

            review=doc.get("review", ""),

            poster_url=doc.get("poster_url", "")
        )

    # --------------------------------------------------
    # Movie Object -> MongoDB
    # --------------------------------------------------

    def to_doc(self) -> dict:
        """
        Convert the Movie object into a dictionary suitable
        for MongoDB insert/update operations.
        """

        return {
            "title": self.title,
            "year": self.year,
            "certificate": self.certificate,
            "duration": self.duration,
            "genres": self.genres,
            "rating": self.rating,
            "metascore": self.metascore,
            "director": self.director,
            "cast": self.cast,
            "votes": self.votes,
            "description": self.description,
            "review_count": self.review_count,
            "review_title": self.review_title,
            "review": self.review,
            "poster_url": self.poster_url
        }

    # --------------------------------------------------
    # GUI Compatibility
    # --------------------------------------------------

    def genre_list(self):
        """Return movie genres as a clean Python list."""
        return self.genres

    def to_gui_dict(self) -> dict:
        """
        Convert the movie into the structure expected by
        CineVault's CustomTkinter frontend.
        """

        return {

            "id": str(self.id) if self.id is not None else None,

            "title": self.title,

            # Keep name temporarily for compatibility with any
            # old frontend code that may still reference "name".
            "name": self.title,

            "year": self.year if self.year is not None else "—",

            "certificate": self.certificate or "NR",

            # Compatibility with old GUI
            "movie_rated": self.certificate or "NR",

            "duration": (
                f"{self.duration} min"
                if self.duration is not None
                else "—"
            ),

            "genres": self.genres,

            "genre_list": self.genres,

            "genre": (
                self.genres[0]
                if self.genres
                else "Unknown"
            ),

            "rating": self.rating,

            "metascore": self.metascore,

            "director": self.director or "—",

            "cast": self.cast,

            "votes": self.votes,

            # Compatibility with old GUI
            "num_raters": self.votes,

            "description": (
                self.description
                if self.description
                else "No description available."
            ),

            "review_count": self.review_count,

            # Compatibility with old GUI
            "num_reviews": self.review_count,

            "review_title": self.review_title,

            "review": self.review,

            "poster_url": self.poster_url
        }

    def __repr__(self):
        return f"<Movie {self.title!r} ({self.year})>"


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def parse_list(value):
    """
    Convert genres/cast into a clean Python list.

    Supports:
        ["Action", "Drama"]

    and:

        "Action, Drama"

    and older data such as:

        "Action; Drama;"
    """

    if value is None:
        return []

    if isinstance(value, list):

        return [
            str(item).strip()
            for item in value
            if item is not None and str(item).strip()
        ]

    value = str(value).strip()

    if not value:
        return []

    # Support old semicolon format
    if ";" in value:
        parts = value.split(";")
    else:
        parts = value.split(",")

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def parse_genres(value):
    """
    Compatibility helper for existing controllers.

    Older CineVault code may still import parse_genres()
    from this module.
    """
    return parse_list(value)


def _safe_float(value, default=0.0):
    """Safely convert a value to float."""

    if value is None or value == "":
        return default

    try:
        return float(value)

    except (TypeError, ValueError):
        return default


def _safe_int(value, default=0):
    """Safely convert a value to integer."""

    if value is None or value == "":
        return default

    try:
        return int(float(value))

    except (TypeError, ValueError):
        return default