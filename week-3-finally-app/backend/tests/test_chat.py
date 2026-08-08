import json
import pytest

from app.services.llm_provider import MockLLMProvider


@pytest.mark.asyncio
async def test_mock_provider_buy_intent():
    provider = MockLLMProvider()
    messages = [{"role": "user", "content": "Buy 10 shares of AAPL"}]
    res_str = await provider.generate_response(messages)
    data = json.loads(res_str)

    assert "trades" in data
    assert len(data["trades"]) == 1
    assert data["trades"][0]["ticker"] == "AAPL"
    assert data["trades"][0]["side"] == "buy"
    assert data["trades"][0]["quantity"] == 10.0


@pytest.mark.asyncio
async def test_mock_provider_sell_intent():
    provider = MockLLMProvider()
    messages = [{"role": "user", "content": "Sell 5 shares of TSLA"}]
    res_str = await provider.generate_response(messages)
    data = json.loads(res_str)

    assert "trades" in data
    assert len(data["trades"]) == 1
    assert data["trades"][0]["ticker"] == "TSLA"
    assert data["trades"][0]["side"] == "sell"
    assert data["trades"][0]["quantity"] == 5.0


@pytest.mark.asyncio
async def test_mock_provider_watchlist_intent():
    provider = MockLLMProvider()
    messages = [{"role": "user", "content": "Add NVDA to watchlist"}]
    res_str = await provider.generate_response(messages)
    data = json.loads(res_str)

    assert "watchlist_changes" in data
    assert len(data["watchlist_changes"]) == 1
    assert data["watchlist_changes"][0]["action"] == "add"
    assert data["watchlist_changes"][0]["ticker"] == "NVDA"

    # Also test remove watchlist
    messages_rem = [{"role": "user", "content": "Remove NVDA from watchlist"}]
    res_str_rem = await provider.generate_response(messages_rem)
    data_rem = json.loads(res_str_rem)
    assert len(data_rem["watchlist_changes"]) == 1
    assert data_rem["watchlist_changes"][0]["action"] == "remove"
    assert data_rem["watchlist_changes"][0]["ticker"] == "NVDA"


@pytest.mark.asyncio
async def test_mock_provider_general_query():
    provider = MockLLMProvider()
    messages = [{"role": "user", "content": "How is my portfolio doing?"}]
    res_str = await provider.generate_response(messages)
    data = json.loads(res_str)

    assert "message" in data
    assert len(data["message"]) > 0
    assert data["trades"] == []
    assert data["watchlist_changes"] == []


def test_build_system_prompt():
    from app.schemas.portfolio import PortfolioResponse, PositionItem, WatchlistItemResponse
    from app.market.cache import PriceCache
    from app.market.models import PriceUpdate
    from app.services.prompt_builder import build_system_prompt

    cache = PriceCache()
    cache.set(PriceUpdate(ticker="AAPL", price=150.0, previous_price=149.0, change=1.0, direction="up", timestamp="2026-08-08T00:00:00Z"))
    cache.set(PriceUpdate(ticker="NVDA", price=800.0, previous_price=795.0, change=5.0, direction="up", timestamp="2026-08-08T00:00:00Z"))

    portfolio = PortfolioResponse(
        cash_balance=10000.0,
        positions_value=1500.0,
        total_value=11500.0,
        total_unrealized_pnl=0.0,
        total_unrealized_pnl_percent=0.0,
        positions=[
            PositionItem(
                ticker="AAPL",
                quantity=10.0,
                avg_cost=150.0,
                current_price=150.0,
                market_value=1500.0,
                unrealized_pnl=0.0,
                unrealized_pnl_percent=0.0
            )
        ]
    )

    watchlist = [
        WatchlistItemResponse(
            id="watch-1",
            ticker="NVDA",
            price=800.0,
            previous_price=795.0,
            change=5.0,
            direction="up",
            added_at="2026-08-08T00:00:00Z"
        )
    ]

    prompt = build_system_prompt(portfolio, watchlist, cache)

    assert "$10,000.00" in prompt
    assert "AAPL" in prompt
    assert "NVDA" in prompt
    assert "$800.00" in prompt
    assert "REQUIRED JSON OUTPUT SCHEMA" in prompt


