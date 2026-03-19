"""Module responsible for installing and launching Minecraft with Forge."""

import subprocess
import os
import platform

# The single hardcoded vanilla version used everywhere
VERSION = "1.21.4"


def get_minecraft_dir():
    """Return the default .minecraft directory path for the current OS."""
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ.get("APPDATA", ""), ".minecraft")
    elif system == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/minecraft")
    else:  # Linux
        return os.path.expanduser("~/.minecraft")


def _build_callback(progress_callback):
    """Build the callback dict that minecraft-launcher-lib expects."""
    if not progress_callback:
        return {}
    return {
        "setStatus": lambda text: progress_callback(text, None, None),
        "setProgress": lambda value: progress_callback(None, value, None),
        "setMax": lambda value: progress_callback(None, None, value),
    }


# ------------------------------------------------------------------
# Vanilla Minecraft
# ------------------------------------------------------------------

def is_version_installed(minecraft_dir=None):
    """Check whether the hardcoded VERSION is already installed locally."""
    if minecraft_dir is None:
        minecraft_dir = get_minecraft_dir()
    try:
        import minecraft_launcher_lib
        installed = minecraft_launcher_lib.utils.get_installed_versions(minecraft_dir)
        return VERSION in [v["id"] for v in installed]
    except ImportError:
        return False


def install_version(progress_callback=None, minecraft_dir=None):
    """Install the hardcoded VERSION using minecraft-launcher-lib.

    Returns (success, error_message) tuple.
    """
    if minecraft_dir is None:
        minecraft_dir = get_minecraft_dir()

    try:
        import minecraft_launcher_lib
    except ImportError:
        return False, (
            "minecraft-launcher-lib is not installed.\n"
            "Run: pip install minecraft-launcher-lib"
        )

    try:
        minecraft_launcher_lib.install.install_minecraft_version(
            VERSION, minecraft_dir, callback=_build_callback(progress_callback)
        )
        return True, ""
    except Exception as e:
        return False, _friendly_error("Installation failed", e)


# ------------------------------------------------------------------
# Forge
# ------------------------------------------------------------------

def find_forge(minecraft_dir=None):
    """Find the latest Forge version for VERSION.

    Returns (forge_version, installed_id) or (None, None) if unavailable.
    forge_version  – e.g. "1.21.4-54.1.13"  (used by install)
    installed_id   – e.g. "1.21.4-forge-54.1.13" (used by launch)
    """
    try:
        import minecraft_launcher_lib
    except ImportError:
        return None, None

    forge_version = minecraft_launcher_lib.forge.find_forge_version(VERSION)
    if forge_version is None:
        return None, None

    installed_id = minecraft_launcher_lib.forge.forge_to_installed_version(
        forge_version
    )
    return forge_version, installed_id


def is_forge_installed(minecraft_dir=None):
    """Check whether Forge for VERSION is installed."""
    if minecraft_dir is None:
        minecraft_dir = get_minecraft_dir()

    _, installed_id = find_forge()
    if installed_id is None:
        return False

    try:
        import minecraft_launcher_lib
        installed = minecraft_launcher_lib.utils.get_installed_versions(minecraft_dir)
        return installed_id in [v["id"] for v in installed]
    except ImportError:
        return False


def install_forge(progress_callback=None, minecraft_dir=None):
    """Install Forge for VERSION.

    This also installs vanilla Minecraft automatically if needed.
    Returns (success, error_message) tuple.
    """
    if minecraft_dir is None:
        minecraft_dir = get_minecraft_dir()

    try:
        import minecraft_launcher_lib
    except ImportError:
        return False, (
            "minecraft-launcher-lib is not installed.\n"
            "Run: pip install minecraft-launcher-lib"
        )

    forge_version, _ = find_forge()
    if forge_version is None:
        return False, f"No Forge version found for Minecraft {VERSION}."

    try:
        minecraft_launcher_lib.forge.install_forge_version(
            forge_version, minecraft_dir,
            callback=_build_callback(progress_callback),
        )
        return True, ""
    except Exception as e:
        return False, _friendly_error("Forge installation failed", e)


# ------------------------------------------------------------------
# Launch
# ------------------------------------------------------------------

def launch_version(username, minecraft_dir=None):
    """Launch Forge version in offline mode, falling back to vanilla.

    Returns (success, message) tuple.
    """
    if minecraft_dir is None:
        minecraft_dir = get_minecraft_dir()

    try:
        import minecraft_launcher_lib
    except ImportError:
        return _fallback_launch(minecraft_dir, username)

    # Determine which version ID to launch — prefer Forge
    _, forge_id = find_forge()
    if forge_id:
        installed = minecraft_launcher_lib.utils.get_installed_versions(minecraft_dir)
        installed_ids = [v["id"] for v in installed]
        launch_id = forge_id if forge_id in installed_ids else VERSION
    else:
        launch_id = VERSION

    options = minecraft_launcher_lib.utils.generate_test_options()
    options["username"] = username

    try:
        command = minecraft_launcher_lib.command.get_minecraft_command(
            launch_id, minecraft_dir, options
        )
        subprocess.Popen(command)
        label = f"Forge {launch_id}" if launch_id != VERSION else f"Minecraft {VERSION}"
        return True, f"{label} launched as {username}!"
    except Exception as e:
        return False, f"Launch failed: {e}"


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _friendly_error(prefix, exc):
    """Turn common exceptions into user-friendly messages."""
    error_msg = str(exc)
    name = type(exc).__name__
    if "ConnectionError" in name or "URLError" in name:
        error_msg = "No internet connection. Check your network and try again."
    elif "HTTPError" in name:
        error_msg = f"Download failed: {error_msg}"
    return f"{prefix}: {error_msg}"


def _fallback_launch(minecraft_dir, username):
    """Fallback launcher when minecraft-launcher-lib is not installed."""
    if not os.path.isdir(minecraft_dir):
        return False, (
            f"Minecraft directory not found: {minecraft_dir}\n"
            "Install Minecraft or pip install minecraft-launcher-lib"
        )

    system = platform.system()
    launcher_path = None

    if system == "Windows":
        candidates = [
            os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Minecraft Launcher", "MinecraftLauncher.exe"),
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Minecraft Launcher", "MinecraftLauncher.exe"),
        ]
        for path in candidates:
            if os.path.isfile(path):
                launcher_path = path
                break
    elif system == "Linux":
        launcher_path = "minecraft-launcher"

    if launcher_path:
        try:
            subprocess.Popen([launcher_path])
            return True, f"Opened Minecraft launcher (log in as {username})."
        except FileNotFoundError:
            pass

    return False, (
        "Could not find Minecraft launcher.\n"
        "Install minecraft-launcher-lib: pip install minecraft-launcher-lib"
    )
