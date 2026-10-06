"""
views/add_movie_window.py
----------------------------
Screen 12: Add Movie Window
Admin form to add a new movie directly into the real MongoDB
`movies` collection, using the EXISTING dataset schema:
name, year, movie_rated, run_length, genres, release_date,
rating, num_raters, num_reviews.
"""

import customtkinter as ctk
from config import Colors, Fonts
from frontend.widgets.sidebar import Sidebar
from frontend.widgets.custom_widgets import SectionHeader, Card, LabeledEntry, GoldButton, SecondaryButton
from frontend.widgets.dialogs import show_error, show_success
from backend.utils.nav_config import build_admin_nav_items
from backend.controllers.movie_controller import MovieController, MovieError


class AddMovieWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, user=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller
        self.user = user or {}

        nav_items = build_admin_nav_items(self.user)
        Sidebar(self, controller, nav_items, active_label="Add Movie",
                user=self.user).pack(side="left", fill="y")

        main_scroll = ctk.CTkScrollableFrame(self, fg_color=Colors.BACKGROUND,
                                              scrollbar_button_color=Colors.SURFACE_LIGHT)
        main_scroll.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 16))
        SectionHeader(header, title="Add New Movie",
                      subtitle="Fill in the details below to add a movie to the catalog").pack(fill="x")

        card = Card(main_scroll)
        card.pack(fill="x", padx=32, pady=(0, 32))
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=32, pady=32)

        row1 = ctk.CTkFrame(form, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 16))
        self.name_entry = LabeledEntry(row1, "Movie Name", "e.g. Inception", width=340)
        self.name_entry.pack(side="left", padx=(0, 20))
        self.movie_rated_entry = LabeledEntry(row1, "Content Rating", "e.g. PG-13", width=340)
        self.movie_rated_entry.pack(side="left")

        row2 = ctk.CTkFrame(form, fg_color="transparent")
        row2.pack(fill="x", pady=(0, 16))
        self.genres_entry = LabeledEntry(
            row2, "Genres (semicolon-separated)", "e.g. Action; Adventure; Sci-Fi;", width=340
        )
        self.genres_entry.pack(side="left", padx=(0, 20))
        self.year_entry = LabeledEntry(row2, "Release Year", "e.g. 2010", width=340)
        self.year_entry.pack(side="left")

        row3 = ctk.CTkFrame(form, fg_color="transparent")
        row3.pack(fill="x", pady=(0, 16))
        self.run_length_entry = LabeledEntry(row3, "Run Length", "e.g. 2h 28min", width=340)
        self.run_length_entry.pack(side="left", padx=(0, 20))
        self.release_date_entry = LabeledEntry(row3, "Release Date", "e.g. 16 July 2010 (USA)", width=340)
        self.release_date_entry.pack(side="left")

        row4 = ctk.CTkFrame(form, fg_color="transparent")
        row4.pack(fill="x", pady=(0, 16))
        self.rating_entry = LabeledEntry(row4, "Rating (0-10)", "e.g. 8.8", width=340)
        self.rating_entry.pack(side="left", padx=(0, 20))
        self.num_raters_entry = LabeledEntry(row4, "Number of Raters", "e.g. 1981675", width=340)
        self.num_raters_entry.pack(side="left")

        row5 = ctk.CTkFrame(form, fg_color="transparent")
        row5.pack(fill="x", pady=(0, 8))
        self.num_reviews_entry = LabeledEntry(row5, "Number of Reviews", "e.g. 3820", width=340)
        self.num_reviews_entry.pack(side="left")

        poster_note = ctk.CTkLabel(
            form, text="📁 Poster images aren't part of this dataset — a placeholder poster is shown automatically.",
            text_color=Colors.TEXT_MUTED, font=Fonts.SMALL, anchor="w"
        )
        poster_note.pack(fill="x", pady=(14, 0))

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.pack(fill="x", pady=(20, 0))
        GoldButton(actions, text="Save Movie", width=180, command=self._save_movie).pack(side="left", padx=(0, 12))
        SecondaryButton(actions, text="Cancel", width=140, command=self._go_back).pack(side="left")

    def _save_movie(self):
        payload = {
            "name": self.name_entry.get(),
            "movie_rated": self.movie_rated_entry.get(),
            "genres": self.genres_entry.get(),
            "year": self.year_entry.get(),
            "run_length": self.run_length_entry.get(),
            "release_date": self.release_date_entry.get(),
            "rating": self.rating_entry.get(),
            "num_raters": self.num_raters_entry.get() or 0,
            "num_reviews": self.num_reviews_entry.get() or 0,
        }

        try:
            new_movie = MovieController.add_movie(payload)
        except MovieError as e:
            show_error(self, "Could Not Add Movie", str(e))
            return

        show_success(self, "Movie Added", f"\"{new_movie['title']}\" was added to the catalog.")
        self._go_back()

    def _go_back(self):
        from frontend.views.admin_dashboard_window import AdminDashboardWindow
        self.controller.show_view(AdminDashboardWindow, remember_history=False, user=self.user)
