import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, HTTPException, Request, status

from app.config import get_settings
from app.db.database import get_db
from app.schemas.portfolio import WatchlistAddRequest, WatchlistItemResponse

router = APIRouter(prefix="/api/watchlist", tags=["Watchlist"])


@router.get("", response_model=List[WatchlistItemResponse])
async def get_watchlist(request: Request):
    """Get all watchlist tickers with real-time price info."""
    settings = getattr(request.app.state, "settings", None) or get_settings()
    cache = getattr(request.app.state, "price_cache", None)
    async with get_db(settings.DB_PATH) as db:
        async with db.execute(
            "SELECT id, ticker, added_at FROM watchlist WHERE user_id = 'default' ORDER BY added_at ASC"
        ) as cursor:
            rows = await cursor.fetchall()
            result = []
            for item_id, ticker, added_at in rows:
                price_up = cache.get(ticker) if cache else None
                price = price_up.price if price_up else 0.0
                prev = price_up.previous_price if price_up else price
                change = price_up.change if price_up else 0.0
                direction = price_up.direction if price_up else "flat"
                result.append(
                    WatchlistItemResponse(
                        id=item_id,
                        ticker=ticker,
                        price=price,
                        previous_price=prev,
                        change=change,
                        direction=direction,
                        added_at=added_at,
                    )
                )
            return result


@router.post("", response_model=WatchlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_watchlist_item(req: WatchlistAddRequest, request: Request):
    """Add a new ticker symbol to watchlist."""
    settings = getattr(request.app.state, "settings", None) or get_settings()
    cache = getattr(request.app.state, "price_cache", None)
    market_source = getattr(request.app.state, "market_source", None)
    ticker = req.ticker

    async with get_db(settings.DB_PATH) as db:
        async with db.execute(
            "SELECT id FROM watchlist WHERE user_id = 'default' AND ticker = ?", (ticker,)
        ) as cursor:
            if await cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ticker {ticker} is already in watchlist",
                )

        item_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()
        await db.execute(
            "INSERT INTO watchlist (id, user_id, ticker, added_at) VALUES (?, 'default', ?, ?)",
            (item_id, ticker, now_iso),
        )
        await db.commit()

        if market_source and hasattr(market_source, "add_ticker"):
            market_source.add_ticker(ticker)

        price_up = cache.get(ticker) if cache else None
        price = price_up.price if price_up else 100.0
        prev = price_up.previous_price if price_up else price
        change = price_up.change if price_up else 0.0
        direction = price_up.direction if price_up else "flat"

        return WatchlistItemResponse(
            id=item_id,
            ticker=ticker,
            price=price,
            previous_price=prev,
            change=change,
            direction=direction,
            added_at=now_iso,
        )


@router.delete("/{ticker}")
async def remove_watchlist_item(ticker: str, request: Request):
    """Remove a ticker symbol from watchlist."""
    ticker_clean = ticker.strip().upper()
    settings = getattr(request.app.state, "settings", None) or get_settings()
    market_source = getattr(request.app.state, "market_source", None)

    async with get_db(settings.DB_PATH) as db:
        cursor = await db.execute(
            "DELETE FROM watchlist WHERE user_id = 'default' AND ticker = ?", (ticker_clean,)
        )
        await db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticker {ticker_clean} not found in watchlist",
            )

        if market_source and hasattr(market_source, "remove_ticker"):
            market_source.remove_ticker(ticker_clean)

        return {"status": "success", "ticker": ticker_clean}
