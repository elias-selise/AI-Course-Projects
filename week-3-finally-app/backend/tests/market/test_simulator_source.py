import asyncio
import pytest
from app.market.cache import PriceCache
from app.market.simulator import SimulatorDataSource


@pytest.mark.asyncio
async def test_simulator_data_source_lifecycle():
    cache = PriceCache()
    source = SimulatorDataSource(cache, update_interval=0.05)

    await source.start(["AAPL", "MSFT"])
    assert "AAPL" in source.get_tickers()
    assert cache.get("AAPL") is not None

    await asyncio.sleep(0.15)
    assert cache.version >= 2

    await source.add_ticker("TSLA")
    assert "TSLA" in source.get_tickers()
    assert cache.get("TSLA") is not None

    await source.remove_ticker("AAPL")
    assert "AAPL" not in source.get_tickers()

    await source.stop()
