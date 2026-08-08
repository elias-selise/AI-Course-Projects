import asyncio
import pytest
from app.market.cache import PriceCache
from app.market.massive_client import MassiveDataSource


@pytest.mark.asyncio
async def test_massive_data_source_lifecycle():
    cache = PriceCache()
    source = MassiveDataSource(cache, api_key="dummy_key", poll_interval=100.0)

    await source.start(["AAPL", "GOOGL"])
    assert "AAPL" in source.get_tickers()
    assert cache.get("AAPL") is not None

    await source.add_ticker("MSFT")
    assert "MSFT" in source.get_tickers()

    await source.remove_ticker("AAPL")
    assert "AAPL" not in source.get_tickers()

    await source.stop()
