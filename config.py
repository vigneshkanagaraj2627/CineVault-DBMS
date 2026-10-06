"""
config.py
----------
Global application configuration for CineVault.
Holds window settings, appearance mode, and shared constants
so every view stays visually consistent.
"""

import customtkinter as ctk


class AppConfig:
    """Static configuration values for the whole application."""

    # ---------- General ----------
    APP_NAME = "CineVault"
    APP_VERSION = "2.0.0 (MongoDB Integrated)"

    # ---------- Window ----------
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 750
    MIN_WIDTH = 1000
    MIN_HEIGHT = 650

    # ---------- Appearance ----------
    APPEARANCE_MODE = "dark"        # "dark" / "light" / "system"
    COLOR_THEME = "dark-blue"       # base ctk theme, colors are overridden below

    @staticmethod
    def apply_appearance():
        ctk.set_appearance_mode(AppConfig.APPEARANCE_MODE)
        ctk.set_default_color_theme(AppConfig.COLOR_THEME)


class Colors:
    """Netflix/IMDb-inspired dark color palette."""

    BACKGROUND = "#0F0F0F"          # near-black app background
    SURFACE = "#1A1A1A"             # cards / panels
    SURFACE_LIGHT = "#232323"       # hover / secondary panels
    SIDEBAR = "#141414"

    PRIMARY = "#E50914"             # Netflix red (accent / CTA buttons)
    PRIMARY_HOVER = "#B20710"

    SECONDARY = "#F5C518"           # IMDb gold (ratings / highlights)
    SECONDARY_HOVER = "#D4A913"

    TEXT_PRIMARY = "#FFFFFF"
    TEXT_SECONDARY = "#B3B3B3"
    TEXT_MUTED = "#7A7A7A"

    SUCCESS = "#2ECC71"
    WARNING = "#F39C12"
    ERROR = "#E74C3C"

    BORDER = "#2E2E2E"
    ENTRY_BG = "#1F1F1F"


class Fonts:
    """Reusable font tuples. CTkFont objects are created lazily inside
    windows since they need an active Tk root, but these tuples work
    as safe fallbacks anywhere."""

    FAMILY = "Segoe UI"          # Falls back gracefully on non-Windows
    FAMILY_HEADING = "Segoe UI Semibold"

    H1 = (FAMILY_HEADING, 32, "bold")
    H2 = (FAMILY_HEADING, 24, "bold")
    H3 = (FAMILY_HEADING, 18, "bold")
    BODY = (FAMILY, 14)
    BODY_BOLD = (FAMILY, 14, "bold")
    SMALL = (FAMILY, 12)
    BUTTON = (FAMILY, 14, "bold")
    LOGO = (FAMILY_HEADING, 40, "bold")
