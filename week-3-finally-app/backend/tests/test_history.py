import asyncio
import uuid
from datetime import datetime, timezone
import pytest
from httpx import AsyncClient, ASGITransport

from app.db.database import get_db, init_db
from app.main import app, lifespan
from app.market.cache import PriceCache
from app.market.models import PriceUpdate
from app.schemas.portfolio import TradeRequest
from app.services.portfolio_service import execute_trade
from app.services.snapshot_service import SnapshotTask


@pytest.mark.asyncio
async def test_post_trade_snapshot_trigger(tmp_path):
    db_file = tmp_path / "test_trade_snap.db"
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
        # Verify 0 snapshots before trade
        async with db.execute("SELECT COUNT(*) FROM portfolio_snapshots") as cursor:
            count = (await cursor.fetchone())[0]
            assert count == 0

        # Execute trade
        await execute_trade(db, cache, TradeRequest(ticker="AAPL", side="buy", quantity=10.0))

        # Verify 1 snapshot created
        async with db.execute("SELECT total_value FROM portfolio_snapshots") as cursor:
            rows = await cursor.fetchall()
            assert len(rows) == 1
            # Total value should be cash ($8,500) + positions ($1,500) = $10,000.0
            assert rows[0][0] == 10000.0


@pytest.mark.asyncio
async def test_background_snapshot_task(tmp_path):
    db_file = tmp_path / "test_bg_snap.db"
    await init_db(db_file)

    cache = PriceCache()
    task = SnapshotTask(db_file, cache, interval_seconds=1)
    task.start()
    await asyncio.sleep(2.5)
    await task.stop()

    async with get_db(db_file) as db:
        async with db.execute("SELECT COUNT(*) FROM portfolio_snapshots") as cursor:
            count = (await cursor.fetchone())[0]
            # Should have recorded at least 2 snapshots in 2.5s with 1s interval
            assert count >= 2


@pytest.mark.asyncio
async def test_get_portfolio_history(tmp_path, monkeypatch):
    db_file = tmp_path / "test_get_history.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    await init_db(db_file)

    now = datetime.now(timezone.utc).isoformat()
    async with get_db(db_file) as db:
        await db.execute(
            "INSERT INTO portfolio_snapshots (id, user_id, total_value, recorded_at) VALUES (?, 'default', 10000.0, '2026-08-08T10:00:00Z')",
            (str(uuid.uuid4()),)
        )
        await db.execute(
            "INSERT INTO portfolio_snapshots (id, user_id, total_value, recorded_at) VALUES (?, 'default', 10500.0, '2026-08-08T11:00:00Z')",
            (str(uuid.uuid4()),)
        )
        await db.execute(
            "INSERT INTO portfolio_snapshots (id, user_id, total_value, recorded_at) VALUES (?, 'default', 11000.0, '2026-08-08T12:00:00Z')",
            (str(uuid.uuid4()),)
        )
        await db.commit()

    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/api/portfolio/history")
            assert res.status_code == 200
            data = res.json()
            # Must contain at least the 3 seeded rows (plus any recorded by lifespan startup)
            timestamps = [item["recorded_at"] for item in data]
            assert timestamps == sorted(timestamps)  # Ascending order
            vals = [item["total_value"] for item in data if item["recorded_at"].startswith("2026-08-08T1")]
            assert vals == [10000.0, 10500.0, 11000.0]
