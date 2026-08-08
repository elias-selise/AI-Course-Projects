import json
import re
from typing import Dict, Any, List, Optional
from app.config import OPENROUTER_API_KEY, LLM_MOCK
from app.db.database import record_chat_message, get_chat_messages
from app.portfolio.service import get_portfolio_summary, execute_trade_action
from app.watchlist.service import get_watchlist_items, add_watchlist_item, remove_watchlist_item
from app.market.cache import PriceCache
from app.market.interface import MarketDataSource


SYSTEM_PROMPT = """You are FinAlly, an AI trading assistant.
You analyze portfolio composition, risk concentration, and P&L.
You suggest trades with reasoning, execute trades when asked or agreed, and manage the watchlist.
Be concise and data-driven.

You MUST respond with valid JSON strictly conforming to this schema:
{
  "message": "Conversational response to the user",
  "trades": [
    {"ticker": "AAPL", "side": "buy", "quantity": 10}
  ],
  "watchlist_changes": [
    {"ticker": "PYPL", "action": "add"}
  ]
}
If no trades or watchlist changes are needed, set them to empty arrays [].
"""


def _generate_mock_llm_response(user_msg: str, portfolio_context: Dict[str, Any]) -> Dict[str, Any]:
    text_lower = user_msg.lower()
    trades = []
    watchlist_changes = []

    # Simple intent parsing for mock testing
    # Check trade intent - handles both "buy 5 MSFT" and "buy 5 shares of MSFT"
    buy_match = re.search(r"buy\s+(\d+(?:\.\d+)?)\s+(?:shares?\s+(?:of\s+)?)?([a-zA-Z]{1,5})\b", text_lower)
    sell_match = re.search(r"sell\s+(\d+(?:\.\d+)?)\s+(?:shares?\s+(?:of\s+)?)?([a-zA-Z]{1,5})\b", text_lower)

    if buy_match:
        qty = float(buy_match.group(1))
        ticker = buy_match.group(2).upper()
        if ticker not in ("SHARES", "SHARE", "THE", "FOR", "OF", "MY", "ME"):
            trades.append({"ticker": ticker, "side": "buy", "quantity": qty})
    if sell_match and not trades:
        qty = float(sell_match.group(1))
        ticker = sell_match.group(2).upper()
        if ticker not in ("SHARES", "SHARE", "THE", "FOR", "OF", "MY", "ME"):
            trades.append({"ticker": ticker, "side": "sell", "quantity": qty})

    # Check watchlist intent
    add_match = re.search(r"(?:add|watch)\s+([a-zA-Z]+)", text_lower)
    rem_match = re.search(r"(?:remove|delete)\s+([a-zA-Z]+)", text_lower)

    if add_match and not buy_match and not sell_match:
        ticker = add_match.group(1).upper()
        if ticker not in ("MY", "THE", "TO", "A", "THIS"):
            watchlist_changes.append({"ticker": ticker, "action": "add"})
    elif rem_match and not buy_match and not sell_match:
        ticker = rem_match.group(1).upper()
        if ticker not in ("MY", "THE", "FROM", "A", "THIS"):
            watchlist_changes.append({"ticker": ticker, "action": "remove"})

    cash = portfolio_context.get("cash_balance", 10000.0)
    total_val = portfolio_context.get("total_portfolio_value", 10000.0)
    pnl = portfolio_context.get("total_unrealized_pnl", 0.0)

    if trades:
        msg = f"I'm processing your trade order. Portfolio value is ${total_val:,.2f} with cash balance ${cash:,.2f}."
    elif watchlist_changes:
        msg = f"Updating your watchlist as requested. Total portfolio value: ${total_val:,.2f}."
    else:
        msg = (
            f"Hello! I am FinAlly, your AI Trading Workstation copilot. "
            f"Your current portfolio value is ${total_val:,.2f} (Cash: ${cash:,.2f}, Unrealized P&L: ${pnl:+,.2f}). "
            f"How can I assist your trading today?"
        )

    return {
        "message": msg,
        "trades": trades,
        "watchlist_changes": watchlist_changes,
    }


async def process_chat_message(
    user_message: str,
    user_id: str = "default",
    price_cache: Optional[PriceCache] = None,
    market_source: Optional[MarketDataSource] = None,
    db_path=None,
) -> Dict[str, Any]:
    # Record user message
    record_chat_message("user", user_message, user_id=user_id, db_path=db_path)

    # Get current context
    portfolio_ctx = get_portfolio_summary(user_id, price_cache, db_path=db_path)
    watchlist_items = get_watchlist_items(user_id, price_cache, db_path=db_path)

    parsed_response = None

    if LLM_MOCK or not OPENROUTER_API_KEY or not OPENROUTER_API_KEY.strip():
        parsed_response = _generate_mock_llm_response(user_message, portfolio_ctx)
    else:
        try:
            import litellm
            context_str = json.dumps({
                "portfolio": portfolio_ctx,
                "watchlist": [w["ticker"] for w in watchlist_items],
            })
            messages = [
                {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nCurrent State: {context_str}"},
                {"role": "user", "content": user_message},
            ]
            response = await asyncio.to_thread(
                litellm.completion,
                model="openrouter/openai/gpt-oss-120b",
                messages=messages,
                response_format={"type": "json_object"},
                api_key=OPENROUTER_API_KEY,
            )
            raw_text = response.choices[0].message.content
            parsed_response = json.loads(raw_text)
        except Exception:
            # Fallback if LiteLLM call fails
            parsed_response = _generate_mock_llm_response(user_message, portfolio_ctx)

    assistant_msg = parsed_response.get("message", "Request processed.")
    raw_trades = parsed_response.get("trades", [])
    raw_watchlist = parsed_response.get("watchlist_changes", [])

    executed_trades = []
    for t in raw_trades:
        try:
            res = execute_trade_action(
                ticker=t["ticker"],
                quantity=float(t["quantity"]),
                side=t["side"],
                user_id=user_id,
                price_cache=price_cache,
                db_path=db_path,
            )
            # Flatten to {ticker, side, quantity, price} for frontend trade-confirmation badges
            trade_rec = res.get("trade", {})
            executed_trades.append({
                "ticker": trade_rec.get("ticker", t["ticker"]),
                "side": trade_rec.get("side", t["side"]),
                "quantity": trade_rec.get("quantity", t["quantity"]),
                "price": trade_rec.get("price", 0),
                "success": True,
            })
        except Exception as e:
            executed_trades.append({
                "success": False,
                "ticker": t.get("ticker"),
                "side": t.get("side", "buy"),
                "quantity": t.get("quantity", 0),
                "error": str(e),
            })

    watchlist_executed = []
    for w in raw_watchlist:
        act = w.get("action", "").lower()
        t_symbol = w.get("ticker", "")
        if act == "add":
            item = await add_watchlist_item(t_symbol, user_id, price_cache, market_source, db_path=db_path)
            watchlist_executed.append({"action": "add", "item": item})
        elif act == "remove":
            ok = await remove_watchlist_item(t_symbol, user_id, market_source, db_path=db_path)
            watchlist_executed.append({"action": "remove", "ticker": t_symbol, "success": ok})

    actions_json = json.dumps({
        "trades": executed_trades,
        "watchlist_changes": watchlist_executed,
    })

    saved_msg = record_chat_message("assistant", assistant_msg, actions=actions_json, user_id=user_id, db_path=db_path)

    return {
        "message": assistant_msg,
        "trades": executed_trades,
        "trades_executed": executed_trades,
        "watchlist_changes": watchlist_executed,
        "chat_message_id": saved_msg["id"],
    }
