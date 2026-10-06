"""
views/login_window.py
------------------------
Screen 2: Login Window
Real MongoDB-backed login via AuthController. Routes to the User
Dashboard or Admin Dashboard based on the account's stored role.
"""

import customtkinter as ctk
from config import Colors, Fonts
from frontend.widgets.custom_widgets import PrimaryButton, LabeledEntry
from frontend.widgets.dialogs import show_error
from backend.utils.image_loader import get_logo_placeholder
from backend.controllers.auth_controller import AuthController, AuthError


class LoginWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller

        # ---- Split layout: left branding panel / right form panel ----
        left_panel = ctk.CTkFrame(self, fg_color=Colors.SURFACE, corner_radius=0)
        left_panel.pack(side="left", fill="both", expand=True)

        right_panel = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND, corner_radius=0, width=460)
        right_panel.pack(side="right", fill="y")
        right_panel.pack_propagate(False)

        # ---- Left branding content ----
        left_center = ctk.CTkFrame(left_panel, fg_color="transparent")
        left_center.place(relx=0.5, rely=0.5, anchor="center")

        logo_img = get_logo_placeholder(width=340, height=110)
        ctk.CTkLabel(left_center, image=logo_img, text="").pack(pady=(0, 16))
        ctk.CTkLabel(
            left_center,
            text="Discover movies tailored to your taste.\nTrack, rate, and revisit your favorites.",
            text_color=Colors.TEXT_SECONDARY, font=("Segoe UI", 15),
            justify="center"
        ).pack()

        # ---- Right form content ----
        form = ctk.CTkFrame(right_panel, fg_color="transparent")
        form.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(form, text="Welcome Back", font=Fonts.H2,
                     text_color=Colors.TEXT_PRIMARY).pack(pady=(0, 4), anchor="w")
        ctk.CTkLabel(form, text="Login to continue to CineVault",
                     font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY).pack(pady=(0, 28), anchor="w")

        self.email_entry = LabeledEntry(form, "Email", "you@example.com", width=320)
        self.email_entry.pack(pady=(0, 16))

        self.password_entry = LabeledEntry(form, "Password", "Enter your password", show="•", width=320)
        self.password_entry.pack(pady=(0, 8))
        self.password_entry.entry.bind("<Return>", lambda e: self._handle_login())

        self.error_label = ctk.CTkLabel(form, text="", text_color=Colors.ERROR, font=Fonts.SMALL,
                                         wraplength=320, justify="left")
        self.error_label.pack(anchor="w", pady=(0, 10))

        PrimaryButton(form, text="Login", width=320, command=self._handle_login).pack(pady=(10, 16))

        # ---- Divider ----
        divider_frame = ctk.CTkFrame(form, fg_color="transparent")
        divider_frame.pack(fill="x", pady=(0, 16))
        ctk.CTkFrame(divider_frame, height=1, fg_color=Colors.BORDER).pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(divider_frame, text="  or  ", text_color=Colors.TEXT_MUTED, font=Fonts.SMALL).pack(side="left")
        ctk.CTkFrame(divider_frame, height=1, fg_color=Colors.BORDER).pack(side="left", fill="x", expand=True)

        bottom_row = ctk.CTkFrame(form, fg_color="transparent")
        bottom_row.pack()
        ctk.CTkLabel(bottom_row, text="Don't have an account?",
                     text_color=Colors.TEXT_SECONDARY, font=Fonts.SMALL).pack(side="left", padx=(0, 6))
        register_link = ctk.CTkLabel(bottom_row, text="Register here",
                                      text_color=Colors.PRIMARY, font=("Segoe UI", 12, "bold"),
                                      cursor="hand2")
        register_link.pack(side="left")
        register_link.bind("<Button-1>", lambda e: self._go_to_register())

    def _handle_login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        self.error_label.configure(text="")

        try:
            user = AuthController.login(email, password)
        except AuthError as e:
            show_error(self, "Login Failed", str(e))
            return
        except Exception as e:
            show_error(self, "Unexpected Error", f"Something went wrong while logging in.\n\n{e}")
            return

        from frontend.views.dashboard_window import DashboardWindow
        from frontend.views.admin_dashboard_window import AdminDashboardWindow

        if user.get("is_admin"):
            self.controller.show_view(AdminDashboardWindow, user=user)
        else:
            self.controller.show_view(DashboardWindow, user=user)

    def _go_to_register(self):
        from frontend.views.register_window import RegisterWindow
        self.controller.show_view(RegisterWindow)
