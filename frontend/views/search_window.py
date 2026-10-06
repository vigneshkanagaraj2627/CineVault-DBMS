"""
views/search_window.py
-------------------------
Screen 6: Search Interface
Sidebar + search bar + live-filtering movie grid, backed by
MovieController.search_movies() (case-insensitive partial match
on the real `name` field in MongoDB).
"""

import customtkinter as ctk
from config import Colors, Fonts
from frontend.widgets.sidebar import Sidebar
from frontend.widgets.movie_card import MovieCard
from frontend.widgets.custom_widgets import SectionHeader, PrimaryButton
from frontend.widgets.dialogs import show_error
from backend.controllers.movie_controller import MovieController, MovieError
from backend.controllers.user_controller import UserController, UserError
from backend.utils.nav_config import build_nav_items


class SearchWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, user=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller
        self.user = user or {}

        nav_items = build_nav_items(self.user)
        Sidebar(self, controller, nav_items, active_label="Search",
                user=self.user).pack(side="left", fill="y")

        main = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        main.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 10))
        SectionHeader(header, title="Search Movies",
                      subtitle="Find your next favorite watch").pack(fill="x")

        # ---- Search bar ----
        search_bar = ctk.CTkFrame(main, fg_color="transparent")
        search_bar.pack(fill="x", padx=32, pady=(0, 16))

        self.search_entry = ctk.CTkEntry(
            search_bar, placeholder_text="Search by movie title...",
            height=44, corner_radius=10, width=400,
            fg_color=Colors.ENTRY_BG, border_color=Colors.BORDER,
            font=("Segoe UI", 14)
        )
        self.search_entry.pack(side="left", padx=(0, 12))
        self.search_entry.bind("<Return>", lambda e: self._perform_search())

        PrimaryButton(search_bar, text="Search", width=120,
                      command=self._perform_search).pack(side="left")

        self.result_label = ctk.CTkLabel(
            main, text="Showing all movies", text_color=Colors.TEXT_MUTED,
            font=Fonts.SMALL, anchor="w"
        )
        self.result_label.pack(fill="x", padx=32, pady=(0, 6))

        self.grid_scroll = ctk.CTkScrollableFrame(main, fg_color="transparent",
                                                   scrollbar_button_color=Colors.SURFACE_LIGHT)
        self.grid_scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        try:
            self.movies = MovieController.get_all_movies()
        except MovieError as e:
            show_error(self, "Could Not Load Movies", str(e))
            self.movies = []
        self._render_grid()

    def _perform_search(self):
        query = self.search_entry.get()
        try:
            self.movies = MovieController.search_movies(query)
        except MovieError as e:
            show_error(self, "Search Failed", str(e))
            return

        count = len(self.movies)
        self.result_label.configure(
            text=f"Showing {count} result{'s' if count != 1 else ''} for \"{query}\"" if query
            else "Showing all movies"
        )
        self._render_grid()

    def _render_grid(self, columns=4):
        for child in self.grid_scroll.winfo_children():
            child.destroy()

        for col in range(columns):
            self.grid_scroll.grid_columnconfigure(col, weight=1)

        if not self.movies:
            ctk.CTkLabel(self.grid_scroll, text="No movies found.",
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
