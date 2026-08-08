from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class TradeRequest(BaseModel):
    ticker: str
    quantity: float = Field(..., gt=0, description="Quantity must be greater than zero")
    side: str = Field(..., description="Trade side: 'buy' or 'sell'")

    @field_validator("side")
    @classmethod
    def validate_side(cls, v: str) -> str:
        s = v.lower().strip()
        if s not in ("buy", "sell"):
            raise ValueError("Trade side must be 'buy' or 'sell'")
        return s

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        t = v.upper().strip()
        if not t:
            raise ValueError("Ticker cannot be empty")
        return t


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
    positions: List[PositionItem]
    total_positions_value: float
    total_portfolio_value: float
    total_value: Optional[float] = None
    total_unrealized_pnl: float
    unrealized_pnl: Optional[float] = None
    unrealized_pnl_pct: Optional[float] = None


class TradeResult(BaseModel):
    id: str
    ticker: str
    side: str
    quantity: float
    price: float
    executed_at: str


class TradeResponse(BaseModel):
    success: bool
    trade: Optional[TradeResult] = None
    cash_balance: float
    message: Optional[str] = None
