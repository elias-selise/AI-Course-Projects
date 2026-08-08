import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import DATABASE_PATH

DEFAULT_WATCHLIST_TICKERS = [
    "AAPL", "GOOGL", "MSFT", "AMZN", "TSLA",
    "NVDA", "META", "JPM", "V", "NFLX"
]


def get_db_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    target_path = db_path or DATABASE_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    conn = get_db_connection(db_path)
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users_profile (
                id TEXT PRIMARY KEY,
                cash_balance REAL NOT NULL DEFAULT 10000.0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS watchlist (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'default',
                ticker TEXT NOT NULL,
                added_at TEXT NOT NULL,
                UNIQUE(user_id, ticker)
            );

            CREATE TABLE IF NOT EXISTS positions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'default',
                ticker TEXT NOT NULL,
                quantity REAL NOT NULL,
                avg_cost REAL NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(user_id, ticker)
            );

            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'default',
                ticker TEXT NOT NULL,
                side TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                executed_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'default',
                total_value REAL NOT NULL,
                recorded_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL DEFAULT 'default',
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                actions TEXT,
                created_at TEXT NOT NULL
            );
        """)

        # Seed user profile if missing
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users_profile WHERE id = 'default'")
        if not cursor.fetchone():
            now_iso = datetime.now(timezone.utc).isoformat()
            cursor.execute(
                "INSERT INTO users_profile (id, cash_balance, created_at) VALUES (?, ?, ?)",
                ("default", 10000.0, now_iso)
            )

        # Seed watchlist if missing for default user
        cursor.execute("SELECT COUNT(*) as count FROM watchlist WHERE user_id = 'default'")
        count = cursor.fetchone()["count"]
        if count == 0:
            now_iso = datetime.now(timezone.utc).isoformat()
            for ticker in DEFAULT_WATCHLIST_TICKERS:
                cursor.execute(
                    "INSERT INTO watchlist (id, user_id, ticker, added_at) VALUES (?, ?, ?, ?)",
                    (str(uuid.uuid4()), "default", ticker, now_iso)
                )

        # Record initial portfolio snapshot if empty
        cursor.execute("SELECT COUNT(*) as count FROM portfolio_snapshots WHERE user_id = 'default'")
        snapshot_count = cursor.fetchone()["count"]
        if snapshot_count == 0:
            now_iso = datetime.now(timezone.utc).isoformat()
            cursor.execute(
                "INSERT INTO portfolio_snapshots (id, user_id, total_value, recorded_at) VALUES (?, ?, ?, ?)",
                (str(uuid.uuid4()), "default", 10000.0, now_iso)
            )

    conn.close()


def get_user_profile(user_id: str = "default", db_path: Optional[Path] = None) -> Dict[str, Any]:
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users_profile WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        # Fallback if profile doesn't exist
        now_iso = datetime.now(timezone.utc).isoformat()
        with conn:
            conn.execute(
                "INSERT INTO users_profile (id, cash_balance, created_at) VALUES (?, ?, ?)",
                (user_id, 10000.0, now_iso)
            )
        return {"id": user_id, "cash_balance": 10000.0, "created_at": now_iso}
    finally:
        conn.close()


def update_cash_balance(new_balance: float, user_id: str = "default", db_path: Optional[Path] = None) -> None:
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute("UPDATE users_profile SET cash_balance = ? WHERE id = ?", (new_balance, user_id))
    finally:
        conn.close()


def get_watchlist(user_id: str = "default", db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM watchlist WHERE user_id = ? ORDER BY added_at ASC", (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def add_watchlist_ticker(ticker: str, user_id: str = "default", db_path: Optional[Path] = None) -> Dict[str, Any]:
    ticker_clean = ticker.strip().upper()
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM watchlist WHERE user_id = ? AND ticker = ?", (user_id, ticker_clean))
        existing = cursor.fetchone()
        if existing:
            return dict(existing)

        now_iso = datetime.now(timezone.utc).isoformat()
        item_id = str(uuid.uuid4())
        with conn:
            conn.execute(
                "INSERT INTO watchlist (id, user_id, ticker, added_at) VALUES (?, ?, ?, ?)",
                (item_id, user_id, ticker_clean, now_iso)
            )
        return {"id": item_id, "user_id": user_id, "ticker": ticker_clean, "added_at": now_iso}
    finally:
        conn.close()


def remove_watchlist_ticker(ticker: str, user_id: str = "default", db_path: Optional[Path] = None) -> bool:
    ticker_clean = ticker.strip().upper()
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM watchlist WHERE user_id = ? AND ticker = ?", (user_id, ticker_clean))
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_positions(user_id: str = "default", db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE user_id = ? ORDER BY ticker ASC", (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_position(ticker: str, user_id: str = "default", db_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    ticker_clean = ticker.strip().upper()
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE user_id = ? AND ticker = ?", (user_id, ticker_clean))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def upsert_position(ticker: str, quantity: float, avg_cost: float, user_id: str = "default", db_path: Optional[Path] = None) -> Dict[str, Any]:
    ticker_clean = ticker.strip().upper()
    conn = get_db_connection(db_path)
    now_iso = datetime.now(timezone.utc).isoformat()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM positions WHERE user_id = ? AND ticker = ?", (user_id, ticker_clean))
        existing = cursor.fetchone()
        with conn:
            if existing:
                pos_id = existing["id"]
                conn.execute(
                    "UPDATE positions SET quantity = ?, avg_cost = ?, updated_at = ? WHERE id = ?",
                    (quantity, avg_cost, now_iso, pos_id)
                )
            else:
                pos_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO positions (id, user_id, ticker, quantity, avg_cost, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (pos_id, user_id, ticker_clean, quantity, avg_cost, now_iso)
                )
        return {
            "id": pos_id,
            "user_id": user_id,
            "ticker": ticker_clean,
            "quantity": quantity,
            "avg_cost": avg_cost,
            "updated_at": now_iso,
        }
    finally:
        conn.close()


def delete_position(ticker: str, user_id: str = "default", db_path: Optional[Path] = None) -> bool:
    ticker_clean = ticker.strip().upper()
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM positions WHERE user_id = ? AND ticker = ?", (user_id, ticker_clean))
            return cursor.rowcount > 0
    finally:
        conn.close()


def record_trade(ticker: str, side: str, quantity: float, price: float, user_id: str = "default", db_path: Optional[Path] = None) -> Dict[str, Any]:
    ticker_clean = ticker.strip().upper()
    now_iso = datetime.now(timezone.utc).isoformat()
    trade_id = str(uuid.uuid4())
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                "INSERT INTO trades (id, user_id, ticker, side, quantity, price, executed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (trade_id, user_id, ticker_clean, side.lower(), quantity, price, now_iso)
            )
        return {
            "id": trade_id,
            "user_id": user_id,
            "ticker": ticker_clean,
            "side": side.lower(),
            "quantity": quantity,
            "price": price,
            "executed_at": now_iso,
        }
    finally:
        conn.close()


def record_snapshot(total_value: float, user_id: str = "default", db_path: Optional[Path] = None) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    snapshot_id = str(uuid.uuid4())
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                "INSERT INTO portfolio_snapshots (id, user_id, total_value, recorded_at) VALUES (?, ?, ?, ?)",
                (snapshot_id, user_id, total_value, now_iso)
            )
        return {
            "id": snapshot_id,
            "user_id": user_id,
            "total_value": total_value,
            "recorded_at": now_iso,
        }
    finally:
        conn.close()


def get_snapshots(user_id: str = "default", db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM portfolio_snapshots WHERE user_id = ? ORDER BY recorded_at ASC", (user_id,))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def get_chat_messages(user_id: str = "default", limit: int = 50, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_messages WHERE user_id = ? ORDER BY created_at ASC LIMIT ?", (user_id, limit))
        return [dict(row) for row in cursor.fetchall()]
    finally:
        conn.close()


def record_chat_message(role: str, content: str, actions: Optional[str] = None, user_id: str = "default", db_path: Optional[Path] = None) -> Dict[str, Any]:
    now_iso = datetime.now(timezone.utc).isoformat()
    msg_id = str(uuid.uuid4())
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                "INSERT INTO chat_messages (id, user_id, role, content, actions, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (msg_id, user_id, role, content, actions, now_iso)
            )
        return {
            "id": msg_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "actions": actions,
            "created_at": now_iso,
        }
    finally:
        conn.close()
