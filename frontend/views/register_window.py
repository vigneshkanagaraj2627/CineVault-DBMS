"""
views/register_window.py
---------------------------
Screen 3: Registration Window
Real MongoDB-backed signup via AuthController (bcrypt-hashed
password, duplicate-email check). On success, logs the new user in
and routes to the Dashboard.
"""

import customtkinter as ctk
from config import Colors, Fonts
from frontend.widgets.custom_widgets import PrimaryButton, SecondaryButton, LabeledEntry
from frontend.widgets.dialogs import show_error
from backend.utils.image_loader import get_logo_placeholder
from backend.controllers.auth_controller import AuthController, AuthError


class RegisterWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller

        left_panel = ctk.CTkFrame(self, fg_color=Colors.SURFACE, corner_radius=0)
        left_panel.pack(side="left", fill="both", expand=True)

        right_panel = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND, corner_radius=0, width=480)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        left_center = ctk.CTkFrame(left_panel, fg_color="transparent")
        left_center.place(relx=0.5, rely=0.5, anchor="center")
        logo_img = get_logo_placeholder(width=340, height=110)
        ctk.CTkLabel(left_center, image=logo_img, text="").pack(pady=(0, 16))
        ctk.CTkLabel(
            left_center, text="Join CineVault today.\nBuild your own watchlist in seconds.",
            text_color=Colors.TEXT_SECONDARY, font=("Segoe UI", 15), justify="center"
        ).pack()

        # Scrollable form (in case of small windows)
        form_scroll = ctk.CTkScrollableFrame(right_panel, fg_color="transparent",
                                              scrollbar_button_color=Colors.SURFACE_LIGHT)
        form_scroll.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(form_scroll, text="Create Account", font=Fonts.H2,
                     text_color=Colors.TEXT_PRIMARY).pack(pady=(0, 4), anchor="w")
        ctk.CTkLabel(form_scroll, text="Sign up to start building your watchlist",
                     font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY).pack(pady=(0, 24), anchor="w")

        self.name_entry = LabeledEntry(form_scroll, "Full Name", "Enter your full name", width=320)
        self.name_entry.pack(pady=(0, 14))

        self.email_entry = LabeledEntry(form_scroll, "Email", "Enter your email", width=320)
        self.email_entry.pack(pady=(0, 14))

        self.password_entry = LabeledEntry(form_scroll, "Password", "Create a password", show="•", width=320)
        self.password_entry.pack(pady=(0, 14))

        self.confirm_entry = LabeledEntry(form_scroll, "Confirm Password", "Re-enter your password", show="•", width=320)
        self.confirm_entry.pack(pady=(0, 8))

        self.error_label = ctk.CTkLabel(form_scroll, text="", text_color=Colors.ERROR, font=Fonts.SMALL)
        self.error_label.pack(anchor="w", pady=(0, 10))

        PrimaryButton(form_scroll, text="Register", width=320, command=self._handle_register).pack(pady=(6, 12))
        SecondaryButton(form_scroll, text="Back to Login", width=320,
                         command=self._go_to_login).pack()

    def _handle_register(self):
        name = self.name_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        self.error_label.configure(text="")

        try:
            new_user = AuthController.register(name, email, password, confirm)
        except AuthError as e:
            show_error(self, "Registration Failed", str(e))
            return
        except Exception as e:
            show_error(self, "Unexpected Error", f"Something went wrong while registering.\n\n{e}")
            return

        from frontend.views.dashboard_window import DashboardWindow
        self.controller.show_view(DashboardWindow, user=new_user)

    def _go_to_login(self):
        from frontend.views.login_window import LoginWindow
        self.controller.show_view(LoginWindow)
