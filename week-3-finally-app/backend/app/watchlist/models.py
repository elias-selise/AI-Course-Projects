from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any


class WatchlistAddRequest(BaseModel):
    ticker: str = Field(..., description="Ticker symbol to watch")

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, v: str) -> str:
        t = v.upper().strip()
        if not t:
            raise ValueError("Ticker symbol cannot be empty")
        return t


class WatchlistItem(BaseModel):
    id: str
    ticker: str
    added_at: str
    current_price: Optional[float] = None
    price_update: Optional[Dict[str, Any]] = None
