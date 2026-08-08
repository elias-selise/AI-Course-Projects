from abc import ABC, abstractmethod
from typing import List


class MarketDataSource(ABC):
    """Abstract interface for live or simulated market data providers."""

    @abstractmethod
    async def start(self) -> None:
        """Start continuous background tick polling or generation."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Gracefully stop background tick task."""
        pass

    @abstractmethod
    def add_ticker(self, ticker: str) -> None:
        """Add ticker symbol to tracking list."""
        pass

    @abstractmethod
    def remove_ticker(self, ticker: str) -> None:
        """Remove ticker symbol from tracking list."""
        pass

    @abstractmethod
    def get_tickers(self) -> List[str]:
        """Return copy of active tracked tickers list."""
        pass
