import asyncio
import numpy as np
import pytest

from app.market.cache import PriceCache
from app.market.simulator import GBMSimulator, SimulatorDataSource


def test_gbm_simulator_single_tick():
    sim = GBMSimulator()
    updates = sim.tick()

    assert len(updates) == len(sim.tickers)
    for update in updates:
        assert update.ticker in sim.tickers
        assert update.price > 0.0
        # Check rounded to 2 decimal places
        assert round(update.price, 2) == update.price
        assert update.direction in ("up", "down", "flat")


def test_gbm_simulator_positive_prices_and_rounding():
    # Test with initial low prices to ensure price floor max(0.01, ...) works
    sim = GBMSimulator(tickers=["LOW1", "LOW2"], initial_prices={"LOW1": 0.02, "LOW2": 0.01})
    for _ in range(50):
        updates = sim.tick()
        for u in updates:
            assert u.price >= 0.01
            assert round(u.price, 2) == u.price


def test_sector_correlation():
    sim = GBMSimulator()
    num_ticks = 200
    price_history = {t: [] for t in sim.tickers}

    for _ in range(num_ticks):
        updates = sim.tick()
        for u in updates:
            price_history[u.ticker].append(u.price)

    # Convert to log returns
    returns = []
    for t in ["AAPL", "GOOGL", "MSFT", "JPM"]:
        prices = np.array(price_history[t])
        ret = np.diff(np.log(prices))
        returns.append(ret)

    returns = np.array(returns)
    corr_matrix = np.corrcoef(returns)

    # Tech stocks (AAPL, GOOGL, MSFT) should have positive correlation
    assert corr_matrix[0, 1] > 0.0  # AAPL vs GOOGL
    assert corr_matrix[0, 2] > 0.0  # AAPL vs MSFT


def test_add_and_remove_ticker():
    sim = GBMSimulator(tickers=["AAPL", "MSFT"])
    assert len(sim.tickers) == 2

    sim.add_ticker("NVDA", initial_price=800.0)
    assert "NVDA" in sim.tickers
    assert len(sim.tickers) == 3

    updates = sim.tick()
    tickers_in_updates = {u.ticker for u in updates}
    assert "NVDA" in tickers_in_updates

    sim.remove_ticker("MSFT")
    assert "MSFT" not in sim.tickers
    assert len(sim.tickers) == 2


@pytest.mark.asyncio
async def test_simulator_data_source_lifecycle():
    cache = PriceCache()
    source = SimulatorDataSource(cache=cache)

    assert cache.version == 0
    await source.start()

    # Wait for a couple tick iterations (~1.2s)
    await asyncio.sleep(1.2)

    assert cache.version >= 2
    all_ticks = cache.get_all()
    assert len(all_ticks) == len(source.get_tickers())

    await source.stop()
    old_version = cache.version

    # Wait 0.6s and ensure no new updates occur after stop
    await asyncio.sleep(0.6)
    assert cache.version == old_version
