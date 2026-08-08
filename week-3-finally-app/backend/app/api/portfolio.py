from typing import List
from fastapi import APIRouter, HTTPException, Request, status

from app.config import get_settings
from app.db.database import get_db
from app.schemas.portfolio import PortfolioResponse, SnapshotResponse, TradeRequest, TradeResponse
from app.services.portfolio_service import calculate_portfolio, execute_trade

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(request: Request):
    """Retrieve current portfolio cash balance, positions, total value, and unrealized P&L."""
    settings = getattr(request.app.state, "settings", None) or get_settings()
    cache = getattr(request.app.state, "price_cache", None)
    async with get_db(settings.DB_PATH) as db:
        return await calculate_portfolio(db, cache)


@router.post("/trade", response_model=TradeResponse)
async def submit_trade(trade_req: TradeRequest, request: Request):
    """Execute a market buy/sell order."""
    settings = getattr(request.app.state, "settings", None) or get_settings()
    cache = getattr(request.app.state, "price_cache", None)
    async with get_db(settings.DB_PATH) as db:
        try:
            return await execute_trade(db, cache, trade_req)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/history", response_model=List[SnapshotResponse])
async def get_portfolio_history(request: Request):
    """Retrieve chronological portfolio snapshot history."""
    settings = getattr(request.app.state, "settings", None) or get_settings()
    async with get_db(settings.DB_PATH) as db:
        async with db.execute(
            "SELECT id, total_value, recorded_at FROM portfolio_snapshots WHERE user_id = 'default' ORDER BY recorded_at ASC"
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                SnapshotResponse(id=r[0], total_value=r[1], recorded_at=r[2])
                for r in rows
            ]
