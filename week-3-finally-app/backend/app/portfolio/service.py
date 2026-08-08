from typing import Dict, Any, List, Optional
from app.db.database import (
    get_user_profile,
    update_cash_balance,
    get_positions,
    get_position,
    upsert_position,
    delete_position,
    record_trade,
    record_snapshot,
    get_snapshots,
)
from app.market.cache import PriceCache
from app.market.seed_prices import SEED_PRICES


def get_portfolio_summary(user_id: str = "default", price_cache: Optional[PriceCache] = None, db_path=None) -> Dict[str, Any]:
    profile = get_user_profile(user_id, db_path=db_path)
    cash_balance = profile.get("cash_balance", 10000.0)

    db_positions = get_positions(user_id, db_path=db_path)
    position_items = []
    total_positions_val = 0.0
    total_pnl = 0.0

    for pos in db_positions:
        ticker = pos["ticker"]
        qty = float(pos["quantity"])
        cost = float(pos["avg_cost"])

        cp = None
        if price_cache:
            cp = price_cache.get_price(ticker)
        if cp is None or cp <= 0:
            cp = SEED_PRICES.get(ticker, cost)

        mkt_val = round(qty * cp, 2)
        pnl = round((cp - cost) * qty, 2)
        pnl_pct = round(((cp - cost) / cost) * 100, 2) if cost > 0 else 0.0

        total_positions_val += mkt_val
        total_pnl += pnl

        position_items.append({
            "ticker": ticker,
            "quantity": qty,
            "avg_cost": cost,
            "current_price": cp,
            "market_value": mkt_val,
            "unrealized_pnl": pnl,
            "unrealized_pnl_percent": pnl_pct,
        })

    total_portfolio_val = round(cash_balance + total_positions_val, 2)

    return {
        "cash_balance": round(cash_balance, 2),
        "positions": position_items,
        "total_positions_value": round(total_positions_val, 2),
        "total_portfolio_value": total_portfolio_val,
        "total_value": total_portfolio_val,
        "total_unrealized_pnl": round(total_pnl, 2),
        "unrealized_pnl": round(total_pnl, 2),
        "unrealized_pnl_pct": round(((total_pnl / (total_portfolio_val - total_pnl)) * 100) if (total_portfolio_val - total_pnl) > 0 else 0.0, 2),
    }


def execute_trade_action(
    ticker: str,
    quantity: float,
    side: str,
    user_id: str = "default",
    price_cache: Optional[PriceCache] = None,
    db_path=None,
) -> Dict[str, Any]:
    ticker_clean = ticker.strip().upper()
    side_clean = side.strip().lower()

    if quantity <= 0:
        raise ValueError("Quantity must be greater than zero.")
    if side_clean not in ("buy", "sell"):
        raise ValueError("Side must be 'buy' or 'sell'.")

    # Retrieve current price
    exec_price = None
    if price_cache:
        exec_price = price_cache.get_price(ticker_clean)
    if exec_price is None or exec_price <= 0:
        exec_price = SEED_PRICES.get(ticker_clean, 100.0)

    profile = get_user_profile(user_id, db_path=db_path)
    cash = float(profile["cash_balance"])

    if side_clean == "buy":
        total_cost = quantity * exec_price
        if cash < total_cost - 1e-6:
            raise ValueError(f"Insufficient cash balance (${cash:.2f}) for buy order of ${total_cost:.2f}.")
        
        new_cash = cash - total_cost
        existing_pos = get_position(ticker_clean, user_id, db_path=db_path)

        if existing_pos:
            old_q = float(existing_pos["quantity"])
            old_cost = float(existing_pos["avg_cost"])
            new_q = old_q + quantity
            new_avg_cost = ((old_q * old_cost) + total_cost) / new_q
        else:
            new_q = quantity
            new_avg_cost = exec_price

        update_cash_balance(new_cash, user_id, db_path=db_path)
        upsert_position(ticker_clean, new_q, round(new_avg_cost, 4), user_id, db_path=db_path)

    else:  # sell
        existing_pos = get_position(ticker_clean, user_id, db_path=db_path)
        if not existing_pos or float(existing_pos["quantity"]) < quantity - 1e-6:
            owned = float(existing_pos["quantity"]) if existing_pos else 0.0
            raise ValueError(f"Insufficient shares owned ({owned}) for sell order of {quantity} {ticker_clean}.")

        proceeds = quantity * exec_price
        new_cash = cash + proceeds
        old_q = float(existing_pos["quantity"])
        new_q = old_q - quantity

        if new_q <= 1e-6:
            delete_position(ticker_clean, user_id, db_path=db_path)
        else:
            upsert_position(ticker_clean, new_q, float(existing_pos["avg_cost"]), user_id, db_path=db_path)

        update_cash_balance(new_cash, user_id, db_path=db_path)

    # Log trade record
    trade_rec = record_trade(ticker_clean, side_clean, quantity, exec_price, user_id, db_path=db_path)

    # Record snapshot immediately after trade
    summary = get_portfolio_summary(user_id, price_cache, db_path=db_path)
    record_snapshot(summary["total_portfolio_value"], user_id, db_path=db_path)

    return {
        "success": True,
        "trade": trade_rec,
        "cash_balance": summary["cash_balance"],
        "message": f"Successfully executed {side_clean.upper()} {quantity} shares of {ticker_clean} at ${exec_price:.2f}.",
    }


def get_portfolio_history_records(user_id: str = "default", db_path=None) -> List[Dict[str, Any]]:
    return get_snapshots(user_id, db_path=db_path)
