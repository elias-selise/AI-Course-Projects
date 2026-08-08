"""Database domain models for FinAlly AI Trading Workstation."""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Union
import json


@dataclass
class UserProfile:
    """User profile model storing account state like cash balance."""
    id: str = "default"
    cash_balance: float = 10000.0
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Any) -> "UserProfile":
        return cls(
            id=row["id"],
            cash_balance=float(row["cash_balance"]),
            created_at=row["created_at"],
        )


@dataclass
class WatchlistItem:
    """Watchlist model representing tickers tracked by a user."""
    id: str
    user_id: str = "default"
    ticker: str = ""
    added_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Any) -> "WatchlistItem":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            ticker=row["ticker"],
            added_at=row["added_at"],
        )


@dataclass
class Position:
    """Position model representing active portfolio holdings."""
    id: str
    user_id: str = "default"
    ticker: str = ""
    quantity: float = 0.0
    avg_cost: float = 0.0
    updated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Any) -> "Position":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            ticker=row["ticker"],
            quantity=float(row["quantity"]),
            avg_cost=float(row["avg_cost"]),
            updated_at=row["updated_at"],
        )


@dataclass
class Trade:
    """Trade model representing historical trade transactions."""
    id: str
    user_id: str = "default"
    ticker: str = ""
    side: str = "buy"
    quantity: float = 0.0
    price: float = 0.0
    executed_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Any) -> "Trade":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            ticker=row["ticker"],
            side=row["side"],
            quantity=float(row["quantity"]),
            price=float(row["price"]),
            executed_at=row["executed_at"],
        )


@dataclass
class PortfolioSnapshot:
    """Portfolio snapshot model representing total portfolio value over time."""
    id: str
    user_id: str = "default"
    total_value: float = 0.0
    recorded_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Any) -> "PortfolioSnapshot":
        return cls(
            id=row["id"],
            user_id=row["user_id"],
            total_value=float(row["total_value"]),
            recorded_at=row["recorded_at"],
        )


@dataclass
class ChatMessage:
    """Chat message model representing LLM & user conversation history."""
    id: str
    user_id: str = "default"
    role: str = "user"
    content: str = ""
    actions: Optional[Union[Dict[str, Any], List[Any]]] = None
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d

    @classmethod
    def from_row(cls, row: Any) -> "ChatMessage":
        raw_actions = row["actions"]
        parsed_actions = None
        if raw_actions:
            if isinstance(raw_actions, str):
                try:
                    parsed_actions = json.loads(raw_actions)
                except Exception:
                    parsed_actions = raw_actions
            else:
                parsed_actions = raw_actions

        return cls(
            id=row["id"],
            user_id=row["user_id"],
            role=row["role"],
            content=row["content"],
            actions=parsed_actions,
            created_at=row["created_at"],
        )
