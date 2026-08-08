from dataclasses import dataclass, asdict
import json
from datetime import datetime, timezone


@dataclass(frozen=True)
class PriceUpdate:
    ticker: str
    price: float
    previous_price: float
    timestamp: str
    change: float
    direction: str  # "up", "down", "flat"

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
