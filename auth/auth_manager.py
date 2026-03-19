"""Authentication manager handling registration and login logic."""

import hashlib
from auth.database import user_exists, add_user, get_password_hash

MIN_PASSWORD_LENGTH = 4


def _hash_password(password):
    """Hash a password using SHA-256. Simple and requires no extra dependencies."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def validate_input(username, password):
    """Validate that username and password meet requirements.

    Returns (ok, error_message) tuple.
    """
    if not username or not username.strip():
        return False, "Username cannot be empty."
    if not password:
        return False, "Password cannot be empty."
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
    return True, ""


def register(username, password):
    """Register a new user.

    Returns (success, message) tuple.
    """
    ok, err = validate_input(username, password)
    if not ok:
        return False, err

    username = username.strip()
    if user_exists(username):
        return False, "Username already taken."

    add_user(username, _hash_password(password))
    return True, "Registration successful!"


def login(username, password):
    """Authenticate a user.

    Returns (success, message) tuple.
    """
    ok, err = validate_input(username, password)
    if not ok:
        return False, err

    username = username.strip()
    stored_hash = get_password_hash(username)
    if stored_hash is None:
        return False, "User not found."

    if stored_hash != _hash_password(password):
        return False, "Incorrect password."

    return True, "Login successful!"
