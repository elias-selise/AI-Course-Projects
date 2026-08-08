"""Unit tests for user profile repository operations."""

import pytest
from app.db import DatabaseRepository, UserProfile


def test_get_user_profile(repo: DatabaseRepository):
    """Test retrieving existing user profile."""
    profile = repo.get_user_profile("default")
    assert profile is not None
    assert isinstance(profile, UserProfile)
    assert profile.id == "default"
    assert profile.cash_balance == 10000.0


def test_get_user_profile_non_existent(repo: DatabaseRepository):
    """Test retrieving non-existent user profile returns None."""
    profile = repo.get_user_profile("non_existent_user")
    assert profile is None


def test_update_cash_balance(repo: DatabaseRepository):
    """Test updating user cash balance."""
    updated = repo.update_cash_balance("default", 15000.50)
    assert updated.cash_balance == 15000.50

    profile = repo.get_user_profile("default")
    assert profile is not None
    assert profile.cash_balance == 15000.50


def test_update_cash_balance_negative_raises(repo: DatabaseRepository):
    """Test that setting a negative cash balance raises ValueError."""
    with pytest.raises(ValueError, match="Cash balance cannot be negative"):
        repo.update_cash_balance("default", -100.0)


def test_adjust_cash_balance(repo: DatabaseRepository):
    """Test atomic cash balance adjustments (deposit & withdrawal)."""
    # Deposit $2,500
    p1 = repo.adjust_cash_balance("default", 2500.0)
    assert p1.cash_balance == 12500.0

    # Withdraw $1,000
    p2 = repo.adjust_cash_balance("default", -1000.0)
    assert p2.cash_balance == 11500.0


def test_adjust_cash_balance_insufficient_raises(repo: DatabaseRepository):
    """Test that deducting more cash than available raises ValueError."""
    with pytest.raises(ValueError, match="Insufficient cash balance"):
        repo.adjust_cash_balance("default", -15000.0)
