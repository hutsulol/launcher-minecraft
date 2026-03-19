"""Image-based server / mode card component for Lungi Launcher.

Each card uses a PNG background image loaded from the assets folder.
Text is drawn on top of the image. Fully data-driven — no hardcoded content.
"""

import os
import tkinter as tk

from PIL import Image, ImageTk

from ui.theme import (
    GOLD, GOLD_DIM, FG_TEXT, FG_MUTED,
    FONT_CARD_TITLE, FONT_CARD_SUB, FONT_TINY,
    CARD_WIDTH, CARD_HEIGHT,
)


class ServerCard(tk.Canvas):
    """A clickable server/mode card with a PNG background image.

    server_data: dict with keys title, desc, image, players.
    on_select:   callback(server_data) when clicked.
    """

    def __init__(self, master, server_data, on_select, is_selected=False):
        super().__init__(
            master, width=CARD_WIDTH, height=CARD_HEIGHT,
            bg=master["bg"], highlightthickness=0, bd=0,
        )
        self.server_data = server_data
        self.on_select = on_select
        self.is_selected = is_selected
        self._hovered = False

        # Keep reference to prevent garbage collection
        self._bg_image = None
        self._load_image()
        self._draw()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _load_image(self):
        """Load and resize the background PNG image."""
        image_path = self.server_data.get("image", "")
        if image_path and os.path.isfile(image_path):
            img = Image.open(image_path)
            img = img.resize((CARD_WIDTH, CARD_HEIGHT), Image.LANCZOS)
            self._bg_image = ImageTk.PhotoImage(img)
        else:
            # Fallback: create a solid dark image if file missing
            img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), (30, 41, 59))
            self._bg_image = ImageTk.PhotoImage(img)

    def _draw(self):
        """Draw the card: background image + text overlay."""
        self.delete("all")
        w, h = CARD_WIDTH, CARD_HEIGHT

        # Background image
        self.create_image(0, 0, image=self._bg_image, anchor="nw")

        # Semi-transparent overlay effect for text readability (dark gradient at bottom)
        # Drawn as a series of dark lines with increasing opacity
        for y in range(h // 3, h):
            alpha = int(180 * (y - h // 3) / (h - h // 3))
            gray = max(0, 2 - alpha // 90)
            color = f"#{gray:02x}{gray:02x}{gray + 3:02x}"
            self.create_line(0, y, w, y, fill=color, stipple="gray50")

        d = self.server_data

        # Title (centered, near bottom)
        self.create_text(
            w // 2, h - 55, text=d.get("title", ""),
            font=FONT_CARD_TITLE, fill=FG_TEXT,
        )

        # Description / subtitle
        self.create_text(
            w // 2, h - 35, text=d.get("desc", ""),
            font=FONT_CARD_SUB, fill=FG_MUTED,
        )

        # Player count (bottom)
        players = d.get("players", 0)
        player_text = f"\u25cf {players:,} online"
        self.create_text(
            w // 2, h - 15, text=player_text, font=FONT_TINY,
            fill="#10b981" if players > 0 else FG_MUTED,
        )

        # Border highlight for hover / selected state
        if self.is_selected:
            self.create_rectangle(
                1, 1, w - 1, h - 1,
                outline=GOLD, width=3,
            )
        elif self._hovered:
            self.create_rectangle(
                1, 1, w - 1, h - 1,
                outline=GOLD_DIM, width=2,
            )

    def set_selected(self, selected):
        """Update selection state and redraw."""
        self.is_selected = selected
        self._draw()

    def _on_enter(self, _event):
        self._hovered = True
        self._draw()

    def _on_leave(self, _event):
        self._hovered = False
        self._draw()

    def _on_click(self, _event):
        self.on_select(self.server_data)
