"""
views/splash_screen.py
-------------------------
Screen 1: Splash Screen
Shown briefly on app launch before auto-navigating to Login.
"""

import customtkinter as ctk
from config import Colors, AppConfig
from backend.utils.image_loader import get_logo_placeholder


class SplashScreen(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller

        # Center content
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        logo_img = get_logo_placeholder(width=420, height=140)
        ctk.CTkLabel(center, image=logo_img, text="").pack(pady=(0, 12))

        ctk.CTkLabel(
            center, text="Your Personal Movie Recommendation Vault",
            text_color=Colors.TEXT_SECONDARY,
            font=("Segoe UI", 16)
        ).pack(pady=(0, 30))

        self.progress = ctk.CTkProgressBar(
            center, width=300, height=8, corner_radius=6,
            progress_color=Colors.PRIMARY, fg_color=Colors.SURFACE
        )
        self.progress.pack()
        self.progress.set(0)

        ctk.CTkLabel(
            center, text=f"v{AppConfig.APP_VERSION}",
            text_color=Colors.TEXT_MUTED, font=("Segoe UI", 11)
        ).pack(pady=(14, 0))

        self._animate_progress()

    def _animate_progress(self, value=0.0):
        """Fake loading animation, then auto-navigate to Login."""
        if value <= 1.0:
            self.progress.set(value)
            self.after(25, lambda: self._animate_progress(value + 0.02))
        else:
            self._go_to_login()

    def _go_to_login(self):
        from frontend.views.login_window import LoginWindow
        self.controller.show_view(LoginWindow)
