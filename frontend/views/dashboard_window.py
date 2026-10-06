"""
views/dashboard_window.py
----------------------------
Screen 4: Dashboard
Main landing screen after login. Shows a sidebar, a "Recommended
For You" shelf (from RecommendationController, based on the user's
watchlist genres), and the full movie catalog loaded from MongoDB.
"""

import customtkinter as ctk
from config import Colors, Fonts
from frontend.widgets.sidebar import Sidebar
from frontend.widgets.movie_card import MovieCard
from frontend.widgets.custom_widgets import SectionHeader
from frontend.widgets.dialogs import show_error
from backend.controllers.movie_controller import MovieController, MovieError
from backend.controllers.user_controller import UserController, UserError
from backend.controllers.recommendation_controller import RecommendationController, RecommendationError
from backend.utils.nav_config import build_nav_items


class DashboardWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, user=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller
        self.user = user or {}

        # ---- Sidebar ----
        nav_items = build_nav_items(self.user)
        Sidebar(self, controller, nav_items, active_label="Dashboard",
                user=self.user).pack(side="left", fill="y")

        # ---- Main content ----
        main_scroll = ctk.CTkScrollableFrame(self, fg_color=Colors.BACKGROUND,
                                              scrollbar_button_color=Colors.SURFACE_LIGHT)
        main_scroll.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 10))
        SectionHeader(
            header,
            title=f"Welcome back, {self.user.get('full_name', 'Guest')} 👋",
            subtitle="Here are some movies picked for you"
        ).pack(side="left", fill="x", expand=True)

        # ---- "Recommended For You" shelf ----
        self._render_recommendations(main_scroll)

        # ---- All Movies ----
        catalog_header = ctk.CTkFrame(main_scroll, fg_color="transparent")
        catalog_header.pack(fill="x", padx=32, pady=(10, 6))
        ctk.CTkLabel(catalog_header, text="All Movies", font=Fonts.H3,
                     text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left")

        self.grid_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        try:
            self.movies = MovieController.get_all_movies()
        except MovieError as e:
            show_error(self, "Could Not Load Movies", str(e))
            self.movies = []

        self._render_grid()

    def _render_recommendations(self, parent):
        user_id = self.user.get("id")
        if not user_id:
            return
        try:
            recommendations = RecommendationController.get_recommendations(user_id, limit=8)
        except RecommendationError:
            recommendations = []

        if not recommendations:
            return

        rec_header = ctk.CTkFrame(parent, fg_color="transparent")
        rec_header.pack(fill="x", padx=32, pady=(0, 6))
        ctk.CTkLabel(rec_header, text="🎯 Recommended For You", font=Fonts.H3,
                     text_color=Colors.SECONDARY, anchor="w").pack(side="left")

        rec_scroll = ctk.CTkScrollableFrame(
            parent, fg_color="transparent", orientation="horizontal",
            height=440, scrollbar_button_color=Colors.SURFACE_LIGHT
        )
        rec_scroll.pack(fill="x", padx=24, pady=(0, 20))

        for movie in recommendations:
            card = MovieCard(
                rec_scroll, movie,
                on_view=self._open_details,
                on_watchlist=self._add_to_watchlist,
            )
            card.pack(side="left", padx=10, pady=10)

    def _render_grid(self, columns=4):
        for child in self.grid_frame.winfo_children():
            child.destroy()

        for col in range(columns):
            self.grid_frame.grid_columnconfigure(col, weight=1)

        if not self.movies:
            ctk.CTkLabel(self.grid_frame, text="No movies available.",
                         text_color=Colors.TEXT_MUTED, font=Fonts.BODY).grid(row=0, column=0, pady=40)
            return

        for index, movie in enumerate(self.movies):
            row, col = divmod(index, columns)
            card = MovieCard(
                self.grid_frame, movie,
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
