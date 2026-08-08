import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncGenerator
import aiosqlite

from app.db.schema import CREATE_TABLES_SQL, DEFAULT_TICKERS

logger = logging.getLogger("finally.db")


@asynccontextmanager
async def get_db(db_path: Path) -> AsyncGenerator[aiosqlite.Connection, None]:
    """Async context manager for SQLite database connection."""
    async with aiosqlite.connect(db_path) as db:
        await db.execute("PRAGMA journal_mode=WAL;")
        await db.execute("PRAGMA busy_timeout=5000;")
        yield db


async def init_db(db_path: Path) -> None:
    """Initialize database tables and default seed data if not present."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(CREATE_TABLES_SQL)
        await db.commit()

        # Check and seed user profile
        async with db.execute("SELECT id FROM users_profile WHERE id = 'default'") as cursor:
            row = await cursor.fetchone()
            if not row:
                now = datetime.now(timezone.utc).isoformat()
                await db.execute(
                    "INSERT INTO users_profile (id, cash_balance, created_at) VALUES ('default', 10000.0, ?)",
                    (now,)
                )
                logger.info("Seeded default user profile with $10,000 balance.")

        # Check and seed watchlist
        async with db.execute("SELECT COUNT(*) FROM watchlist WHERE user_id = 'default'") as cursor:
            count_row = await cursor.fetchone()
            count = count_row[0] if count_row else 0
            if count == 0:
                now = datetime.now(timezone.utc).isoformat()
                seed_rows = [
                    (str(uuid.uuid4()), "default", ticker, now)
                    for ticker in DEFAULT_TICKERS
                ]
                await db.executemany(
                    "INSERT INTO watchlist (id, user_id, ticker, added_at) VALUES (?, ?, ?, ?)",
                    seed_rows
                )
                logger.info(f"Seeded watchlist with {len(DEFAULT_TICKERS)} default tickers.")

        await db.commit()
