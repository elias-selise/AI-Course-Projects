import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import FRONTEND_STATIC_DIR, DATABASE_PATH
from app.db.database import (
    init_db,
    get_watchlist,
    get_positions,
)
from app.market.cache import PriceCache
from app.market.factory import create_market_data_source
from app.market.stream import create_stream_router

from app.portfolio.models import TradeRequest, PortfolioResponse, TradeResponse
from app.portfolio.service import (
    get_portfolio_summary,
    execute_trade_action,
    get_portfolio_history_records,
)

from app.watchlist.models import WatchlistAddRequest, WatchlistItem
from app.watchlist.service import (
    get_watchlist_items,
    add_watchlist_item,
    remove_watchlist_item,
)

from app.chat.models import ChatMessageRequest, ChatMessageResponse
from app.chat.service import process_chat_message

from app.background.snapshot_task import SnapshotTask


# Shared state instances
price_cache = PriceCache()
market_source = None
snapshot_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global market_source, snapshot_task

    # 1. Initialize Database
    init_db()

    # 2. Instantiate and start Market Data Source
    market_source = create_market_data_source(price_cache)
    wl_items = get_watchlist("default")
    pos_items = get_positions("default")
    initial_tickers = list(set([w["ticker"] for w in wl_items] + [p["ticker"] for p in pos_items]))
    if not initial_tickers:
        initial_tickers = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "JPM", "V", "NFLX"]

    await market_source.start(initial_tickers)

    # 3. Instantiate and start Background Snapshot Task
    snapshot_task = SnapshotTask(price_cache, interval=30.0)
    await snapshot_task.start()

    yield

    # Shutdown logic
    if snapshot_task:
        await snapshot_task.stop()
    if market_source:
        await market_source.stop()


def create_app() -> FastAPI:
    app = FastAPI(
        title="FinAlly Trading Workstation API",
        description="FastAPI Backend for FinAlly AI Trading Workstation",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Mount SSE stream router
    app.include_router(create_stream_router(price_cache))

    # --- REST API ROUTES ---

    # Health Check
    @app.get("/api/health", tags=["system"])
    async def get_health():
        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected" if DATABASE_PATH.exists() else "uninitialized",
            "market_data": "running" if market_source else "stopped",
        }

    # Portfolio Routes
    @app.get("/api/portfolio", tags=["portfolio"])
    async def get_portfolio():
        return get_portfolio_summary("default", price_cache)

    @app.post("/api/portfolio/trade", tags=["portfolio"])
    async def post_trade(trade_req: TradeRequest):
        try:
            res = execute_trade_action(
                ticker=trade_req.ticker,
                quantity=trade_req.quantity,
                side=trade_req.side,
                user_id="default",
                price_cache=price_cache,
            )
            return res
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    @app.get("/api/portfolio/history", tags=["portfolio"])
    async def get_portfolio_history():
        return get_portfolio_history_records("default")

    # Watchlist Routes
    @app.get("/api/watchlist", tags=["watchlist"])
    async def get_watchlist():
        return get_watchlist_items("default", price_cache)

    @app.post("/api/watchlist", tags=["watchlist"])
    async def post_watchlist(add_req: WatchlistAddRequest):
        try:
            return await add_watchlist_item(
                ticker=add_req.ticker,
                user_id="default",
                price_cache=price_cache,
                market_source=market_source,
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    @app.delete("/api/watchlist/{ticker}", tags=["watchlist"])
    async def delete_watchlist(ticker: str):
        success = await remove_watchlist_item(
            ticker=ticker,
            user_id="default",
            market_source=market_source,
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Ticker '{ticker}' not found in watchlist.")
        return {"success": True, "ticker": ticker.upper()}

    # Chat Route
    @app.post("/api/chat", tags=["chat"])
    async def post_chat(chat_req: ChatMessageRequest):
        try:
            return await process_chat_message(
                user_message=chat_req.message,
                user_id="default",
                price_cache=price_cache,
                market_source=market_source,
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    # --- STATIC FILE SERVING FOR NEXT.JS STATIC BUILD ---
    static_dir = Path(FRONTEND_STATIC_DIR)
    if static_dir.exists() and static_dir.is_dir():
        # Mount _next directory for static assets
        next_static = static_dir / "_next"
        if next_static.exists():
            app.mount("/_next", StaticFiles(directory=str(next_static)), name="next_static")

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_static_or_spa(full_path: str):
            # Skip API paths
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="API path not found")

            target_file = static_dir / full_path
            if target_file.exists() and target_file.is_file():
                return FileResponse(target_file)

            # Check if full_path + '.html' exists
            html_file = static_dir / f"{full_path}.html"
            if html_file.exists() and html_file.is_file():
                return FileResponse(html_file)

            # Fallback to index.html
            index_file = static_dir / "index.html"
            if index_file.exists():
                return FileResponse(index_file)

            return JSONResponse({"detail": "Not Found"}, status_code=404)

    return app


app = create_app()
