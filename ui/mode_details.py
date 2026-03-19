"""Mode details screen — shows full info about a game mode before playing."""

import tkinter as tk
from tkinter import ttk
import threading

from launcher.minecraft_runner import (
    is_version_installed, install_version, launch_version, VERSION,
    is_forge_installed, install_forge,
)
from ui.theme import (
    BG_DEEP, BG_DARK, BG_CARD, BG_CARD_HOVER,
    GOLD, GOLD_DIM, EMERALD, EMERALD_HOVER,
    FG_TEXT, FG_MUTED, FG_ERROR, FG_SUCCESS,
    BTN_SECONDARY,
    FONT_HEADING, FONT_BODY, FONT_SMALL, FONT_TINY, FONT_PLAY,
    WIN_WIDTH,
    draw_rounded_rect,
)


class ModeDetailsScreen(tk.Frame):
    """Full-screen details view for a single game mode.

    Shows description, image gallery, stats, features, and a Play button.
    If the mode is marked coming_soon, Play is disabled.
    """

    def __init__(self, master, mode_data, username, on_back):
        super().__init__(master, bg=BG_DEEP)
        self.mode = mode_data
        self.username = username
        self.on_back = on_back
        self.is_busy = False
        self._progress_max = 0
        self._progress_current = 0
        self._gallery_index = 0

        self._build_ui()

    # ==================================================================
    # UI construction
    # ==================================================================

    def _build_ui(self):
        # -- Top bar with back button and mode title --
        self._build_topbar()

        # Gold separator
        tk.Frame(self, bg=GOLD_DIM, height=1).pack(fill="x")

        # Scrollable body — use a canvas so the content can overflow
        container = tk.Frame(self, bg=BG_DEEP)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=BG_DEEP, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self._scroll_frame = tk.Frame(canvas, bg=BG_DEEP)

        self._scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw",
                             width=WIN_WIDTH)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind mousewheel scrolling
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))
        canvas.bind_all("<Button-4>",
                        lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>",
                        lambda e: canvas.yview_scroll(1, "units"))

        body = self._scroll_frame

        # -- Two-column layout: left = content, right = play panel --
        columns = tk.Frame(body, bg=BG_DEEP)
        columns.pack(fill="x", padx=25, pady=(15, 10))

        left = tk.Frame(columns, bg=BG_DEEP)
        left.pack(side="left", fill="both", expand=True, padx=(0, 15))

        right = tk.Frame(columns, bg=BG_DARK, padx=20, pady=20, width=260)
        right.pack(side="right", anchor="n")
        right.pack_propagate(False)
        right.config(width=260, height=320)

        # Build each section
        self._build_gallery(left)
        self._build_description(left)
        self._build_stats_row(body)
        self._build_features(body)

        # Right panel: play section
        self._build_play_panel(right)

    # ------------------------------------------------------------------
    # Top bar
    # ------------------------------------------------------------------

    def _build_topbar(self):
        bar = tk.Frame(self, bg="#0f172a", height=50)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Back button
        back_btn = tk.Button(
            bar, text="\u2190  Back", font=FONT_SMALL,
            fg=FG_TEXT, bg="#0f172a", activebackground="#0f172a",
            activeforeground=GOLD, relief="flat", bd=0,
            cursor="hand2", command=self.on_back,
        )
        back_btn.pack(side="left", padx=15)

        # Mode title
        icon = self.mode.get("icon", "\u2693")
        tk.Label(
            bar, text=f"{icon}  {self.mode['title']}", font=("Arial", 16, "bold"),
            fg=GOLD, bg="#0f172a",
        ).pack(side="left", padx=10)

        # Coming soon badge (if applicable)
        if self.mode.get("coming_soon"):
            tk.Label(
                bar, text="COMING SOON", font=("Arial", 9, "bold"),
                fg="#020617", bg=GOLD, padx=8, pady=2,
            ).pack(side="right", padx=15)

    # ------------------------------------------------------------------
    # Image gallery (placeholder cards with text)
    # ------------------------------------------------------------------

    def _build_gallery(self, parent):
        """Create a gallery viewer showing image descriptions as placeholders."""
        gallery = self.mode.get("gallery", [])
        if not gallery:
            return

        gallery_frame = tk.Frame(parent, bg=BG_DEEP)
        gallery_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            gallery_frame, text="\u26f5  Gallery", font=FONT_HEADING,
            fg=FG_TEXT, bg=BG_DEEP,
        ).pack(anchor="w", pady=(0, 8))

        # Main image canvas
        self._gallery_canvas = tk.Canvas(
            gallery_frame, width=640, height=160,
            bg=BG_DEEP, highlightthickness=0,
        )
        self._gallery_canvas.pack(anchor="w")

        self._draw_gallery_item()

        # Navigation dots + arrows
        nav = tk.Frame(gallery_frame, bg=BG_DEEP)
        nav.pack(anchor="w", pady=(6, 0))

        if len(gallery) > 1:
            tk.Button(
                nav, text="\u25C0", font=FONT_SMALL, fg=FG_TEXT,
                bg=BG_CARD, activebackground=BG_CARD_HOVER, relief="flat",
                bd=0, cursor="hand2", padx=6,
                command=lambda: self._gallery_navigate(-1),
            ).pack(side="left", padx=(0, 8))

            self._dots_label = tk.Label(
                nav, text=self._dots_text(), font=FONT_TINY,
                fg=FG_MUTED, bg=BG_DEEP,
            )
            self._dots_label.pack(side="left")

            tk.Button(
                nav, text="\u25B6", font=FONT_SMALL, fg=FG_TEXT,
                bg=BG_CARD, activebackground=BG_CARD_HOVER, relief="flat",
                bd=0, cursor="hand2", padx=6,
                command=lambda: self._gallery_navigate(1),
            ).pack(side="left", padx=(8, 0))

    def _draw_gallery_item(self):
        """Draw the current gallery image placeholder on the canvas."""
        c = self._gallery_canvas
        c.delete("all")
        gallery = self.mode.get("gallery", [])
        if not gallery:
            return

        w, h = 640, 160
        draw_rounded_rect(c, 0, 0, w, h, radius=12,
                          fill="#0c1a3d", outline="#1e3a5f", width=1)

        # Large icon
        icon = self.mode.get("icon", "\u2693")
        c.create_text(w // 2, h // 2 - 18, text=icon, font=("Arial", 36),
                      fill=GOLD_DIM)

        # Caption text
        caption = gallery[self._gallery_index]
        c.create_text(w // 2, h // 2 + 28, text=caption, font=FONT_BODY,
                      fill=FG_MUTED)

        # Counter
        c.create_text(w - 30, h - 15, text=f"{self._gallery_index + 1}/{len(gallery)}",
                      font=FONT_TINY, fill=FG_MUTED)

    def _gallery_navigate(self, direction):
        gallery = self.mode.get("gallery", [])
        if not gallery:
            return
        self._gallery_index = (self._gallery_index + direction) % len(gallery)
        self._draw_gallery_item()
        if hasattr(self, "_dots_label"):
            self._dots_label.config(text=self._dots_text())

    def _dots_text(self):
        gallery = self.mode.get("gallery", [])
        return "  ".join(
            "\u25CF" if i == self._gallery_index else "\u25CB"
            for i in range(len(gallery))
        )

    # ------------------------------------------------------------------
    # Description
    # ------------------------------------------------------------------

    def _build_description(self, parent):
        desc_frame = tk.Frame(parent, bg=BG_DEEP)
        desc_frame.pack(fill="x", pady=(0, 5))

        tk.Label(
            desc_frame, text="\u2620  About this mode", font=FONT_HEADING,
            fg=FG_TEXT, bg=BG_DEEP,
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            desc_frame, text=self.mode.get("description", ""),
            font=FONT_BODY, fg=FG_MUTED, bg=BG_DEEP,
            wraplength=620, justify="left", anchor="w",
        ).pack(anchor="w")

    # ------------------------------------------------------------------
    # Stats row (players, wipe date)
    # ------------------------------------------------------------------

    def _build_stats_row(self, parent):
        stats_frame = tk.Frame(parent, bg=BG_DEEP)
        stats_frame.pack(fill="x", padx=25, pady=(5, 5))

        # Build stat cards
        stats = []

        players = self.mode.get("players", 0)
        if self.mode.get("coming_soon"):
            stats.append(("\u25CF  Status", "Coming Soon", GOLD))
        else:
            color = FG_SUCCESS if players > 0 else FG_MUTED
            stats.append(("\u25CF  Online", f"{players:,} players", color))

        wipe = self.mode.get("wipe_date")
        if wipe:
            stats.append(("\u23F0  Last Wipe", wipe, FG_TEXT))

        mode_count = len(self.mode.get("features", []))
        stats.append(("\u2694  Features", f"{mode_count} features", FG_TEXT))

        for label_text, value_text, color in stats:
            card = tk.Frame(stats_frame, bg=BG_CARD, padx=18, pady=10)
            card.pack(side="left", padx=(0, 10))

            tk.Label(
                card, text=label_text, font=FONT_TINY,
                fg=FG_MUTED, bg=BG_CARD,
            ).pack(anchor="w")
            tk.Label(
                card, text=value_text, font=FONT_HEADING,
                fg=color, bg=BG_CARD,
            ).pack(anchor="w")

    # ------------------------------------------------------------------
    # Features list
    # ------------------------------------------------------------------

    def _build_features(self, parent):
        features = self.mode.get("features", [])
        if not features:
            return

        feat_frame = tk.Frame(parent, bg=BG_DEEP)
        feat_frame.pack(fill="x", padx=25, pady=(5, 15))

        tk.Label(
            feat_frame, text="\u2699  Features", font=FONT_HEADING,
            fg=FG_TEXT, bg=BG_DEEP,
        ).pack(anchor="w", pady=(0, 6))

        # Two-column grid
        grid = tk.Frame(feat_frame, bg=BG_DEEP)
        grid.pack(anchor="w")

        for i, feat in enumerate(features):
            row, col = divmod(i, 2)
            tk.Label(
                grid, text=f"  \u2022  {feat}", font=FONT_BODY,
                fg=FG_MUTED, bg=BG_DEEP, anchor="w", width=35,
            ).grid(row=row, column=col, sticky="w", pady=2)

    # ------------------------------------------------------------------
    # Play panel (right side)
    # ------------------------------------------------------------------

    def _build_play_panel(self, parent):
        """Build the right-side panel with Play button and progress."""
        coming_soon = self.mode.get("coming_soon", False)

        # Mode icon + title
        tk.Label(
            parent, text=self.mode.get("icon", ""), font=("Arial", 32),
            fg=GOLD, bg=BG_DARK,
        ).pack(pady=(0, 5))

        tk.Label(
            parent, text=self.mode["title"], font=FONT_HEADING,
            fg=FG_TEXT, bg=BG_DARK,
        ).pack(pady=(0, 15))

        # Play button
        if coming_soon:
            self.play_btn = tk.Button(
                parent, text="COMING SOON", font=FONT_PLAY,
                bg=BTN_SECONDARY, fg=FG_MUTED,
                activebackground=BTN_SECONDARY, activeforeground=FG_MUTED,
                relief="flat", bd=0, padx=20, pady=8, state="disabled",
            )
        else:
            self.play_btn = tk.Button(
                parent, text="\u25B6  SET SAIL", font=FONT_PLAY,
                bg=EMERALD, fg="white",
                activebackground=EMERALD_HOVER, activeforeground="white",
                relief="flat", cursor="hand2", bd=0, padx=20, pady=8,
                command=self._handle_play,
            )
            self.play_btn.bind("<Enter>", lambda e: self._play_hover(True))
            self.play_btn.bind("<Leave>", lambda e: self._play_hover(False))

        self.play_btn.pack(pady=(5, 10))

        # Status + progress (below play button)
        self.status_label = tk.Label(
            parent, text="Ready to play" if not coming_soon else "",
            font=FONT_TINY, fg=FG_MUTED, bg=BG_DARK,
            wraplength=220, anchor="w",
        )
        self.status_label.pack(anchor="w", pady=(2, 0))

        self.detail_label = tk.Label(
            parent, text="", font=FONT_TINY, fg=FG_MUTED, bg=BG_DARK,
        )
        self.detail_label.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(
            parent, mode="determinate", length=220, maximum=100,
        )

    def _play_hover(self, entering):
        if not self.is_busy:
            self.play_btn.config(bg=EMERALD_HOVER if entering else EMERALD)

    # ==================================================================
    # Play / Install flow (threaded) — same pattern as LauncherScreen
    # ==================================================================

    def _handle_play(self):
        if self.is_busy:
            return
        self.is_busy = True
        self._set_controls_enabled(False)

        self.progress_bar.pack(anchor="w", pady=(4, 0))
        self.progress_bar["value"] = 0
        self.progress_bar.update_idletasks()
        self._progress_max = 0
        self._progress_current = 0

        thread = threading.Thread(
            target=self._install_and_launch, daemon=True
        )
        thread.start()

    def _install_and_launch(self):
        """Worker thread: install Minecraft + Forge if needed, then launch."""
        try:
            # Step 1 — install vanilla Minecraft if needed
            self.after(0, self._show_status, "Checking installation...")

            if not is_version_installed():
                self.after(0, self._show_status, "Installing Minecraft...")
                ok, err = install_version(
                    progress_callback=self._on_install_progress
                )
                if not ok:
                    self.after(0, self._on_error, err)
                    return
                self.after(0, self._show_status, "Minecraft installed!")

            # Step 2 — install Forge if needed
            if not is_forge_installed():
                self.after(0, self._show_status, "Installing Forge...")
                ok, err = install_forge(
                    progress_callback=self._on_install_progress
                )
                if not ok:
                    self.after(0, self._on_error, err)
                    return
                self.after(0, self._show_status, "Forge installed!")

            # Step 3 — launch (automatically uses Forge version)
            self.after(0, self._show_status, "Launching game...")
            ok, msg = launch_version(self.username)

            if ok:
                self.after(0, self._on_launch_success, msg)
            else:
                self.after(0, self._on_error, msg)
        except Exception as e:
            self.after(0, self._on_error, f"Unexpected error: {e}")

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
        """Update progress bar and labels. Runs on main thread via after()."""
        if stage:
            self.status_label.config(text=stage, fg=FG_SUCCESS)
        self.progress_bar["value"] = pct
        self.detail_label.config(text=detail)
        # Force Tkinter to repaint the progress bar immediately
        self.progress_bar.update_idletasks()

    def _show_status(self, text):
        self.status_label.config(text=text, fg=FG_SUCCESS)
        self.detail_label.config(text="")

    def _on_launch_success(self, message):
        self.progress_bar["value"] = 100
        self.progress_bar.update_idletasks()
        self.status_label.config(text=message, fg=FG_SUCCESS)
        self.detail_label.config(text="")
        self.after(2500, self._reset_ui)

    def _on_error(self, message):
        self.progress_bar["value"] = 0
        self.progress_bar.update_idletasks()
        self.status_label.config(text=message, fg=FG_ERROR)
        self.detail_label.config(text="")
        self._reset_ui()

    def _reset_ui(self):
        self.is_busy = False
        self._set_controls_enabled(True)
        self.progress_bar.pack_forget()
        self.status_label.config(text="Ready to play", fg=FG_MUTED)

    def _set_controls_enabled(self, enabled):
        state = "normal" if enabled else "disabled"
        self.play_btn.config(state=state, bg=EMERALD if enabled else BTN_SECONDARY)
