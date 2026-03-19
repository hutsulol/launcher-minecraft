"""Mod manager — downloads required mods into .minecraft/mods/ before launch."""

import os
import requests

from launcher.minecraft_runner import get_minecraft_dir


def get_mods_dir(minecraft_dir=None):
    """Return the path to .minecraft/mods/, creating it if needed."""
    if minecraft_dir is None:
        minecraft_dir = get_minecraft_dir()
    mods_dir = os.path.join(minecraft_dir, "mods")
    os.makedirs(mods_dir, exist_ok=True)
    return mods_dir


def install_mods(mods, progress_callback=None, minecraft_dir=None):
    """Download any missing mods into the mods folder.

    mods: list of dicts with "name" and "url" keys.
    progress_callback(stage, progress, max_progress):
        stage        - status text (str or None)
        progress     - current item index (int or None)
        max_progress - total item count (int or None)

    Returns (success, error_message) tuple.
    """
    if not mods:
        return True, ""

    mods_dir = get_mods_dir(minecraft_dir)
    total = len(mods)

    if progress_callback:
        progress_callback("Downloading mods...", None, total)

    for i, mod in enumerate(mods):
        name = mod["name"]
        url = mod["url"]
        dest = os.path.join(mods_dir, name)

        # Skip mods that are already downloaded
        if os.path.isfile(dest):
            if progress_callback:
                progress_callback(None, i + 1, None)
            continue

        # Download the mod
        if progress_callback:
            progress_callback(f"Downloading {name}...", i, None)

        try:
            resp = requests.get(url, timeout=60, stream=True)
            resp.raise_for_status()

            # Write to a temp file first, then rename — avoids partial files
            tmp_path = dest + ".tmp"
            with open(tmp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            os.replace(tmp_path, dest)

        except requests.ConnectionError:
            return False, (
                f"No internet connection.\n"
                f"Could not download {name}."
            )
        except requests.HTTPError as e:
            return False, f"Download failed for {name}: {e}"
        except requests.Timeout:
            return False, f"Download timed out for {name}."
        except OSError as e:
            return False, f"Could not save {name}: {e}"

        if progress_callback:
            progress_callback(None, i + 1, None)

    if progress_callback:
        progress_callback("Mods installed!", total, None)

    return True, ""
