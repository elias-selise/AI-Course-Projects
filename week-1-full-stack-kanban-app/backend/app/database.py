import json
import sqlite3

from . import config


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS boards (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        cursor.execute("SELECT id FROM users WHERE username = ?", (config.USERNAME,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (id, username, password) VALUES ('user-1', ?, ?)",
                (config.USERNAME, config.PASSWORD),
            )
            cursor.execute(
                "INSERT INTO boards (id, user_id, data) VALUES ('board-1', 'user-1', ?)",
                (json.dumps(config.DEFAULT_COLUMNS),),
            )
        conn.commit()
    finally:
        conn.close()
