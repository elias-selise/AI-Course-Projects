import os
from .interface import MarketDataSource
from .cache import PriceCache
from .simulator import SimulatorDataSource
from .massive_client import MassiveDataSource
from app.config import MASSIVE_API_KEY


def create_market_data_source(cache: PriceCache) -> MarketDataSource:
    """Factory function to instantiate appropriate market data source based on env vars."""
    api_key = MASSIVE_API_KEY or os.getenv("MASSIVE_API_KEY", "")
    if api_key and api_key.strip():
        return MassiveDataSource(cache=cache, api_key=api_key.strip())
    return SimulatorDataSource(cache=cache)
