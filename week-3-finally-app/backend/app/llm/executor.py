import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Callable
import sqlite3

from app.llm.models import LLMResponse, TradeAction, WatchlistAction, PortfolioContext
from app.llm.client import LLMClient


class ExecutionResult:
    """Stores execution metrics for trades and watchlist changes."""
    def __init__(self):
        self.executed_trades: List[Dict[str, Any]] = []
        self.failed_trades: List[Dict[str, Any]] = []
        self.executed_watchlist: List[Dict[str, Any]] = []
        self.failed_watchlist: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "executed_trades": self.executed_trades,
            "failed_trades": self.failed_trades,
            "executed_watchlist": self.executed_watchlist,
            "failed_watchlist": self.failed_watchlist,
        }


class ChatExecutor:
    """
    Coordinates chat flow:
    1. Calls LLM Client to generate structured LLMResponse.
    2. Validates and auto-executes requested trades & watchlist updates.
    3. Persists conversation and actions to the database (`chat_messages` table).
    """

    def __init__(self,
                 llm_client: Optional[LLMClient] = None,
                 db_connection_factory: Optional[Callable[[], sqlite3.Connection]] = None,
                 price_lookup: Optional[Callable[[str], float]] = None):
        self.llm_client = llm_client or LLMClient()
        self.db_factory = db_connection_factory
        self.price_lookup = price_lookup or (lambda ticker: 100.0)  # Default price fallback

    def execute_actions(
        self,
        response: LLMResponse,
        context: PortfolioContext,
        conn: Optional[sqlite3.Connection] = None
    ) -> ExecutionResult:
        """
        Executes trade and watchlist actions specified in response against DB/portfolio state.
        If validation fails for a trade (e.g. insufficient cash), records it in ExecutionResult.
        """
        result = ExecutionResult()

        # Build position lookup for current holdings
        positions_map = {pos.ticker: pos for pos in context.positions}
        watchlist_set = {item.ticker for item in context.watchlist}
        current_cash = context.cash_balance

        # 1. Process Trades
        for trade in response.trades:
            ticker = trade.ticker.upper()
            qty = trade.quantity
            side = trade.side.lower()
            current_price = self.price_lookup(ticker)

            if side == "buy":
                total_cost = qty * current_price
                if total_cost > current_cash:
                    err_msg = f"Insufficient cash (${current_cash:,.2f}) to buy {qty} shares of {ticker} at ${current_price:,.2f} (${total_cost:,.2f} required)"
                    result.failed_trades.append({
                        "ticker": ticker, "side": side, "quantity": qty, "price": current_price, "error": err_msg
                    })
                    continue

                # Execute buy in DB if connection available
                if conn:
                    self._db_execute_buy(conn, "default", ticker, qty, current_price)

                current_cash -= total_cost
                result.executed_trades.append({
                    "ticker": ticker, "side": side, "quantity": qty, "price": current_price, "status": "executed"
                })

            elif side == "sell":
                current_pos = positions_map.get(ticker)
                avail_qty = current_pos.quantity if current_pos else 0.0

                if qty > avail_qty:
                    err_msg = f"Insufficient shares ({avail_qty:.2f} owned) to sell {qty} shares of {ticker}"
                    result.failed_trades.append({
                        "ticker": ticker, "side": side, "quantity": qty, "price": current_price, "error": err_msg
                    })
                    continue

                # Execute sell in DB if connection available
                if conn:
                    self._db_execute_sell(conn, "default", ticker, qty, current_price)

                current_cash += qty * current_price
                result.executed_trades.append({
                    "ticker": ticker, "side": side, "quantity": qty, "price": current_price, "status": "executed"
                })

        # 2. Process Watchlist Changes
        for wl in response.watchlist_changes:
            ticker = wl.ticker.upper()
            action = wl.action.lower()

            if action == "add":
                if conn:
                    self._db_add_watchlist(conn, "default", ticker)
                result.executed_watchlist.append({"ticker": ticker, "action": "add", "status": "executed"})

            elif action == "remove":
                if conn:
                    self._db_remove_watchlist(conn, "default", ticker)
                result.executed_watchlist.append({"ticker": ticker, "action": "remove", "status": "executed"})

        # Append execution failure warnings to the LLM message text if any failed
        if result.failed_trades:
            fail_notes = "\n".join([f"⚠️ Trade Warning: {item['error']}" for item in result.failed_trades])
            response.message = f"{response.message}\n\n{fail_notes}"

        return result

    def process_chat(
        self,
        user_message: str,
        context: PortfolioContext,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Main entry point for handling user chat:
        1. Generate response from LLM
        2. Auto-execute actions
        3. Save user & assistant messages to database
        """
        # Call LLM / Mock provider
        response = self.llm_client.generate_response(user_message, context, context.history)

        conn = None
        if self.db_factory:
            conn = self.db_factory()

        try:
            # Execute actions
            exec_result = self.execute_actions(response, context, conn)

            # Persist to database if connection available
            if conn:
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
                
                # Save user message
                user_msg_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO chat_messages (id, user_id, role, content, actions, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_msg_id, user_id, "user", user_message, None, now_iso)
                )

                # Save assistant response
                asst_msg_id = str(uuid.uuid4())
                actions_json = json.dumps(exec_result.to_dict()) if (exec_result.executed_trades or exec_result.executed_watchlist or exec_result.failed_trades) else None
                conn.execute(
                    "INSERT INTO chat_messages (id, user_id, role, content, actions, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (asst_msg_id, user_id, "assistant", response.message, actions_json, now_iso)
                )
                conn.commit()

            return {
                "message": response.message,
                "trades": response.trades,
                "watchlist_changes": response.watchlist_changes,
                "execution_result": exec_result.to_dict()
            }
        finally:
            if conn:
                conn.close()

    # --- DB Helper Methods ---
    def _db_execute_buy(self, conn: sqlite3.Connection, user_id: str, ticker: str, qty: float, price: float):
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        total_cost = qty * price

        # Deduct cash
        conn.execute("UPDATE users_profile SET cash_balance = cash_balance - ? WHERE id = ?", (total_cost, user_id))

        # Check existing position
        cursor = conn.execute("SELECT quantity, avg_cost FROM positions WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        row = cursor.fetchone()

        if row:
            old_qty, old_avg = row[0], row[1]
            new_qty = old_qty + qty
            new_avg = ((old_qty * old_avg) + (qty * price)) / new_qty
            conn.execute(
                "UPDATE positions SET quantity = ?, avg_cost = ?, updated_at = ? WHERE user_id = ? AND ticker = ?",
                (new_qty, new_avg, now_iso, user_id, ticker)
            )
        else:
            conn.execute(
                "INSERT INTO positions (id, user_id, ticker, quantity, avg_cost, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (str(uuid.uuid4()), user_id, ticker, qty, price, now_iso)
            )

        # Log trade
        conn.execute(
            "INSERT INTO trades (id, user_id, ticker, side, quantity, price, executed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, ticker, "buy", qty, price, now_iso)
        )

    def _db_execute_sell(self, conn: sqlite3.Connection, user_id: str, ticker: str, qty: float, price: float):
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        total_proceeds = qty * price

        # Add cash
        conn.execute("UPDATE users_profile SET cash_balance = cash_balance + ? WHERE id = ?", (total_proceeds, user_id))

        cursor = conn.execute("SELECT quantity, avg_cost FROM positions WHERE user_id = ? AND ticker = ?", (user_id, ticker))
        row = cursor.fetchone()

        if row:
            old_qty, old_avg = row[0], row[1]
            new_qty = old_qty - qty
            if new_qty <= 1e-6:
                conn.execute("DELETE FROM positions WHERE user_id = ? AND ticker = ?", (user_id, ticker))
            else:
                conn.execute(
                    "UPDATE positions SET quantity = ?, updated_at = ? WHERE user_id = ? AND ticker = ?",
                    (new_qty, now_iso, user_id, ticker)
                )

        # Log trade
        conn.execute(
            "INSERT INTO trades (id, user_id, ticker, side, quantity, price, executed_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, ticker, "sell", qty, price, now_iso)
        )

    def _db_add_watchlist(self, conn: sqlite3.Connection, user_id: str, ticker: str):
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        conn.execute(
            "INSERT OR IGNORE INTO watchlist (id, user_id, ticker, added_at) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, ticker, now_iso)
        )

    def _db_remove_watchlist(self, conn: sqlite3.Connection, user_id: str, ticker: str):
        conn.execute("DELETE FROM watchlist WHERE user_id = ? AND ticker = ?", (user_id, ticker))
