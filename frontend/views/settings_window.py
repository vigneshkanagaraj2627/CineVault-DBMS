"""
views/settings_window.py
---------------------------
Screen 15: Settings Window
Sidebar + toggles for appearance/notifications (dummy, non-persistent)
and a change-password form placeholder.
"""

import customtkinter as ctk
from config import Colors, Fonts
from frontend.widgets.sidebar import Sidebar
from frontend.widgets.custom_widgets import SectionHeader, Card, PrimaryButton, LabeledEntry
from frontend.widgets.dialogs import show_error, show_success
from backend.utils.nav_config import build_nav_items
from backend.controllers.user_controller import UserController, UserError


class SettingsWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, user=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller
        self.user = user or {}

        nav_items = build_nav_items(self.user)
        Sidebar(self, controller, nav_items, active_label="Settings",
                user=self.user).pack(side="left", fill="y")

        main_scroll = ctk.CTkScrollableFrame(self, fg_color=Colors.BACKGROUND,
                                              scrollbar_button_color=Colors.SURFACE_LIGHT)
        main_scroll.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main_scroll, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 20))
        SectionHeader(header, title="Settings",
                      subtitle="Customize your CineVault experience").pack(fill="x")

        # ---- Appearance card ----
        appearance_card = Card(main_scroll)
        appearance_card.pack(fill="x", padx=32, pady=(0, 20))
        inner1 = ctk.CTkFrame(appearance_card, fg_color="transparent")
        inner1.pack(fill="x", padx=28, pady=24)

        ctk.CTkLabel(inner1, text="Appearance", font=Fonts.H3,
                     text_color=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x", pady=(0, 16))

        self._toggle_row(inner1, "Dark Mode", "Always on for this preview build", default=True, disabled=True)
        self._toggle_row(inner1, "Compact Movie Cards", "Show more movies per row")

        # ---- Notifications card ----
        notif_card = Card(main_scroll)
        notif_card.pack(fill="x", padx=32, pady=(0, 20))
        inner2 = ctk.CTkFrame(notif_card, fg_color="transparent")
        inner2.pack(fill="x", padx=28, pady=24)

        ctk.CTkLabel(inner2, text="Notifications", font=Fonts.H3,
                     text_color=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x", pady=(0, 16))

        self._toggle_row(inner2, "New Release Alerts", "Get notified about new movies", default=True)
        self._toggle_row(inner2, "Recommendation Emails", "Weekly picks based on your taste")

        # ---- Security card ----
        security_card = Card(main_scroll)
        security_card.pack(fill="x", padx=32, pady=(0, 32))
        inner3 = ctk.CTkFrame(security_card, fg_color="transparent")
        inner3.pack(fill="x", padx=28, pady=24)

        ctk.CTkLabel(inner3, text="Change Password", font=Fonts.H3,
                     text_color=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x", pady=(0, 16))

        self.current_pw = LabeledEntry(inner3, "Current Password", show="•", width=340)
        self.current_pw.pack(pady=(0, 14))
        self.new_pw = LabeledEntry(inner3, "New Password", show="•", width=340)
        self.new_pw.pack(pady=(0, 20))

        PrimaryButton(inner3, text="Save Settings", width=200,
                      command=self._save_settings).pack(anchor="w")

    def _toggle_row(self, parent, title, subtitle, default=False, disabled=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=8)

        text_box = ctk.CTkFrame(row, fg_color="transparent")
        text_box.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(text_box, text=title, font=Fonts.BODY_BOLD,
                     text_color=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        ctk.CTkLabel(text_box, text=subtitle, font=Fonts.SMALL,
                     text_color=Colors.TEXT_MUTED, anchor="w").pack(fill="x")

        switch = ctk.CTkSwitch(row, text="", progress_color=Colors.PRIMARY)
        if default:
            switch.select()
        if disabled:
            switch.configure(state="disabled")
        switch.pack(side="right")

    def _save_settings(self):
        user_id = self.user.get("id")
        if not user_id:
            show_error(self, "Not Logged In", "Please log in to change settings.")
            return

        current_password = self.current_pw.get()
        new_password = self.new_pw.get()

        try:
            UserController.update_settings(user_id, {
                "current_password": current_password,
                "new_password": new_password,
            })
        except UserError as e:
            show_error(self, "Settings Not Saved", str(e))
            return

        if current_password or new_password:
            self.current_pw.set("")
            self.new_pw.set("")
            show_success(self, "Password Updated", "Your password was changed successfully.")
        else:
            show_success(self, "Settings Saved", "Your preferences were saved.")
