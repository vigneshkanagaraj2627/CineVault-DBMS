"""
widgets/sidebar.py
--------------------
Reusable left-hand navigation sidebar used by Dashboard, Search,
Watchlist, Profile, Settings, Admin, etc. Highlights the currently
active section and fires navigation callbacks via the controller.
"""

import customtkinter as ctk
from config import Colors
from backend.utils.image_loader import get_logo_placeholder


class Sidebar(ctk.CTkFrame):
    """
    A fixed-width vertical navigation bar.

    nav_items: list of (label, icon_text, view_class, kwargs) tuples
    active_label: label of the currently active screen (for highlighting)
    """

    def __init__(self, parent, controller, nav_items, active_label=None,
                 user=None, width=230, **kwargs):
        super().__init__(parent, fg_color=Colors.SIDEBAR, corner_radius=0, width=width, **kwargs)
        self.controller = controller
        self.pack_propagate(False)

        # ---- Logo ----
        logo_img = get_logo_placeholder(width=190, height=60)
        ctk.CTkLabel(self, image=logo_img, text="").pack(pady=(28, 10))

        # ---- User chip (optional) ----
        if user:
            user_frame = ctk.CTkFrame(self, fg_color=Colors.SURFACE, corner_radius=10)
            user_frame.pack(fill="x", padx=18, pady=(4, 20))
            ctk.CTkLabel(
                user_frame, text=f"👤  {user.get('full_name', 'Guest')}",
                text_color=Colors.TEXT_PRIMARY, font=("Segoe UI", 13, "bold"),
                anchor="w"
            ).pack(fill="x", padx=12, pady=(10, 2))
            ctk.CTkLabel(
                user_frame, text=user.get("email", ""),
                text_color=Colors.TEXT_MUTED, font=("Segoe UI", 11),
                anchor="w"
            ).pack(fill="x", padx=12, pady=(0, 10))

        # ---- Nav buttons ----
        nav_container = ctk.CTkFrame(self, fg_color="transparent")
        nav_container.pack(fill="x", padx=14)

        for label, icon, view_class, kwargs_for_view in nav_items:
            is_active = (label == active_label)
            btn = ctk.CTkButton(
                nav_container,
                text=f"{icon}   {label}",
                anchor="w",
                height=44,
                corner_radius=10,
                fg_color=Colors.PRIMARY if is_active else "transparent",
                hover_color=Colors.SURFACE_LIGHT if not is_active else Colors.PRIMARY_HOVER,
                text_color=Colors.TEXT_PRIMARY,
                font=("Segoe UI", 14, "bold" if is_active else "normal"),
                command=lambda vc=view_class, kw=kwargs_for_view: self._navigate(vc, kw)
            )
            btn.pack(fill="x", pady=4)

        # ---- Spacer + Logout ----
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        logout_btn = ctk.CTkButton(
            self, text="⏻   Logout", anchor="w", height=44, corner_radius=10,
            fg_color="transparent", hover_color=Colors.ERROR,
            text_color=Colors.TEXT_SECONDARY, font=("Segoe UI", 14),
            command=self._logout
        )
        logout_btn.pack(fill="x", padx=14, pady=(0, 24))

    def _navigate(self, view_class, kwargs_for_view):
        print(f"Navigating to: {view_class.__name__}")
        self.controller.show_view(view_class, **kwargs_for_view)

    def _logout(self):
        print("Logout Clicked")
        # Local import avoids circular import at module load time
        from frontend.views.login_window import LoginWindow
        self.controller.show_view(LoginWindow)
