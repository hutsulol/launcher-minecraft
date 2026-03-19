"""Registration screen for the Minecraft launcher."""

import tkinter as tk
from auth.auth_manager import register
from ui.components import (
    BG_DARK, FG_PRIMARY, FG_MUTED,
    FONT_TITLE, FONT_HEADING, FONT_SMALL,
    BTN_GREEN, BTN_GRAY,
    make_label, make_entry, make_button, make_status_label,
    show_status, make_separator,
)


class RegisterScreen(tk.Frame):
    """Registration form for new users."""

    def __init__(self, master, on_back_click):
        super().__init__(master, bg=BG_DARK)
        self.on_back_click = on_back_click
        self._build_ui()

    def _build_ui(self):
        # -- Title --
        make_label(
            self, text="⛏  Minecraft Launcher", font=FONT_TITLE, fg=FG_PRIMARY
        ).pack(pady=(30, 5))

        make_separator(self).pack(pady=8)

        make_label(
            self, text="Create Account", font=FONT_HEADING
        ).pack(pady=(5, 15))

        # -- Username --
        make_label(self, text="Username", fg=FG_MUTED, font=FONT_SMALL).pack(anchor="center")
        self.username_entry = make_entry(self)
        self.username_entry.pack(pady=(2, 8))
        self.username_entry.focus_set()

        # -- Password --
        make_label(self, text="Password", fg=FG_MUTED, font=FONT_SMALL).pack(anchor="center")
        self.password_entry = make_entry(self, show="*")
        self.password_entry.pack(pady=(2, 8))

        # -- Confirm password --
        make_label(self, text="Confirm Password", fg=FG_MUTED, font=FONT_SMALL).pack(anchor="center")
        self.confirm_entry = make_entry(self, show="*")
        self.confirm_entry.pack(pady=(2, 8))

        # Bind Enter key
        self.confirm_entry.bind("<Return>", lambda e: self._handle_register())

        # -- Status --
        self.status_label = make_status_label(self)
        self.status_label.pack(pady=5)

        # -- Buttons --
        make_button(
            self, text="Register", command=self._handle_register, bg=BTN_GREEN
        ).pack(pady=(5, 5))

        make_button(
            self, text="Back to Login", command=self.on_back_click,
            bg=BTN_GRAY, font=FONT_SMALL, width=18,
        ).pack(pady=5)

    def _handle_register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if password != confirm:
            show_status(self.status_label, "Passwords do not match.", is_error=True)
            return

        success, message = register(username, password)
        show_status(self.status_label, message, is_error=not success)
