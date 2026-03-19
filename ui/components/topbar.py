"""Top bar component for Lungi Launcher."""

import tkinter as tk
from ui.theme import (
    BG_TOPBAR, GOLD, GOLD_DIM, FG_TEXT, FG_MUTED,
    FONT_LOGO, FONT_SMALL,
)


class TopBar(tk.Frame):
    """Top navigation bar with logo, settings, and logout buttons."""

    def __init__(self, master, username, on_settings=None, on_logout=None):
        super().__init__(master, bg=BG_TOPBAR, height=50)
        self.pack_propagate(False)

        # -- Left side: logo --
        left = tk.Frame(self, bg=BG_TOPBAR)
        left.pack(side="left", padx=15)

        # Anchor icon + name
        tk.Label(
            left, text="\u2693", font=("Arial", 18), fg=GOLD, bg=BG_TOPBAR,
        ).pack(side="left")
        tk.Label(
            left, text=" Lungi Launcher", font=FONT_LOGO, fg=GOLD, bg=BG_TOPBAR,
        ).pack(side="left", padx=(2, 0))

        # -- Right side: user + buttons --
        right = tk.Frame(self, bg=BG_TOPBAR)
        right.pack(side="right", padx=15)

        # Username label
        tk.Label(
            right, text=f"\u2694 {username}", font=FONT_SMALL,
            fg=FG_MUTED, bg=BG_TOPBAR,
        ).pack(side="left", padx=(0, 12))

        # Settings button
        if on_settings:
            self._make_topbar_btn(right, "\u2699 Settings", on_settings).pack(
                side="left", padx=4
            )

        # Logout button
        if on_logout:
            self._make_topbar_btn(right, "Logout", on_logout, fg="#ef4444").pack(
                side="left", padx=4
            )

    @staticmethod
    def _make_topbar_btn(parent, text, command, fg=FG_TEXT):
        """Create a minimal flat button for the top bar."""
        return tk.Button(
            parent, text=text, command=command,
            font=("Arial", 9), fg=fg, bg=BG_TOPBAR,
            activebackground=BG_TOPBAR, activeforeground=GOLD,
            relief="flat", bd=0, cursor="hand2", padx=6, pady=2,
        )
