"""
views/rating_filter_window.py
----------------------------------
Screen 8: Rating Filter / Top Rated
Sidebar + minimum-rating chips (0-10 scale, matching the real
dataset) + a grid sorted by rating descending.
"""

import customtkinter as ctk
from config import Colors, Fonts
from frontend.widgets.sidebar import Sidebar
from frontend.widgets.movie_card import MovieCard
from frontend.widgets.custom_widgets import SectionHeader
from frontend.widgets.dialogs import show_error
from backend.controllers.movie_controller import MovieController, MovieError
from backend.controllers.user_controller import UserController, UserError
from backend.utils.nav_config import build_nav_items


class RatingFilterWindow(ctk.CTkFrame):
    RATING_OPTIONS = [
        ("All Ratings", 0.0),
        ("★ 5.0 & above", 5.0),
        ("★ 7.0 & above", 7.0),
        ("★ 8.0 & above", 8.0),
        ("★ 9.0 & above", 9.0),
    ]

    def __init__(self, parent, controller, user=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller
        self.user = user or {}
        self.active_index = 0
        self.rating_buttons = []

        nav_items = build_nav_items(self.user)
        Sidebar(self, controller, nav_items, active_label="Top Rated",
                user=self.user).pack(side="left", fill="y")

        main = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        main.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 10))
        SectionHeader(header, title="Top Rated Movies",
                      subtitle="Sorted highest-rated first (IMDb-style 0-10 scale)").pack(fill="x")

        chips_frame = ctk.CTkFrame(main, fg_color="transparent")
        chips_frame.pack(fill="x", padx=32, pady=(0, 16))

        for i, (label, value) in enumerate(self.RATING_OPTIONS):
            btn = ctk.CTkButton(
                chips_frame, text=label, width=150, height=36, corner_radius=18,
                fg_color=Colors.SECONDARY if i == 0 else "transparent",
                text_color="#1A1A1A" if i == 0 else Colors.TEXT_PRIMARY,
                border_width=1, border_color=Colors.BORDER,
                hover_color=Colors.SECONDARY_HOVER if i == 0 else Colors.SURFACE_LIGHT,
                font=("Segoe UI", 12, "bold"),
                command=lambda idx=i, v=value: self._select_rating(idx, v)
            )
            btn.pack(side="left", padx=6)
            self.rating_buttons.append(btn)

        self.grid_scroll = ctk.CTkScrollableFrame(main, fg_color="transparent",
                                                   scrollbar_button_color=Colors.SURFACE_LIGHT)
        self.grid_scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        try:
            self.movies = MovieController.get_top_rated(limit=200)
        except MovieError as e:
            show_error(self, "Could Not Load Movies", str(e))
            self.movies = []
        self._render_grid()

    def _select_rating(self, index, min_rating):
        self.active_index = index
        for i, btn in enumerate(self.rating_buttons):
            is_active = (i == index)
            btn.configure(
                fg_color=Colors.SECONDARY if is_active else "transparent",
                text_color="#1A1A1A" if is_active else Colors.TEXT_PRIMARY,
                hover_color=Colors.SECONDARY_HOVER if is_active else Colors.SURFACE_LIGHT
            )
        try:
            if min_rating == 0.0:
                self.movies = MovieController.get_top_rated(limit=200)
            else:
                self.movies = MovieController.filter_by_rating(min_rating)
                self.movies.sort(key=lambda m: m.get("rating", 0), reverse=True)
        except MovieError as e:
            show_error(self, "Filter Failed", str(e))
            return
        self._render_grid()

    def _render_grid(self, columns=4):
        for child in self.grid_scroll.winfo_children():
            child.destroy()
        for col in range(columns):
            self.grid_scroll.grid_columnconfigure(col, weight=1)

        if not self.movies:
            ctk.CTkLabel(self.grid_scroll, text="No movies match this rating.",
                         text_color=Colors.TEXT_MUTED, font=Fonts.BODY).grid(row=0, column=0, pady=40)
            return

        for index, movie in enumerate(self.movies):
            row, col = divmod(index, columns)
            card = MovieCard(
                self.grid_scroll, movie,
                on_view=self._open_details,
                on_watchlist=self._add_to_watchlist,
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="n")

    def _open_details(self, movie):
        from frontend.views.movie_details_window import MovieDetailsWindow
        self.controller.show_view(MovieDetailsWindow, movie=movie, user=self.user)

    def _add_to_watchlist(self, movie):
        user_id = self.user.get("id")
        if not user_id:
            show_error(self, "Not Logged In", "Please log in to use the watchlist.")
            return
        try:
            UserController.add_to_watchlist(user_id, movie["id"])
        except UserError as e:
            show_error(self, "Watchlist Error", str(e))
