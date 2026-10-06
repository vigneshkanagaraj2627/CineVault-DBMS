"""
views/genre_filter_window.py
--------------------------------
Screen 7: Genre Filter
Sidebar + horizontal scrollable genre chips (dynamically extracted
from the real dataset's semicolon-separated genres field) + a
filtered movie grid.
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


class GenreFilterWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, user=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller
        self.user = user or {}
        self.active_genre = "All"
        self.genre_buttons = {}

        nav_items = build_nav_items(self.user)
        Sidebar(self, controller, nav_items, active_label="Genres",
                user=self.user).pack(side="left", fill="y")

        main = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        main.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 10))
        SectionHeader(header, title="Browse by Genre",
                      subtitle="Pick a genre to filter the movie list").pack(fill="x")

        # ---- Genre chips row (horizontally scrollable — the real
        # dataset can have dozens of distinct genres) ----
        try:
            genres = MovieController.get_all_genres()
        except MovieError as e:
            show_error(self, "Could Not Load Genres", str(e))
            genres = ["All"]

        chips_scroll = ctk.CTkScrollableFrame(
            main, fg_color="transparent", orientation="horizontal",
            height=60, scrollbar_button_color=Colors.SURFACE_LIGHT
        )
        chips_scroll.pack(fill="x", padx=32, pady=(0, 16))

        for genre in genres:
            btn = ctk.CTkButton(
                chips_scroll, text=genre, width=110, height=36, corner_radius=18,
                fg_color=Colors.PRIMARY if genre == "All" else "transparent",
                border_width=1, border_color=Colors.BORDER,
                hover_color=Colors.PRIMARY_HOVER if genre == "All" else Colors.SURFACE_LIGHT,
                text_color=Colors.TEXT_PRIMARY, font=("Segoe UI", 12, "bold"),
                command=lambda g=genre: self._select_genre(g)
            )
            btn.pack(side="left", padx=6)
            self.genre_buttons[genre] = btn

        self.grid_scroll = ctk.CTkScrollableFrame(main, fg_color="transparent",
                                                   scrollbar_button_color=Colors.SURFACE_LIGHT)
        self.grid_scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        try:
            self.movies = MovieController.get_all_movies()
        except MovieError as e:
            show_error(self, "Could Not Load Movies", str(e))
            self.movies = []
        self._render_grid()

    def _select_genre(self, genre):
        self.active_genre = genre
        for g, btn in self.genre_buttons.items():
            is_active = (g == genre)
            btn.configure(
                fg_color=Colors.PRIMARY if is_active else "transparent",
                hover_color=Colors.PRIMARY_HOVER if is_active else Colors.SURFACE_LIGHT
            )
        try:
            self.movies = MovieController.filter_by_genre(genre)
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
            ctk.CTkLabel(self.grid_scroll, text="No movies found in this genre.",
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
