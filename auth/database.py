"""Database module for storing user credentials using SQLite."""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "users.db")


def get_connection():
    """Return a connection to the SQLite database, creating it if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )"""
    )
    conn.commit()
    return conn


def user_exists(username):
    """Check if a username is already taken."""
    conn = get_connection()
    cursor = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def add_user(username, password_hash):
    """Insert a new user into the database."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    conn.commit()
    conn.close()


def get_password_hash(username):
    """Retrieve the stored password hash for a given username."""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT password_hash FROM users WHERE username = ?", (username,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None
