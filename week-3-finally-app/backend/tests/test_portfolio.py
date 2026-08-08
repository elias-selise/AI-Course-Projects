import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient, ASGITransport

from app.db.database import get_db, init_db
from app.main import app, lifespan
from app.market.cache import PriceCache
from app.market.models import PriceUpdate
from app.schemas.portfolio import TradeRequest
from app.services.portfolio_service import calculate_portfolio, execute_trade


@pytest.mark.asyncio
async def test_get_portfolio_initial(tmp_path, monkeypatch):
    db_file = tmp_path / "test_portfolio_initial.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/api/portfolio")
            assert res.status_code == 200
            data = res.json()
            assert data["cash_balance"] == 10000.0
            assert data["positions_value"] == 0.0
            assert data["total_value"] == 10000.0
            assert data["total_unrealized_pnl"] == 0.0
            assert data["total_unrealized_pnl_percent"] == 0.0
            assert data["positions"] == []


@pytest.mark.asyncio
async def test_get_portfolio_with_positions(tmp_path):
    db_file = tmp_path / "test_portfolio_pos.db"
    await init_db(db_file)

    cache = PriceCache()
    cache.set(
        PriceUpdate(
            ticker="AAPL",
            price=150.0,
            previous_price=145.0,
            timestamp="2026-08-08T22:00:00Z",
            change=5.0,
            direction="up",
        )
    )

    now_iso = datetime.now(timezone.utc).isoformat()
    async with get_db(db_file) as db:
        await db.execute(
            """
            INSERT INTO positions (id, user_id, ticker, quantity, avg_cost, updated_at)
            VALUES (?, 'default', 'AAPL', 10.0, 100.0, ?)
            """,
            (str(uuid.uuid4()), now_iso)
        )
        await db.commit()

        portfolio = await calculate_portfolio(db, cache)
        assert portfolio.cash_balance == 10000.0
        assert portfolio.positions_value == 1500.0
        assert portfolio.total_value == 11500.0
        assert portfolio.total_unrealized_pnl == 500.0
        assert portfolio.total_unrealized_pnl_percent == 50.0
        assert len(portfolio.positions) == 1
        pos = portfolio.positions[0]
        assert pos.ticker == "AAPL"
        assert pos.quantity == 10.0
        assert pos.avg_cost == 100.0
        assert pos.current_price == 150.0
        assert pos.market_value == 1500.0
        assert pos.unrealized_pnl == 500.0
        assert pos.unrealized_pnl_percent == 50.0


@pytest.mark.asyncio
async def test_trade_buy_success(tmp_path):
    db_file = tmp_path / "test_trade_buy.db"
    await init_db(db_file)

    cache = PriceCache()
    cache.set(
        PriceUpdate(
            ticker="AAPL",
            price=150.0,
            previous_price=150.0,
            timestamp="2026-08-08T22:00:00Z",
            change=0.0,
            direction="flat",
        )
    )

    async with get_db(db_file) as db:
        req = TradeRequest(ticker="aapl", side="buy", quantity=10.0)
        res = await execute_trade(db, cache, req)

        assert res.ticker == "AAPL"
        assert res.side == "buy"
        assert res.quantity == 10.0
        assert res.price == 150.0
        assert res.total_value == 1500.0
        assert res.cash_balance == 8500.0

        # Check DB rows
        async with db.execute("SELECT cash_balance FROM users_profile WHERE id = 'default'") as cursor:
            row = await cursor.fetchone()
            assert row[0] == 8500.0

        async with db.execute("SELECT quantity, avg_cost FROM positions WHERE ticker = 'AAPL'") as cursor:
            row = await cursor.fetchone()
            assert row[0] == 10.0
            assert row[1] == 150.0

        async with db.execute("SELECT side, quantity, price FROM trades WHERE ticker = 'AAPL'") as cursor:
            row = await cursor.fetchone()
            assert row[0] == "buy"
            assert row[1] == 10.0
            assert row[2] == 150.0


