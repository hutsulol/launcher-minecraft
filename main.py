"""Lungi Launcher — Main entry point.

A pirate-themed Minecraft launcher with user authentication,
mode details, version selection, and threaded install/launch.

Navigation flow:
  Login → Launcher (mode cards) → ModeDetails (play/install)
"""

import tkinter as tk
from auth.session import load_session
from auth.database import user_exists
from ui.login import LoginScreen
from ui.register import RegisterScreen
from ui.launcher import LauncherScreen
from ui.mode_details import ModeDetailsScreen
from ui.theme import BG_DEEP, WIN_WIDTH, WIN_HEIGHT


class LungiLauncher(tk.Tk):
    """Root application — manages screen navigation and 16:9 window."""

    def __init__(self):
        super().__init__()
        self.title("Lungi Launcher")
        self.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")
        self.resizable(False, False)
        self.configure(bg=BG_DEEP)

        # Center window on screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() - WIN_WIDTH) // 2
        y = (self.winfo_screenheight() - WIN_HEIGHT) // 2
        self.geometry(f"+{x}+{y}")

        self.current_frame = None
        self._username = None

        # Auto-login if session exists
        saved_user = load_session()
        if saved_user and user_exists(saved_user):
            self._username = saved_user
            self._show_launcher(saved_user)
        else:
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
        """Display the main launcher screen (mode card grid)."""
        self._username = username
        self._clear_frame()
        self.current_frame = LauncherScreen(
            self,
            username=username,
            on_logout=self._show_login,
            on_mode_select=self._show_mode_details,
        )
        self.current_frame.pack(fill="both", expand=True)

    def _show_mode_details(self, mode_data):
        """Display the details screen for a specific mode."""
        self._clear_frame()
        self.current_frame = ModeDetailsScreen(
            self,
            mode_data=mode_data,
            username=self._username,
            on_back=lambda: self._show_launcher(self._username),
        )
        self.current_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = LungiLauncher()
    app.mainloop()
