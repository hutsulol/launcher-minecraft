"""Load launcher content data (servers, banner) from JSON."""

import json
import os

_DATA_DIR = os.path.dirname(__file__)
_SERVERS_FILE = os.path.join(_DATA_DIR, "servers.json")


def load_launcher_data():
    """Load and return the full launcher data dict from servers.json.

    Returns {"banner": {...}, "servers": [...]}.
    Falls back to defaults if the file is missing.
    """
    if os.path.isfile(_SERVERS_FILE):
        with open(_SERVERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    # Fallback defaults
    return {
        "banner": {
            "title": "Welcome to Lungi Launcher",
            "subtitle": "Select a server and start playing",
            "icon": "\u2693",
            "badge": None,
        },
        "servers": [
            {
                "title": "Default Server",
                "desc": "Vanilla Minecraft",
                "icon": "\u2694",
                "players": 0,
            }
        ],
    }
