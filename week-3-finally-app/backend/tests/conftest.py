import os
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from app.db.database import init_db
from app.market.cache import PriceCache
from app.market.simulator import SimulatorDataSource
from app.main import app, price_cache as global_price_cache


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    db_file = tmp_path / "test_finally.db"
    init_db(db_file)
    return db_file


@pytest.fixture
def test_price_cache() -> PriceCache:
    cache = PriceCache()
    return cache


@pytest.fixture
def client(tmp_db_path: Path, monkeypatch) -> TestClient:
    monkeypatch.setenv("DATABASE_PATH", str(tmp_db_path))
    monkeypatch.setenv("LLM_MOCK", "true")
    with TestClient(app) as tc:
        yield tc
