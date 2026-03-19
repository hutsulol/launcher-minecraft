"""Mod manager — switches modpacks per game mode before launching."""

import os
import shutil

# Directory containing per-mode modpack folders, relative to this file.
_MODPACKS_DIR = os.path.join(os.path.dirname(__file__), "modpacks")

# Map mode IDs (from servers.json) to modpack folder names.
MODE_TO_MODPACK = {
    "lungi": "lungi",
    "sea_battle": "seabattle",
}


def get_modpack_path(mode_id):
    """Return the absolute path to the modpack folder for a mode, or None."""
    folder = MODE_TO_MODPACK.get(mode_id)
    if folder is None:
        return None
    path = os.path.join(_MODPACKS_DIR, folder)
    return path if os.path.isdir(path) else None


def apply_modpack(mode_id, minecraft_dir, progress_callback=None):
    """Clear .minecraft/mods/ and copy the modpack for *mode_id* into it.

    Steps:
        1. Remove every file inside <minecraft_dir>/mods/
           (only files — sub-directories are left alone for safety).
        2. Copy all files from modpacks/<pack>/ into <minecraft_dir>/mods/.

    Returns (success, error_message) tuple.
    """
    mods_dir = os.path.join(minecraft_dir, "mods")

    # --- Step 1: clear existing mods ---------------------------------
    if progress_callback:
        progress_callback("Clearing old mods...", None, None)

    if os.path.isdir(mods_dir):
        for entry in os.listdir(mods_dir):
            full = os.path.join(mods_dir, entry)
            if os.path.isfile(full):
                os.remove(full)
    else:
        os.makedirs(mods_dir, exist_ok=True)

    # --- Step 2: resolve modpack -------------------------------------
    pack_path = get_modpack_path(mode_id)
    if pack_path is None:
        # No modpack configured for this mode — running with no mods is fine.
        return True, ""

    mod_files = [f for f in os.listdir(pack_path) if os.path.isfile(os.path.join(pack_path, f))]

    if not mod_files:
        return True, ""

    # --- Step 3: copy mods -------------------------------------------
    if progress_callback:
        progress_callback("Installing mods...", 0, None)
        progress_callback(None, None, len(mod_files))

    for i, filename in enumerate(mod_files):
        src = os.path.join(pack_path, filename)
        dst = os.path.join(mods_dir, filename)
        shutil.copy2(src, dst)
        if progress_callback:
            progress_callback(None, i + 1, None)

    if progress_callback:
        progress_callback("Mods ready!", None, None)

    return True, ""
