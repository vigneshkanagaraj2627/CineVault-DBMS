"""
views/update_movie_window.py
---------------------------------
Screen 13: Update Movie Window
Admin form pre-filled with an existing movie's real MongoDB
details. Submission validates and persists changes via
MovieController.update_movie().
"""

import customtkinter as ctk
from config import Colors, Fonts
from frontend.widgets.sidebar import Sidebar
from frontend.widgets.custom_widgets import SectionHeader, Card, LabeledEntry, GoldButton, SecondaryButton
from frontend.widgets.dialogs import show_error, show_success
from backend.utils.image_loader import get_poster_image
from backend.utils.nav_config import build_admin_nav_items
from backend.controllers.movie_controller import MovieController, MovieError


class UpdateMovieWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, movie=None, user=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller
        self.user = user or {}
        self.movie = movie or {}

        nav_items = build_admin_nav_items(self.user)
        Sidebar(self, controller, nav_items, active_label="Update Movie",
                user=self.user).pack(side="left", fill="y")

        main_scroll = ctk.CTkScrollableFrame(self, fg_color=Colors.BACKGROUND,
                                              scrollbar_button_color=Colors.SURFACE_LIGHT)
        main_scroll.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 16))
        SectionHeader(header, title="Update Movie",
                      subtitle=f"Editing details for \"{self.movie.get('title', 'Untitled')}\"").pack(fill="x")

        if not self.movie or not self.movie.get("id"):
            empty_card = Card(main_scroll)
            empty_card.pack(fill="x", padx=32, pady=(0, 32))
            ctk.CTkLabel(
                empty_card, text="No movie selected. Go to the Admin Dashboard and click "
                                  "\"Update\" on a movie card to edit it here.",
                text_color=Colors.TEXT_MUTED, font=Fonts.BODY, wraplength=600
            ).pack(padx=32, pady=32)
            SecondaryButton(main_scroll, text="Back to Admin Dashboard", width=220,
                            command=self._go_back).pack(padx=32, pady=(0, 20), anchor="w")
            return

        content = ctk.CTkFrame(main_scroll, fg_color="transparent")
        content.pack(fill="x", padx=32, pady=(0, 32))

        # ---- Small poster preview on the left ----
        preview_card = Card(content, width=240)
        preview_card.pack(side="left", padx=(0, 24), anchor="n")
        preview_card.pack_propagate(False)
        poster_img = get_poster_image(self.movie.get("title", "Untitled"), width=190, height=270)
        ctk.CTkLabel(preview_card, image=poster_img, text="").pack(pady=24)

        # ---- Form on the right ----
        card = Card(content)
        card.pack(side="left", fill="both", expand=True)
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=32, pady=32)

        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 16))
        self.name_entry = LabeledEntry(row1, "Movie Name", width=340)
        self.name_entry.set(self.movie.get("title", ""))
        self.name_entry.pack(side="left", padx=(0, 20))

        self.movie_rated_entry = LabeledEntry(row1, "Content Rating", width=340)
        self.movie_rated_entry.set(self.movie.get("movie_rated", ""))
        self.movie_rated_entry.pack(side="left")

        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 16))
        self.genres_entry = LabeledEntry(row2, "Genres (semicolon-separated)", width=340)
        self.genres_entry.set(self.movie.get("genres", ""))
        self.genres_entry.pack(side="left", padx=(0, 20))

        self.year_entry = LabeledEntry(row2, "Release Year", width=340)
        self.year_entry.set(str(self.movie.get("year", "")))
        self.year_entry.pack(side="left")

        row3 = ctk.CTkFrame(form, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 16))
        self.run_length_entry = LabeledEntry(row3, "Run Length", width=340)
        self.run_length_entry.set(self.movie.get("run_length", ""))
        self.run_length_entry.pack(side="left", padx=(0, 20))

        self.release_date_entry = LabeledEntry(row3, "Release Date", width=340)
        self.release_date_entry.set(self.movie.get("release_date", ""))
        self.release_date_entry.pack(side="left")

        row4 = ctk.CTkFrame(form, fg_color="transparent")
        row4.pack(fill="x", pady=(0, 8))
        self.rating_entry = LabeledEntry(row4, "Rating (0-10)", width=340)
        self.rating_entry.set(str(self.movie.get("rating", "")))
        self.rating_entry.pack(side="left", padx=(0, 20))

        self.num_raters_entry = LabeledEntry(row4, "Number of Raters", width=340)
        self.num_raters_entry.set(str(self.movie.get("num_raters", 0)))
        self.num_raters_entry.pack(side="left")

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.pack(fill="x", pady=(20, 0))
        GoldButton(actions, text="Update Movie", width=180, command=self._update_movie).pack(side="left", padx=(0, 12))
        SecondaryButton(actions, text="Cancel", width=140, command=self._go_back).pack(side="left")

    def _update_movie(self):
        updated = {
            "name": self.name_entry.get(),
            "movie_rated": self.movie_rated_entry.get(),
            "genres": self.genres_entry.get(),
            "year": self.year_entry.get(),
            "run_length": self.run_length_entry.get(),
            "release_date": self.release_date_entry.get(),
            "rating": self.rating_entry.get(),
        }

        try:
            MovieController.update_movie(self.movie.get("id"), updated)
        except MovieError as e:
            show_error(self, "Update Failed", str(e))
            return

        show_success(self, "Movie Updated", f"\"{updated['name']}\" was updated successfully.")
        self._go_back()

    def _go_back(self):
        from frontend.views.admin_dashboard_window import AdminDashboardWindow
        self.controller.show_view(AdminDashboardWindow, remember_history=False, user=self.user)
