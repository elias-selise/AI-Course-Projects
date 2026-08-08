import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Optional
import httpx

from .interface import MarketDataSource
from .models import PriceUpdate
from .cache import PriceCache
from .seed_prices import SEED_PRICES


class MassiveDataSource(MarketDataSource):
    """Polygon.io / Massive REST API Client for market data."""

    def __init__(self, cache: PriceCache, api_key: str, poll_interval: float = 15.0):
        self.cache = cache
        self.api_key = api_key
        self.poll_interval = poll_interval
        self.tickers: List[str] = []
        self.prev_prices: Dict[str, float] = {}
        self._task: Optional[asyncio.Task] = None
        self._running = False
        self._http_client: Optional[httpx.AsyncClient] = None

    async def start(self, initial_tickers: List[str]) -> None:
        for t in initial_tickers:
            t_upper = t.upper().strip()
            if t_upper not in self.tickers:
                self.tickers.append(t_upper)
                self.prev_prices[t_upper] = SEED_PRICES.get(t_upper, 100.0)

        self._http_client = httpx.AsyncClient(timeout=10.0)
        self._running = True
        await self._poll_prices()
        self._task = asyncio.create_task(self._run_loop())

    async def _poll_prices(self) -> None:
        if not self.tickers:
            return

        now_iso = datetime.now(timezone.utc).isoformat()
        updates: List[PriceUpdate] = []

        # Try Polygon / Massive REST API
        for ticker in list(self.tickers):
            url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey={self.api_key}"
            try:
                if self._http_client:
                    resp = await self._http_client.get(url)
                    if resp.status_code == 200:
                        data = resp.json()
                        results = data.get("results", [])
                        if results:
                            close_p = float(results[0].get("c", self.prev_prices.get(ticker, 100.0)))
                            prev_p = self.prev_prices.get(ticker, close_p)
                            change = round(close_p - prev_p, 2)
                            direction = "up" if change > 0 else ("down" if change < 0 else "flat")
                            self.prev_prices[ticker] = close_p
                            updates.append(PriceUpdate(
                                ticker=ticker,
                                price=close_p,
                                previous_price=prev_p,
                                timestamp=now_iso,
                                change=change,
                                direction=direction,
                            ))
                            continue
            except Exception:
                pass

            # Fallback if API fails or rate limited
            prev_p = self.prev_prices.get(ticker, SEED_PRICES.get(ticker, 100.0))
            updates.append(PriceUpdate(
                ticker=ticker,
                price=prev_p,
                previous_price=prev_p,
                timestamp=now_iso,
                change=0.0,
                direction="flat",
            ))

        if updates:
            self.cache.update_batch(updates)

    async def _run_loop(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(self.poll_interval)
                await self._poll_prices()
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

        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None

    async def add_ticker(self, ticker: str) -> None:
        t_upper = ticker.upper().strip()
        if t_upper not in self.tickers:
            self.tickers.append(t_upper)
            self.prev_prices[t_upper] = SEED_PRICES.get(t_upper, 100.0)
            await self._poll_prices()

    async def remove_ticker(self, ticker: str) -> None:
        t_upper = ticker.upper().strip()
        if t_upper in self.tickers:
            self.tickers.remove(t_upper)
            self.prev_prices.pop(t_upper, None)

    def get_tickers(self) -> List[str]:
        return list(self.tickers)
