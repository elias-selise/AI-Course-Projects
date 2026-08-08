import pytest
from pydantic import ValidationError
from app.llm.models import (
    TradeAction,
    WatchlistAction,
    LLMResponse,
    PositionContext,
    WatchlistPriceContext,
    PortfolioContext,
)


def test_trade_action_validation():
    # Valid trade action
    trade = TradeAction(ticker="aapl", side="buy", quantity=10.5)
    assert trade.ticker == "AAPL"
    assert trade.side == "buy"
    assert trade.quantity == 10.5

    # Invalid side
    with pytest.raises(ValidationError):
        TradeAction(ticker="AAPL", side="hold", quantity=5.0)

    # Negative quantity
    with pytest.raises(ValidationError):
        TradeAction(ticker="AAPL", side="buy", quantity=-5.0)

    # Zero quantity
    with pytest.raises(ValidationError):
        TradeAction(ticker="AAPL", side="sell", quantity=0.0)


def test_watchlist_action_validation():
    # Valid watchlist action
    wl = WatchlistAction(ticker="pypl", action="add")
    assert wl.ticker == "PYPL"
    assert wl.action == "add"

    # Invalid action
    with pytest.raises(ValidationError):
        WatchlistAction(ticker="PYPL", action="update")


def test_llm_response_schema():
    # Valid response with trades and watchlist changes
    resp = LLMResponse(
        message="I bought 10 shares of AAPL and added PYPL to watchlist.",
        trades=[TradeAction(ticker="AAPL", side="buy", quantity=10)],
        watchlist_changes=[WatchlistAction(ticker="PYPL", action="add")]
    )
    assert resp.message == "I bought 10 shares of AAPL and added PYPL to watchlist."
    assert len(resp.trades) == 1
    assert resp.trades[0].ticker == "AAPL"
    assert len(resp.watchlist_changes) == 1
    assert resp.watchlist_changes[0].action == "add"

    # Default empty arrays
    resp_empty = LLMResponse(message="No trades proposed.")
    assert resp_empty.trades == []
    assert resp_empty.watchlist_changes == []


def test_position_context_calculations():
    pos = PositionContext(
        ticker="AAPL",
        quantity=10.0,
        avg_cost=150.0,
        current_price=200.0,
    )
    assert pos.market_value == 2000.0
    assert pos.unrealized_pnl == 500.0
    assert pos.unrealized_pnl_pct == pytest.approx(33.33, abs=0.01)


def test_portfolio_context_defaults():
    ctx = PortfolioContext()
    assert ctx.cash_balance == 10000.0
    assert ctx.total_value == 10000.0
    assert ctx.positions == []
    assert ctx.watchlist == []
    assert ctx.history == []
