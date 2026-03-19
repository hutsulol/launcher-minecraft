# Minecraft Launcher

A simple Minecraft launcher built with Python and Tkinter.

## Features

- **User Authentication** – Register and log in with hashed passwords (SHA-256) stored in SQLite.
- **Clean UI** – Login, registration, and launcher screens built with Tkinter.
- **Launch Minecraft** – Start Minecraft Java Edition in offline mode with your username.

## Project Structure

```
minecraft-launcher/
├── main.py                  # Application entry point
├── ui/
│   ├── login.py             # Login screen
│   ├── register.py          # Registration screen
│   └── launcher.py          # Main launcher screen
├── auth/
│   ├── auth_manager.py      # Registration & login logic
│   └── database.py          # SQLite user storage
├── launcher/
│   └── minecraft_runner.py  # Minecraft launch logic
├── data/
│   └── users.db             # Created automatically
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
2. Click **PLAY** to launch Minecraft with your username (offline mode).
3. The launcher uses `minecraft-launcher-lib` if available, otherwise attempts to open the system Minecraft launcher.

## Security

- Passwords are hashed with SHA-256 before storage.
- User data is stored locally in an SQLite database.
- All inputs are validated (no empty fields, minimum password length).
