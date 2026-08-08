from app.market.simulator import GBMSimulator


def test_gbm_simulator_init():
    sim = GBMSimulator(["AAPL", "GOOGL"])
    tickers = sim.get_tickers()
    assert "AAPL" in tickers
    assert "GOOGL" in tickers
    assert len(tickers) == 2


def test_gbm_simulator_step():
    sim = GBMSimulator(["AAPL", "GOOGL"])
    updates = sim.step()
    assert len(updates) == 2
    tickers = [u.ticker for u in updates]
    assert "AAPL" in tickers
    assert "GOOGL" in tickers
    for u in updates:
        assert u.price > 0.0
        assert u.direction in ("up", "down", "flat")


def test_gbm_simulator_add_remove_ticker():
    sim = GBMSimulator(["AAPL"])
    sim.add_ticker("NVDA")
    assert "NVDA" in sim.get_tickers()

    updates = sim.step()
    assert len(updates) == 2

    sim.remove_ticker("AAPL")
    assert "AAPL" not in sim.get_tickers()
    updates_after = sim.step()
    assert len(updates_after) == 1
    assert updates_after[0].ticker == "NVDA"
