from app.market.cache import PriceCache
from app.market.models import PriceUpdate


def test_price_cache_operations():
    cache = PriceCache()
    assert cache.version == 0
    assert cache.get("AAPL") is None
    assert cache.get_price("AAPL") is None

    update = PriceUpdate(
        ticker="AAPL",
        price=192.0,
        previous_price=190.0,
        timestamp="2026-08-08T12:00:00Z",
        change=2.0,
        direction="up",
    )
    cache.update(update)

    assert cache.version == 1
    fetched = cache.get("AAPL")
    assert fetched is not None
    assert fetched.price == 192.0
    assert cache.get_price("AAPL") == 192.0
    assert cache.get_price("aapl") == 192.0  # Case insensitivity test


def test_price_cache_update_batch():
    cache = PriceCache()
    u1 = PriceUpdate("AAPL", 190.0, 189.0, "2026-08-08T12:00:00Z", 1.0, "up")
    u2 = PriceUpdate("GOOGL", 175.0, 175.0, "2026-08-08T12:00:00Z", 0.0, "flat")

    cache.update_batch([u1, u2])

    assert cache.version == 1
    all_data = cache.get_all()
    assert len(all_data) == 2
    assert "AAPL" in all_data
    assert "GOOGL" in all_data
