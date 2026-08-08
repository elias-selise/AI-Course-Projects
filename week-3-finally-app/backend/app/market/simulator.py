import asyncio
import logging
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.db.schema import DEFAULT_TICKERS
from app.market.cache import PriceCache
from app.market.interface import MarketDataSource
from app.market.models import PriceUpdate

logger = logging.getLogger("finally.market.simulator")

DEFAULT_INITIAL_PRICES = {
    "AAPL": 180.0,
    "GOOGL": 140.0,
    "MSFT": 400.0,
    "AMZN": 175.0,
    "TSLA": 200.0,
    "NVDA": 850.0,
    "META": 485.0,
    "JPM": 195.0,
    "V": 280.0,
    "NFLX": 600.0,
}

TECH_TICKERS = {"AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META"}
FINANCE_TICKERS = {"JPM", "V"}


class GBMSimulator:
    """Geometric Brownian Motion simulator with Cholesky sector correlation and shock events."""

    def __init__(
        self,
        tickers: Optional[List[str]] = None,
        initial_prices: Optional[Dict[str, float]] = None,
    ):
        self.tickers: List[str] = list(tickers) if tickers else list(DEFAULT_TICKERS)
        self.prices: Dict[str, float] = {}

        base_prices = dict(DEFAULT_INITIAL_PRICES)
        if initial_prices:
            base_prices.update(initial_prices)

        for t in self.tickers:
            self.prices[t] = base_prices.get(t, 100.0)

        self.dt = 0.5 / 86400.0  # 500ms time step in days
        self.mu = 0.0001
        self.sigma = 0.015
        self._rebuild_correlation_matrix()

    def _rebuild_correlation_matrix(self) -> None:
        n = len(self.tickers)
        if n == 0:
            self.L = np.empty((0, 0))
            return

        corr_matrix = np.full((n, n), 0.3)
        np.fill_diagonal(corr_matrix, 1.0)

        for i, t1 in enumerate(self.tickers):
            for j, t2 in enumerate(self.tickers):
                if i == j:
                    continue
                if t1 in TECH_TICKERS and t2 in TECH_TICKERS:
                    corr_matrix[i, j] = 0.6
                elif t1 in FINANCE_TICKERS and t2 in FINANCE_TICKERS:
                    corr_matrix[i, j] = 0.5

        # Ensure positive semi-definite matrix for Cholesky decomposition
        try:
            self.L = np.linalg.cholesky(corr_matrix)
        except np.linalg.LinAlgError:
            # Fallback to eigen-value clipping if numerical issues arise
            eigvals, eigvecs = np.linalg.eigh(corr_matrix)
            eigvals = np.maximum(eigvals, 1e-6)
            corr_matrix = eigvecs @ np.diag(eigvals) @ eigvecs.T
            self.L = np.linalg.cholesky(corr_matrix)

    def add_ticker(self, ticker: str, initial_price: float = 100.0) -> None:
        if ticker not in self.tickers:
            self.tickers.append(ticker)
            self.prices[ticker] = DEFAULT_INITIAL_PRICES.get(ticker, initial_price)
            self._rebuild_correlation_matrix()

    def remove_ticker(self, ticker: str) -> None:
        if ticker in self.tickers:
            self.tickers.remove(ticker)
            self.prices.pop(ticker, None)
            self._rebuild_correlation_matrix()

    def tick(self) -> List[PriceUpdate]:
        n = len(self.tickers)
        if n == 0:
            return []

        uncorrelated = np.random.normal(0, 1, n)
        correlated = self.L @ uncorrelated

        updates: List[PriceUpdate] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for idx, ticker in enumerate(self.tickers):
            prev_price = self.prices[ticker]

            # Random shock event (~0.1% chance)
            shock = 1.0
            if np.random.random() < 0.001:
                shock = 1.0 + np.random.uniform(-0.05, 0.05)

            drift = (self.mu - 0.5 * self.sigma**2) * self.dt
            diffusion = self.sigma * np.sqrt(self.dt) * correlated[idx]
            new_price = max(0.01, round(prev_price * np.exp(drift + diffusion) * shock, 2))

            self.prices[ticker] = new_price
            change = round(new_price - prev_price, 2)
            direction = "up" if change > 0 else ("down" if change < 0 else "flat")

            update = PriceUpdate(
                ticker=ticker,
                price=new_price,
                previous_price=prev_price,
                timestamp=now_iso,
                change=change,
                direction=direction,
            )
            updates.append(update)

        return updates


class SimulatorDataSource(MarketDataSource):
    """Market data source driven by GBMSimulator running on a 500ms background loop."""

    def __init__(
        self,
        cache: PriceCache,
        tickers: Optional[List[str]] = None,
        initial_prices: Optional[Dict[str, float]] = None,
    ):
        self.cache = cache
        self.simulator = GBMSimulator(tickers=tickers, initial_prices=initial_prices)
        self._task: Optional[asyncio.Task] = None
        self._running: bool = False

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("SimulatorDataSource started.")

    async def _run_loop(self) -> None:
        while self._running:
            try:
                updates = self.simulator.tick()
                if updates:
                    self.cache.set_many(updates)
            except Exception as e:
                logger.error(f"Error in simulator tick loop: {e}")
            await asyncio.sleep(0.5)

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
        logger.info("SimulatorDataSource stopped.")

    def add_ticker(self, ticker: str) -> None:
        self.simulator.add_ticker(ticker)

    def remove_ticker(self, ticker: str) -> None:
        self.simulator.remove_ticker(ticker)

    def get_tickers(self) -> List[str]:
        return list(self.simulator.tickers)
