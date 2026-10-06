"""
views/delete_movie_window.py
---------------------------------
Screen 14: Delete Movie Window
Admin confirmation screen before permanently deleting a movie from
the real MongoDB `movies` collection. Requires an explicit
"Confirm Delete" click.
"""

import customtkinter as ctk
from config import Colors, Fonts
from frontend.widgets.sidebar import Sidebar
from frontend.widgets.custom_widgets import SectionHeader, Card, DangerButton, SecondaryButton
from frontend.widgets.rating_stars import RatingStars
from frontend.widgets.dialogs import show_error
from backend.utils.image_loader import get_poster_image
from backend.utils.nav_config import build_admin_nav_items
from backend.controllers.movie_controller import MovieController, MovieError


class DeleteMovieWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, movie=None, user=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller
        self.user = user or {}
        self.movie = movie or {}
        self.deleted = False

        nav_items = build_admin_nav_items(self.user)
        Sidebar(self, controller, nav_items, active_label="Delete Movie",
                user=self.user).pack(side="left", fill="y")

        main = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        main.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 16))
        SectionHeader(header, title="Delete Movie",
                      subtitle="This action permanently removes the movie from MongoDB").pack(fill="x")

        # ---- Centered confirmation card ----
        outer = ctk.CTkFrame(main, fg_color="transparent")
        outer.pack(fill="both", expand=True)

        self.card = Card(outer, width=520)
        self.card.place(relx=0.5, rely=0.45, anchor="center")
        self.card.pack_propagate(False)

        if not self.movie or not self.movie.get("id"):
            self._render_no_movie_selected()
        else:
            self._render_confirmation()

    def _render_no_movie_selected(self):
        self.card.configure(height=220)
        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=32)
        ctk.CTkLabel(
            inner, text="No movie selected. Go to the Admin Dashboard and click "
                        "\"Delete\" on a movie card to remove it here.",
            text_color=Colors.TEXT_MUTED, font=Fonts.BODY, wraplength=440, justify="center"
        ).pack(pady=(10, 20))
        SecondaryButton(inner, text="Back to Admin Dashboard", width=220,
                        command=self._go_back).pack()

    def _render_confirmation(self):
        for child in self.card.winfo_children():
            child.destroy()
        self.card.configure(height=420)

        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=32)

        ctk.CTkLabel(inner, text="⚠️  Confirm Deletion", font=Fonts.H3,
                     text_color=Colors.ERROR, anchor="w").pack(fill="x", pady=(0, 16))

        movie_row = ctk.CTkFrame(inner, fg_color=Colors.SURFACE_LIGHT, corner_radius=10)
        movie_row.pack(fill="x", pady=(0, 20))
        movie_row_inner = ctk.CTkFrame(movie_row, fg_color="transparent")
        movie_row_inner.pack(fill="x", padx=16, pady=16)

        poster_img = get_poster_image(self.movie.get("title", "Untitled"), width=70, height=100)
        ctk.CTkLabel(movie_row_inner, image=poster_img, text="").pack(side="left", padx=(0, 16))

        details_box = ctk.CTkFrame(movie_row_inner, fg_color="transparent")
        details_box.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(details_box, text=self.movie.get("title", "Untitled"),
                     font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        ctk.CTkLabel(details_box,
                     text=f"{self.movie.get('genre', '—')} • {self.movie.get('year', '—')}",
                     font=Fonts.SMALL, text_color=Colors.TEXT_SECONDARY, anchor="w").pack(fill="x", pady=(2, 6))
        RatingStars(details_box, rating=self.movie.get("rating", 0.0), scale_max=10, font_size=13).pack(anchor="w")

        ctk.CTkLabel(
            inner,
            text=f"Are you sure you want to permanently delete\n"
                 f"\"{self.movie.get('title', 'this movie')}\" from the catalog?",
            font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY, justify="center"
        ).pack(pady=(0, 24))

        actions = ctk.CTkFrame(inner, fg_color="transparent")
        actions.pack()
        DangerButton(actions, text="Confirm Delete", width=180,
                     command=self._confirm_delete).pack(side="left", padx=(0, 12))
        SecondaryButton(actions, text="Cancel", width=140,
                        command=self._go_back).pack(side="left")

    def _confirm_delete(self):
        try:
            MovieController.delete_movie(self.movie.get("id"))
        except MovieError as e:
            show_error(self, "Delete Failed", str(e))
            return
        self.deleted = True
        self._render_deleted_state()

    def _render_deleted_state(self):
        for child in self.card.winfo_children():
            child.destroy()

        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=32, pady=32)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(inner, text="✅", font=("Segoe UI", 40)).pack(pady=(0, 12))
        ctk.CTkLabel(inner, text="Movie Deleted", font=Fonts.H3,
                     text_color=Colors.SUCCESS).pack(pady=(0, 6))
        ctk.CTkLabel(inner, text=f"\"{self.movie.get('title', 'Movie')}\" was permanently removed from MongoDB.",
                     font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY, justify="center").pack(pady=(0, 24))
        SecondaryButton(inner, text="Back to Admin Dashboard", width=220,
                        command=self._go_back).pack()

    def _go_back(self):
        from frontend.views.admin_dashboard_window import AdminDashboardWindow
        self.controller.show_view(AdminDashboardWindow, remember_history=False, user=self.user)
