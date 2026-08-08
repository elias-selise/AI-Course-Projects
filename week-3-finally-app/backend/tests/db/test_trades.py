"""Unit tests for trades repository & trade execution logic."""

import pytest
from app.db import DatabaseRepository, Trade


def test_record_trade_standalone(repo: DatabaseRepository):
    """Test recording a trade directly in the trade log."""
    trade = repo.record_trade("default", "AAPL", "buy", 10.0, 150.0)
    assert isinstance(trade, Trade)
    assert trade.ticker == "AAPL"
    assert trade.side == "buy"
    assert trade.quantity == 10.0
    assert trade.price == 150.0

    trades = repo.get_trades("default")
    assert len(trades) == 1
    assert trades[0].id == trade.id


def test_execute_trade_buy_new_position(repo: DatabaseRepository):
    """Test buying shares creating a new position and deducting cash."""
    # Initial balance = $10,000. Buy 10 AAPL @ $150 ($1,500)
    trade, pos, profile = repo.execute_trade("default", "AAPL", "buy", 10.0, 150.0)

    assert trade.ticker == "AAPL"
    assert trade.side == "buy"
    assert trade.quantity == 10.0

    assert pos is not None
    assert pos.ticker == "AAPL"
    assert pos.quantity == 10.0
    assert pos.avg_cost == 150.0

    assert profile.cash_balance == 8500.0


def test_execute_trade_buy_add_to_existing_position(repo: DatabaseRepository):
    """Test buying additional shares recalculates average cost correctly."""
    # 1. Buy 10 AAPL @ $100 ($1,000 total) -> cash $9,000
    repo.execute_trade("default", "AAPL", "buy", 10.0, 100.0)

    # 2. Buy 10 AAPL @ $200 ($2,000 total) -> cash $7,000
    trade, pos, profile = repo.execute_trade("default", "AAPL", "buy", 10.0, 200.0)

    assert pos is not None
    assert pos.quantity == 20.0
    # Average cost = (10*100 + 10*200) / 20 = 3000 / 20 = 150.0
    assert pos.avg_cost == 150.0
    assert profile.cash_balance == 7000.0


def test_execute_trade_buy_insufficient_cash(repo: DatabaseRepository):
    """Test buying shares exceeding cash balance raises ValueError."""
    with pytest.raises(ValueError, match="Insufficient cash balance"):
        # Cash is $10,000. Try buying 100 shares @ $150 ($15,000)
        repo.execute_trade("default", "AAPL", "buy", 100.0, 150.0)


def test_execute_trade_sell_partial_position(repo: DatabaseRepository):
    """Test partial sell reduces quantity while preserving average cost."""
    # Buy 20 AAPL @ $100 ($2,000) -> cash $8,000
    repo.execute_trade("default", "AAPL", "buy", 20.0, 100.0)

    # Sell 5 AAPL @ $120 ($600 proceeds) -> cash $8,600
    trade, pos, profile = repo.execute_trade("default", "AAPL", "sell", 5.0, 120.0)

    assert trade.side == "sell"
    assert trade.quantity == 5.0

    assert pos is not None
    assert pos.quantity == 15.0
    assert pos.avg_cost == 100.0  # Avg cost unchanged on sell

    assert profile.cash_balance == 8600.0


def test_execute_trade_sell_full_position(repo: DatabaseRepository):
    """Test selling entire position removes the position record."""
    # Buy 10 AAPL @ $100 -> cash $9,000
    repo.execute_trade("default", "AAPL", "buy", 10.0, 100.0)

    # Sell 10 AAPL @ $110 ($1,100 proceeds) -> cash $10,100
    trade, pos, profile = repo.execute_trade("default", "AAPL", "sell", 10.0, 110.0)

    assert pos is None
    assert repo.get_position_by_ticker("default", "AAPL") is None
    assert profile.cash_balance == 10100.0


def test_execute_trade_sell_insufficient_position(repo: DatabaseRepository):
    """Test selling shares without owning enough position raises ValueError."""
    # Buy 5 AAPL @ $100
    repo.execute_trade("default", "AAPL", "buy", 5.0, 100.0)

    with pytest.raises(ValueError, match="Insufficient position"):
        # Try selling 10 shares
        repo.execute_trade("default", "AAPL", "sell", 10.0, 100.0)

    with pytest.raises(ValueError, match="Insufficient position"):
        # Try selling unowned ticker
        repo.execute_trade("default", "GOOGL", "sell", 1.0, 100.0)


def test_get_trades_by_ticker(repo: DatabaseRepository):
    """Test retrieving trade history filtered by ticker."""
    repo.execute_trade("default", "AAPL", "buy", 5.0, 150.0)
    repo.execute_trade("default", "MSFT", "buy", 2.0, 400.0)
    repo.execute_trade("default", "AAPL", "sell", 2.0, 160.0)

    aapl_trades = repo.get_trades_by_ticker("default", "AAPL")
    assert len(aapl_trades) == 2
    assert {t.side for t in aapl_trades} == {"buy", "sell"}

    msft_trades = repo.get_trades_by_ticker("default", "MSFT")
    assert len(msft_trades) == 1
