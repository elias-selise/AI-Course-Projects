import threading
from datetime import datetime, timezone
from app.market.cache import PriceCache
from app.market.models import PriceUpdate


def make_update(ticker: str = "AAPL", price: float = 150.0, prev: float = 149.0) -> PriceUpdate:
    change = round(price - prev, 2)
    direction = "up" if change > 0 else ("down" if change < 0 else "flat")
    return PriceUpdate(
        ticker=ticker,
        price=price,
        previous_price=prev,
        timestamp=datetime.now(timezone.utc).isoformat(),
        change=change,
        direction=direction,
    )


def test_initial_cache_state():
    cache = PriceCache()
    assert cache.version == 0
    assert cache.get_all() == {}
    assert cache.get("AAPL") is None


def test_single_set_and_version():
    cache = PriceCache()
    update = make_update("AAPL", 150.0, 149.0)
    cache.set(update)

    assert cache.version == 1
    assert cache.get("AAPL") == update
    assert "AAPL" in cache.get_all()


def test_set_many_and_version():
    cache = PriceCache()
    updates = [
        make_update("AAPL", 150.0, 149.0),
        make_update("GOOGL", 140.0, 141.0),
    ]
    cache.set_many(updates)

    assert cache.version == 1
    all_cached = cache.get_all()
    assert len(all_cached) == 2
    assert all_cached["AAPL"].price == 150.0
    assert all_cached["GOOGL"].price == 140.0


def test_concurrent_writes():
    cache = PriceCache()
    num_threads = 10
    updates_per_thread = 50

    def worker(thread_idx: int):
        for i in range(updates_per_thread):
            update = make_update(f"TICKER_{thread_idx}", float(i + 1), float(i))
            cache.set(update)

    threads = [threading.Thread(target=worker, args=(t,)) for t in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert cache.version == num_threads * updates_per_thread
    all_cached = cache.get_all()
    assert len(all_cached) == num_threads
