"""Image-based banner component for Lungi Launcher.

Loads a PNG background from assets/banner.png, draws text on top.
Falls back to a solid color if the image is missing.
"""

import os
import sys
import tkinter as tk

from PIL import Image, ImageTk, ImageEnhance

from ui.theme import (
    BG_DEEP, GOLD, GOLD_DIM, FG_MUTED,
    FONT_BANNER_BIG, FONT_BANNER_SUB,
    WIN_WIDTH,
)

DEBUG = ("--debug" in sys.argv)

# Resolve project root (two levels up from this file)
_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
BANNER_IMAGE_PATH = os.path.join(_PROJECT_ROOT, "assets", "banner.png")

DEFAULT_BANNER = {
    "title": "\u2620  New Season Available",
    "subtitle": "Sail into Adventure  \u2014  Explore new waters, find buried treasure",
    "icon": "\u2693",
    "badge": "NEW",
}


class Banner(tk.Canvas):
    """A data-driven announcement banner with PNG background."""

    def __init__(self, master, data=None, width=None, height=130):
        self._banner_w = (width or WIN_WIDTH) - 40
        self._banner_h = height
        super().__init__(
            master, width=self._banner_w, height=self._banner_h,
            bg=BG_DEEP, highlightthickness=0, bd=0,
        )
        self._data = data or DEFAULT_BANNER

        # Image references — stored on self to prevent GC
        self._src_image = None
        self._bg_photo_normal = None
        self._bg_photo_hover = None
        self._image_loaded = False

        self._load_image()
        self._hovered = False
        self._draw()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _load_image(self):
        """Load and resize the banner background image."""
        w, h = self._banner_w, self._banner_h
        try:
            if os.path.isfile(BANNER_IMAGE_PATH):
                img = Image.open(BANNER_IMAGE_PATH).convert("RGB")
                img = img.resize((w, h), Image.LANCZOS)
                self._image_loaded = True
                if DEBUG:
                    print(f"[Banner] Loaded: {BANNER_IMAGE_PATH}")
            else:
                if DEBUG:
                    print(f"[Banner] Not found: {BANNER_IMAGE_PATH}, using fallback")
                img = Image.new("RGB", (w, h), (12, 26, 61))
        except Exception as exc:
            print(f"[Banner] ERROR loading image: {exc}")
            img = Image.new("RGB", (w, h), (12, 26, 61))

        self._src_image = img
        # Pre-build both normal and hover photos once (avoids re-creating on every draw)
        self._bg_photo_normal = ImageTk.PhotoImage(img)
        try:
            enhanced = ImageEnhance.Brightness(img).enhance(1.15)
            self._bg_photo_hover = ImageTk.PhotoImage(enhanced)
        except Exception:
            self._bg_photo_hover = self._bg_photo_normal

    def update_data(self, data):
        """Replace banner content and redraw."""
        self._data = data
        self._draw()

    def _draw(self):
        self.delete("all")
        w = self._banner_w
        h = self._banner_h
        d = self._data

        # Background image — use pre-built photo (no new allocations)
        photo = self._bg_photo_hover if self._hovered else self._bg_photo_normal
        if photo:
            self.create_image(0, 0, image=photo, anchor="nw")
        else:
            # Ultimate fallback: solid rectangle
            self.create_rectangle(0, 0, w, h, fill="#0c1a3d", outline="")

        # Border
        border_color = GOLD if self._hovered else GOLD_DIM
        self.create_rectangle(1, 1, w - 1, h - 1, outline=border_color, width=1)

        # Left icon
        icon = d.get("icon", "")
        if icon:
            self.create_text(61, h // 2 - 4, text=icon,
                             font=("Arial", 44), fill="#000000")
            self.create_text(60, h // 2 - 5, text=icon,
                             font=("Arial", 44), fill=GOLD_DIM)

        # Title with shadow
        title = d.get("title", "")
        self.create_text(w // 2 + 1, h // 2 - 19, text=title,
                         font=FONT_BANNER_BIG, fill="#000000")
        self.create_text(w // 2, h // 2 - 20, text=title,
                         font=FONT_BANNER_BIG, fill=GOLD)

        # Subtitle with shadow
        subtitle = d.get("subtitle", "")
        self.create_text(w // 2 + 1, h // 2 + 13, text=subtitle,
                         font=FONT_BANNER_SUB, fill="#000000")
        self.create_text(w // 2, h // 2 + 12, text=subtitle,
                         font=FONT_BANNER_SUB, fill=FG_MUTED)

        # Badge
        badge = d.get("badge")
        if badge:
            bx = w - 60
            self.create_rectangle(bx - 22, 14, bx + 22, 36, fill=GOLD, outline="")
            self.create_text(bx, 25, text=badge,
                             font=("Arial", 10, "bold"), fill="#020617")

    def _on_enter(self, _event):
        self._hovered = True
        self._draw()

    def _on_leave(self, _event):
        self._hovered = False
        self._draw()
