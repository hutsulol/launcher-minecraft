"""Main launcher screen shown after successful login."""

import tkinter as tk
from tkinter import ttk
import threading

from auth.session import save_session, clear_session
from launcher.minecraft_runner import (
    is_version_installed, install_version, launch_version,
)
from ui.components import (
    BG_DARK, FG_PRIMARY, FG_MUTED, FG_TEXT,
    FONT_TITLE, FONT_HEADING, FONT_BODY, FONT_PLAY, FONT_SMALL,
    BTN_GREEN, BTN_GRAY,
    make_label, make_button, make_status_label, show_status,
    make_separator, configure_combobox_style,
)

# Available versions for the dropdown
VERSIONS = ["1.20.4", "1.20.1", "1.19.4", "1.18.2"]


class LauncherScreen(tk.Frame):
    """Main screen with version selector, install + launch flow, and progress."""

    def __init__(self, master, username, on_logout):
        super().__init__(master, bg=BG_DARK)
        self.username = username
        self.on_logout = on_logout
        self.is_busy = False  # True while installing or launching

        # Track install progress values (updated from worker thread)
        self._progress_max = 0
        self._progress_current = 0

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
        self.version_combo = ttk.Combobox(
            self, textvariable=self.version_var, values=VERSIONS,
            state="readonly", width=20, font=FONT_BODY, style="Dark.TCombobox",
        )
        self.version_combo.pack(pady=(0, 20))

        # -- Progress area --
        self.progress_frame = tk.Frame(self, bg=BG_DARK)
        self.progress_frame.pack(pady=5, fill="x", padx=40)

        self.status_label = make_status_label(self.progress_frame)
        self.status_label.config(text="Ready to play", fg=FG_MUTED)
        self.status_label.pack(pady=2)

        # Detail label for install sub-status (e.g. "Downloading libraries...")
        self.detail_label = make_status_label(self.progress_frame)
        self.detail_label.pack(pady=0)

        self.progress_bar = ttk.Progressbar(
            self.progress_frame, mode="determinate", length=280
        )

        # -- Play button --
        self.play_btn = make_button(
            self, text="▶  PLAY", command=self._handle_play,
            bg=BTN_GREEN, width=24, font=FONT_PLAY, height=2,
        )
        self.play_btn.pack(pady=15)

        # -- Logout button --
        self.logout_btn = make_button(
            self, text="Logout", command=self._handle_logout,
            bg=BTN_GRAY, width=16, font=FONT_SMALL,
        )
        self.logout_btn.pack(pady=(10, 5))

    # ------------------------------------------------------------------
    # Play / install flow
    # ------------------------------------------------------------------

    def _handle_play(self):
        """Start the install-then-launch flow in a background thread."""
        if self.is_busy:
            return

        self.is_busy = True
        self._set_controls_enabled(False)

        # Show progress bar
        self.progress_bar.pack(pady=5)
        self.progress_bar["value"] = 0
        self._progress_max = 0
        self._progress_current = 0

        version = self.version_var.get()
        thread = threading.Thread(
            target=self._install_and_launch, args=(version,), daemon=True
        )
        thread.start()

    def _install_and_launch(self, version):
        """Worker thread: install if needed, then launch."""
        try:
            # Step 1 - check if version is installed
            self.after(0, self._show_progress, "Checking installation...", "")

            if not is_version_installed(version):
                # Step 2 - install the version with real progress callbacks
                self.after(0, self._show_progress, "Installing Minecraft...", "")
                ok, err = install_version(
                    version, progress_callback=self._on_install_progress
                )
                if not ok:
                    self.after(0, self._on_error, err)
                    return
                self.after(0, self._show_progress, "Installation complete!", "")

            # Step 3 - launch the game
            self.after(0, self._show_progress, "Launching game...", "")
            ok, msg = launch_version(self.username, version)

            if ok:
                self.after(0, self._on_launch_success, msg)
            else:
                self.after(0, self._on_error, msg)

        except Exception as e:
            self.after(0, self._on_error, f"Unexpected error: {e}")

    # ------------------------------------------------------------------
    # Callbacks from minecraft-launcher-lib (called on worker thread)
    # ------------------------------------------------------------------

    def _on_install_progress(self, stage, progress, max_progress):
        """Called by minecraft-launcher-lib during installation.

        Any of the arguments may be None if only one value changed.
        """
        if max_progress is not None:
            self._progress_max = max_progress
        if progress is not None:
            self._progress_current = progress

        # Calculate percentage for the progress bar
        if self._progress_max > 0:
            pct = int(self._progress_current / self._progress_max * 100)
        else:
            pct = 0

        # Build the detail text
        detail = ""
        if self._progress_max > 0:
            detail = f"{self._progress_current} / {self._progress_max}"

        # Schedule UI update on the main thread
        self.after(0, self._update_install_ui, stage, pct, detail)

    def _update_install_ui(self, stage, pct, detail):
        """Update the UI with install progress (runs on main thread)."""
        if stage:
            self.status_label.config(text=stage, fg=FG_PRIMARY)
        self.progress_bar["value"] = pct
        self.detail_label.config(text=detail, fg=FG_MUTED)

    # ------------------------------------------------------------------
    # Result handlers (all run on main thread via after())
    # ------------------------------------------------------------------

    def _show_progress(self, status, detail):
        """Update status and detail labels."""
        show_status(self.status_label, status)
        self.detail_label.config(text=detail, fg=FG_MUTED)

    def _on_launch_success(self, message):
        """Game launched successfully."""
        self.progress_bar["value"] = 100
        show_status(self.status_label, message)
        self.detail_label.config(text="", fg=FG_MUTED)
        # Re-enable controls after a short delay
        self.after(2000, self._reset_ui)

    def _on_error(self, message):
        """Something went wrong during install or launch."""
        self.progress_bar["value"] = 0
        show_status(self.status_label, message, is_error=True)
        self.detail_label.config(text="", fg=FG_MUTED)
        self._reset_ui()

    def _reset_ui(self):
        """Re-enable controls and hide the progress bar."""
        self.is_busy = False
        self._set_controls_enabled(True)
        self.progress_bar.pack_forget()

    def _set_controls_enabled(self, enabled):
        """Enable or disable interactive controls during install/launch."""
        state = "normal" if enabled else "disabled"
        bg = BTN_GREEN if enabled else BTN_GRAY
        self.play_btn.config(state=state, bg=bg)
        self.version_combo.config(state="readonly" if enabled else "disabled")
        self.logout_btn.config(state=state)

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    def _handle_logout(self):
        """Clear the saved session and return to login."""
        clear_session()
        self.on_logout()
