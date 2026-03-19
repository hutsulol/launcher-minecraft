"""Login screen for the Minecraft launcher."""

import tkinter as tk
from auth.auth_manager import login
from ui.components import (
    BG_DARK, FG_PRIMARY, FG_MUTED,
    FONT_TITLE, FONT_HEADING, FONT_SMALL,
    BTN_GREEN, BTN_GRAY,
    make_label, make_entry, make_button, make_status_label,
    show_status, make_separator,
)


class LoginScreen(tk.Frame):
    """Login form that authenticates existing users."""

    def __init__(self, master, on_register_click, on_login_success):
        super().__init__(master, bg=BG_DARK)
        self.on_register_click = on_register_click
        self.on_login_success = on_login_success
        self._build_ui()

    def _build_ui(self):
        # -- Title --
        make_label(
            self, text="⛏  Minecraft Launcher", font=FONT_TITLE, fg=FG_PRIMARY
        ).pack(pady=(40, 5))

        make_separator(self).pack(pady=8)

        make_label(
            self, text="Sign In", font=FONT_HEADING
        ).pack(pady=(5, 15))

        # -- Username --
        make_label(self, text="Username", fg=FG_MUTED, font=FONT_SMALL).pack(anchor="center")
        self.username_entry = make_entry(self)
        self.username_entry.pack(pady=(2, 10))
        self.username_entry.focus_set()

        # -- Password --
        make_label(self, text="Password", fg=FG_MUTED, font=FONT_SMALL).pack(anchor="center")
        self.password_entry = make_entry(self, show="*")
        self.password_entry.pack(pady=(2, 10))

        # Bind Enter key to login
        self.password_entry.bind("<Return>", lambda e: self._handle_login())

        # -- Status message --
        self.status_label = make_status_label(self)
        self.status_label.pack(pady=5)

        # -- Buttons --
        make_button(
            self, text="Login", command=self._handle_login, bg=BTN_GREEN
        ).pack(pady=(5, 5))

        make_button(
            self, text="Create Account", command=self.on_register_click,
            bg=BTN_GRAY, font=FONT_SMALL, width=18,
        ).pack(pady=5)

    def _handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message = login(username, password)

        if success:
            show_status(self.status_label, message)
            self.on_login_success(username)
        else:
            show_status(self.status_label, message, is_error=True)
