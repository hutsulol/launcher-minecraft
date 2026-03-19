"""Registration screen for Lungi Launcher — pirate theme."""

import tkinter as tk
from auth.auth_manager import register
from ui.theme import (
    BG_DEEP, BG_DARK, GOLD, GOLD_DIM,
    FG_TEXT, FG_MUTED, FG_ERROR, FG_SUCCESS,
    BTN_PRIMARY, BTN_SECONDARY,
    FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_SMALL,
    create_themed_entry, create_themed_button,
)


class RegisterScreen(tk.Frame):
    """Registration form with centered card on a pirate-themed background."""

    def __init__(self, master, on_back_click):
        super().__init__(master, bg=BG_DEEP)
        self.on_back_click = on_back_click
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -- Central card --
        card = tk.Frame(self, bg=BG_DARK, padx=40, pady=25)
        card.grid(row=1, column=0)

        # Title
        tk.Label(
            card, text="\u2693 Lungi Launcher", font=FONT_TITLE,
            fg=GOLD, bg=BG_DARK,
        ).pack(pady=(0, 5))

        tk.Frame(card, bg=GOLD_DIM, height=1, width=280).pack(pady=8)

        tk.Label(
            card, text="Create Account", font=FONT_HEADING,
            fg=FG_TEXT, bg=BG_DARK,
        ).pack(pady=(5, 12))

        # Username
        tk.Label(card, text="Username", font=FONT_SMALL,
                 fg=FG_MUTED, bg=BG_DARK).pack(anchor="center")
        self.username_entry = create_themed_entry(card)
        self.username_entry.pack(pady=(2, 8))
        self.username_entry.focus_set()

        # Password
        tk.Label(card, text="Password", font=FONT_SMALL,
                 fg=FG_MUTED, bg=BG_DARK).pack(anchor="center")
        self.password_entry = create_themed_entry(card, show="*")
        self.password_entry.pack(pady=(2, 8))

        # Confirm password
        tk.Label(card, text="Confirm Password", font=FONT_SMALL,
                 fg=FG_MUTED, bg=BG_DARK).pack(anchor="center")
        self.confirm_entry = create_themed_entry(card, show="*")
        self.confirm_entry.pack(pady=(2, 8))
        self.confirm_entry.bind("<Return>", lambda e: self._handle_register())

        # Status
        self.status_label = tk.Label(
            card, text="", font=FONT_SMALL, fg=FG_MUTED,
            bg=BG_DARK, wraplength=260,
        )
        self.status_label.pack(pady=4)

        # Buttons
        create_themed_button(
            card, text="Register", command=self._handle_register, bg=BTN_PRIMARY,
        ).pack(pady=(4, 6))

        create_themed_button(
            card, text="Back to Login", command=self.on_back_click,
            bg=BTN_SECONDARY, font=FONT_SMALL, width=18,
        ).pack(pady=4)

    def _handle_register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if password != confirm:
            self.status_label.config(text="Passwords do not match.", fg=FG_ERROR)
            return

        success, message = register(username, password)
        self.status_label.config(
            text=message, fg=FG_SUCCESS if success else FG_ERROR
        )
