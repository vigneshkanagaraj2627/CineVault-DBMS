"""
views/watchlist_window.py
----------------------------
Screen 9: Watchlist Window
Sidebar + grid of movies the CURRENT logged-in user has saved.
Persists across restarts since it's stored on the user's MongoDB
document. Each card allows removing the movie from the watchlist.
"""

import customtkinter as ctk
from config import Colors, Fonts
from frontend.widgets.sidebar import Sidebar
from frontend.widgets.movie_card import MovieCard
from frontend.widgets.custom_widgets import SectionHeader
from frontend.widgets.dialogs import show_error
from backend.controllers.user_controller import UserController, UserError
from backend.utils.nav_config import build_nav_items


class WatchlistWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, user=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller
        self.user = user or {}

        nav_items = build_nav_items(self.user)
        Sidebar(self, controller, nav_items, active_label="Watchlist",
                user=self.user).pack(side="left", fill="y")

        main = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        main.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 10))
        SectionHeader(header, title="My Watchlist",
                      subtitle="Movies you've saved to watch later").pack(fill="x")

        self.grid_scroll = ctk.CTkScrollableFrame(main, fg_color="transparent",
                                                   scrollbar_button_color=Colors.SURFACE_LIGHT)
        self.grid_scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self._refresh()

    def _refresh(self):
        user_id = self.user.get("id")
        if not user_id:
            self.movies = []
            self._render_grid()
            return
        try:
            self.movies = UserController.get_watchlist(user_id)
        except UserError as e:
            show_error(self, "Could Not Load Watchlist", str(e))
            self.movies = []
        self._render_grid()

    def _render_grid(self, columns=4):
        for child in self.grid_scroll.winfo_children():
            child.destroy()
        for col in range(columns):
            self.grid_scroll.grid_columnconfigure(col, weight=1)

        if not self.movies:
            empty = ctk.CTkFrame(self.grid_scroll, fg_color="transparent")
            empty.grid(row=0, column=0, columnspan=columns, pady=60)
            ctk.CTkLabel(empty, text="📌", font=("Segoe UI", 40)).pack()
            ctk.CTkLabel(empty, text="Your watchlist is empty",
                         text_color=Colors.TEXT_SECONDARY, font=Fonts.BODY_BOLD).pack(pady=(8, 0))
            ctk.CTkLabel(empty, text="Add movies from the Dashboard or Search page",
                         text_color=Colors.TEXT_MUTED, font=Fonts.SMALL).pack()
            return

        for index, movie in enumerate(self.movies):
            row, col = divmod(index, columns)
            card = MovieCard(
                self.grid_scroll, movie,
                on_view=self._open_details,
                on_watchlist=self._remove_from_watchlist,
                watchlist_label="− Remove",
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="n")

    def _open_details(self, movie):
        from frontend.views.movie_details_window import MovieDetailsWindow
        self.controller.show_view(MovieDetailsWindow, movie=movie, user=self.user)

    def _remove_from_watchlist(self, movie):
        user_id = self.user.get("id")
        if not user_id:
            return
        try:
            UserController.remove_from_watchlist(user_id, movie["id"])
        except UserError as e:
            show_error(self, "Watchlist Error", str(e))
            return
        self._refresh()
