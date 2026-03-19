"""Registration screen for the Minecraft launcher."""

import tkinter as tk
from auth.auth_manager import register


class RegisterScreen(tk.Frame):
    """Registration form for new users."""

    def __init__(self, master, on_back_click):
        super().__init__(master)
        self.on_back_click = on_back_click
        self._build_ui()

    def _build_ui(self):
        self.configure(bg="#2b2b2b")

        tk.Label(
            self, text="Create Account", font=("Arial", 16, "bold"),
            fg="white", bg="#2b2b2b"
        ).pack(pady=(40, 20))

        # Username
        tk.Label(self, text="Username", fg="white", bg="#2b2b2b").pack()
        self.username_entry = tk.Entry(self, width=30)
        self.username_entry.pack(pady=5)

        # Password
        tk.Label(self, text="Password", fg="white", bg="#2b2b2b").pack()
        self.password_entry = tk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)

        # Confirm password
        tk.Label(self, text="Confirm Password", fg="white", bg="#2b2b2b").pack()
        self.confirm_entry = tk.Entry(self, width=30, show="*")
        self.confirm_entry.pack(pady=5)

        # Status label
        self.status_label = tk.Label(
            self, text="", fg="red", bg="#2b2b2b", wraplength=250
        )
        self.status_label.pack(pady=5)

        # Buttons
        tk.Button(
            self, text="Register", width=20, command=self._handle_register,
            bg="#4CAF50", fg="white"
        ).pack(pady=5)

        tk.Button(
            self, text="Back to Login", width=20,
            command=self.on_back_click, bg="#555555", fg="white"
        ).pack(pady=5)

    def _handle_register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if password != confirm:
            self.status_label.config(text="Passwords do not match.", fg="red")
            return

        success, message = register(username, password)
        if success:
            self.status_label.config(text=message, fg="#55ff55")
        else:
            self.status_label.config(text=message, fg="red")
