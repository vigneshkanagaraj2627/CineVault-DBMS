"""
widgets/movie_card.py
-----------------------
Reusable "movie card" component — a poster, title, genre badge,
star rating and action buttons. Used in Dashboard, Search, Genre
Filter, Rating Filter, Watchlist, and Admin screens so the grid
of movies always looks consistent.
"""

import customtkinter as ctk
from config import Colors
from backend.utils.image_loader import get_poster_image
from frontend.widgets.rating_stars import RatingStars


class MovieCard(ctk.CTkFrame):
    """
    A single movie card for use inside a scrollable grid.

    on_view: callback(movie_dict) -> called when "View" is clicked
    on_watchlist: callback(movie_dict) -> called when "Add to Watchlist" is clicked
    show_admin_actions: if True, shows Update/Delete instead of Watchlist button
    on_update / on_delete: admin-only callbacks
    """

    def __init__(self, parent, movie: dict,
                 on_view=None, on_watchlist=None,
                 show_admin_actions=False, on_update=None, on_delete=None,
                 watchlist_label="+ Watchlist",
                 width=220, **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.SURFACE,
            corner_radius=14,
            border_width=1,
            border_color=Colors.BORDER,
            width=width,
            **kwargs
        )
        self.movie = movie
        self.pack_propagate(False)
        self.grid_propagate(False)
        self.configure(width=width, height=430)

        # ---- Poster ----
        poster_img = get_poster_image(movie["title"], width=width - 24, height=260)
        self.poster_label = ctk.CTkLabel(self, image=poster_img, text="")
        self.poster_label.pack(padx=12, pady=(12, 8))

        # ---- Title ----
        self.title_label = ctk.CTkLabel(
            self, text=movie["title"],
            text_color=Colors.TEXT_PRIMARY,
            font=("Segoe UI", 15, "bold"),
            anchor="w", justify="left",
            wraplength=width - 24
        )
        self.title_label.pack(fill="x", padx=12)

        # ---- Genre + Year ----
        self.meta_label = ctk.CTkLabel(
            self, text=f"{movie['genre']}  •  {movie['year']}",
            text_color=Colors.TEXT_SECONDARY,
            font=("Segoe UI", 12),
            anchor="w"
        )
        self.meta_label.pack(fill="x", padx=12, pady=(2, 4))

        # ---- Rating ----
        RatingStars(self, rating=movie["rating"], scale_max=10, font_size=13).pack(anchor="w", padx=12, pady=(0, 8))

        # ---- Action buttons ----
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=12, pady=(0, 12), side="bottom")

        view_btn = ctk.CTkButton(
            btn_frame, text="View", width=80, height=32,
            corner_radius=8, fg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER,
            font=("Segoe UI", 12, "bold"),
            command=lambda: self._handle_view(on_view)
        )
        view_btn.pack(side="left", padx=(0, 6))

        if show_admin_actions:
            update_btn = ctk.CTkButton(
                btn_frame, text="Update", width=60, height=32,
                corner_radius=8, fg_color=Colors.SECONDARY, hover_color=Colors.SECONDARY_HOVER,
                text_color="#1A1A1A", font=("Segoe UI", 12, "bold"),
                command=lambda: self._handle_generic(on_update)
            )
            update_btn.pack(side="left", padx=(0, 6))

            delete_btn = ctk.CTkButton(
                btn_frame, text="Delete", width=60, height=32,
                corner_radius=8, fg_color=Colors.ERROR, hover_color="#C0392B",
                font=("Segoe UI", 12, "bold"),
                command=lambda: self._handle_generic(on_delete)
            )
            delete_btn.pack(side="left")
        else:
            watchlist_btn = ctk.CTkButton(
                btn_frame, text=watchlist_label, width=100, height=32,
                corner_radius=8, fg_color="transparent",
                border_width=1, border_color=Colors.BORDER,
                hover_color=Colors.SURFACE_LIGHT,
                font=("Segoe UI", 12, "bold"),
                command=lambda: self._handle_generic(on_watchlist)
            )
            watchlist_btn.pack(side="left")

    def _handle_view(self, callback):
        print(f"Movie Selected: {self.movie['title']}")
        if callback:
            callback(self.movie)

    def _handle_generic(self, callback):
        if callback:
            callback(self.movie)
