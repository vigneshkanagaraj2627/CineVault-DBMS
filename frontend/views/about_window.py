"""
views/about_window.py
------------------------
Screen 16: About Window
Sidebar + static info about the project (name, version, tech stack,
team/college project note). Purely informational.
"""

import customtkinter as ctk
from config import Colors, Fonts, AppConfig
from frontend.widgets.sidebar import Sidebar
from frontend.widgets.custom_widgets import SectionHeader, Card
from backend.utils.image_loader import get_logo_placeholder
from backend.utils.nav_config import build_nav_items


class AboutWindow(ctk.CTkFrame):
    def __init__(self, parent, controller, user=None, **kwargs):
        super().__init__(parent, fg_color=Colors.BACKGROUND, **kwargs)
        self.controller = controller
        self.user = user or {}

        nav_items = build_nav_items(self.user)
        Sidebar(self, controller, nav_items, active_label="About",
                user=self.user).pack(side="left", fill="y")

        main = ctk.CTkFrame(self, fg_color=Colors.BACKGROUND)
        main.pack(side="left", fill="both", expand=True)

        header = ctk.CTkFrame(main, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(28, 10))
        SectionHeader(header, title="About CineVault").pack(fill="x")

        card = Card(main)
        card.pack(fill="both", expand=True, padx=32, pady=(10, 32))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        logo_img = get_logo_placeholder(width=300, height=100)
        ctk.CTkLabel(inner, image=logo_img, text="").pack(pady=(0, 8))

        ctk.CTkLabel(inner, text=f"Version {AppConfig.APP_VERSION}",
                     font=Fonts.SMALL, text_color=Colors.TEXT_MUTED).pack(pady=(0, 24))

        ctk.CTkLabel(
            inner,
            text="CineVault is a Movie Recommendation System built as a\n"
                 "DBMS Mini Project, showcasing a modular MVC desktop\n"
                 "application backed by a real MongoDB database.",
            font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY, justify="center"
        ).pack(pady=(0, 24))

        tech_frame = ctk.CTkFrame(inner, fg_color="transparent")
        tech_frame.pack(pady=(0, 24))
        for tech in ["Python", "CustomTkinter", "Pillow", "MongoDB", "PyMongo", "bcrypt"]:
            ctk.CTkLabel(
                tech_frame, text=f"  {tech}  ",
                fg_color=Colors.SURFACE_LIGHT, text_color=Colors.SECONDARY,
                corner_radius=8, font=("Segoe UI", 12, "bold")
            ).pack(side="left", padx=6)

        ctk.CTkLabel(
            inner, text="Developed as a college DBMS Mini Project.",
            font=Fonts.SMALL, text_color=Colors.TEXT_MUTED
        ).pack()
