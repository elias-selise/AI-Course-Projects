"""Unit tests for SQLite connection and lazy initialization logic."""

import os
import sqlite3
from app.db import DEFAULT_SEED_TICKERS, get_db_connection, init_db


def test_lazy_init_creates_tables_and_seeds_data(db_conn):
    """Test that lazy initialization creates schema and seeds default data."""
    cursor = db_conn.cursor()

    # 1. Verify all 6 tables exist
    expected_tables = {
        "users_profile",
        "watchlist",
        "positions",
        "trades",
        "portfolio_snapshots",
        "chat_messages",
    }
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row["name"] for row in cursor.fetchall()}
    assert expected_tables.issubset(existing_tables)

    # 2. Verify default user profile
    cursor.execute("SELECT * FROM users_profile WHERE id = 'default'")
    profile = cursor.fetchone()
    assert profile is not None
    assert profile["id"] == "default"
    assert profile["cash_balance"] == 10000.0
    assert profile["created_at"] != ""

    # 3. Verify default 10 seed tickers
    cursor.execute("SELECT ticker FROM watchlist WHERE user_id = 'default'")
    seeded_tickers = [row["ticker"] for row in cursor.fetchall()]
    assert len(seeded_tickers) == 10
    assert set(seeded_tickers) == set(DEFAULT_SEED_TICKERS)

    # 4. Verify initial portfolio snapshot
    cursor.execute("SELECT * FROM portfolio_snapshots WHERE user_id = 'default'")
    snapshots = cursor.fetchall()
    assert len(snapshots) == 1
    assert snapshots[0]["total_value"] == 10000.0


def test_init_db_idempotency(db_conn):
    """Test that calling init_db multiple times does not duplicate seed data."""
    cursor = db_conn.cursor()

    # Call init_db again on already initialized connection
    init_db(db_conn)
    init_db(db_conn)

    cursor.execute("SELECT COUNT(*) as count FROM users_profile WHERE id = 'default'")
    assert cursor.fetchone()["count"] == 1

    cursor.execute("SELECT COUNT(*) as count FROM watchlist WHERE user_id = 'default'")
    assert cursor.fetchone()["count"] == 10


def test_disk_db_lazy_initialization(temp_db_path):
    """Test lazy initialization against a disk-backed database file."""
    assert not os.path.exists(temp_db_path)

    conn = get_db_connection(temp_db_path)
    try:
        assert os.path.exists(temp_db_path)

        cursor = conn.cursor()
        cursor.execute("SELECT cash_balance FROM users_profile WHERE id = 'default'")
        row = cursor.fetchone()
        assert row is not None
        assert row["cash_balance"] == 10000.0
    finally:
        conn.close()
