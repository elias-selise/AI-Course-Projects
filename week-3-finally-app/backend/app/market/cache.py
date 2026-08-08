import threading
from typing import Dict, Optional, List
from .models import PriceUpdate


class PriceCache:
    def __init__(self):
        self._cache: Dict[str, PriceUpdate] = {}
        self._lock = threading.Lock()
        self._version = 0

    @property
    def version(self) -> int:
        with self._lock:
            return self._version

    def update(self, update: PriceUpdate) -> None:
        with self._lock:
            self._cache[update.ticker] = update
            self._version += 1

    def update_batch(self, updates: List[PriceUpdate]) -> None:
        with self._lock:
            for update in updates:
                self._cache[update.ticker] = update
            self._version += 1

    def get(self, ticker: str) -> Optional[PriceUpdate]:
        with self._lock:
            return self._cache.get(ticker.upper())

    def get_price(self, ticker: str) -> Optional[float]:
        update = self.get(ticker.upper())
        return update.price if update else None

    def get_all(self) -> Dict[str, PriceUpdate]:
        with self._lock:
            return dict(self._cache)
