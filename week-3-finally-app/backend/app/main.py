import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import chat, health, portfolio, stream, watchlist
from app.config import get_settings
from app.db.database import init_db
from app.market.cache import PriceCache
from app.market.factory import create_market_data_source
from app.services.snapshot_service import SnapshotTask

logger = logging.getLogger("finally.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Initializing database...")
    await init_db(settings.DB_PATH)

    logger.info("Initializing price cache and market data source...")
    app.state.price_cache = PriceCache()
    app.state.market_source = create_market_data_source(settings, app.state.price_cache)
    await app.state.market_source.start()

    logger.info("Starting background snapshot task...")
    app.state.snapshot_task = SnapshotTask(settings.DB_PATH, app.state.price_cache, interval_seconds=30)
    app.state.snapshot_task.start()

    yield

    logger.info("Stopping background snapshot task...")
    if hasattr(app.state, "snapshot_task") and app.state.snapshot_task:
        await app.state.snapshot_task.stop()

    logger.info("Stopping market data source...")
    if hasattr(app.state, "market_source") and app.state.market_source:
        await app.state.market_source.stop()


app = FastAPI(title="FinAlly API", version="0.1.0", lifespan=lifespan)

app.include_router(health.router)
app.include_router(stream.router)
app.include_router(portfolio.router)
app.include_router(watchlist.router)
app.include_router(chat.router)

# Mount static frontend build LAST (serves Next.js static export at root /)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    logger.info(f"Mounting static frontend files from {static_dir}")
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


