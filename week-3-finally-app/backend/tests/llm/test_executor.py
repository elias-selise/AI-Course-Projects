import sqlite3
import pytest
from app.llm.models import (
    LLMResponse,
    TradeAction,
    WatchlistAction,
    PortfolioContext,
    PositionContext,
    WatchlistPriceContext,
)
from app.llm.executor import ChatExecutor
from app.llm.client import LLMClient


def create_in_memory_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE users_profile (
            id TEXT PRIMARY KEY,
            cash_balance REAL,
            created_at TEXT
        );
        CREATE TABLE watchlist (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            ticker TEXT,
            added_at TEXT,
            UNIQUE(user_id, ticker)
        );
        CREATE TABLE positions (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            ticker TEXT,
            quantity REAL,
            avg_cost REAL,
            updated_at TEXT,
            UNIQUE(user_id, ticker)
        );
        CREATE TABLE trades (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            ticker TEXT,
            side TEXT,
            quantity REAL,
            price REAL,
            executed_at TEXT
        );
        CREATE TABLE chat_messages (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            role TEXT,
            content TEXT,
            actions TEXT,
            created_at TEXT
        );
        INSERT INTO users_profile (id, cash_balance, created_at) VALUES ('default', 10000.0, '2026-01-01T00:00:00Z');
    """)
    conn.commit()
    return conn


def test_execute_buy_trade_success():
    conn = create_in_memory_db()
    executor = ChatExecutor(
        llm_client=LLMClient(mock_mode=True),
        price_lookup=lambda ticker: 150.0
    )

    ctx = PortfolioContext(cash_balance=10000.0)
    resp = LLMResponse(
        message="Buying 10 AAPL",
        trades=[TradeAction(ticker="AAPL", side="buy", quantity=10.0)]
    )

    result = executor.execute_actions(resp, ctx, conn)

    assert len(result.executed_trades) == 1
    assert result.executed_trades[0]["ticker"] == "AAPL"
    assert result.executed_trades[0]["price"] == 150.0
    assert result.failed_trades == []

    # Check DB state
    cur = conn.execute("SELECT cash_balance FROM users_profile WHERE id = 'default'")
    assert cur.fetchone()[0] == 8500.0  # 10000 - (10 * 150)

    cur = conn.execute("SELECT quantity, avg_cost FROM positions WHERE ticker = 'AAPL'")
    row = cur.fetchone()
    assert row[0] == 10.0
    assert row[1] == 150.0


def test_execute_buy_trade_insufficient_cash():
    conn = create_in_memory_db()
    executor = ChatExecutor(
        llm_client=LLMClient(mock_mode=True),
        price_lookup=lambda ticker: 200.0
    )

    ctx = PortfolioContext(cash_balance=500.0)
    resp = LLMResponse(
        message="Attempting buy",
        trades=[TradeAction(ticker="AAPL", side="buy", quantity=10.0)]
    )

    result = executor.execute_actions(resp, ctx, conn)

    assert len(result.executed_trades) == 0
    assert len(result.failed_trades) == 1
    assert "Insufficient cash" in result.failed_trades[0]["error"]
    assert "⚠️ Trade Warning" in resp.message


def test_execute_sell_trade_success():
    conn = create_in_memory_db()
    # Pre-seed position of 10 AAPL
    conn.execute("INSERT INTO positions (id, user_id, ticker, quantity, avg_cost, updated_at) VALUES ('1', 'default', 'AAPL', 10.0, 100.0, '2026-01-01')")
    conn.commit()

    executor = ChatExecutor(
        llm_client=LLMClient(mock_mode=True),
        price_lookup=lambda ticker: 150.0
    )

    ctx = PortfolioContext(
        cash_balance=10000.0,
        positions=[PositionContext(ticker="AAPL", quantity=10.0, avg_cost=100.0, current_price=150.0)]
    )
    resp = LLMResponse(
        message="Selling 4 AAPL",
        trades=[TradeAction(ticker="AAPL", side="sell", quantity=4.0)]
    )

    result = executor.execute_actions(resp, ctx, conn)

    assert len(result.executed_trades) == 1
    assert result.executed_trades[0]["quantity"] == 4.0

    # Check cash updated (+ 4 * 150 = +600)
    cur = conn.execute("SELECT cash_balance FROM users_profile WHERE id = 'default'")
    assert cur.fetchone()[0] == 10600.0

    # Check position remaining (10 - 4 = 6)
    cur = conn.execute("SELECT quantity FROM positions WHERE ticker = 'AAPL'")
    assert cur.fetchone()[0] == 6.0


def test_execute_watchlist_add_and_remove():
    conn = create_in_memory_db()
    executor = ChatExecutor(llm_client=LLMClient(mock_mode=True))

    ctx = PortfolioContext(watchlist=[WatchlistPriceContext(ticker="TSLA", price=200.0)])
    resp = LLMResponse(
        message="Updating watchlist",
        watchlist_changes=[
            WatchlistAction(ticker="PYPL", action="add"),
            WatchlistAction(ticker="TSLA", action="remove"),
        ]
    )

    result = executor.execute_actions(resp, ctx, conn)

    assert len(result.executed_watchlist) == 2

    cur = conn.execute("SELECT ticker FROM watchlist")
    tickers = [row[0] for row in cur.fetchall()]
    assert "PYPL" in tickers
    assert "TSLA" not in tickers


def test_process_chat_full_flow():
    db_conn = create_in_memory_db()
    
    # Connection factory that returns our existing db_conn
    executor = ChatExecutor(
        llm_client=LLMClient(mock_mode=True),
        db_connection_factory=lambda: db_conn,
        price_lookup=lambda ticker: 100.0
    )

    ctx = PortfolioContext(cash_balance=10000.0)
    res = executor.process_chat("Buy 10 AAPL", ctx)

    assert "message" in res
    assert len(res["trades"]) == 1
    assert res["trades"][0].ticker == "AAPL"

    # Verify chat_messages saved to DB
    cur = db_conn.execute("SELECT role, content, actions FROM chat_messages ORDER BY created_at ASC")
    rows = cur.fetchall()

    assert len(rows) == 2
    assert rows[0][0] == "user"
    assert rows[0][1] == "Buy 10 AAPL"

    assert rows[1][0] == "assistant"
    assert "executed_trades" in rows[1][2]
