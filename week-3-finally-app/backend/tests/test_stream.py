import json
import pytest
from app.api.stream import create_stream_router, price_event_generator
from app.market.cache import PriceCache
from app.market.models import PriceUpdate
from app.main import app, lifespan


class DummyRequest:
    def __init__(self, disconnected: bool = False):
        self._disconnected = disconnected

    async def is_disconnected(self):
        return self._disconnected


def get_all_route_paths(fastapi_app):
    paths = []
    for r in fastapi_app.routes:
        if hasattr(r, "path"):
            paths.append(r.path)
        elif hasattr(r, "original_router"):
            for sub in r.original_router.routes:
                if hasattr(sub, "path"):
                    paths.append(sub.path)
    return paths


@pytest.mark.asyncio
async def test_price_event_generator_yields_events():
    cache = PriceCache()
    update = PriceUpdate(
        ticker="AAPL",
        price=185.5,
        previous_price=184.0,
        timestamp="2026-08-08T22:00:00Z",
        change=1.5,
        direction="up",
    )
    cache.set(update)

    req = DummyRequest(disconnected=False)
    gen = price_event_generator(req, cache)

    event = await anext(gen)
    assert event["event"] == "price_update"
    data = json.loads(event["data"])
    assert len(data) == 1
    assert data[0]["ticker"] == "AAPL"
    assert data[0]["price"] == 185.5

    # Test disconnection breaks loop
    req._disconnected = True
    with pytest.raises(StopAsyncIteration):
        await anext(gen)


@pytest.mark.asyncio
async def test_create_stream_router():
    cache = PriceCache()
    stream_router = create_stream_router(cache)
    routes = [r.path for r in stream_router.routes if hasattr(r, "path")]
    assert "/api/stream/prices" in routes


@pytest.mark.asyncio
async def test_app_lifespan_and_routes(tmp_path, monkeypatch):
    db_file = tmp_path / "test_lifespan.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        assert hasattr(app.state, "price_cache")
        assert hasattr(app.state, "market_source")
        assert app.state.market_source._running is True

        routes = get_all_route_paths(app)
        assert "/api/stream/prices" in routes
        assert "/api/health" in routes

    # After lifespan exit, market source should be stopped
    assert app.state.market_source._running is False
