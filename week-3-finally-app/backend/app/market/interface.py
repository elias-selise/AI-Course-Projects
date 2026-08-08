from abc import ABC, abstractmethod
from typing import List


class MarketDataSource(ABC):
    @abstractmethod
    async def start(self, initial_tickers: List[str]) -> None:
        """Start streaming or polling price updates for tickers."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop streaming or polling price updates."""
        pass

    @abstractmethod
    async def add_ticker(self, ticker: str) -> None:
        """Add a ticker to the active subscription list."""
        pass

    @abstractmethod
    async def remove_ticker(self, ticker: str) -> None:
        """Remove a ticker from the active subscription list."""
        pass

    @abstractmethod
    def get_tickers(self) -> List[str]:
        """Get the current list of subscribed tickers."""
        pass
