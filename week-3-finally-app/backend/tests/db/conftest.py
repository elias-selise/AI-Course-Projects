"""Pytest fixtures for database unit tests."""

import os
import sys
import sqlite3
from pathlib import Path
import pytest

# Ensure backend root is in python path
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.db import DatabaseRepository, get_db_connection, init_db


@pytest.fixture
def db_conn():
    """Provides a fresh, initialized in-memory SQLite database connection per test."""
    conn = get_db_connection(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def repo(db_conn):
    """Provides a DatabaseRepository bound to the shared in-memory database connection."""
    return DatabaseRepository(conn=db_conn)


@pytest.fixture
def temp_db_path(tmp_path):
    """Provides a temporary file path for disk-based database testing."""
    return str(tmp_path / "test_finally.db")
