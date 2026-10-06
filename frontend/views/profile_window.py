"""
views/profile_window.py
--------------------------
Screen 10: User Profile
Sidebar + profile card with avatar, real account stats (watchlist
count, joined date), and an editable name/email form persisted via
UserController.update_profile().
"""

import customtkinter as ctk
from config import Colors, Fonts
from frontend.widgets.sidebar import Sidebar
from frontend.widgets.custom_widgets import SectionHeader, Card, PrimaryButton, LabeledEntry
from frontend.widgets.dialogs import show_error, show_success
from backend.utils.image_loader import get_avatar_image
from backend.utils.nav_config import build_nav_items
from backend.controllers.user_controller import UserController, UserError


class ProfileWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, user=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller
        self.user = user or {}

        nav_items = build_nav_items(self.user)
        Sidebar(self, controller, nav_items, active_label="Profile",
                user=self.user).pack(side="left", fill="y")

        main = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        main.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 10))
        SectionHeader(header, title="My Profile",
                      subtitle="Manage your account information").pack(fill="x")

        content = ctk.CTkFrame(main, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=32, pady=(10, 24))

        # ---- Profile summary card ----
        summary_card = Card(content, width=280)
        summary_card.pack(side="left", fill="y", padx=(0, 24))
        summary_card.pack_propagate(False)

        avatar_img = get_avatar_image(self.user.get("full_name", "Guest User"), size=110)
        ctk.CTkLabel(summary_card, image=avatar_img, text="").pack(pady=(32, 14))

        ctk.CTkLabel(summary_card, text=self.user.get("full_name", "Guest User"),
                     font=Fonts.H3, text_color=Colors.TEXT_PRIMARY).pack()
        ctk.CTkLabel(summary_card, text=self.user.get("email", ""),
                     font=Fonts.SMALL, text_color=Colors.TEXT_MUTED).pack(pady=(2, 20))

        stats_row = ctk.CTkFrame(summary_card, fg_color="transparent")
        stats_row.pack(pady=(0, 20))
        self._stat(stats_row, str(self.user.get("watchlist_count", 0)), "Watchlist")
        self._stat(stats_row, self.user.get("joined", "—"), "Joined")

        role_badge = ctk.CTkLabel(
            summary_card, text=f"  {self.user.get('role', 'user').upper()}  ",
            fg_color=Colors.SURFACE_LIGHT, text_color=Colors.SECONDARY,
            corner_radius=8, font=("Segoe UI", 11, "bold")
        )
        role_badge.pack()

        # ---- Edit form card ----
        form_card = Card(content)
        form_card.pack(side="left", fill="both", expand=True)

        form_inner = ctk.CTkFrame(form_card, fg_color="transparent")
        form_inner.pack(fill="both", expand=True, padx=32, pady=32)

        ctk.CTkLabel(form_inner, text="Account Details", font=Fonts.H3,
                     text_color=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x", pady=(0, 20))

        self.name_entry = LabeledEntry(form_inner, "Full Name", width=340)
        self.name_entry.set(self.user.get("full_name", ""))
        self.name_entry.pack(pady=(0, 16))

        self.email_entry = LabeledEntry(form_inner, "Email", width=340)
        self.email_entry.set(self.user.get("email", ""))
        self.email_entry.pack(pady=(0, 24))

        PrimaryButton(form_inner, text="Save Changes", width=200,
                      command=self._save_profile).pack(anchor="w")

    def _stat(self, parent, value, label):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(side="left", padx=14)
        ctk.CTkLabel(box, text=value, font=Fonts.H3, text_color=Colors.SECONDARY).pack()
        ctk.CTkLabel(box, text=label, font=Fonts.SMALL, text_color=Colors.TEXT_MUTED).pack()

    def _save_profile(self):
        user_id = self.user.get("id")
        if not user_id:
            show_error(self, "Not Logged In", "Please log in to edit your profile.")
            return

        payload = {
            "full_name": self.name_entry.get(),
            "email": self.email_entry.get(),
        }
        try:
            updated_user = UserController.update_profile(user_id, payload)
        except UserError as e:
            show_error(self, "Update Failed", str(e))
            return

        show_success(self, "Profile Updated", "Your account details were saved successfully.")
        # Re-render this screen with the fresh user data so the
        # Sidebar/summary card reflect the new name/email immediately.
        self.controller.show_view(ProfileWindow, remember_history=False, user=updated_user)
