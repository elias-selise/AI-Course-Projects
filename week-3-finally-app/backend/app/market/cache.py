import threading
from typing import Dict, List, Optional
from app.market.models import PriceUpdate


class PriceCache:
    """Thread-safe in-memory cache for ticker prices with versioning."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cache: Dict[str, PriceUpdate] = {}
        self._version: int = 0

    @property
    def version(self) -> int:
        with self._lock:
            return self._version

    def set(self, update: PriceUpdate) -> None:
        with self._lock:
            self._cache[update.ticker] = update
            self._version += 1

    def set_many(self, updates: List[PriceUpdate]) -> None:
        if not updates:
            return
        with self._lock:
            for update in updates:
                self._cache[update.ticker] = update
            self._version += 1

    def get(self, ticker: str) -> Optional[PriceUpdate]:
        with self._lock:
            return self._cache.get(ticker)

    def get_all(self) -> Dict[str, PriceUpdate]:
        with self._lock:
            return dict(self._cache)
