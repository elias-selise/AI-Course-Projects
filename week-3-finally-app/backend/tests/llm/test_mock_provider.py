from app.llm.mock_provider import MockLLMProvider
from app.llm.models import PortfolioContext


def test_mock_buy_trade():
    mock = MockLLMProvider()
    resp = mock.generate_response("Please buy 15 AAPL shares for me.")
    assert len(resp.trades) == 1
    assert resp.trades[0].ticker == "AAPL"
    assert resp.trades[0].side == "buy"
    assert resp.trades[0].quantity == 15.0
    assert "buy 15 shares of AAPL" in resp.message.lower()


def test_mock_sell_trade():
    mock = MockLLMProvider()
    resp = mock.generate_response("Sell 4.5 MSFT shares.")
    assert len(resp.trades) == 1
    assert resp.trades[0].ticker == "MSFT"
    assert resp.trades[0].side == "sell"
    assert resp.trades[0].quantity == 4.5


def test_mock_watchlist_add():
    mock = MockLLMProvider()
    resp = mock.generate_response("Add PYPL to my watchlist.")
    assert len(resp.watchlist_changes) == 1
    assert resp.watchlist_changes[0].ticker == "PYPL"
    assert resp.watchlist_changes[0].action == "add"


def test_mock_watchlist_remove():
    mock = MockLLMProvider()
    resp = mock.generate_response("Remove TSLA from watchlist.")
    assert len(resp.watchlist_changes) == 1
    assert resp.watchlist_changes[0].ticker == "TSLA"
    assert resp.watchlist_changes[0].action == "remove"


def test_mock_general_portfolio_analysis():
    mock = MockLLMProvider()
    ctx = PortfolioContext(cash_balance=9000.0, total_value=12000.0)
    resp = mock.generate_response("How is my portfolio performing?", context=ctx)
    assert resp.trades == []
    assert resp.watchlist_changes == []
    assert "$12,000.00" in resp.message
    assert "$9,000.00" in resp.message
