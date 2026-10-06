"""
views/movie_details_window.py
---------------------------------
Screen 5: Movie Details Window
Full-detail view for a single movie, showing every field from the
real dataset. The watchlist button toggles between "Add" and "Remove"
based on the current user's saved state.

AI Recommendation integration:
    - Opens the AI Recommendations Window
    - Uses the selected movie title as input
    - Gets recommendations from the TF-IDF + Cosine Similarity model
"""

import customtkinter as ctk

from config import Colors, Fonts
from frontend.widgets.custom_widgets import PrimaryButton, SecondaryButton
from frontend.widgets.rating_stars import RatingStars
from frontend.widgets.dialogs import show_error, show_success
from backend.utils.image_loader import get_poster_image
from backend.controllers.user_controller import UserController, UserError
from frontend.views.ai_recommendations_window import AIRecommendationsWindow


class MovieDetailsWindow(ctk.CTkFrame):

    def __init__(self, parent, controller, movie=None, user=None, **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.BACKGROUND,
            **kwargs
        )

        self.controller = controller
        self.movie = movie or {}
        self.user = user or {}

        self.in_watchlist = self._check_watchlist_state()

        # --------------------------------------------------
        # Top bar with Back button
        # --------------------------------------------------

        topbar = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        topbar.pack(
            fill="x",
            padx=32,
            pady=(24, 0)
        )

        SecondaryButton(
            topbar,
            text="← Back",
            width=100,
            height=36,
            command=self._go_back
        ).pack(anchor="w")

        # --------------------------------------------------
        # Content area
        # --------------------------------------------------

        content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        content.pack(
            fill="both",
            expand=True,
            padx=32,
            pady=24
        )

        # --------------------------------------------------
        # Poster
        # --------------------------------------------------

        poster_img = get_poster_image(
            self.movie.get("title", "Untitled"),
            width=300,
            height=440
        )

        ctk.CTkLabel(
            content,
            image=poster_img,
            text=""
        ).pack(
            side="left",
            padx=(0, 40),
            anchor="n"
        )

        # --------------------------------------------------
        # Details
        # --------------------------------------------------

        details = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )

        details.pack(
            side="left",
            fill="both",
            expand=True,
            anchor="n"
        )

        # Movie title
        ctk.CTkLabel(
            details,
            text=self.movie.get("title", "Untitled"),
            font=Fonts.H1,
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 6)
        )

        # Movie metadata
        ctk.CTkLabel(
            details,
            text=(
                f"{self.movie.get('movie_rated', 'NR')}"
                f"   •   "
                f"{self.movie.get('year', '—')}"
                f"   •   "
                f"{self.movie.get('run_length', '—')}"
            ),
            font=Fonts.BODY,
            text_color=Colors.TEXT_SECONDARY,
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 12)
        )

        # Rating
        RatingStars(
            details,
            rating=self.movie.get("rating", 0.0),
            scale_max=10,
            font_size=20
        ).pack(
            anchor="w",
            pady=(0, 6)
        )

        # Raters and reviews
        ctk.CTkLabel(
            details,
            text=(
                f"{self.movie.get('num_raters', 0):,} raters"
                f"   •   "
                f"{self.movie.get('num_reviews', 0):,} reviews"
            ),
            font=Fonts.SMALL,
            text_color=Colors.TEXT_MUTED,
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 16)
        )

        # --------------------------------------------------
        # Genre badges
        # --------------------------------------------------

        genre_row = ctk.CTkFrame(
            details,
            fg_color="transparent"
        )

        genre_row.pack(
            anchor="w",
            pady=(0, 20)
        )

        genre_list = (
            self.movie.get("genre_list")
            or (
                [self.movie.get("genre")]
                if self.movie.get("genre")
                else []
            )
        )

        for g in genre_list:

            ctk.CTkLabel(
                genre_row,
                text=f"  {g}  ",
                fg_color=Colors.SURFACE_LIGHT,
                text_color=Colors.SECONDARY,
                corner_radius=8,
                font=("Segoe UI", 12, "bold")
            ).pack(
                side="left",
                padx=(0, 6)
            )

        # --------------------------------------------------
        # Release Date
        # --------------------------------------------------

        ctk.CTkLabel(
            details,
            text="Release Date",
            font=Fonts.BODY_BOLD,
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        ).pack(
            fill="x"
        )

        ctk.CTkLabel(
            details,
            text=self.movie.get(
                "release_date",
                "Unknown"
            ),
            font=Fonts.BODY,
            text_color=Colors.TEXT_SECONDARY,
            anchor="w"
        ).pack(
            fill="x",
            pady=(0, 16)
        )

        # --------------------------------------------------
        # Overview
        # --------------------------------------------------

        ctk.CTkLabel(
            details,
            text="Overview",
            font=Fonts.BODY_BOLD,
            text_color=Colors.TEXT_PRIMARY,
            anchor="w"
        ).pack(
            fill="x"
        )

        ctk.CTkLabel(
            details,
            text=self.movie.get(
                "description",
                "No description available."
            ),
            font=Fonts.BODY,
            text_color=Colors.TEXT_SECONDARY,
            anchor="w",
            justify="left",
            wraplength=500
        ).pack(
            fill="x",
            pady=(0, 28)
        )

        # --------------------------------------------------
        # Action buttons
        # --------------------------------------------------

        actions = ctk.CTkFrame(
            details,
            fg_color="transparent"
        )

        actions.pack(
            fill="x",
            anchor="w"
        )

        # Watchlist button
        self.watchlist_btn = PrimaryButton(
            actions,
            text=self._watchlist_button_text(),
            width=220,
            command=self._toggle_watchlist
        )

        self.watchlist_btn.pack(
            side="left",
            padx=(0, 12)
        )

        # AI Recommendations button
        SecondaryButton(
            actions,
            text="🤖 AI Recommendations",
            width=220,
            command=self._show_ai_recommendations
        ).pack(
            side="left",
            padx=(0, 12)
        )

        # Back to Dashboard button
        SecondaryButton(
            actions,
            text="Back to Dashboard",
            width=200,
            command=self._go_back
        ).pack(
            side="left"
        )

    # ==================================================
    # WATCHLIST
    # ==================================================

    def _check_watchlist_state(self) -> bool:

        user_id = self.user.get("id")
        movie_id = self.movie.get("id")

        if not user_id or not movie_id:
            return False

        try:
            return UserController.is_in_watchlist(
                user_id,
                movie_id
            )

        except UserError:
            return False

    def _watchlist_button_text(self) -> str:

        if self.in_watchlist:
            return "✓ In Watchlist (Remove)"

        return "+ Add to Watchlist"

    def _toggle_watchlist(self):

        user_id = self.user.get("id")

        if not user_id:

            show_error(
                self,
                "Not Logged In",
                "Please log in to use the watchlist."
            )

            return

        try:

            if self.in_watchlist:

                UserController.remove_from_watchlist(
                    user_id,
                    self.movie["id"]
                )

                self.in_watchlist = False

                show_success(
                    self,
                    "Removed",
                    f"'{self.movie.get('title')}' "
                    "removed from your watchlist."
                )

            else:

                UserController.add_to_watchlist(
                    user_id,
                    self.movie["id"]
                )

                self.in_watchlist = True

                show_success(
                    self,
                    "Added",
                    f"'{self.movie.get('title')}' "
                    "added to your watchlist."
                )

        except UserError as e:

            show_error(
                self,
                "Watchlist Error",
                str(e)
            )

            return

        self.watchlist_btn.configure(
            text=self._watchlist_button_text()
        )

    # ==================================================
    # AI RECOMMENDATIONS
    # ==================================================

    def _show_ai_recommendations(self):

        self.controller.show_view(
            AIRecommendationsWindow,
            movie=self.movie,
            user=self.user
        )

    # ==================================================
    # BACK
    # ==================================================

    def _go_back(self):

        self.controller.go_back()