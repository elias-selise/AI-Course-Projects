import pytest
import aiosqlite
from pathlib import Path
from app.db.database import init_db, get_db
from app.db.schema import DEFAULT_TICKERS


@pytest.mark.asyncio
async def test_init_db_creates_tables_and_seeds(tmp_path: Path):
    db_file = tmp_path / "test_finally.db"
    
    # Run init_db
    await init_db(db_file)
    assert db_file.exists()

    async with get_db(db_file) as db:
        # Assert all 6 core tables exist
        async with db.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
            tables = [row[0] for row in await cursor.fetchall()]
        
        expected_tables = {
            "users_profile",
            "watchlist",
            "positions",
            "trades",
            "portfolio_snapshots",
            "chat_messages",
        }
        assert expected_tables.issubset(set(tables))

        # Assert users_profile seed
        async with db.execute("SELECT id, cash_balance FROM users_profile WHERE id = 'default'") as cursor:
            user_row = await cursor.fetchone()
            assert user_row is not None
            assert user_row[0] == "default"
            assert user_row[1] == 10000.0

        # Assert watchlist seed
        async with db.execute("SELECT ticker FROM watchlist WHERE user_id = 'default'") as cursor:
            watchlist_tickers = [row[0] for row in await cursor.fetchall()]
            assert len(watchlist_tickers) == 10
            assert set(watchlist_tickers) == set(DEFAULT_TICKERS)


@pytest.mark.asyncio
async def test_init_db_is_idempotent(tmp_path: Path):
    db_file = tmp_path / "test_idempotent.db"
    
    # Run init_db twice
    await init_db(db_file)
    await init_db(db_file)

    async with get_db(db_file) as db:
        async with db.execute("SELECT COUNT(*) FROM users_profile") as cursor:
            count = (await cursor.fetchone())[0]
            assert count == 1

        async with db.execute("SELECT COUNT(*) FROM watchlist") as cursor:
            count = (await cursor.fetchone())[0]
            assert count == 10
