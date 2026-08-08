from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class TradeAction(BaseModel):
    """Represents a trade action proposed by the LLM."""
    ticker: str = Field(..., description="Stock ticker symbol in uppercase, e.g. AAPL")
    side: Literal["buy", "sell"] = Field(..., description="Trade side: 'buy' or 'sell'")
    quantity: float = Field(..., gt=0, description="Quantity of shares to buy or sell")

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("Ticker must be a non-empty string")
        return v.strip().upper()


class WatchlistAction(BaseModel):
    """Represents a watchlist modification proposed by the LLM."""
    ticker: str = Field(..., description="Stock ticker symbol in uppercase, e.g. PYPL")
    action: Literal["add", "remove"] = Field(..., description="Watchlist action: 'add' or 'remove'")

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        if not v or not isinstance(v, str):
            raise ValueError("Ticker must be a non-empty string")
        return v.strip().upper()


class LLMResponse(BaseModel):
    """Enforces the structured output JSON schema required for LLM chat responses."""
    message: str = Field(..., description="Conversational response shown to the user")
    trades: List[TradeAction] = Field(default_factory=list, description="Array of trades to auto-execute")
    watchlist_changes: List[WatchlistAction] = Field(default_factory=list, description="Array of watchlist modifications")


class PositionContext(BaseModel):
    """Context information for a single portfolio position."""
    ticker: str
    quantity: float
    avg_cost: float
    current_price: float
    market_value: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0

    def model_post_init(self, __context):
        if self.market_value == 0.0 and self.quantity > 0 and self.current_price > 0:
            self.market_value = round(self.quantity * self.current_price, 2)
        cost_basis = self.quantity * self.avg_cost
        if cost_basis > 0:
            if self.unrealized_pnl == 0.0:
                self.unrealized_pnl = round(self.market_value - cost_basis, 2)
            if self.unrealized_pnl_pct == 0.0:
                self.unrealized_pnl_pct = round((self.unrealized_pnl / cost_basis) * 100, 2)


class WatchlistPriceContext(BaseModel):
    """Context information for a ticker in the watchlist."""
    ticker: str
    price: float
    change: float = 0.0
    direction: str = "flat"  # "up", "down", "flat"


class ChatMessageContext(BaseModel):
    """Representation of recent chat message for context building."""
    role: str  # "user" or "assistant"
    content: str
    actions: Optional[dict] = None
    created_at: Optional[str] = None


class PortfolioContext(BaseModel):
    """Complete user environment context passed to the LLM prompt builder."""
    cash_balance: float = 10000.0
    total_value: float = 10000.0
    total_pnl: float = 0.0
    total_pnl_pct: float = 0.0
    positions: List[PositionContext] = Field(default_factory=list)
    watchlist: List[WatchlistPriceContext] = Field(default_factory=list)
    history: List[ChatMessageContext] = Field(default_factory=list)
