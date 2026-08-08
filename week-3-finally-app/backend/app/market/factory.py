from app.config import Settings
from app.market.cache import PriceCache
from app.market.interface import MarketDataSource
from app.market.massive_client import MassiveDataSource
from app.market.simulator import SimulatorDataSource


def create_market_data_source(settings: Settings, cache: PriceCache) -> MarketDataSource:
    """Factory creating MarketDataSource based on MASSIVE_API_KEY setting."""
    if settings.MASSIVE_API_KEY and settings.MASSIVE_API_KEY.strip():
        return MassiveDataSource(api_key=settings.MASSIVE_API_KEY.strip(), cache=cache)
    return SimulatorDataSource(cache=cache)
