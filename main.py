"""Minecraft Launcher - Main entry point.

A simple Minecraft launcher with user authentication and a Tkinter GUI.
"""

import tkinter as tk
from ui.login import LoginScreen
from ui.register import RegisterScreen
from ui.launcher import LauncherScreen

WINDOW_WIDTH = 400
WINDOW_HEIGHT = 500


class MinecraftLauncher(tk.Tk):
    """Root application that manages screen navigation."""

    def __init__(self):
        super().__init__()
        self.title("Minecraft Launcher")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)
        self.configure(bg="#2b2b2b")

        self.current_frame = None
        self._show_login()

    def _clear_frame(self):
        """Remove the current screen."""
        if self.current_frame is not None:
            self.current_frame.destroy()

    def _show_login(self):
        """Display the login screen."""
        self._clear_frame()
        self.current_frame = LoginScreen(
            self,
            on_register_click=self._show_register,
            on_login_success=self._show_launcher,
        )
        self.current_frame.pack(fill="both", expand=True)

    def _show_register(self):
        """Display the registration screen."""
        self._clear_frame()
        self.current_frame = RegisterScreen(
            self,
            on_back_click=self._show_login,
        )
        self.current_frame.pack(fill="both", expand=True)

    def _show_launcher(self, username):
        """Display the main launcher screen after login."""
        self._clear_frame()
        self.current_frame = LauncherScreen(
            self,
            username=username,
            on_logout=self._show_login,
        )
        self.current_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = MinecraftLauncher()
    app.mainloop()
