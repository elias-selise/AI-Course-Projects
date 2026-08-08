import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
import httpx

from app.db.schema import DEFAULT_TICKERS
from app.market.cache import PriceCache
from app.market.interface import MarketDataSource
from app.market.models import PriceUpdate

logger = logging.getLogger("finally.market.massive")


class MassiveDataSource(MarketDataSource):
    """Polygon.io (Massive API) REST market data client implementation."""

    def __init__(
        self,
        api_key: str,
        cache: PriceCache,
        tickers: Optional[List[str]] = None,
        poll_interval: float = 2.0,
    ):
        self.api_key = api_key
        self.cache = cache
        self.tickers: List[str] = list(tickers) if tickers else list(DEFAULT_TICKERS)
        self.poll_interval = poll_interval
        self._previous_prices: Dict[str, float] = {}
        self._task: Optional[asyncio.Task] = None
        self._running: bool = False
        self._client: Optional[httpx.AsyncClient] = None

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._client = httpx.AsyncClient(timeout=5.0)
        self._task = asyncio.create_task(self._run_loop())
        logger.info("MassiveDataSource started.")

    async def _run_loop(self) -> None:
        while self._running:
            try:
                await self._fetch_and_update()
            except Exception as e:
                logger.error(f"Error fetching Polygon market data: {e}")
            await asyncio.sleep(self.poll_interval)

    async def _fetch_and_update(self) -> None:
        if not self._client or not self.tickers:
            return

        tickers_csv = ",".join(self.tickers)
        url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers={tickers_csv}&apiKey={self.api_key}"

        response = await self._client.get(url)
        if response.status_code != 200:
            logger.warning(f"Polygon API returned status {response.status_code}")
            return

        data = response.json()
        updates: List[PriceUpdate] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for item in data.get("tickers", []):
            ticker = item.get("ticker")
            if not ticker:
                continue

            last_trade = item.get("lastTrade", {})
            price = last_trade.get("p")
            if price is None:
                day_info = item.get("day", {})
                price = day_info.get("c") or day_info.get("vw")

            if price is None:
                continue

            prev_price = self._previous_prices.get(ticker, price)
            change = round(price - prev_price, 2)
            direction = "up" if change > 0 else ("down" if change < 0 else "flat")
            self._previous_prices[ticker] = price

            update = PriceUpdate(
                ticker=ticker,
                price=float(price),
                previous_price=float(prev_price),
                timestamp=now_iso,
                change=change,
                direction=direction,
            )
            updates.append(update)

        if updates:
            self.cache.set_many(updates)

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self._client:
            await self._client.aclose()
            self._client = None
        logger.info("MassiveDataSource stopped.")

    def add_ticker(self, ticker: str) -> None:
        if ticker not in self.tickers:
            self.tickers.append(ticker)

    def remove_ticker(self, ticker: str) -> None:
        if ticker in self.tickers:
            self.tickers.remove(ticker)
            self._previous_prices.pop(ticker, None)

    def get_tickers(self) -> List[str]:
        return list(self.tickers)
