import asyncio
import random
import math
from datetime import datetime, timezone
from typing import List, Dict, Optional
import numpy as np

from .interface import MarketDataSource
from .models import PriceUpdate
from .cache import PriceCache
from .seed_prices import (
    SEED_PRICES,
    GBM_PARAMS,
    CORRELATION_GROUPS,
    SAME_GROUP_CORR,
    CROSS_GROUP_CORR,
)


class GBMSimulator:
    def __init__(self, initial_tickers: Optional[List[str]] = None):
        self.tickers: List[str] = []
        self.prices: Dict[str, float] = {}
        self.prev_prices: Dict[str, float] = {}
        
        tickers_to_add = initial_tickers or list(SEED_PRICES.keys())
        for t in tickers_to_add:
            self.add_ticker(t)

    def get_tickers(self) -> List[str]:
        return list(self.tickers)

    def add_ticker(self, ticker: str) -> None:
        t_upper = ticker.upper().strip()
        if t_upper not in self.tickers:
            self.tickers.append(t_upper)
            seed = SEED_PRICES.get(t_upper, 100.0)
            self.prices[t_upper] = seed
            self.prev_prices[t_upper] = seed

    def remove_ticker(self, ticker: str) -> None:
        t_upper = ticker.upper().strip()
        if t_upper in self.tickers:
            self.tickers.remove(t_upper)
            self.prices.pop(t_upper, None)
            self.prev_prices.pop(t_upper, None)

    def _build_correlation_matrix(self) -> np.ndarray:
        n = len(self.tickers)
        if n == 0:
            return np.empty((0, 0))
        corr = np.eye(n)
        
        # Build ticker to group map
        ticker_to_group = {}
        for group, members in CORRELATION_GROUPS.items():
            for m in members:
                ticker_to_group[m] = group

        for i in range(n):
            for j in range(i + 1, n):
                t1, t2 = self.tickers[i], self.tickers[j]
                g1 = ticker_to_group.get(t1)
                g2 = ticker_to_group.get(t2)
                
                if g1 and g2 and g1 == g2:
                    c_val = SAME_GROUP_CORR
                else:
                    c_val = CROSS_GROUP_CORR
                corr[i, j] = c_val
                corr[j, i] = c_val
        return corr

    def step(self, dt: float = 1.0 / (252 * 6.5 * 3600)) -> List[PriceUpdate]:
        """Perform one simulation step and return PriceUpdate objects."""
        n = len(self.tickers)
        if n == 0:
            return []

        corr = self._build_correlation_matrix()

        # Compute Cholesky decomposition or nearest positive semi-definite matrix
        try:
            L = np.linalg.cholesky(corr)
        except np.linalg.LinAlgError:
            # Fallback to eigenvalue adjustment if non-positive definite
            eigvals, eigvecs = np.linalg.eigh(corr)
            eigvals = np.maximum(eigvals, 1e-6)
            corr_psd = eigvecs @ np.diag(eigvals) @ eigvecs.T
            # Normalize diagonal to 1
            inv_std = 1.0 / np.sqrt(np.diag(corr_psd))
            corr_psd = np.outer(inv_std, inv_std) * corr_psd
            L = np.linalg.cholesky(corr_psd)

        uncorrelated = np.random.normal(0.0, 1.0, size=n)
        Z = L @ uncorrelated

        updates: List[PriceUpdate] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for i, ticker in enumerate(self.tickers):
            mu, sigma = GBM_PARAMS.get(ticker, (0.05, 0.25))
            current_p = self.prices[ticker]
            self.prev_prices[ticker] = current_p

            # GBM calculation
            drift = (mu - 0.5 * (sigma ** 2)) * dt
            diffusion = sigma * math.sqrt(dt) * Z[i]
            new_p = current_p * math.exp(drift + diffusion)

            # Random shock event check (~0.2% chance per tick)
            if random.random() < 0.002:
                shock_factor = random.uniform(0.95, 1.05)
                new_p *= shock_factor

            new_p = max(0.01, round(new_p, 2))
            self.prices[ticker] = new_p

            change = round(new_p - current_p, 2)
            if change > 0:
                direction = "up"
            elif change < 0:
                direction = "down"
            else:
                direction = "flat"

            update = PriceUpdate(
                ticker=ticker,
                price=new_p,
                previous_price=current_p,
                timestamp=now_iso,
                change=change,
                direction=direction,
            )
            updates.append(update)

        return updates


class SimulatorDataSource(MarketDataSource):
    def __init__(self, cache: PriceCache, update_interval: float = 0.5):
        self.cache = cache
        self.update_interval = update_interval
        self.simulator = GBMSimulator()
        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self, initial_tickers: List[str]) -> None:
        for t in initial_tickers:
            self.simulator.add_ticker(t)
        
        # Initial step to populate cache
        updates = self.simulator.step()
        self.cache.update_batch(updates)

        self._running = True
        self._task = asyncio.create_task(self._run_loop())

    async def _run_loop(self) -> None:
        while self._running:
            try:
                await asyncio.sleep(self.update_interval)
                updates = self.simulator.step()
                if updates:
                    self.cache.update_batch(updates)
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

    async def add_ticker(self, ticker: str) -> None:
        self.simulator.add_ticker(ticker)
        # Immediate update for new ticker
        updates = self.simulator.step()
        self.cache.update_batch(updates)

    async def remove_ticker(self, ticker: str) -> None:
        self.simulator.remove_ticker(ticker)

    def get_tickers(self) -> List[str]:
        return self.simulator.get_tickers()
