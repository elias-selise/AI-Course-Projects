import asyncio
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiosqlite

from app.db.database import get_db
from app.market.cache import PriceCache

logger = logging.getLogger("finally.snapshot")


async def record_snapshot(db: aiosqlite.Connection, cache: PriceCache, user_id: str = "default") -> float:
    """Record current total portfolio value into portfolio_snapshots table."""
    async with db.execute("SELECT cash_balance FROM users_profile WHERE id = ?", (user_id,)) as cursor:
        row = await cursor.fetchone()
        cash = row[0] if row else 10000.0

    pos_value = 0.0
    async with db.execute(
        "SELECT ticker, quantity, avg_cost FROM positions WHERE user_id = ? AND quantity > 0",
        (user_id,)
    ) as cursor:
        rows = await cursor.fetchall()
        for ticker, qty, avg_cost in rows:
            price_update = cache.get(ticker) if cache else None
            price = price_update.price if price_update else avg_cost
            pos_value += (qty * price)

    total_val = round(cash + pos_value, 2)
    now_iso = datetime.now(timezone.utc).isoformat()
    snap_id = str(uuid.uuid4())

    await db.execute(
        "INSERT INTO portfolio_snapshots (id, user_id, total_value, recorded_at) VALUES (?, ?, ?, ?)",
        (snap_id, user_id, total_val, now_iso)
    )
    return total_val


class SnapshotTask:
    """Periodic portfolio snapshot background service."""

    def __init__(self, db_path: Path, cache: PriceCache, interval_seconds: int = 30):
        self.db_path = db_path
        self.cache = cache
        self.interval = interval_seconds
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def _run_loop(self):
        logger.info(f"Starting portfolio snapshot background task ({self.interval}s interval)...")
        while self._running:
            try:
                async with get_db(self.db_path) as db:
                    total_val = await record_snapshot(db, self.cache)
                    await db.commit()
                    logger.debug(f"Recorded background snapshot: ${total_val:.2f}")
            except Exception as e:
                logger.error(f"Error in snapshot background task: {e}")

            try:
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break

    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._run_loop())

    async def stop(self):
        if self._running:
            self._running = False
            if self._task:
                self._task.cancel()
                try:
                    await self._task
                except asyncio.CancelledError:
                    pass
            logger.info("Stopped snapshot background task.")
