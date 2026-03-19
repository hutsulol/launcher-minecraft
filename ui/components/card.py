"""Server / mode card component for Lungi Launcher.

Each card renders from a data dict — no hardcoded content in the widget.
"""

import tkinter as tk
from ui.theme import (
    BG_CARD, BG_CARD_HOVER, GOLD, GOLD_DIM, FG_TEXT, FG_MUTED,
    FONT_CARD_TITLE, FONT_CARD_SUB, FONT_TINY,
    CARD_WIDTH, CARD_HEIGHT,
    draw_rounded_rect,
)


class ServerCard(tk.Canvas):
    """A clickable server/mode card drawn on Canvas for rounded corners.

    server_data: dict with keys title, desc, icon, players.
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

        self._draw()

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

    def _draw(self):
        """Draw the card contents based on server_data."""
        self.delete("all")
        w, h = CARD_WIDTH, CARD_HEIGHT
        d = self.server_data

        # Choose fill and border based on state
        if self.is_selected:
            fill, border = BG_CARD_HOVER, GOLD
        elif self._hovered:
            fill, border = BG_CARD_HOVER, GOLD_DIM
        else:
            fill, border = BG_CARD, "#334155"

        # Card background
        draw_rounded_rect(self, 2, 2, w - 2, h - 2, radius=14,
                          fill=fill, outline=border, width=2)

        # Glow border for selected card
        if self.is_selected:
            draw_rounded_rect(self, 0, 0, w, h, radius=16,
                              fill="", outline=GOLD_DIM, width=1)

        # Icon
        icon = d.get("icon", "\u2693")
        self.create_text(w // 2, 40, text=icon, font=("Arial", 28),
                         fill=GOLD if self.is_selected else FG_MUTED)

        # Title
        self.create_text(w // 2, 80, text=d.get("title", ""),
                         font=FONT_CARD_TITLE, fill=FG_TEXT)

        # Description
        self.create_text(w // 2, 102, text=d.get("desc", ""),
                         font=FONT_CARD_SUB, fill=FG_MUTED)

        # Player count
        players = d.get("players", 0)
        player_text = f"\u25CF {players:,} online"
        self.create_text(w // 2, 135, text=player_text, font=FONT_TINY,
                         fill="#10b981" if players > 0 else FG_MUTED)

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
