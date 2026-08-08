"""Unit tests for portfolio snapshots repository operations."""

from app.db import DatabaseRepository, PortfolioSnapshot


def test_record_portfolio_snapshot(repo: DatabaseRepository):
    """Test recording a portfolio snapshot."""
    snapshot = repo.record_portfolio_snapshot("default", 10500.25)
    assert isinstance(snapshot, PortfolioSnapshot)
    assert snapshot.user_id == "default"
    assert snapshot.total_value == 10500.25
    assert snapshot.recorded_at != ""


def test_get_portfolio_snapshots(repo: DatabaseRepository):
    """Test retrieving portfolio snapshot history."""
    repo.record_portfolio_snapshot("default", 10200.0)
    repo.record_portfolio_snapshot("default", 10450.0)

    # Initial seed snapshot ($10,000) + 2 new snapshots = 3 total
    snapshots = repo.get_portfolio_snapshots("default")
    assert len(snapshots) == 3
    assert snapshots[0].total_value == 10000.0
    assert snapshots[1].total_value == 10200.0
    assert snapshots[2].total_value == 10450.0
