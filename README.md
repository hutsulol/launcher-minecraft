# Minecraft Launcher

A simple Minecraft launcher built with Python and Tkinter.

## Features

- **User Authentication** – Register and log in with hashed passwords (SHA-256) stored in SQLite.
- **Persistent Login** – Remembers your last session; skip the login screen on next launch.
- **Version Selector** – Choose between Minecraft versions (1.20.4, 1.20.1, 1.19.4, 1.18.2).
- **Threaded Launching** – Progress feedback while launching; UI never freezes.
- **Clean UI** – Consistent dark theme with reusable components.
- **Error Handling** – Clear error messages for login failures, duplicate users, and launch issues.

## Project Structure

```
minecraft-launcher/
├── main.py                  # Application entry point
├── ui/
│   ├── components.py        # Reusable UI components & theme
│   ├── login.py             # Login screen
│   ├── register.py          # Registration screen
│   └── launcher.py          # Main launcher screen
├── auth/
│   ├── auth_manager.py      # Registration & login logic
│   ├── session.py           # Persistent login (auto-login)
│   └── database.py          # SQLite user storage
├── launcher/
│   └── minecraft_runner.py  # Minecraft launch logic
├── data/
│   ├── users.db             # Created automatically
│   └── session.json         # Created automatically
├── requirements.txt
└── README.md
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd minecraft-launcher
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   > `minecraft-launcher-lib` is optional – the launcher works without it but provides a better experience with it installed.

3. **Run the launcher**
   ```bash
   python main.py
   ```

## Requirements

- Python 3.10+
- Tkinter (included with most Python installations)
- Minecraft Java Edition installed (for launching)

## How It Works

1. Register a new account or log in with existing credentials.
2. On next launch, you are automatically logged in (persistent session).
3. Select a Minecraft version from the dropdown.
4. Click **PLAY** – a progress indicator shows launch stages without freezing the UI.
5. Click **Logout** to clear your session and return to the login screen.

## Security

- Passwords are hashed with SHA-256 before storage.
- User data is stored locally in an SQLite database.
- All inputs are validated (no empty fields, minimum password length).
