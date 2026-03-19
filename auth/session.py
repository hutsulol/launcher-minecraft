"""Session manager for persistent login (remember last logged-in user)."""

import json
import os

SESSION_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "session.json")


def save_session(username):
    """Save the logged-in username to a local JSON file."""
    os.makedirs(os.path.dirname(SESSION_PATH), exist_ok=True)
    with open(SESSION_PATH, "w") as f:
        json.dump({"username": username}, f)


def load_session():
    """Load the saved username, or return None if no session exists."""
    if not os.path.isfile(SESSION_PATH):
        return None
    try:
        with open(SESSION_PATH, "r") as f:
            data = json.load(f)
        return data.get("username")
    except (json.JSONDecodeError, OSError):
        return None


def clear_session():
    """Remove the saved session file (logout)."""
    if os.path.isfile(SESSION_PATH):
        os.remove(SESSION_PATH)
