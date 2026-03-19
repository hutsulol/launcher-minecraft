"""Login screen for Lungi Launcher — pirate theme."""

import tkinter as tk
from auth.auth_manager import login
from ui.theme import (
    BG_DEEP, BG_DARK, GOLD, GOLD_DIM,
    FG_TEXT, FG_MUTED, FG_ERROR, FG_SUCCESS,
    BTN_PRIMARY, BTN_SECONDARY,
    FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_SMALL,
    WIN_WIDTH, WIN_HEIGHT,
    create_themed_entry, create_themed_button,
    draw_rounded_rect,
)


class LoginScreen(tk.Frame):
    """Login form with centered card on a pirate-themed background."""

    def __init__(self, master, on_register_click, on_login_success):
        super().__init__(master, bg=BG_DEEP)
        self.on_register_click = on_register_click
        self.on_login_success = on_login_success
        self._build_ui()

    def _build_ui(self):
        # Center the login card vertically and horizontally
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -- Central card --
        card = tk.Frame(self, bg=BG_DARK, padx=40, pady=30)
        card.grid(row=1, column=0)

        # Title
        tk.Label(
            card, text="\u2693 Lungi Launcher", font=FONT_TITLE,
            fg=GOLD, bg=BG_DARK,
        ).pack(pady=(0, 5))

        # Separator
        tk.Frame(card, bg=GOLD_DIM, height=1, width=280).pack(pady=8)

        tk.Label(
            card, text="Sign In", font=FONT_HEADING,
            fg=FG_TEXT, bg=BG_DARK,
        ).pack(pady=(5, 15))

        # Username
        tk.Label(card, text="Username", font=FONT_SMALL,
                 fg=FG_MUTED, bg=BG_DARK).pack(anchor="center")
        self.username_entry = create_themed_entry(card)
        self.username_entry.pack(pady=(2, 10))
        self.username_entry.focus_set()

        # Password
        tk.Label(card, text="Password", font=FONT_SMALL,
                 fg=FG_MUTED, bg=BG_DARK).pack(anchor="center")
        self.password_entry = create_themed_entry(card, show="*")
        self.password_entry.pack(pady=(2, 12))
        self.password_entry.bind("<Return>", lambda e: self._handle_login())

        # Status
        self.status_label = tk.Label(
            card, text="", font=FONT_SMALL, fg=FG_MUTED,
            bg=BG_DARK, wraplength=260,
        )
        self.status_label.pack(pady=4)

        # Buttons
        create_themed_button(
            card, text="Login", command=self._handle_login, bg=BTN_PRIMARY,
        ).pack(pady=(4, 6))

        create_themed_button(
            card, text="Create Account", command=self.on_register_click,
            bg=BTN_SECONDARY, font=FONT_SMALL, width=18,
        ).pack(pady=4)

    def _handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message = login(username, password)

        if success:
            self.status_label.config(text=message, fg=FG_SUCCESS)
            self.on_login_success(username)
        else:
            self.status_label.config(text=message, fg=FG_ERROR)
