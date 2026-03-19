"""Module responsible for installing and launching Minecraft with NeoForge."""

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


def _get_lib():
    """Import and return minecraft_launcher_lib, or raise ImportError."""
    import minecraft_launcher_lib
    return minecraft_launcher_lib


# ------------------------------------------------------------------
# Vanilla Minecraft
# ------------------------------------------------------------------

def is_version_installed(minecraft_dir=None):
    """Check whether the hardcoded VERSION is already installed locally."""
    if minecraft_dir is None:
        minecraft_dir = get_minecraft_dir()
    try:
        lib = _get_lib()
        installed = lib.utils.get_installed_versions(minecraft_dir)
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
        lib = _get_lib()
    except ImportError:
        return False, (
            "minecraft-launcher-lib is not installed.\n"
            "Run: pip install minecraft-launcher-lib"
        )

    try:
        lib.install.install_minecraft_version(
            VERSION, minecraft_dir, callback=_build_callback(progress_callback)
        )
        return True, ""
    except Exception as e:
        return False, _friendly_error("Installation failed", e)


# ------------------------------------------------------------------
# NeoForge
# ------------------------------------------------------------------

def _get_neoforge_loader():
    """Return the NeoForge ModLoader instance."""
    lib = _get_lib()
    return lib.mod_loader.get_mod_loader("neoforge")


def _get_neoforge_installed_id():
    """Return the version ID that NeoForge installs under, or None."""
    try:
        loader = _get_neoforge_loader()
        loader_version = loader.get_latest_loader_version(VERSION)
        if loader_version is None:
            return None
        return loader.get_installed_version(VERSION, loader_version)
    except Exception:
        return None


def is_neoforge_installed(minecraft_dir=None):
    """Check whether NeoForge for VERSION is installed."""
    if minecraft_dir is None:
        minecraft_dir = get_minecraft_dir()

    installed_id = _get_neoforge_installed_id()
    if installed_id is None:
        return False

    try:
        lib = _get_lib()
        installed = lib.utils.get_installed_versions(minecraft_dir)
        return installed_id in [v["id"] for v in installed]
    except ImportError:
        return False


def install_neoforge(progress_callback=None, minecraft_dir=None):
    """Install NeoForge for VERSION.

    This also installs vanilla Minecraft automatically if needed.
    Returns (success, error_message) tuple.
    """
    if minecraft_dir is None:
        minecraft_dir = get_minecraft_dir()

    try:
        loader = _get_neoforge_loader()
    except ImportError:
        return False, (
            "minecraft-launcher-lib is not installed.\n"
            "Run: pip install minecraft-launcher-lib"
        )
    except Exception as e:
        return False, f"NeoForge not available: {e}"

    try:
        loader.install(
            VERSION, minecraft_dir,
            callback=_build_callback(progress_callback),
        )
        return True, ""
    except Exception as e:
        return False, _friendly_error("NeoForge installation failed", e)


# ------------------------------------------------------------------
# Launch
# ------------------------------------------------------------------

def launch_version(username, minecraft_dir=None):
    """Launch NeoForge version in offline mode, falling back to vanilla.

    Returns (success, message) tuple.
    """
    if minecraft_dir is None:
        minecraft_dir = get_minecraft_dir()

    try:
        lib = _get_lib()
    except ImportError:
        return _fallback_launch(minecraft_dir, username)

    # Determine which version ID to launch — prefer NeoForge
    neoforge_id = _get_neoforge_installed_id()
    if neoforge_id:
        installed = lib.utils.get_installed_versions(minecraft_dir)
        installed_ids = [v["id"] for v in installed]
        launch_id = neoforge_id if neoforge_id in installed_ids else VERSION
    else:
        launch_id = VERSION

    options = lib.utils.generate_test_options()
    options["username"] = username

    try:
        command = lib.command.get_minecraft_command(
            launch_id, minecraft_dir, options
        )
        subprocess.Popen(command)
        label = f"NeoForge {launch_id}" if launch_id != VERSION else f"Minecraft {VERSION}"
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
