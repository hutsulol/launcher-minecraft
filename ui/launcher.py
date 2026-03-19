"""Main launcher screen — pirate-themed 16:9 layout for Lungi Launcher.

All content (banner, server cards) is loaded from data/servers.json
and rendered dynamically through reusable components.
"""

import tkinter as tk
from tkinter import ttk
import threading

from auth.session import save_session, clear_session
from data.loader import load_launcher_data
from launcher.minecraft_runner import (
    is_version_installed, install_version, launch_version,
)
from ui.theme import (
    BG_DEEP, BG_CARD,
    GOLD, GOLD_DIM, EMERALD, EMERALD_HOVER,
    FG_TEXT, FG_MUTED, FG_ERROR, FG_SUCCESS,
    BTN_SECONDARY,
    FONT_HEADING, FONT_SMALL, FONT_TINY, FONT_PLAY,
    CARD_PAD, WIN_WIDTH,
)
from ui.components.topbar import TopBar
from ui.components.banner import Banner
from ui.components.card import ServerCard

# Available Minecraft versions
VERSIONS = ["1.20.4", "1.20.1", "1.19.4", "1.18.2"]


class LauncherScreen(tk.Frame):
    """Full pirate-themed launcher: top bar, banner, card grid, play section."""

    def __init__(self, master, username, on_logout):
        super().__init__(master, bg=BG_DEEP)
        self.username = username
        self.on_logout = on_logout
        self.is_busy = False
        self._progress_max = 0
        self._progress_current = 0

        # Load all content from data file
        self._data = load_launcher_data()
        self._servers = self._data.get("servers", [])
        self.selected_server = self._servers[0] if self._servers else {"title": "None"}

        # Save session for auto-login
        save_session(username)

        self._build_ui()

    # ==================================================================
    # UI construction
    # ==================================================================

    def _build_ui(self):
        # -- Top bar --
        self.topbar = TopBar(
            self, self.username,
            on_settings=self._on_settings,
            on_logout=self._handle_logout,
        )
        self.topbar.pack(fill="x")

        # Thin gold separator under top bar
        tk.Frame(self, bg=GOLD_DIM, height=1).pack(fill="x")

        # Body area
        body = tk.Frame(self, bg=BG_DEEP)
        body.pack(fill="both", expand=True)

        # -- Banner (data-driven) --
        banner_data = self._data.get("banner")
        self.banner = Banner(body, data=banner_data)
        self.banner.pack(padx=20, pady=(15, 5))

        # -- Server cards (data-driven) --
        self._build_card_section(body)

        # -- Bottom play section --
        self._build_bottom(body)

    # ------------------------------------------------------------------
    # Server cards — rendered dynamically from self._servers
    # ------------------------------------------------------------------

    def _build_card_section(self, parent):
        """Build the server card grid from loaded data."""
        section_header = tk.Frame(parent, bg=BG_DEEP)
        section_header.pack(fill="x", padx=30, pady=(12, 5))
        tk.Label(
            section_header, text="\u2694  Choose Your Adventure",
            font=FONT_HEADING, fg=FG_TEXT, bg=BG_DEEP,
        ).pack(side="left")

        card_frame = tk.Frame(parent, bg=BG_DEEP)
        card_frame.pack(padx=20, pady=5)

        self.card_widgets = []
        for i, server in enumerate(self._servers):
            card = ServerCard(
                card_frame, server,
                on_select=self._on_card_select,
                is_selected=(i == 0),
            )
            card.grid(row=0, column=i, padx=CARD_PAD, pady=5)
            self.card_widgets.append(card)

    def _on_card_select(self, server_data):
        """Handle clicking a server card."""
        self.selected_server = server_data
        for card in self.card_widgets:
            card.set_selected(card.server_data["title"] == server_data["title"])
        self.selected_label.config(text=f"\u2693  {server_data['title']}")

    # ------------------------------------------------------------------
    # Bottom section — play button, version selector, progress
    # ------------------------------------------------------------------

    def _build_bottom(self, parent):
        tk.Frame(parent, bg="#1e293b", height=1).pack(fill="x", padx=20, pady=(10, 0))

        bottom = tk.Frame(parent, bg=BG_DEEP)
        bottom.pack(fill="x", padx=30, pady=(8, 10))

        # Left column: selected server + status
        left_col = tk.Frame(bottom, bg=BG_DEEP)
        left_col.pack(side="left", fill="y", padx=(0, 20))

        self.selected_label = tk.Label(
            left_col, text=f"\u2693  {self.selected_server['title']}",
            font=FONT_HEADING, fg=GOLD, bg=BG_DEEP,
        )
        self.selected_label.pack(anchor="w")

        self.status_label = tk.Label(
            left_col, text="Ready to set sail",
            font=FONT_SMALL, fg=FG_MUTED, bg=BG_DEEP, anchor="w",
            wraplength=350,
        )
        self.status_label.pack(anchor="w", pady=(2, 0))

        self.detail_label = tk.Label(
            left_col, text="", font=FONT_TINY, fg=FG_MUTED,
            bg=BG_DEEP, anchor="w",
        )
        self.detail_label.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(
            left_col, mode="determinate", length=340,
        )

        # Right column: version + play
        right_col = tk.Frame(bottom, bg=BG_DEEP)
        right_col.pack(side="right")

        ver_frame = tk.Frame(right_col, bg=BG_DEEP)
        ver_frame.pack(pady=(0, 6))

        tk.Label(
            ver_frame, text="Version:", font=FONT_SMALL,
            fg=FG_MUTED, bg=BG_DEEP,
        ).pack(side="left", padx=(0, 5))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Pirate.TCombobox",
            fieldbackground=BG_CARD,
            background=BTN_SECONDARY,
            foreground=FG_TEXT,
            arrowcolor=GOLD,
            selectbackground=BG_CARD,
            selectforeground=FG_TEXT,
        )

        self.version_var = tk.StringVar(value=VERSIONS[0])
        self.version_combo = ttk.Combobox(
            ver_frame, textvariable=self.version_var, values=VERSIONS,
            state="readonly", width=10, font=FONT_SMALL, style="Pirate.TCombobox",
        )
        self.version_combo.pack(side="left")

        # Big play button
        self.play_btn = tk.Button(
            right_col, text="\u25B6   SET SAIL", font=FONT_PLAY,
            bg=EMERALD, fg="white", activebackground=EMERALD_HOVER,
            activeforeground="white", relief="flat", cursor="hand2",
            bd=0, padx=30, pady=10, command=self._handle_play,
        )
        self.play_btn.pack()

        self.play_btn.bind("<Enter>", lambda e: self._play_hover(True))
        self.play_btn.bind("<Leave>", lambda e: self._play_hover(False))

    def _play_hover(self, entering):
        """Change play button color on hover (only when not busy)."""
        if not self.is_busy:
            self.play_btn.config(bg=EMERALD_HOVER if entering else EMERALD)

    # ==================================================================
    # Play / Install flow (threaded)
    # ==================================================================

    def _handle_play(self):
        if self.is_busy:
            return
        self.is_busy = True
        self._set_controls_enabled(False)

        self.progress_bar.pack(anchor="w", pady=(2, 0))
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
            self.after(0, self._show_status, "Checking installation...", "")

            if not is_version_installed(version):
                self.after(0, self._show_status, "Installing Minecraft...", "")
                ok, err = install_version(
                    version, progress_callback=self._on_install_progress
                )
                if not ok:
                    self.after(0, self._on_error, err)
                    return
                self.after(0, self._show_status, "Installation complete!", "")

            self.after(0, self._show_status, "Launching game...", "")
            ok, msg = launch_version(self.username, version)

            if ok:
                self.after(0, self._on_launch_success, msg)
            else:
                self.after(0, self._on_error, msg)
        except Exception as e:
            self.after(0, self._on_error, f"Unexpected error: {e}")

    # ------------------------------------------------------------------
    # Install progress callbacks (worker thread → main thread)
    # ------------------------------------------------------------------

    def _on_install_progress(self, stage, progress, max_progress):
        if max_progress is not None:
            self._progress_max = max_progress
        if progress is not None:
            self._progress_current = progress

        pct = 0
        if self._progress_max > 0:
            pct = int(self._progress_current / self._progress_max * 100)

        detail = ""
        if self._progress_max > 0:
            detail = f"{self._progress_current} / {self._progress_max}"

        self.after(0, self._update_install_ui, stage, pct, detail)

    def _update_install_ui(self, stage, pct, detail):
        if stage:
            self.status_label.config(text=stage, fg=FG_SUCCESS)
        self.progress_bar["value"] = pct
        self.detail_label.config(text=detail)

    # ------------------------------------------------------------------
    # Result handlers (main thread)
    # ------------------------------------------------------------------

    def _show_status(self, status, detail):
        self.status_label.config(text=status, fg=FG_SUCCESS)
        self.detail_label.config(text=detail)

    def _on_launch_success(self, message):
        self.progress_bar["value"] = 100
        self.status_label.config(text=message, fg=FG_SUCCESS)
        self.detail_label.config(text="")
        self.after(2500, self._reset_ui)

    def _on_error(self, message):
        self.progress_bar["value"] = 0
        self.status_label.config(text=message, fg=FG_ERROR)
        self.detail_label.config(text="")
        self._reset_ui()

    def _reset_ui(self):
        self.is_busy = False
        self._set_controls_enabled(True)
        self.progress_bar.pack_forget()
        self.status_label.config(text="Ready to set sail", fg=FG_MUTED)

    def _set_controls_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.play_btn.config(state=state, bg=EMERALD if enabled else BTN_SECONDARY)
        self.version_combo.config(state="readonly" if enabled else "disabled")
        for card in self.card_widgets:
            card.config(state=state)

    # ------------------------------------------------------------------
    # Other actions
    # ------------------------------------------------------------------

    def _on_settings(self):
        self.status_label.config(text="Settings coming soon...", fg=GOLD)

    def _handle_logout(self):
        clear_session()
        self.on_logout()
