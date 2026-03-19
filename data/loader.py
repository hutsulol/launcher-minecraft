"""Load launcher content data (modes, banner) from JSON."""

import json
import os

_DATA_DIR = os.path.dirname(__file__)
_SERVERS_FILE = os.path.join(_DATA_DIR, "servers.json")

# Fallback used when servers.json is missing
_FALLBACK = {
    "banner": {
        "title": "Welcome to Lungi Launcher",
        "subtitle": "Select a mode and start playing",
        "icon": "\u2693",
        "badge": None,
    },
    "modes": [
        {
            "id": "default",
            "title": "Default",
            "desc": "Vanilla Minecraft",
            "icon": "\u2694",
            "players": 0,
            "coming_soon": False,
            "description": "Standard Minecraft experience.",
            "features": [],
            "wipe_date": None,
            "gallery": [],
        }
    ],
}


def load_launcher_data():
    """Load and return the full launcher data dict from servers.json.

    Returns {"banner": {...}, "modes": [...]}.
    Falls back to defaults if the file is missing.
    """
    if os.path.isfile(_SERVERS_FILE):
        with open(_SERVERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return _FALLBACK
