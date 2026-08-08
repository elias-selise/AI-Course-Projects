from typing import Literal
from pydantic import BaseModel, Field


class PriceUpdate(BaseModel):
    ticker: str
    price: float
    previous_price: float
    timestamp: str
    change: float
    direction: Literal["up", "down", "flat"]
