"""Main launcher screen shown after successful login."""

import tkinter as tk
from launcher.minecraft_runner import launch_minecraft


class LauncherScreen(tk.Frame):
    """Main screen with Play button and version info."""

    def __init__(self, master, username, on_logout):
        super().__init__(master)
        self.username = username
        self.on_logout = on_logout
        self._build_ui()

    def _build_ui(self):
        self.configure(bg="#2b2b2b")

        # Welcome header
        tk.Label(
            self, text="Minecraft Launcher", font=("Arial", 20, "bold"),
            fg="#55ff55", bg="#2b2b2b"
        ).pack(pady=(30, 10))

        tk.Label(
            self, text=f"Welcome, {self.username}!", font=("Arial", 12),
            fg="white", bg="#2b2b2b"
        ).pack(pady=5)

        # Version display (hardcoded for MVP)
        tk.Label(
            self, text="Version: 1.20.4", font=("Arial", 10),
            fg="#aaaaaa", bg="#2b2b2b"
        ).pack(pady=10)

        # Status label
        self.status_label = tk.Label(
            self, text="Ready to play", fg="#aaaaaa", bg="#2b2b2b",
            wraplength=300
        )
        self.status_label.pack(pady=10)

        # Play button
        tk.Button(
            self, text="▶  PLAY", width=25, height=2,
            command=self._handle_play, bg="#4CAF50", fg="white",
            font=("Arial", 14, "bold")
        ).pack(pady=15)

        # Logout button
        tk.Button(
            self, text="Logout", width=15, command=self.on_logout,
            bg="#555555", fg="white"
        ).pack(pady=5)

    def _handle_play(self):
        self.status_label.config(text="Launching Minecraft...", fg="#55ff55")
        self.update_idletasks()
        success, message = launch_minecraft(self.username)
        if success:
            self.status_label.config(text=message, fg="#55ff55")
        else:
            self.status_label.config(text=message, fg="red")
