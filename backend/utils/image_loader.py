"""
image_loader.py
-----------------
Generates placeholder poster / avatar images using Pillow since we
have no real image assets or backend yet. Results are cached in
memory so repeated calls for the same movie/user don't regenerate
the image every time a screen redraws.
"""

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

from config import Colors

_CACHE = {}

# A small rotating palette so placeholder posters look distinct
_PALETTE = [
    "#3B3B98", "#B33939", "#227093", "#218C74",
    "#B71540", "#0C2461", "#6F1E51", "#833471",
]


def _get_font(size: int):
    """Try to load a nice system font, fall back to default."""
    for name in ("arialbd.ttf", "DejaVuSans-Bold.ttf", "Arial Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def get_poster_image(title: str, width: int = 220, height: int = 320) -> ctk.CTkImage:
    """
    Returns a CTkImage placeholder poster with the movie's initials
    on a colored background, mimicking a poster thumbnail.
    """
    cache_key = f"poster_{title}_{width}_{height}"
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    color_index = sum(ord(c) for c in title) % len(_PALETTE)
    bg_color = _PALETTE[color_index]

    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Draw a subtle darker gradient band at the bottom for a "poster" feel
    band_height = int(height * 0.28)
    for i in range(band_height):
        alpha = i / band_height
        shade = tuple(int(c * (1 - alpha * 0.6)) for c in img.getpixel((0, height - band_height + i)))
        draw.line([(0, height - band_height + i), (width, height - band_height + i)], fill=shade)

    # Initials / short label in the center
    initials = "".join([w[0].upper() for w in title.split()[:2]])
    font_big = _get_font(int(width * 0.22))
    bbox = draw.textbbox((0, 0), initials, font=font_big)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - tw) / 2, (height * 0.38) - th / 2), initials,
               fill="#FFFFFF", font=font_big)

    # Title text near the bottom band
    font_small = _get_font(int(width * 0.075))
    title_display = title if len(title) < 18 else title[:16] + "…"
    bbox2 = draw.textbbox((0, 0), title_display, font=font_small)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((width - tw2) / 2, height - band_height + 8), title_display,
               fill="#FFFFFF", font=font_small)

    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(width, height))
    _CACHE[cache_key] = ctk_img
    return ctk_img


def get_avatar_image(name: str, size: int = 100) -> ctk.CTkImage:
    """Returns a circular-style placeholder avatar with the user's initials."""
    cache_key = f"avatar_{name}_{size}"
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    color_index = sum(ord(c) for c in name) % len(_PALETTE)
    bg_color = _PALETTE[color_index]

    img = Image.new("RGB", (size, size), color=bg_color)
    draw = ImageDraw.Draw(img)

    initials = "".join([w[0].upper() for w in name.split()[:2]]) or "U"
    font = _get_font(int(size * 0.4))
    bbox = draw.textbbox((0, 0), initials, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) / 2, (size - th) / 2 - 4), initials,
               fill="#FFFFFF", font=font)

    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
    _CACHE[cache_key] = ctk_img
    return ctk_img


def get_logo_placeholder(width: int = 260, height: int = 90) -> ctk.CTkImage:
    """Simple CineVault wordmark-style placeholder for splash/login screens."""
    cache_key = f"logo_{width}_{height}"
    if cache_key in _CACHE:
        return _CACHE[cache_key]

    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _get_font(int(height * 0.5))
    text = "CineVault"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width - tw) / 2, (height - th) / 2 - 6), text,
               fill=Colors.PRIMARY, font=font)

    ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(width, height))
    _CACHE[cache_key] = ctk_img
    return ctk_img
