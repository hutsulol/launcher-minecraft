"""Login screen for the Minecraft launcher."""

import tkinter as tk
from auth.auth_manager import login


class LoginScreen(tk.Frame):
    """Login form that authenticates existing users."""

    def __init__(self, master, on_register_click, on_login_success):
        super().__init__(master)
        self.on_register_click = on_register_click
        self.on_login_success = on_login_success
        self._build_ui()

    def _build_ui(self):
        self.configure(bg="#2b2b2b")

        # Title
        tk.Label(
            self, text="Minecraft Launcher", font=("Arial", 20, "bold"),
            fg="#55ff55", bg="#2b2b2b"
        ).pack(pady=(40, 20))

        tk.Label(
            self, text="Login", font=("Arial", 14),
            fg="white", bg="#2b2b2b"
        ).pack(pady=(0, 10))

        # Username
        tk.Label(self, text="Username", fg="white", bg="#2b2b2b").pack()
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        # Password
        tk.Label(self, text="Password", fg="white", bg="#2b2b2b").pack()
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        # Status label for error/success messages
        self.status_label = tk.Label(
            self, text="", fg="red", bg="#2b2b2b", wraplength=250
        )
        self.status_label.pack(pady=5)

        # Buttons
        tk.Button(
            self, text="Login", width=20, command=self._handle_login,
            bg="#4CAF50", fg="white"
        ).pack(pady=5)

        tk.Button(
            self, text="Create Account", width=20,
            command=self.on_register_click, bg="#555555", fg="white"
        ).pack(pady=5)

    def _handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message = login(username, password)

        if success:
            self.status_label.config(text=message, fg="#55ff55")
            self.on_login_success(username)
        else:
            self.status_label.config(text=message, fg="red")
