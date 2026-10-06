"""
main.py
--------
Entry point for the CineVault desktop application.

Run with:
    python main.py

This file only sets up the root window and a shared container frame.
All actual screens live in frontend/views and are swapped in via the
NavigationController. Backend/database logic lives under backend/.
"""

import customtkinter as ctk

from config import AppConfig, Colors
from backend.utils.navigation import NavigationController
from frontend.views.splash_screen import SplashScreen


class CineVaultApp(ctk.CTk):
    """Root application window that hosts every screen."""

    def __init__(self):
        super().__init__()

        AppConfig.apply_appearance()

        self.title(AppConfig.APP_NAME)
        self.geometry(f"{AppConfig.WINDOW_WIDTH}x{AppConfig.WINDOW_HEIGHT}")
        self.minsize(AppConfig.MIN_WIDTH, AppConfig.MIN_HEIGHT)
        self.configure(fg_color=Colors.BACKGROUND)

        # Center window on screen
        self._center_window()

        # Shared container that every view is mounted into
        self.container = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND, corner_radius=0)
        self.container.pack(fill="both", expand=True)

        # Controller responsible for swapping views in/out of the container
        self.nav = NavigationController(self)

        # Launch the first screen
        self.nav.show_view(SplashScreen)

    def _center_window(self):
        self.update_idletasks()
        w, h = AppConfig.WINDOW_WIDTH, AppConfig.WINDOW_HEIGHT
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = int((screen_w - w) / 2)
        y = int((screen_h - h) / 2)
        self.geometry(f"{w}x{h}+{x}+{y}")


if __name__ == "__main__":
    app = CineVaultApp()
    app.mainloop()
