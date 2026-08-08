"""CRUD Repository operations for FinAlly database entities."""

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

from .connection import get_db_connection
from .models import (
    ChatMessage,
    PortfolioSnapshot,
    Position,
    Trade,
    UserProfile,
    WatchlistItem,
)


class DatabaseRepository:
    """Repository class encapsulating all SQLite database operations."""

    def __init__(self, db_path: Optional[str] = None, conn: Optional[sqlite3.Connection] = None):
        self.db_path = db_path
        self._external_conn = conn

    def _get_connection(self) -> sqlite3.Connection:
        if self._external_conn is not None:
            return self._external_conn
        return get_db_connection(self.db_path)

    # -------------------------------------------------------------------------
    # Users Profile Operations
    # -------------------------------------------------------------------------

    def get_user_profile(self, user_id: str = "default", conn: Optional[sqlite3.Connection] = None) -> Optional[UserProfile]:
        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute("SELECT * FROM users_profile WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if not conn and not self._external_conn:
            c.close()
        if row:
            return UserProfile.from_row(row)
        return None

    def update_cash_balance(
        self, user_id: str = "default", new_balance: float = 10000.0, conn: Optional[sqlite3.Connection] = None
    ) -> UserProfile:
        if new_balance < 0:
            raise ValueError("Cash balance cannot be negative")

        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute(
            "UPDATE users_profile SET cash_balance = ? WHERE id = ?",
            (round(new_balance, 4), user_id),
        )
        if cursor.rowcount == 0:
            now_iso = datetime.now(timezone.utc).isoformat()
            cursor.execute(
                "INSERT INTO users_profile (id, cash_balance, created_at) VALUES (?, ?, ?)",
                (user_id, round(new_balance, 4), now_iso),
            )
        if not conn and not self._external_conn:
            c.commit()
            c.close()
        elif conn:
            conn.commit()

        profile = self.get_user_profile(user_id, conn=conn)
        assert profile is not None
        return profile

    def adjust_cash_balance(
        self, user_id: str = "default", amount_change: float = 0.0, conn: Optional[sqlite3.Connection] = None
    ) -> UserProfile:
        c = conn or self._get_connection()
        try:
            profile = self.get_user_profile(user_id, conn=c)
            if not profile:
                raise ValueError(f"User profile '{user_id}' not found.")

            new_balance = profile.cash_balance + amount_change
            if new_balance < -1e-6:  # Precision floating tolerance
                raise ValueError(f"Insufficient cash balance. Current: ${profile.cash_balance:.2f}, requested change: ${amount_change:.2f}")

            return self.update_cash_balance(user_id, max(0.0, new_balance), conn=c)
        finally:
            if not conn and not self._external_conn:
                c.close()

    # -------------------------------------------------------------------------
    # Watchlist Operations
    # -------------------------------------------------------------------------

    def get_watchlist(self, user_id: str = "default", conn: Optional[sqlite3.Connection] = None) -> List[WatchlistItem]:
        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute("SELECT * FROM watchlist WHERE user_id = ? ORDER BY added_at ASC", (user_id,))
        rows = cursor.fetchall()
        if not conn and not self._external_conn:
            c.close()
        return [WatchlistItem.from_row(r) for r in rows]

    def is_in_watchlist(self, user_id: str = "default", ticker: str = "", conn: Optional[sqlite3.Connection] = None) -> bool:
        ticker = ticker.upper().strip()
        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM watchlist WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        row = cursor.fetchone()
        if not conn and not self._external_conn:
            c.close()
        return bool(row and row["count"] > 0)

    def add_to_watchlist(
        self, user_id: str = "default", ticker: str = "", conn: Optional[sqlite3.Connection] = None
    ) -> WatchlistItem:
        ticker = ticker.upper().strip()
        if not ticker:
            raise ValueError("Ticker symbol cannot be empty")

        c = conn or self._get_connection()
        cursor = c.cursor()
        
        # Check if already exists
        cursor.execute("SELECT * FROM watchlist WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        row = cursor.fetchone()
        if row:
            if not conn and not self._external_conn:
                c.close()
            return WatchlistItem.from_row(row)

        item_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()
        cursor.execute(
            """
            INSERT INTO watchlist (id, user_id, ticker, added_at)
            VALUES (?, ?, ?, ?)
            """,
            (item_id, user_id, ticker, now_iso),
        )
        if not conn and not self._external_conn:
            c.commit()
            c.close()
        elif conn:
            conn.commit()

        return WatchlistItem(id=item_id, user_id=user_id, ticker=ticker, added_at=now_iso)

    def remove_from_watchlist(
        self, user_id: str = "default", ticker: str = "", conn: Optional[sqlite3.Connection] = None
    ) -> bool:
        ticker = ticker.upper().strip()
        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute("DELETE FROM watchlist WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        deleted = cursor.rowcount > 0
        if not conn and not self._external_conn:
            c.commit()
            c.close()
        elif conn:
            conn.commit()
        return deleted

    # -------------------------------------------------------------------------
    # Positions Operations
    # -------------------------------------------------------------------------

    def get_positions(self, user_id: str = "default", conn: Optional[sqlite3.Connection] = None) -> List[Position]:
        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute("SELECT * FROM positions WHERE user_id = ? ORDER BY ticker ASC", (user_id,))
        rows = cursor.fetchall()
        if not conn and not self._external_conn:
            c.close()
        return [Position.from_row(r) for r in rows]

    def get_position_by_ticker(
        self, user_id: str = "default", ticker: str = "", conn: Optional[sqlite3.Connection] = None
    ) -> Optional[Position]:
        ticker = ticker.upper().strip()
        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute("SELECT * FROM positions WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        row = cursor.fetchone()
        if not conn and not self._external_conn:
            c.close()
        if row:
            return Position.from_row(row)
        return None

    def upsert_position(
        self,
        user_id: str = "default",
        ticker: str = "",
        quantity: float = 0.0,
        avg_cost: float = 0.0,
        conn: Optional[sqlite3.Connection] = None,
    ) -> Position:
        ticker = ticker.upper().strip()
        if quantity <= 0:
            raise ValueError("Position quantity must be greater than 0")

        c = conn or self._get_connection()
        cursor = c.cursor()
        now_iso = datetime.now(timezone.utc).isoformat()

        cursor.execute("SELECT id FROM positions WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        row = cursor.fetchone()

        if row:
            pos_id = row["id"]
            cursor.execute(
                """
                UPDATE positions
                SET quantity = ?, avg_cost = ?, updated_at = ?
                WHERE id = ?
                """,
                (round(quantity, 6), round(avg_cost, 4), now_iso, pos_id),
            )
        else:
            pos_id = str(uuid.uuid4())
            cursor.execute(
                """
                INSERT INTO positions (id, user_id, ticker, quantity, avg_cost, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (pos_id, user_id, ticker, round(quantity, 6), round(avg_cost, 4), now_iso),
            )

        if not conn and not self._external_conn:
            c.commit()
            c.close()
        elif conn:
            conn.commit()

        return Position(
            id=pos_id,
            user_id=user_id,
            ticker=ticker,
            quantity=round(quantity, 6),
            avg_cost=round(avg_cost, 4),
            updated_at=now_iso,
        )

    def delete_position(
        self, user_id: str = "default", ticker: str = "", conn: Optional[sqlite3.Connection] = None
    ) -> bool:
        ticker = ticker.upper().strip()
        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute("DELETE FROM positions WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        deleted = cursor.rowcount > 0
        if not conn and not self._external_conn:
            c.commit()
            c.close()
        elif conn:
            conn.commit()
        return deleted

    # -------------------------------------------------------------------------
    # Trades & Combined Execution Operations
    # -------------------------------------------------------------------------

    def record_trade(
        self,
        user_id: str = "default",
        ticker: str = "",
        side: str = "buy",
        quantity: float = 0.0,
        price: float = 0.0,
        conn: Optional[sqlite3.Connection] = None,
    ) -> Trade:
        ticker = ticker.upper().strip()
        side = side.lower().strip()
        if side not in ("buy", "sell"):
            raise ValueError(f"Invalid trade side '{side}'. Must be 'buy' or 'sell'.")
        if quantity <= 0:
            raise ValueError("Trade quantity must be greater than 0")
        if price <= 0:
            raise ValueError("Trade price must be greater than 0")

        c = conn or self._get_connection()
        cursor = c.cursor()
        trade_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """
            INSERT INTO trades (id, user_id, ticker, side, quantity, price, executed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (trade_id, user_id, ticker, side, round(quantity, 6), round(price, 4), now_iso),
        )

        if not conn and not self._external_conn:
            c.commit()
            c.close()
        elif conn:
            conn.commit()

        return Trade(
            id=trade_id,
            user_id=user_id,
            ticker=ticker,
            side=side,
            quantity=round(quantity, 6),
            price=round(price, 4),
            executed_at=now_iso,
        )

    def execute_trade(
        self,
        user_id: str = "default",
        ticker: str = "",
        side: str = "buy",
        quantity: float = 0.0,
        price: float = 0.0,
        conn: Optional[sqlite3.Connection] = None,
    ) -> Tuple[Trade, Optional[Position], UserProfile]:
        """
        Executes a trade:
        1. Validates cash balance (for buys) or position quantity (for sells).
        2. Adjusts cash balance.
        3. Updates or removes position.
        4. Logs trade history entry.
        Returns tuple: (Trade, Position | None, UserProfile)
        """
        ticker = ticker.upper().strip()
        side = side.lower().strip()

        if side not in ("buy", "sell"):
            raise ValueError(f"Invalid trade side '{side}'. Must be 'buy' or 'sell'.")
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        if price <= 0:
            raise ValueError("Price must be greater than 0")

        c = conn or self._get_connection()
        try:
            profile = self.get_user_profile(user_id, conn=c)
            if not profile:
                raise ValueError(f"User profile '{user_id}' does not exist.")

            existing_pos = self.get_position_by_ticker(user_id, ticker, conn=c)
            trade_total = round(quantity * price, 4)

            if side == "buy":
                if profile.cash_balance < trade_total - 1e-4:
                    raise ValueError(
                        f"Insufficient cash balance. Required: ${trade_total:.2f}, Available: ${profile.cash_balance:.2f}"
                    )

                # Update position
                if existing_pos:
                    new_qty = existing_pos.quantity + quantity
                    new_avg_cost = ((existing_pos.quantity * existing_pos.avg_cost) + (quantity * price)) / new_qty
                    updated_pos = self.upsert_position(user_id, ticker, new_qty, new_avg_cost, conn=c)
                else:
                    updated_pos = self.upsert_position(user_id, ticker, quantity, price, conn=c)

                # Adjust cash
                updated_profile = self.adjust_cash_balance(user_id, -trade_total, conn=c)

            else:  # sell
                if not existing_pos or existing_pos.quantity < quantity - 1e-6:
                    avail_qty = existing_pos.quantity if existing_pos else 0.0
                    raise ValueError(
                        f"Insufficient position for {ticker}. Requested sell: {quantity}, Available: {avail_qty}"
                    )

                new_qty = existing_pos.quantity - quantity
                if new_qty <= 1e-6:
                    self.delete_position(user_id, ticker, conn=c)
                    updated_pos = None
                else:
                    updated_pos = self.upsert_position(user_id, ticker, new_qty, existing_pos.avg_cost, conn=c)

                # Adjust cash
                updated_profile = self.adjust_cash_balance(user_id, trade_total, conn=c)

            # Record trade log
            trade = self.record_trade(user_id, ticker, side, quantity, price, conn=c)

            if not conn and not self._external_conn:
                c.commit()

            return trade, updated_pos, updated_profile

        finally:
            if not conn and not self._external_conn:
                c.close()

    def get_trades(
        self, user_id: str = "default", limit: int = 100, conn: Optional[sqlite3.Connection] = None
    ) -> List[Trade]:
        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute(
            "SELECT * FROM trades WHERE user_id = ? ORDER BY executed_at DESC LIMIT ?",
            (user_id, limit),
        )
        rows = cursor.fetchall()
        if not conn and not self._external_conn:
            c.close()
        return [Trade.from_row(r) for r in rows]

    def get_trades_by_ticker(
        self, user_id: str = "default", ticker: str = "", limit: int = 100, conn: Optional[sqlite3.Connection] = None
    ) -> List[Trade]:
        ticker = ticker.upper().strip()
        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute(
            "SELECT * FROM trades WHERE user_id = ? AND ticker = ? ORDER BY executed_at DESC LIMIT ?",
            (user_id, ticker, limit),
        )
        rows = cursor.fetchall()
        if not conn and not self._external_conn:
            c.close()
        return [Trade.from_row(r) for r in rows]

    # -------------------------------------------------------------------------
    # Portfolio Snapshots Operations
    # -------------------------------------------------------------------------

    def record_portfolio_snapshot(
        self, user_id: str = "default", total_value: float = 0.0, conn: Optional[sqlite3.Connection] = None
    ) -> PortfolioSnapshot:
        c = conn or self._get_connection()
        cursor = c.cursor()
        snapshot_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        cursor.execute(
            """
            INSERT INTO portfolio_snapshots (id, user_id, total_value, recorded_at)
            VALUES (?, ?, ?, ?)
            """,
            (snapshot_id, user_id, round(total_value, 4), now_iso),
        )

        if not conn and not self._external_conn:
            c.commit()
            c.close()
        elif conn:
            conn.commit()

        return PortfolioSnapshot(
            id=snapshot_id, user_id=user_id, total_value=round(total_value, 4), recorded_at=now_iso
        )

    def get_portfolio_snapshots(
        self, user_id: str = "default", limit: int = 100, conn: Optional[sqlite3.Connection] = None
    ) -> List[PortfolioSnapshot]:
        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute(
            "SELECT * FROM portfolio_snapshots WHERE user_id = ? ORDER BY recorded_at ASC LIMIT ?",
            (user_id, limit),
        )
        rows = cursor.fetchall()
        if not conn and not self._external_conn:
            c.close()
        return [PortfolioSnapshot.from_row(r) for r in rows]

    # -------------------------------------------------------------------------
    # Chat Messages Operations
    # -------------------------------------------------------------------------

    def add_chat_message(
        self,
        user_id: str = "default",
        role: str = "user",
        content: str = "",
        actions: Optional[Union[Dict[str, Any], List[Any], str]] = None,
        conn: Optional[sqlite3.Connection] = None,
    ) -> ChatMessage:
        role = role.lower().strip()
        if role not in ("user", "assistant"):
            raise ValueError(f"Invalid role '{role}'. Must be 'user' or 'assistant'.")

        c = conn or self._get_connection()
        cursor = c.cursor()
        msg_id = str(uuid.uuid4())
        now_iso = datetime.now(timezone.utc).isoformat()

        actions_str = None
        if actions is not None:
            if isinstance(actions, str):
                actions_str = actions
            else:
                actions_str = json.dumps(actions)

        cursor.execute(
            """
            INSERT INTO chat_messages (id, user_id, role, content, actions, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (msg_id, user_id, role, content, actions_str, now_iso),
        )

        if not conn and not self._external_conn:
            c.commit()
            c.close()
        elif conn:
            conn.commit()

        parsed_actions = None
        if actions_str:
            try:
                parsed_actions = json.loads(actions_str)
            except Exception:
                parsed_actions = actions_str

        return ChatMessage(
            id=msg_id,
            user_id=user_id,
            role=role,
            content=content,
            actions=parsed_actions,
            created_at=now_iso,
        )

    def get_chat_messages(
        self, user_id: str = "default", limit: int = 50, conn: Optional[sqlite3.Connection] = None
    ) -> List[ChatMessage]:
        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute(
            "SELECT * FROM chat_messages WHERE user_id = ? ORDER BY created_at ASC LIMIT ?",
            (user_id, limit),
        )
        rows = cursor.fetchall()
        if not conn and not self._external_conn:
            c.close()
        return [ChatMessage.from_row(r) for r in rows]

    def clear_chat_messages(
        self, user_id: str = "default", conn: Optional[sqlite3.Connection] = None
    ) -> bool:
        c = conn or self._get_connection()
        cursor = c.cursor()
        cursor.execute("DELETE FROM chat_messages WHERE user_id = ?", (user_id,))
        deleted = cursor.rowcount > 0
        if not conn and not self._external_conn:
            c.commit()
            c.close()
        elif conn:
            conn.commit()
        return deleted
