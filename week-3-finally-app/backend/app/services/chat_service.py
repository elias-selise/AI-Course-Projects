import json
import logging
import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import aiosqlite

from app.schemas.chat import (
    ChatResponse,
    ChatMessageResponse,
    LLMResponseSchema,
    ExecutedTradeResult,
    ExecutedWatchlistResult,
    TradeAction,
    WatchlistAction
)
from app.schemas.portfolio import TradeRequest, WatchlistItemResponse
from app.services.llm_provider import BaseLLMProvider
from app.services.prompt_builder import build_system_prompt
from app.services.portfolio_service import calculate_portfolio, execute_trade
from app.market.cache import PriceCache

logger = logging.getLogger("finally.chat")


def parse_llm_response(raw_text: str) -> LLMResponseSchema:
    """Parse raw LLM completion string into structured LLMResponseSchema, handling markdown code fences."""
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        data = json.loads(cleaned)
        return LLMResponseSchema(**data)
    except Exception as e:
        logger.warning(f"Failed to parse LLM JSON response: {e}. Raw text: {raw_text[:100]}...")
        return LLMResponseSchema(message=raw_text, trades=[], watchlist_changes=[])


async def process_chat_message(
    db: aiosqlite.Connection,
    cache: PriceCache,
    provider: BaseLLMProvider,
    user_message: str,
    market_source: Any = None,
    user_id: str = "default"
) -> ChatResponse:
    """Process incoming user chat message, call LLM provider, auto-execute actions, and persist chat log."""
    now_iso = datetime.now(timezone.utc).isoformat()
    user_msg_id = str(uuid.uuid4())

    # 1. Store user message in chat_messages table
    await db.execute(
        "INSERT INTO chat_messages (id, user_id, role, content, created_at) VALUES (?, ?, 'user', ?, ?)",
        (user_msg_id, user_id, user_message, now_iso)
    )
    await db.commit()

    # 2. Fetch recent chat history (last 10 messages)
    history_messages = []
    async with db.execute(
        "SELECT role, content FROM chat_messages WHERE user_id = ? ORDER BY created_at ASC LIMIT 10",
        (user_id,)
    ) as cursor:
        async for role, content in cursor:
            history_messages.append({"role": role, "content": content})

    # 3. Fetch portfolio state and watchlist items
    portfolio = await calculate_portfolio(db, cache, user_id)
    
    watchlist_items: List[WatchlistItemResponse] = []
    async with db.execute("SELECT id, ticker, added_at FROM watchlist WHERE user_id = ?", (user_id,)) as cursor:
        async for item_id, ticker, added_at in cursor:
            price_up = cache.get(ticker) if cache else None
            price = price_up.price if price_up else 0.0
            prev = price_up.previous_price if price_up else 0.0
            change = price_up.change if price_up else 0.0
            direction = price_up.direction if price_up else "flat"
            watchlist_items.append(
                WatchlistItemResponse(
                    id=item_id,
                    ticker=ticker,
                    price=price,
                    previous_price=prev,
                    change=change,
                    direction=direction,
                    added_at=added_at
                )
            )

    # 4. Build system prompt & prepare messages
    system_prompt = build_system_prompt(portfolio, watchlist_items, cache)
    messages = [{"role": "system", "content": system_prompt}] + history_messages

    # 5. Generate completion from provider
    raw_completion = await provider.generate_response(messages)
    llm_schema = parse_llm_response(raw_completion)

    # 6. Auto-execute trades
    executed_trades: List[ExecutedTradeResult] = []
    for trade_act in llm_schema.trades:
        try:
            trade_req = TradeRequest(
                ticker=trade_act.ticker,
                side=trade_act.side,
                quantity=trade_act.quantity
            )
            res = await execute_trade(db, cache, trade_req, user_id)
            executed_trades.append(
                ExecutedTradeResult(
                    trade_id=res.trade_id,
                    ticker=res.ticker,
                    side=res.side,
                    quantity=res.quantity,
                    price=res.price,
                    total_value=res.total_value,
                    status="success"
                )
            )
        except Exception as e:
            logger.error(f"Auto-execution failed for trade {trade_act}: {e}")
            executed_trades.append(
                ExecutedTradeResult(
                    ticker=trade_act.ticker,
                    side=trade_act.side,
                    quantity=trade_act.quantity,
                    status="failed",
                    error=str(e)
                )
            )

    # 7. Auto-execute watchlist changes
    executed_watchlist: List[ExecutedWatchlistResult] = []
    for watch_act in llm_schema.watchlist_changes:
        ticker = watch_act.ticker.upper()
        try:
            if watch_act.action == "add":
                async with db.execute(
                    "SELECT id FROM watchlist WHERE user_id = ? AND ticker = ?", (user_id, ticker)
                ) as cursor:
                    if not await cursor.fetchone():
                        item_id = str(uuid.uuid4())
                        await db.execute(
                            "INSERT INTO watchlist (id, user_id, ticker, added_at) VALUES (?, ?, ?, ?)",
                            (item_id, user_id, ticker, now_iso)
                        )
                        if market_source and hasattr(market_source, "add_ticker"):
                            market_source.add_ticker(ticker)
                executed_watchlist.append(ExecutedWatchlistResult(ticker=ticker, action="add", status="success"))
            else:  # remove
                await db.execute(
                    "DELETE FROM watchlist WHERE user_id = ? AND ticker = ?", (user_id, ticker)
                )
                if market_source and hasattr(market_source, "remove_ticker"):
                    market_source.remove_ticker(ticker)
                executed_watchlist.append(ExecutedWatchlistResult(ticker=ticker, action="remove", status="success"))
        except Exception as e:
            logger.error(f"Auto-execution failed for watchlist change {watch_act}: {e}")
            executed_watchlist.append(ExecutedWatchlistResult(ticker=ticker, action=watch_act.action, status="failed", error=str(e)))

    await db.commit()

    # 8. Store assistant message in chat_messages table
    assistant_msg_id = str(uuid.uuid4())
    actions_json = json.dumps({
        "trades": [t.model_dump() for t in executed_trades],
        "watchlist_changes": [w.model_dump() for w in executed_watchlist]
    })

    await db.execute(
        "INSERT INTO chat_messages (id, user_id, role, content, actions, created_at) VALUES (?, ?, 'assistant', ?, ?, ?)",
        (assistant_msg_id, user_id, llm_schema.message, actions_json, now_iso)
    )
    await db.commit()

    return ChatResponse(
        message_id=assistant_msg_id,
        user_message=user_message,
        assistant_message=llm_schema.message,
        executed_trades=executed_trades,
        executed_watchlist_changes=executed_watchlist,
        created_at=now_iso
    )
