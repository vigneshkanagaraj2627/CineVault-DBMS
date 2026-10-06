"""
widgets/custom_widgets.py
---------------------------
Small reusable UI building blocks (buttons, entries, section
headers) so every window shares the exact same look and feel
instead of re-styling widgets from scratch each time.
"""

import customtkinter as ctk
from config import Colors, Fonts


class PrimaryButton(ctk.CTkButton):
    """Solid red rounded button — used for main call-to-action actions."""

    def __init__(self, parent, text="Button", command=None, width=200, height=42, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=10,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            text_color=Colors.TEXT_PRIMARY,
            font=("Segoe UI", 14, "bold"),
            **kwargs
        )


class SecondaryButton(ctk.CTkButton):
    """Outlined / muted button — used for secondary actions like Back, Cancel."""

    def __init__(self, parent, text="Button", command=None, width=160, height=42, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=10,
            fg_color="transparent",
            hover_color=Colors.SURFACE_LIGHT,
            border_width=2,
            border_color=Colors.BORDER,
            text_color=Colors.TEXT_PRIMARY,
            font=("Segoe UI", 14, "bold"),
            **kwargs
        )


class GoldButton(ctk.CTkButton):
    """Gold accent button — used for admin/highlight actions (Add Movie, Save)."""

    def __init__(self, parent, text="Button", command=None, width=200, height=42, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=10,
            fg_color=Colors.SECONDARY,
            hover_color=Colors.SECONDARY_HOVER,
            text_color="#1A1A1A",
            font=("Segoe UI", 14, "bold"),
            **kwargs
        )


class DangerButton(ctk.CTkButton):
    """Red-outlined button used for destructive actions like Delete."""

    def __init__(self, parent, text="Delete", command=None, width=160, height=42, **kwargs):
        super().__init__(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            corner_radius=10,
            fg_color=Colors.ERROR,
            hover_color="#C0392B",
            text_color=Colors.TEXT_PRIMARY,
            font=("Segoe UI", 14, "bold"),
            **kwargs
        )


class LabeledEntry(ctk.CTkFrame):
    """A label stacked above a rounded entry field, used in forms."""

    def __init__(self, parent, label_text="Label", placeholder="", show=None,
                 width=320, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.label = ctk.CTkLabel(
            self, text=label_text,
            text_color=Colors.TEXT_SECONDARY,
            font=("Segoe UI", 13, "bold"),
            anchor="w"
        )
        self.label.pack(fill="x", pady=(0, 6))

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text=placeholder,
            width=width,
            height=42,
            corner_radius=8,
            fg_color=Colors.ENTRY_BG,
            border_color=Colors.BORDER,
            border_width=1,
            text_color=Colors.TEXT_PRIMARY,
            font=("Segoe UI", 14),
            show=show
        )
        self.entry.pack(fill="x")

    def get(self):
        return self.entry.get()

    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)


class SectionHeader(ctk.CTkFrame):
    """A page heading with optional subtitle, used at the top of each window."""

    def __init__(self, parent, title="Title", subtitle=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self.title_label = ctk.CTkLabel(
            self, text=title,
            text_color=Colors.TEXT_PRIMARY,
            font=Fonts.H2,
            anchor="w"
        )
        self.title_label.pack(fill="x")

        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                self, text=subtitle,
                text_color=Colors.TEXT_SECONDARY,
                font=Fonts.BODY,
                anchor="w"
            )
            self.subtitle_label.pack(fill="x", pady=(4, 0))


class Card(ctk.CTkFrame):
    """A generic rounded dark card container used across settings/profile/admin."""

    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color=Colors.SURFACE,
            corner_radius=14,
            border_width=1,
            border_color=Colors.BORDER,
            **kwargs
        )
