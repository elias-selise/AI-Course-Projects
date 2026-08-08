"""SQLite database connection and lazy initialization logic for FinAlly."""

import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Default tickers seeded on initial startup
DEFAULT_SEED_TICKERS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
    "NVDA", "META", "JPM", "V", "NFLX"
]

# Default DB Path: resolution checks environment variable or falls back to project root db/finally.db
def get_default_db_path() -> str:
    env_path = os.getenv("FINALLY_DB_PATH")
    if env_path:
        return env_path
    
    # Locate project root (assuming backend/app/db/connection.py)
    backend_dir = Path(__file__).resolve().parent.parent.parent
    root_dir = backend_dir.parent
    target_db_dir = root_dir / "db"
    target_db_dir.mkdir(parents=True, exist_ok=True)
    return str(target_db_dir / "finally.db")


CREATE_TABLES_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users_profile (
    id TEXT PRIMARY KEY DEFAULT 'default',
    cash_balance REAL DEFAULT 10000.0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS watchlist (
    id TEXT PRIMARY KEY,
    user_id TEXT DEFAULT 'default',
    ticker TEXT NOT NULL,
    added_at TEXT NOT NULL,
    UNIQUE(user_id, ticker)
);

CREATE TABLE IF NOT EXISTS positions (
    id TEXT PRIMARY KEY,
    user_id TEXT DEFAULT 'default',
    ticker TEXT NOT NULL,
    quantity REAL NOT NULL,
    avg_cost REAL NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(user_id, ticker)
);

CREATE TABLE IF NOT EXISTS trades (
    id TEXT PRIMARY KEY,
    user_id TEXT DEFAULT 'default',
    ticker TEXT NOT NULL,
    side TEXT NOT NULL CHECK(side IN ('buy', 'sell')),
    quantity REAL NOT NULL,
    price REAL NOT NULL,
    executed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    id TEXT PRIMARY KEY,
    user_id TEXT DEFAULT 'default',
    total_value REAL NOT NULL,
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id TEXT PRIMARY KEY,
    user_id TEXT DEFAULT 'default',
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    actions TEXT,
    created_at TEXT NOT NULL
);
"""


def init_db(conn: sqlite3.Connection) -> None:
    """Initialize database tables and seed default data if empty."""
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.executescript(CREATE_TABLES_SQL)

    # Check if default user profile exists
    cursor.execute("SELECT COUNT(*) as count FROM users_profile WHERE id = 'default'")
    row = cursor.fetchone()
    if not row or row["count"] == 0:
        now_iso = datetime.now(timezone.utc).isoformat()
        
        # Insert default user profile ($10,000 cash balance)
        cursor.execute(
            "INSERT INTO users_profile (id, cash_balance, created_at) VALUES (?, ?, ?)",
            ("default", 10000.0, now_iso),
        )

        # Seed 10 default tickers in watchlist
        for ticker in DEFAULT_SEED_TICKERS:
            item_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT OR IGNORE INTO watchlist (id, user_id, ticker, added_at)
                VALUES (?, ?, ?, ?)
                """,
                (item_id, "default", ticker, now_iso),
            )

        # Seed initial portfolio snapshot ($10,000 cash)
        snapshot_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO portfolio_snapshots (id, user_id, total_value, recorded_at)
            VALUES (?, ?, ?, ?)
            """,
            (snapshot_id, "default", 10000.0, now_iso),
        )

        conn.commit()


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Get SQLite database connection with lazy initialization.
    If db_path is None, defaults to `get_default_db_path()`.
    """
    if db_path is None:
        db_path = get_default_db_path()

    if db_path != ":memory:":
        parent_dir = os.path.dirname(os.path.abspath(db_path))
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    if db_path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL;")

    conn.execute("PRAGMA foreign_keys = ON;")
    
    # Lazy initialization
    init_db(conn)

    return conn
