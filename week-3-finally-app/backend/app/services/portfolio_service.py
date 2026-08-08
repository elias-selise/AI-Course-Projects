import uuid
from datetime import datetime, timezone
from typing import List
import aiosqlite

from app.market.cache import PriceCache
from app.schemas.portfolio import PositionItem, PortfolioResponse, TradeRequest, TradeResponse
from app.services.snapshot_service import record_snapshot


async def calculate_portfolio(
    db: aiosqlite.Connection,
    cache: PriceCache,
    user_id: str = "default"
) -> PortfolioResponse:
    """Calculate cash balance, position valuation, total portfolio value, and unrealized P&L."""
    async with db.execute("SELECT cash_balance FROM users_profile WHERE id = ?", (user_id,)) as cursor:
        row = await cursor.fetchone()
        cash_balance = row[0] if row else 10000.0

    positions: List[PositionItem] = []
    positions_value = 0.0
    total_cost_basis = 0.0

    async with db.execute(
        "SELECT ticker, quantity, avg_cost FROM positions WHERE user_id = ? AND quantity > 0",
        (user_id,)
    ) as cursor:
        rows = await cursor.fetchall()
        for ticker, qty, avg_cost in rows:
            price_update = cache.get(ticker) if cache else None
            current_price = price_update.price if price_update else avg_cost

            market_val = round(qty * current_price, 2)
            cost_basis = round(qty * avg_cost, 2)
            pnl = round(market_val - cost_basis, 2)
            pnl_pct = round((pnl / cost_basis * 100.0), 2) if cost_basis > 0 else 0.0

            positions_value += market_val
            total_cost_basis += cost_basis

            positions.append(
                PositionItem(
                    ticker=ticker,
                    quantity=qty,
                    avg_cost=avg_cost,
                    current_price=current_price,
                    market_value=market_val,
                    unrealized_pnl=pnl,
                    unrealized_pnl_percent=pnl_pct
                )
            )

    positions_value = round(positions_value, 2)
    total_value = round(cash_balance + positions_value, 2)
    total_pnl = round(positions_value - total_cost_basis, 2)
    total_pnl_pct = round((total_pnl / total_cost_basis * 100.0), 2) if total_cost_basis > 0 else 0.0

    return PortfolioResponse(
        cash_balance=cash_balance,
        positions_value=positions_value,
        total_value=total_value,
        total_unrealized_pnl=total_pnl,
        total_unrealized_pnl_percent=total_pnl_pct,
        positions=positions
    )


async def execute_trade(
    db: aiosqlite.Connection,
    cache: PriceCache,
    trade_req: TradeRequest,
    user_id: str = "default"
) -> TradeResponse:
    """Execute market buy/sell order with atomic transaction, cost basis tracking, and snapshot trigger."""
    ticker = trade_req.ticker
    side = trade_req.side
    qty = trade_req.quantity

    price_update = cache.get(ticker) if cache else None
    if not price_update or price_update.price <= 0:
        raise ValueError(f"Market price unavailable for ticker: {ticker}")

    price = price_update.price
    trade_cost = round(qty * price, 2)
    now_iso = datetime.now(timezone.utc).isoformat()
    trade_id = str(uuid.uuid4())

    async with db.execute("SELECT cash_balance FROM users_profile WHERE id = ?", (user_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise ValueError(f"User profile '{user_id}' not found.")
        current_cash = row[0]

    async with db.execute(
        "SELECT quantity, avg_cost FROM positions WHERE user_id = ? AND ticker = ?",
        (user_id, ticker)
    ) as cursor:
        pos_row = await cursor.fetchone()
        existing_qty = pos_row[0] if pos_row else 0.0
        existing_avg_cost = pos_row[1] if pos_row else 0.0

    if side == "buy":
        if current_cash < trade_cost:
            raise ValueError(
                f"Insufficient funds: Trade requires ${trade_cost:.2f}, but cash balance is ${current_cash:.2f}"
            )
        new_cash = round(current_cash - trade_cost, 2)
        new_qty = round(existing_qty + qty, 4)
        new_avg_cost = round(
            ((existing_qty * existing_avg_cost) + (qty * price)) / new_qty, 2
        )
    else:  # sell
        if existing_qty < qty:
            raise ValueError(
                f"Insufficient position: Cannot sell {qty} shares of {ticker}. Holding: {existing_qty}"
            )
        new_cash = round(current_cash + trade_cost, 2)
        new_qty = round(existing_qty - qty, 4)
        new_avg_cost = existing_avg_cost if new_qty > 0 else 0.0

    await db.execute(
        "UPDATE users_profile SET cash_balance = ? WHERE id = ?",
        (new_cash, user_id)
    )

    pos_id = str(uuid.uuid4())
    await db.execute(
        """
        INSERT INTO positions (id, user_id, ticker, quantity, avg_cost, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, ticker) DO UPDATE SET
            quantity = excluded.quantity,
            avg_cost = excluded.avg_cost,
            updated_at = excluded.updated_at
        """,
        (pos_id, user_id, ticker, new_qty, new_avg_cost, now_iso)
    )

    await db.execute(
        """
        INSERT INTO trades (id, user_id, ticker, side, quantity, price, executed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (trade_id, user_id, ticker, side, qty, price, now_iso)
    )

    await record_snapshot(db, cache, user_id)
    await db.commit()

    return TradeResponse(
        trade_id=trade_id,
        ticker=ticker,
        side=side,
        quantity=qty,
        price=price,
        total_value=trade_cost,
        cash_balance=new_cash,
        executed_at=now_iso
    )