@pytest.mark.asyncio
async def test_trade_buy_weighted_average_cost(tmp_path):
    db_file = tmp_path / "test_trade_wac.db"
    await init_db(db_file)

    cache = PriceCache()
    # Buy 10 @ 100
    cache.set(
        PriceUpdate(
            ticker="AAPL",
            price=100.0,
            previous_price=100.0,
            timestamp="2026-08-08T22:00:00Z",
            change=0.0,
            direction="flat",
        )
    )
    async with get_db(db_file) as db:
        await execute_trade(db, cache, TradeRequest(ticker="AAPL", side="buy", quantity=10.0))

        # Buy 10 @ 200
        cache.set(
            PriceUpdate(
                ticker="AAPL",
                price=200.0,
                previous_price=100.0,
                timestamp="2026-08-08T22:01:00Z",
                change=100.0,
                direction="up",
            )
        )
        await execute_trade(db, cache, TradeRequest(ticker="AAPL", side="buy", quantity=10.0))

        async with db.execute("SELECT quantity, avg_cost FROM positions WHERE ticker = 'AAPL'") as cursor:
            row = await cursor.fetchone()
            assert row[0] == 20.0
            assert row[1] == 150.0  # Weighted avg: (10*100 + 10*200)/20 = 150.0


@pytest.mark.asyncio
async def test_trade_buy_insufficient_funds(tmp_path, monkeypatch):
    db_file = tmp_path / "test_trade_funds.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        cache = app.state.price_cache
        cache.set(
            PriceUpdate(
                ticker="AAPL",
                price=500.0,
                previous_price=500.0,
                timestamp="2026-08-08T22:00:00Z",
                change=0.0,
                direction="flat",
            )
        )

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # 1000 shares @ $500 = $500,000 > $10,000
            res = await ac.post("/api/portfolio/trade", json={"ticker": "AAPL", "side": "buy", "quantity": 1000.0})
            assert res.status_code == 400
            assert "Insufficient funds" in res.json()["detail"]


@pytest.mark.asyncio
async def test_trade_sell_success(tmp_path):
    db_file = tmp_path / "test_trade_sell.db"
    await init_db(db_file)

    cache = PriceCache()
    # Buy 10 @ 100
    cache.set(
        PriceUpdate(
            ticker="AAPL",
            price=100.0,
            previous_price=100.0,
            timestamp="2026-08-08T22:00:00Z",
            change=0.0,
            direction="flat",
        )
    )
    async with get_db(db_file) as db:
        await execute_trade(db, cache, TradeRequest(ticker="AAPL", side="buy", quantity=10.0))

        # Sell 5 @ 150
        cache.set(
            PriceUpdate(
                ticker="AAPL",
                price=150.0,
                previous_price=100.0,
                timestamp="2026-08-08T22:01:00Z",
                change=50.0,
                direction="up",
            )
        )
        res = await execute_trade(db, cache, TradeRequest(ticker="AAPL", side="sell", quantity=5.0))

        assert res.cash_balance == 9750.0  # initial 10000 - 1000 + 750 = 9750
        assert res.side == "sell"

        async with db.execute("SELECT quantity, avg_cost FROM positions WHERE ticker = 'AAPL'") as cursor:
            row = await cursor.fetchone()
            assert row[0] == 5.0
            assert row[1] == 100.0  # Cost basis preserved on sell


@pytest.mark.asyncio
async def test_trade_sell_insufficient_position(tmp_path, monkeypatch):
    db_file = tmp_path / "test_trade_sell_no_pos.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        cache = app.state.price_cache
        cache.set(
            PriceUpdate(
                ticker="AAPL",
                price=150.0,
                previous_price=150.0,
                timestamp="2026-08-08T22:00:00Z",
                change=0.0,
                direction="flat",
            )
        )

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post("/api/portfolio/trade", json={"ticker": "AAPL", "side": "sell", "quantity": 5.0})
            assert res.status_code == 400
            assert "Insufficient position" in res.json()["detail"]


@pytest.mark.asyncio
async def test_trade_missing_price(tmp_path, monkeypatch):
    db_file = tmp_path / "test_trade_no_price.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post("/api/portfolio/trade", json={"ticker": "UNKNOWN", "side": "buy", "quantity": 1.0})
            assert res.status_code == 400
            assert "Market price unavailable" in res.json()["detail"]
