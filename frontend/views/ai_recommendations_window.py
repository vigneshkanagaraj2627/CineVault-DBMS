"""
views/ai_recommendations_window.py
-----------------------------------
AI-powered movie recommendations using the TF-IDF
recommendation model from backend.recommendation_model.
"""

import customtkinter as ctk

from config import Colors, Fonts
from frontend.widgets.movie_card import MovieCard
from frontend.widgets.custom_widgets import SectionHeader
from frontend.widgets.dialogs import show_error
from backend.recommendation_model import recommend_movies


class AIRecommendationsWindow(ctk.CTkFrame):

    def __init__(self, parent, controller, movie=None, user=None, **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.BACKGROUND,
            **kwargs
        )

        self.controller = controller
        self.movie = movie or {}
        self.user = user or {}

        movie_title = self.movie.get("title", "Unknown Movie")

        # --------------------------------------------------
        # Header
        # --------------------------------------------------

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=32,
            pady=(28, 10)
        )

        SectionHeader(
            header,
            title="🤖 AI Recommendations",
            subtitle=f'Movies similar to "{movie_title}"'
        ).pack(fill="x")

        # --------------------------------------------------
        # Back button
        # --------------------------------------------------

        ctk.CTkButton(
            self,
            text="← Back to Movie",
            width=140,
            height=36,
            corner_radius=8,
            fg_color=Colors.SURFACE_LIGHT,
            hover_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            command=self._go_back
        ).pack(
            anchor="w",
            padx=32,
            pady=(0, 12)
        )

        # --------------------------------------------------
        # Scrollable movie grid
        # --------------------------------------------------

        self.grid_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Colors.SURFACE_LIGHT
        )

        self.grid_scroll.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=(0, 20)
        )

        # --------------------------------------------------
        # Load AI recommendations
        # --------------------------------------------------

        self._load_recommendations()

    # ======================================================
    # LOAD AI RECOMMENDATIONS
    # ======================================================

    def _load_recommendations(self):

        movie_title = self.movie.get("title")

        if not movie_title:

            show_error(
                self,
                "Recommendation Error",
                "Movie title is missing."
            )

            return

        try:

            recommendations = recommend_movies(
                movie_title,
                n=10
            )

        except Exception as e:

            show_error(
                self,
                "AI Recommendation Error",
                str(e)
            )

            return

        # --------------------------------------------------
        # No recommendations
        # --------------------------------------------------

        if not recommendations:

            ctk.CTkLabel(
                self.grid_scroll,
                text="No AI recommendations found.",
                text_color=Colors.TEXT_MUTED,
                font=Fonts.BODY
            ).grid(
                row=0,
                column=0,
                pady=40
            )

            return

        # --------------------------------------------------
        # Convert MongoDB documents into GUI format
        # --------------------------------------------------

        self.movies = [
            self._convert_movie(movie)
            for movie in recommendations
        ]

        self._render_grid()

    # ======================================================
    # CONVERT MONGODB MOVIE TO CINEVAULT GUI FORMAT
    # ======================================================

    def _convert_movie(self, movie):

        # --------------------------------------------------
        # Genres
        # --------------------------------------------------

        genres = movie.get("genres", [])

        if isinstance(genres, list):

            genre = (
                genres[0]
                if genres
                else "Unknown"
            )

            genre_list = genres

        else:

            genre = (
                str(genres)
                if genres
                else "Unknown"
            )

            genre_list = [genre]

        # --------------------------------------------------
        # Movie ID
        # --------------------------------------------------

        movie_id = movie.get("id")

        if movie_id is None:
            movie_id = movie.get("_id")

        # --------------------------------------------------
        # Rating
        # --------------------------------------------------

        rating = movie.get("rating")

        # Fix None rating
        if rating is None:

            rating = 0.0

        else:

            try:

                rating = float(rating)

            except (TypeError, ValueError):

                rating = 0.0

        # --------------------------------------------------
        # Year
        # --------------------------------------------------

        year = movie.get("year")

        if year is None:
            year = "—"

        # --------------------------------------------------
        # Return CineVault GUI movie format
        # --------------------------------------------------

        return {
            "id": movie_id,

            "title": (
                movie.get("title")
                or "Unknown"
            ),

            "genre": genre,

            "genre_list": genre_list,

            "year": year,

            "rating": rating,

            "description": (
                movie.get("description")
                or "No description available."
            ),

            "poster_url": (
                movie.get("poster_url")
                or ""
            ),

            "movie_rated": (
                movie.get("movie_rated")
                or "NR"
            ),

            "run_length": (
                movie.get("run_length")
                or "—"
            ),

            "release_date": (
                movie.get("release_date")
                or "Unknown"
            ),

            "num_raters": (
                movie.get("num_raters")
                or 0
            ),

            "num_reviews": (
                movie.get("num_reviews")
                or 0
            ),
        }

    # ======================================================
    # RENDER MOVIE GRID
    # ======================================================

    def _render_grid(self, columns=4):

        # Remove previous cards

        for child in self.grid_scroll.winfo_children():
            child.destroy()

        # Configure columns

        for col in range(columns):

            self.grid_scroll.grid_columnconfigure(
                col,
                weight=1
            )

        # --------------------------------------------------
        # Create movie cards
        # --------------------------------------------------

        for index, movie in enumerate(self.movies):

            row, col = divmod(
                index,
                columns
            )

            card = MovieCard(
                self.grid_scroll,
                movie,
                on_view=self._open_details,
                on_watchlist=None
            )

            card.grid(
                row=row,
                column=col,
                padx=10,
                pady=10,
                sticky="n"
            )

    # ======================================================
    # OPEN MOVIE DETAILS
    # ======================================================

    def _open_details(self, movie):

        from frontend.views.movie_details_window import MovieDetailsWindow

        self.controller.show_view(
            MovieDetailsWindow,
            movie=movie,
            user=self.user
        )

    # ======================================================
    # BACK TO MOVIE
    # ======================================================

    def _go_back(self):

        self.controller.go_back()