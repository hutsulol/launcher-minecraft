"""Module responsible for launching Minecraft Java Edition."""

import subprocess
import os
import platform


def _find_minecraft_dir():
    """Return the default .minecraft directory path for the current OS."""
    system = platform.system()
    if system == "Windows":
        return os.path.join(os.environ.get("APPDATA", ""), ".minecraft")
    elif system == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/minecraft")
    else:  # Linux
        return os.path.expanduser("~/.minecraft")


def launch_minecraft(username, version="1.20.4"):
    """Launch Minecraft in offline mode with the given username.

    Attempts to use minecraft-launcher-lib if installed,
    otherwise falls back to direct subprocess launch.

    Returns (success, message) tuple.
    """
    minecraft_dir = _find_minecraft_dir()

    # Try using minecraft-launcher-lib first
    try:
        import minecraft_launcher_lib

        # Check if the version is installed
        installed = minecraft_launcher_lib.utils.get_installed_versions(minecraft_dir)
        version_ids = [v["id"] for v in installed]

        if version not in version_ids:
            return False, (
                f"Version {version} not installed.\n"
                f"Minecraft dir: {minecraft_dir}\n"
                f"Installed versions: {', '.join(version_ids) or 'none'}"
            )

        # Build launch options for offline mode
        options = minecraft_launcher_lib.utils.generate_test_options()
        options["username"] = username

        command = minecraft_launcher_lib.command.get_minecraft_command(
            version, minecraft_dir, options
        )
        subprocess.Popen(command)
        return True, f"Minecraft {version} launched as {username}!"

    except ImportError:
        # Fallback: try launching the system Minecraft directly
        return _fallback_launch(minecraft_dir, username)


def _fallback_launch(minecraft_dir, username):
    """Fallback launcher when minecraft-launcher-lib is not installed."""
    if not os.path.isdir(minecraft_dir):
        return False, (
            f"Minecraft directory not found: {minecraft_dir}\n"
            "Install Minecraft or pip install minecraft-launcher-lib"
        )

    # Look for the official launcher executable
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
        # Try common Linux launcher command
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
