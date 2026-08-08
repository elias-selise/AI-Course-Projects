import asyncio
from typing import Optional
from app.market.cache import PriceCache
from app.portfolio.service import get_portfolio_summary
from app.db.database import record_snapshot


class SnapshotTask:
    def __init__(self, price_cache: PriceCache, interval: float = 30.0, user_id: str = "default", db_path=None):
        self.price_cache = price_cache
        self.interval = interval
        self.user_id = user_id
        self.db_path = db_path
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def _run_loop(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(self.interval)
                summary = get_portfolio_summary(self.user_id, self.price_cache, db_path=self.db_path)
                total_val = summary["total_portfolio_value"]
                record_snapshot(total_val, self.user_id, db_path=self.db_path)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(1.0)

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
