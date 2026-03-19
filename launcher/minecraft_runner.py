"""Module responsible for installing and launching Minecraft Java Edition."""

import subprocess
import os
import platform

# The single hardcoded version used everywhere
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

    progress_callback(stage, progress, max_progress):
        stage       - string like "Installing Minecraft...", "Downloading libraries..."
        progress    - current item count
        max_progress - total item count (0 if unknown)

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

    # Build the callback dict that minecraft-launcher-lib expects
    callback = {}
    if progress_callback:
        callback["setStatus"] = lambda text: progress_callback(text, 0, 0)
        callback["setProgress"] = lambda value: progress_callback(None, value, None)
        callback["setMax"] = lambda value: progress_callback(None, None, value)

    try:
        minecraft_launcher_lib.install.install_minecraft_version(
            VERSION, minecraft_dir, callback=callback
        )
        return True, ""
    except Exception as e:
        error_msg = str(e)
        # Provide user-friendly messages for common errors
        if "ConnectionError" in type(e).__name__ or "URLError" in type(e).__name__:
            error_msg = "No internet connection. Check your network and try again."
        elif "HTTPError" in type(e).__name__:
            error_msg = f"Download failed: {error_msg}"
        return False, f"Installation failed: {error_msg}"


def launch_version(username, minecraft_dir=None):
    """Launch the hardcoded VERSION in offline mode.

    Returns (success, message) tuple.
    """
    if minecraft_dir is None:
        minecraft_dir = get_minecraft_dir()

    try:
        import minecraft_launcher_lib
    except ImportError:
        return _fallback_launch(minecraft_dir, username)

    # Build launch options for offline mode
    options = minecraft_launcher_lib.utils.generate_test_options()
    options["username"] = username

    try:
        command = minecraft_launcher_lib.command.get_minecraft_command(
            VERSION, minecraft_dir, options
        )
        subprocess.Popen(command)
        return True, f"Minecraft {VERSION} launched as {username}!"
    except Exception as e:
        return False, f"Launch failed: {e}"


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
