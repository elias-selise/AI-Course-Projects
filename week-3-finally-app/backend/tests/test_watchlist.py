import pytest
from httpx import AsyncClient, ASGITransport

from app.db.schema import DEFAULT_TICKERS
from app.main import app, lifespan


@pytest.mark.asyncio
async def test_get_watchlist_initial(tmp_path, monkeypatch):
    db_file = tmp_path / "test_get_watchlist.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/api/watchlist")
            assert res.status_code == 200
            data = res.json()
            assert len(data) == len(DEFAULT_TICKERS)
            tickers = [item["ticker"] for item in data]
            assert "AAPL" in tickers
            assert "MSFT" in tickers


@pytest.mark.asyncio
async def test_add_watchlist_ticker(tmp_path, monkeypatch):
    db_file = tmp_path / "test_add_watchlist.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post("/api/watchlist", json={"ticker": "amd"})
            assert res.status_code == 201
            data = res.json()
            assert data["ticker"] == "AMD"
            assert "id" in data

            # Verify present in get_watchlist
            get_res = await ac.get("/api/watchlist")
            tickers = [item["ticker"] for item in get_res.json()]
            assert "AMD" in tickers
            assert "AMD" in app.state.market_source.get_tickers()


@pytest.mark.asyncio
async def test_add_duplicate_watchlist_ticker(tmp_path, monkeypatch):
    db_file = tmp_path / "test_dup_watchlist.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post("/api/watchlist", json={"ticker": "AAPL"})
            assert res.status_code == 400
            assert "already in watchlist" in res.json()["detail"]


@pytest.mark.asyncio
async def test_delete_watchlist_ticker(tmp_path, monkeypatch):
    db_file = tmp_path / "test_del_watchlist.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.delete("/api/watchlist/AAPL")
            assert res.status_code == 200
            assert res.json() == {"status": "success", "ticker": "AAPL"}

            # Verify deleted from watchlist
            get_res = await ac.get("/api/watchlist")
            tickers = [item["ticker"] for item in get_res.json()]
            assert "AAPL" not in tickers
            assert "AAPL" not in app.state.market_source.get_tickers()


@pytest.mark.asyncio
async def test_delete_nonexistent_watchlist_ticker(tmp_path, monkeypatch):
    db_file = tmp_path / "test_del_missing.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.delete("/api/watchlist/INVALID")
            assert res.status_code == 404
            assert "not found in watchlist" in res.json()["detail"]
