"""Unit tests for watchlist repository operations."""

import pytest
from app.db import DatabaseRepository, WatchlistItem, DEFAULT_SEED_TICKERS


def test_get_watchlist_default_seed(repo: DatabaseRepository):
    """Test retrieving default seed watchlist."""
    items = repo.get_watchlist("default")
    assert len(items) == 10
    tickers = [item.ticker for item in items]
    for seed in DEFAULT_SEED_TICKERS:
        assert seed in tickers


def test_add_to_watchlist(repo: DatabaseRepository):
    """Test adding a new ticker to watchlist."""
    item = repo.add_to_watchlist("default", "amd")
    assert isinstance(item, WatchlistItem)
    assert item.ticker == "AMD"
    assert item.user_id == "default"

    assert repo.is_in_watchlist("default", "AMD")
    items = repo.get_watchlist("default")
    assert len(items) == 11


def test_add_duplicate_ticker_idempotent(repo: DatabaseRepository):
    """Test adding a duplicate ticker returns existing item without error."""
    item1 = repo.add_to_watchlist("default", "AAPL")
    item2 = repo.add_to_watchlist("default", "AAPL")
    assert item1.ticker == "AAPL"
    assert item2.ticker == "AAPL"
    assert item1.id == item2.id

    items = repo.get_watchlist("default")
    assert len(items) == 10


def test_remove_from_watchlist(repo: DatabaseRepository):
    """Test removing a ticker from watchlist."""
    assert repo.is_in_watchlist("default", "TSLA")
    deleted = repo.remove_from_watchlist("default", "TSLA")
    assert deleted is True
    assert not repo.is_in_watchlist("default", "TSLA")

    items = repo.get_watchlist("default")
    assert len(items) == 9

    # Removing non-existent returns False
    assert repo.remove_from_watchlist("default", "TSLA") is False


def test_add_empty_ticker_raises(repo: DatabaseRepository):
    """Test that adding an empty ticker raises ValueError."""
    with pytest.raises(ValueError, match="Ticker symbol cannot be empty"):
        repo.add_to_watchlist("default", "   ")
