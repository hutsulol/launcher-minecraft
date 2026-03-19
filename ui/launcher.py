"""Main launcher screen shown after successful login."""

import tkinter as tk
from tkinter import ttk
import threading

from auth.session import save_session, clear_session
from launcher.minecraft_runner import launch_minecraft
from ui.components import (
    BG_DARK, BG_CARD, FG_PRIMARY, FG_TEXT, FG_MUTED,
    FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_PLAY, FONT_SMALL,
    BTN_GREEN, BTN_GRAY, BTN_RED,
    make_label, make_button, make_status_label, show_status,
    make_separator, configure_combobox_style,
)

# Available versions for the dropdown
VERSIONS = ["1.20.4", "1.20.1", "1.19.4", "1.18.2"]


class LauncherScreen(tk.Frame):
    """Main screen with version selector, Play button, and loading feedback."""

    def __init__(self, master, username, on_logout):
        super().__init__(master, bg=BG_DARK)
        self.username = username
        self.on_logout = on_logout
        self.is_launching = False
        self._build_ui()

        # Save session so user is auto-logged-in next time
        save_session(username)

    def _build_ui(self):
        # -- Title --
        make_label(
            self, text="⛏  Minecraft Launcher", font=FONT_TITLE, fg=FG_PRIMARY
        ).pack(pady=(30, 5))

        make_separator(self).pack(pady=8)

        # -- Welcome --
        make_label(
            self, text=f"Logged in as: {self.username}", font=FONT_BODY, fg=FG_MUTED
        ).pack(pady=(5, 15))

        # -- Version selector --
        make_label(self, text="Select Version", font=FONT_HEADING).pack(pady=(0, 5))

        configure_combobox_style()
        self.version_var = tk.StringVar(value=VERSIONS[0])
        version_combo = ttk.Combobox(
            self, textvariable=self.version_var, values=VERSIONS,
            state="readonly", width=20, font=FONT_BODY, style="Dark.TCombobox",
        )
        version_combo.pack(pady=(0, 20))

        # -- Progress / status area --
        self.progress_frame = tk.Frame(self, bg=BG_DARK)
        self.progress_frame.pack(pady=5, fill="x", padx=40)

        self.status_label = make_status_label(self.progress_frame)
        self.status_label.config(text="Ready to play", fg=FG_MUTED)
        self.status_label.pack(pady=2)

        self.progress_bar = ttk.Progressbar(
            self.progress_frame, mode="determinate", length=250
        )

        # -- Play button --
        self.play_btn = make_button(
            self, text="▶  PLAY", command=self._handle_play,
            bg=BTN_GREEN, width=24, font=FONT_PLAY, height=2,
        )
        self.play_btn.pack(pady=15)

        # -- Bottom buttons --
        make_button(
            self, text="Logout", command=self._handle_logout,
            bg=BTN_GRAY, width=16, font=FONT_SMALL,
        ).pack(pady=(10, 5))

    def _handle_play(self):
        """Launch Minecraft in a background thread to avoid freezing the UI."""
        if self.is_launching:
            return
        self.is_launching = True
        self.play_btn.config(state="disabled", bg=BTN_GRAY)

        # Show progress bar
        self.progress_bar.pack(pady=5)
        self.progress_bar["value"] = 0

        version = self.version_var.get()
        thread = threading.Thread(
            target=self._launch_thread, args=(version,), daemon=True
        )
        thread.start()

    def _launch_thread(self, version):
        """Run launch steps in a background thread, updating UI via after()."""
        steps = [
            (20, "Preparing files..."),
            (50, "Checking version..."),
            (80, "Launching game..."),
        ]

        for progress, message in steps:
            self.after(0, self._update_progress, progress, message)
            # Small delay so user can see the progress stages
            import time
            time.sleep(0.6)

        # Actually launch
        success, result_msg = launch_minecraft(self.username, version)
        self.after(0, self._on_launch_done, success, result_msg)

    def _update_progress(self, value, message):
        """Update progress bar and status text (called on main thread)."""
        self.progress_bar["value"] = value
        show_status(self.status_label, message)

    def _on_launch_done(self, success, message):
        """Handle launch result (called on main thread)."""
        self.progress_bar["value"] = 100 if success else 0
        show_status(self.status_label, message, is_error=not success)

        if success:
            # Hide progress bar after a moment
            self.after(2000, self._reset_ui)
        else:
            self._reset_ui()

    def _reset_ui(self):
        """Re-enable the Play button and hide progress bar."""
        self.is_launching = False
        self.play_btn.config(state="normal", bg=BTN_GREEN)
        self.progress_bar.pack_forget()

    def _handle_logout(self):
        """Clear the saved session and return to login."""
        clear_session()
        self.on_logout()
