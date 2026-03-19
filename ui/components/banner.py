"""Reusable banner component for Lungi Launcher.

Renders a banner from a data dict, not hardcoded content.
"""

import tkinter as tk
from ui.theme import (
    BG_DEEP, GOLD, GOLD_DIM, FG_MUTED,
    FONT_BANNER_BIG, FONT_BANNER_SUB,
    WIN_WIDTH, draw_rounded_rect,
)

# Banner data — change this dict (or load from JSON) to update the banner.
DEFAULT_BANNER = {
    "title": "\u2620  New Season Available",
    "subtitle": "Sail into Adventure  \u2014  Explore new waters, find buried treasure",
    "icon": "\u2693",
    "badge": "NEW",
}


class Banner(tk.Canvas):
    """A data-driven announcement banner drawn on Canvas."""

    def __init__(self, master, data=None, width=None, height=130):
        self._banner_w = (width or WIN_WIDTH) - 40  # padded width
        self._banner_h = height
        super().__init__(
            master, width=self._banner_w, height=self._banner_h,
            bg=BG_DEEP, highlightthickness=0, bd=0,
        )
        self._data = data or DEFAULT_BANNER
        self._draw()

    def update_data(self, data):
        """Replace banner content and redraw."""
        self._data = data
        self._draw()

    def _draw(self):
        self.delete("all")
        w = self._banner_w
        h = self._banner_h
        d = self._data

        # Background rounded rect
        draw_rounded_rect(self, 0, 0, w, h, radius=16,
                          fill="#0c1a3d", outline="#1e3a5f", width=1)
        draw_rounded_rect(self, 3, 3, w - 3, h - 3, radius=14,
                          fill="", outline="#1e3a5f", width=1)

        # Left icon
        icon = d.get("icon", "")
        if icon:
            self.create_text(60, h // 2 - 5, text=icon,
                             font=("Arial", 44), fill=GOLD_DIM)

        # Title and subtitle
        self.create_text(w // 2, h // 2 - 20, text=d.get("title", ""),
                         font=FONT_BANNER_BIG, fill=GOLD)
        self.create_text(w // 2, h // 2 + 12, text=d.get("subtitle", ""),
                         font=FONT_BANNER_SUB, fill=FG_MUTED)

        # Badge (optional)
        badge = d.get("badge")
        if badge:
            bx = w - 60
            draw_rounded_rect(self, bx - 22, 14, bx + 22, 36, radius=8,
                              fill=GOLD, outline="")
            self.create_text(bx, 25, text=badge,
                             font=("Arial", 10, "bold"), fill="#020617")