def test_parse_llm_response_markdown_strip():
    from app.services.chat_service import parse_llm_response
    raw = """```json
{
  "message": "Executed buy order for AAPL",
  "trades": [{"ticker": "AAPL", "side": "buy", "quantity": 10.0}],
  "watchlist_changes": []
}
```"""
    parsed = parse_llm_response(raw)
    assert parsed.message == "Executed buy order for AAPL"
    assert len(parsed.trades) == 1
    assert parsed.trades[0].ticker == "AAPL"
    assert parsed.trades[0].quantity == 10.0


@pytest.mark.asyncio
async def test_auto_execution_buy_trade(tmp_path):
    from app.db.database import get_db, init_db
    from app.market.cache import PriceCache
    from app.market.models import PriceUpdate
    from app.services.chat_service import process_chat_message

    db_file = tmp_path / "test_auto_buy.db"
    await init_db(db_file)

    cache = PriceCache()
    cache.set(PriceUpdate(ticker="AAPL", price=150.0, previous_price=145.0, change=5.0, direction="up", timestamp="2026-08-08T00:00:00Z"))

    provider = MockLLMProvider()

    async with get_db(db_file) as db:
        res = await process_chat_message(db=db, cache=cache, provider=provider, user_message="Buy 10 shares of AAPL")

        assert len(res.executed_trades) == 1
        trade_res = res.executed_trades[0]
        assert trade_res.status == "success"
        assert trade_res.ticker == "AAPL"
        assert trade_res.side == "buy"
        assert trade_res.quantity == 10.0
        assert trade_res.price == 150.0
        assert trade_res.total_value == 1500.0

        # Check DB cash balance
        async with db.execute("SELECT cash_balance FROM users_profile WHERE id = 'default'") as cursor:
            row = await cursor.fetchone()
            assert row[0] == 8500.0

        # Check DB positions
        async with db.execute("SELECT quantity, avg_cost FROM positions WHERE ticker = 'AAPL'") as cursor:
            row = await cursor.fetchone()
            assert row[0] == 10.0
            assert row[1] == 150.0


@pytest.mark.asyncio
async def test_auto_execution_sell_trade(tmp_path):
    import uuid
    from datetime import datetime, timezone
    from app.db.database import get_db, init_db
    from app.market.cache import PriceCache
    from app.market.models import PriceUpdate
    from app.services.chat_service import process_chat_message

    db_file = tmp_path / "test_auto_sell.db"
    await init_db(db_file)

    cache = PriceCache()
    cache.set(PriceUpdate(ticker="AAPL", price=150.0, previous_price=145.0, change=5.0, direction="up", timestamp="2026-08-08T00:00:00Z"))

    provider = MockLLMProvider()

    now_iso = datetime.now(timezone.utc).isoformat()
    async with get_db(db_file) as db:
        # Seed 10 AAPL position @ $100
        await db.execute(
            "INSERT INTO positions (id, user_id, ticker, quantity, avg_cost, updated_at) VALUES (?, 'default', 'AAPL', 10.0, 100.0, ?)",
            (str(uuid.uuid4()), now_iso)
        )
        await db.commit()

        res = await process_chat_message(db=db, cache=cache, provider=provider, user_message="Sell 5 shares of AAPL")

        assert len(res.executed_trades) == 1
        trade_res = res.executed_trades[0]
        assert trade_res.status == "success"
        assert trade_res.ticker == "AAPL"
        assert trade_res.side == "sell"
        assert trade_res.quantity == 5.0

        # Check DB positions quantity reduced to 5
        async with db.execute("SELECT quantity, avg_cost FROM positions WHERE ticker = 'AAPL'") as cursor:
            row = await cursor.fetchone()
            assert row[0] == 5.0


