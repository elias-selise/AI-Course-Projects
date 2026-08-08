"""Unit tests for positions repository operations."""

import pytest
from app.db import DatabaseRepository, Position


def test_get_positions_empty_initial(repo: DatabaseRepository):
    """Test retrieving positions when user has none."""
    positions = repo.get_positions("default")
    assert len(positions) == 0


def test_upsert_position_create_and_update(repo: DatabaseRepository):
    """Test creating a new position and updating it."""
    # 1. Create initial position
    pos1 = repo.upsert_position("default", "AAPL", 10.0, 150.0)
    assert isinstance(pos1, Position)
    assert pos1.ticker == "AAPL"
    assert pos1.quantity == 10.0
    assert pos1.avg_cost == 150.0

    # 2. Update existing position
    pos2 = repo.upsert_position("default", "AAPL", 25.0, 160.0)
    assert pos2.id == pos1.id
    assert pos2.quantity == 25.0
    assert pos2.avg_cost == 160.0

    positions = repo.get_positions("default")
    assert len(positions) == 1


def test_get_position_by_ticker(repo: DatabaseRepository):
    """Test retrieving position by ticker symbol."""
    repo.upsert_position("default", "MSFT", 5.0, 400.0)

    pos = repo.get_position_by_ticker("default", "msft")
    assert pos is not None
    assert pos.ticker == "MSFT"
    assert pos.quantity == 5.0
    assert pos.avg_cost == 400.0

    assert repo.get_position_by_ticker("default", "GOOGL") is None


def test_delete_position(repo: DatabaseRepository):
    """Test deleting a position."""
    repo.upsert_position("default", "NVDA", 2.0, 120.0)
    assert repo.get_position_by_ticker("default", "NVDA") is not None

    deleted = repo.delete_position("default", "NVDA")
    assert deleted is True
    assert repo.get_position_by_ticker("default", "NVDA") is None
    assert repo.delete_position("default", "NVDA") is False


def test_upsert_position_invalid_quantity_raises(repo: DatabaseRepository):
    """Test that zero or negative quantity raises ValueError."""
    with pytest.raises(ValueError, match="Position quantity must be greater than 0"):
        repo.upsert_position("default", "AAPL", 0.0, 150.0)
