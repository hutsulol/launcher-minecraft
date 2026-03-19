"""Main launcher screen — modern game-style layout for Lungi Launcher.

Displays an image banner and animated image-based mode cards.
Clicking a card navigates to the ModeDetailsScreen.
"""

import tkinter as tk

from auth.session import save_session, clear_session
from data.loader import load_launcher_data
from ui.theme import (
    BG_DEEP, GOLD, GOLD_DIM, FG_TEXT, FG_MUTED,
    FONT_HEADING, CARD_PAD,
)
from ui.components.topbar import TopBar
from ui.components.banner import Banner
from ui.components.card import ServerCard


class LauncherScreen(tk.Frame):
    """Main menu: top bar, image banner, animated card grid.

    Clicking a card calls on_mode_select(mode_data) so the parent can
    navigate to the ModeDetailsScreen.
    """

    def __init__(self, master, username, on_logout, on_mode_select):
        super().__init__(master, bg=BG_DEEP)
        self.username = username
        self.on_logout = on_logout
        self.on_mode_select = on_mode_select

        # Load all content from data file
        self._data = load_launcher_data()
        self._modes = self._data.get("modes", [])

        # Save session for auto-login
        save_session(username)

        self._build_ui()

    # ==================================================================
    # UI construction
    # ==================================================================

    def _build_ui(self):
        # -- Top bar --
        self.topbar = TopBar(
            self, self.username,
            on_settings=self._on_settings,
            on_logout=self._handle_logout,
        )
        self.topbar.pack(fill="x")

        # Thin gold separator
        tk.Frame(self, bg=GOLD_DIM, height=1).pack(fill="x")

        # Body
        body = tk.Frame(self, bg=BG_DEEP)
        body.pack(fill="both", expand=True)

        # Banner (image-based, data-driven)
        banner_data = self._data.get("banner")
        self.banner = Banner(body, data=banner_data)
        self.banner.pack(padx=20, pady=(15, 5))

        # Mode cards
        self._build_card_section(body)

        # Hint (Canvas-drawn for visual consistency)
        hint = tk.Canvas(body, height=30, bg=BG_DEEP, highlightthickness=0, bd=0)
        hint.pack(fill="x", pady=(10, 5))
        hint.create_text(
            500, 15, text="Click a mode to see details and play",
            font=("Arial", 9), fill=FG_MUTED,
        )

    # ------------------------------------------------------------------
    # Mode cards
    # ------------------------------------------------------------------

    def _build_card_section(self, parent):
        """Build the animated card grid from loaded data."""
        # Section header drawn on Canvas
        header_canvas = tk.Canvas(
            parent, height=30, bg=BG_DEEP, highlightthickness=0, bd=0,
        )
        header_canvas.pack(fill="x", padx=30, pady=(12, 2))
        header_canvas.create_text(
            5, 15, text="\u2694  Choose Your Adventure",
            font=FONT_HEADING, fill=FG_TEXT, anchor="w",
        )

        card_frame = tk.Frame(parent, bg=BG_DEEP)
        card_frame.pack(padx=10, pady=0)

        self.card_widgets = []
        for i, mode in enumerate(self._modes):
            card = ServerCard(
                card_frame, mode,
                on_select=self._on_card_click,
                is_selected=False,
            )
            card.grid(row=0, column=i, padx=CARD_PAD // 2, pady=0)
            self.card_widgets.append(card)

    def _on_card_click(self, mode_data):
        """Navigate to the mode details screen."""
        for card in self.card_widgets:
            card.set_selected(card.server_data["title"] == mode_data["title"])
        self.on_mode_select(mode_data)

    # ------------------------------------------------------------------
    # Other actions
    # ------------------------------------------------------------------

    def _on_settings(self):
        pass  # Placeholder for future settings screen

    def _handle_logout(self):
        clear_session()
        self.on_logout()
