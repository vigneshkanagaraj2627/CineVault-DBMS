"""
widgets/rating_stars.py
-------------------------
Reusable star-rating widget. Converts a numeric rating on any scale
(e.g. 8.8 out of 10, or 4.5 out of 5) into a row of filled/half/empty
star glyphs plus a "X.X/scale_max" label.
"""

import customtkinter as ctk
from config import Colors


class RatingStars(ctk.CTkFrame):
    """
    Displays a star rating like ★★★★☆ based on `rating` out of
    `scale_max` (defaults to 5, but the CineVault movie dataset uses
    IMDb-style 0-10 ratings, so pass scale_max=10 there).

    Usage:
        RatingStars(parent, rating=8.8, scale_max=10, font_size=16).pack()
    """

    def __init__(self, parent, rating: float = 0.0, scale_max: float = 5,
                 max_stars: int = 5, font_size: int = 16, show_number: bool = True, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.rating = rating
        self.scale_max = scale_max or 5
        self.max_stars = max_stars

        # Normalize whatever scale the rating came in on (e.g. 0-10)
        # down to the 0-max_stars range used for drawing stars.
        normalized = (rating / self.scale_max) * max_stars if self.scale_max else 0
        stars_text = self._build_star_string(normalized, max_stars)

        self.stars_label = ctk.CTkLabel(
            self, text=stars_text,
            text_color=Colors.SECONDARY,
            font=("Segoe UI", font_size, "bold")
        )
        self.stars_label.pack(side="left")

        if show_number:
            scale_label = int(self.scale_max) if float(self.scale_max).is_integer() else self.scale_max
            self.number_label = ctk.CTkLabel(
                self, text=f"  {rating:.1f}/{scale_label}",
                text_color=Colors.TEXT_SECONDARY,
                font=("Segoe UI", font_size - 2)
            )
            self.number_label.pack(side="left")

    @staticmethod
    def _build_star_string(rating: float, max_stars: int) -> str:
        full_stars = int(rating)
        has_half = (rating - full_stars) >= 0.5
        empty_stars = max_stars - full_stars - (1 if has_half else 0)

        stars = "★" * max(full_stars, 0)
        if has_half:
            stars += "☆"  # simple half-star approximation
        stars += "☆" * max(empty_stars, 0)
        return stars
