"""
views/admin_dashboard_window.py
------------------------------------
Screen 11: Admin Dashboard
Uses a separate admin-focused sidebar (Add/Update/Delete Movie)
and shows the full movie catalog (from MongoDB) with inline
Update/Delete actions on each card, plus real stat cards computed
from the database.
"""

import customtkinter as ctk
from config import Colors, Fonts
from frontend.widgets.sidebar import Sidebar
from frontend.widgets.movie_card import MovieCard
from frontend.widgets.custom_widgets import SectionHeader, Card, GoldButton
from frontend.widgets.dialogs import show_error, ask_confirm, show_success
from backend.controllers.movie_controller import MovieController, MovieError
from backend.controllers.auth_controller import AuthController
from backend.utils.nav_config import build_admin_nav_items


class AdminDashboardWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, user=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller
        self.user = user or {}

        nav_items = build_admin_nav_items(self.user)
        Sidebar(self, controller, nav_items, active_label="Admin Home",
                user=self.user).pack(side="left", fill="y")

        main_scroll = ctk.CTkScrollableFrame(self, fg_color=Colors.BACKGROUND,
                                              scrollbar_button_color=Colors.SURFACE_LIGHT)
        main_scroll.pack(side="left", fill="both", expand=True)

        header_row = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header_row.pack(fill="x", padx=32, pady=(28, 16))
        SectionHeader(header_row, title="Admin Dashboard",
                      subtitle="Manage the CineVault movie catalog").pack(side="left", fill="x", expand=True)
        GoldButton(header_row, text="+ Add New Movie", width=200,
                   command=self._go_add_movie).pack(side="right")

        # ---- Stat cards (computed live from MongoDB) ----
        stats_row = ctk.CTkFrame(main_scroll, fg_color="transparent")
        stats_row.pack(fill="x", padx=32, pady=(0, 20))

        try:
            stats = MovieController.get_stats()
            admin_count = AuthController.count_admins()
        except MovieError as e:
            show_error(self, "Could Not Load Stats", str(e))
            stats = {"total_movies": 0, "total_genres": 0, "avg_rating": 0.0}
            admin_count = 0

        self._stat_card(stats_row, str(stats["total_movies"]), "Total Movies")
        self._stat_card(stats_row, str(stats["total_genres"]), "Genres")
        self._stat_card(stats_row, str(admin_count), "Registered Admins")
        self._stat_card(stats_row, f"{stats['avg_rating']:.1f}", "Avg. Rating")

        # ---- Catalog header + search ----
        catalog_header = ctk.CTkFrame(main_scroll, fg_color="transparent")
        catalog_header.pack(fill="x", padx=32, pady=(0, 10))
        ctk.CTkLabel(catalog_header, text="Movie Catalog", font=Fonts.H3,
                     text_color=Colors.TEXT_PRIMARY, anchor="w").pack(side="left", fill="x", expand=True)

        self.search_entry = ctk.CTkEntry(
            catalog_header, placeholder_text="Search movies to manage...",
            height=38, corner_radius=8, width=280,
            fg_color=Colors.ENTRY_BG, border_color=Colors.BORDER, font=("Segoe UI", 13)
        )
        self.search_entry.pack(side="right")
        self.search_entry.bind("<Return>", lambda e: self._search_catalog())

        self.grid_frame = ctk.CTkFrame(main_scroll, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True, padx=24, pady=(0, 30))

        try:
            self.movies = MovieController.get_all_movies()
        except MovieError as e:
            show_error(self, "Could Not Load Movies", str(e))
            self.movies = []
        self._render_grid()

    def _search_catalog(self):
        query = self.search_entry.get()
        try:
            self.movies = MovieController.search_movies(query)
        except MovieError as e:
            show_error(self, "Search Failed", str(e))
            return
        self._render_grid()

    def _stat_card(self, parent, value, label):
        card = Card(parent, width=190, height=90)
        card.pack(side="left", padx=(0, 16))
        card.pack_propagate(False)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(inner, text=value, font=Fonts.H2, text_color=Colors.SECONDARY).pack()
        ctk.CTkLabel(inner, text=label, font=Fonts.SMALL, text_color=Colors.TEXT_MUTED).pack()

    def _render_grid(self, columns=4):
        for child in self.grid_frame.winfo_children():
            child.destroy()
        for col in range(columns):
            self.grid_frame.grid_columnconfigure(col, weight=1)

        if not self.movies:
            ctk.CTkLabel(self.grid_frame, text="No movies found.",
                         text_color=Colors.TEXT_MUTED, font=Fonts.BODY).grid(row=0, column=0, pady=40)
            return

        for index, movie in enumerate(self.movies):
            row, col = divmod(index, columns)
            card = MovieCard(
                self.grid_frame, movie,
                on_view=self._open_details,
                show_admin_actions=True,
                on_update=self._go_update_movie,
                on_delete=self._confirm_delete_movie,
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="n")

    def _open_details(self, movie):
        from frontend.views.movie_details_window import MovieDetailsWindow
        self.controller.show_view(MovieDetailsWindow, movie=movie, user=self.user)

    def _go_add_movie(self):
        from frontend.views.add_movie_window import AddMovieWindow
        self.controller.show_view(AddMovieWindow, user=self.user)

    def _go_update_movie(self, movie):
        from frontend.views.update_movie_window import UpdateMovieWindow
        self.controller.show_view(UpdateMovieWindow, movie=movie, user=self.user)

    def _confirm_delete_movie(self, movie):
        """Inline quick-delete straight from the catalog grid, with a
        confirmation dialog (the dedicated Delete Movie screen is
        also reachable via the sidebar for a more detailed view)."""
        if not ask_confirm(self, "Delete Movie",
                            f"Permanently delete \"{movie.get('title')}\" from the catalog?"):
            return
        try:
            MovieController.delete_movie(movie["id"])
        except MovieError as e:
            show_error(self, "Delete Failed", str(e))
            return
        show_success(self, "Movie Deleted", f"\"{movie.get('title')}\" was removed from the catalog.")
        self.controller.show_view(AdminDashboardWindow, remember_history=False, user=self.user)
