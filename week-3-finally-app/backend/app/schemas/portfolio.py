from datetime import datetime
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


class TradeRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol")
    side: Literal["buy", "sell"] = Field(..., description="Trade direction: buy or sell")
    quantity: float = Field(..., gt=0, description="Quantity of shares to trade")

    @field_validator("ticker")
    @classmethod
    def sanitize_ticker(cls, v: str) -> str:
        return v.strip().upper()


class TradeResponse(BaseModel):
    trade_id: str
    ticker: str
    side: Literal["buy", "sell"]
    quantity: float
    price: float
    total_value: float
    cash_balance: float
    executed_at: str


class PositionItem(BaseModel):
    ticker: str
    quantity: float
    avg_cost: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_percent: float


class PortfolioResponse(BaseModel):
    cash_balance: float
    positions_value: float
    total_value: float
    total_unrealized_pnl: float
    total_unrealized_pnl_percent: float
    positions: List[PositionItem]


class SnapshotResponse(BaseModel):
    id: str
    total_value: float
    recorded_at: str


class WatchlistAddRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, description="Stock ticker symbol to add")

    @field_validator("ticker")
    @classmethod
    def sanitize_ticker(cls, v: str) -> str:
        return v.strip().upper()


class WatchlistItemResponse(BaseModel):
    id: str
    ticker: str
    price: float
    previous_price: float
    change: float
    direction: Literal["up", "down", "flat"]
    added_at: str