@pytest.mark.asyncio
async def test_auto_execution_watchlist_add(tmp_path):
    from app.db.database import get_db, init_db
    from app.market.cache import PriceCache
    from app.services.chat_service import process_chat_message

    db_file = tmp_path / "test_auto_watch.db"
    await init_db(db_file)

    cache = PriceCache()
    provider = MockLLMProvider()

    async with get_db(db_file) as db:
        res = await process_chat_message(db=db, cache=cache, provider=provider, user_message="Add NVDA to watchlist")

        assert len(res.executed_watchlist_changes) == 1
        w_res = res.executed_watchlist_changes[0]
        assert w_res.status == "success"
        assert w_res.action == "add"
        assert w_res.ticker == "NVDA"

        # Check DB watchlist
        async with db.execute("SELECT ticker FROM watchlist WHERE user_id = 'default' AND ticker = 'NVDA'") as cursor:
            row = await cursor.fetchone()
            assert row is not None
            assert row[0] == "NVDA"


@pytest.mark.asyncio
async def test_auto_execution_failed_trade_insufficient_funds(tmp_path):
    from app.db.database import get_db, init_db
    from app.market.cache import PriceCache
    from app.market.models import PriceUpdate
    from app.services.chat_service import process_chat_message

    db_file = tmp_path / "test_auto_fail.db"
    await init_db(db_file)

    cache = PriceCache()
    cache.set(PriceUpdate(ticker="NVDA", price=800.0, previous_price=795.0, change=5.0, direction="up", timestamp="2026-08-08T00:00:00Z"))

    provider = MockLLMProvider()

    async with get_db(db_file) as db:
        # Buy 1000 NVDA @ $800 = $800,000 > $10,000 cash
        res = await process_chat_message(db=db, cache=cache, provider=provider, user_message="Buy 1000 shares of NVDA")

        assert len(res.executed_trades) == 1
        t_res = res.executed_trades[0]
        assert t_res.status == "failed"
        assert "Insufficient funds" in t_res.error


@pytest.mark.asyncio
async def test_post_chat_endpoint(tmp_path, monkeypatch):
    from httpx import AsyncClient, ASGITransport
    from app.main import app, lifespan
    from app.market.models import PriceUpdate

    db_file = tmp_path / "test_chat_endpoint.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        cache = app.state.price_cache
        cache.set(PriceUpdate(ticker="AAPL", price=150.0, previous_price=145.0, change=5.0, direction="up", timestamp="2026-08-08T00:00:00Z"))

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post("/api/chat", json={"message": "Buy 5 shares of AAPL"})
            assert res.status_code == 200
            data = res.json()
            assert "message_id" in data
            assert data["user_message"] == "Buy 5 shares of AAPL"
            assert "executed_trades" in data
            assert len(data["executed_trades"]) == 1
            assert data["executed_trades"][0]["ticker"] == "AAPL"


@pytest.mark.asyncio
async def test_get_chat_history_endpoint(tmp_path, monkeypatch):
    from httpx import AsyncClient, ASGITransport
    from app.main import app, lifespan

    db_file = tmp_path / "test_chat_history.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Post a message first
            await ac.post("/api/chat", json={"message": "Hello FinAlly"})

            # Fetch history
            res = await ac.get("/api/chat/history")
            assert res.status_code == 200
            data = res.json()
            assert len(data) >= 2  # 1 user, 1 assistant
            roles = [item["role"] for item in data]
            assert "user" in roles
            assert "assistant" in roles


@pytest.mark.asyncio
async def test_clear_chat_history_endpoint(tmp_path, monkeypatch):
    from httpx import AsyncClient, ASGITransport
    from app.main import app, lifespan

    db_file = tmp_path / "test_clear_history.db"
    monkeypatch.setenv("DB_PATH", str(db_file))
    from app.config import get_settings
    get_settings.cache_clear()

    async with lifespan(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Post a message
            await ac.post("/api/chat", json={"message": "Clear test"})

            # Clear history
            del_res = await ac.delete("/api/chat/history")
            assert del_res.status_code == 200
            assert del_res.json()["status"] == "success"

            # Verify history is empty
            get_res = await ac.get("/api/chat/history")
            assert get_res.status_code == 200
            assert get_res.json() == []



