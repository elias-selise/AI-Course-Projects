from datetime import datetime
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class TradeAction(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    side: Literal["buy", "sell"] = Field(...)
    quantity: float = Field(..., gt=0)

    @field_validator("ticker")
    @classmethod
    def sanitize_ticker(cls, v: str) -> str:
        return v.strip().upper()


class WatchlistAction(BaseModel):
    action: Literal["add", "remove"] = Field(...)
    ticker: str = Field(..., min_length=1, max_length=10)

    @field_validator("ticker")
    @classmethod
    def sanitize_ticker(cls, v: str) -> str:
        return v.strip().upper()


class LLMResponseSchema(BaseModel):
    message: str = Field(..., description="Natural language message to display to user")
    trades: List[TradeAction] = Field(default_factory=list, description="List of trade actions to auto-execute")
    watchlist_changes: List[WatchlistAction] = Field(default_factory=list, description="List of watchlist updates")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="User prompt text")


class ExecutedTradeResult(BaseModel):
    trade_id: Optional[str] = None
    ticker: str
    side: Literal["buy", "sell"]
    quantity: float
    price: float = 0.0
    total_value: float = 0.0
    status: Literal["success", "failed"] = "success"
    error: Optional[str] = None


class ExecutedWatchlistResult(BaseModel):
    ticker: str
    action: Literal["add", "remove"]
    status: Literal["success", "failed"] = "success"
    error: Optional[str] = None


class ChatResponse(BaseModel):
    message_id: str
    user_message: str
    assistant_message: str
    executed_trades: List[ExecutedTradeResult] = Field(default_factory=list)
    executed_watchlist_changes: List[ExecutedWatchlistResult] = Field(default_factory=list)
    created_at: str


class ChatMessageResponse(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: str
    actions: Optional[Dict[str, Any]] = None
    created_at: str
