from typing import List, Dict, Any, Optional
from app.db.database import (
    get_watchlist,
    add_watchlist_ticker,
    remove_watchlist_ticker,
    get_position,
)
from app.market.cache import PriceCache
from app.market.interface import MarketDataSource


def get_watchlist_items(
    user_id: str = "default",
    price_cache: Optional[PriceCache] = None,
    db_path=None,
) -> List[Dict[str, Any]]:
    db_items = get_watchlist(user_id, db_path=db_path)
    result = []
    for item in db_items:
        ticker = item["ticker"]
        update_obj = price_cache.get(ticker) if price_cache else None
        curr_price = update_obj.price if update_obj else None
        
        result.append({
            "id": item["id"],
            "ticker": ticker,
            "added_at": item["added_at"],
            "current_price": curr_price,
            "price_update": update_obj.to_dict() if update_obj else None,
        })
    return result


async def add_watchlist_item(
    ticker: str,
    user_id: str = "default",
    price_cache: Optional[PriceCache] = None,
    market_source: Optional[MarketDataSource] = None,
    db_path=None,
) -> Dict[str, Any]:
    item = add_watchlist_ticker(ticker, user_id, db_path=db_path)
    ticker_clean = item["ticker"]

    if market_source:
        await market_source.add_ticker(ticker_clean)

    update_obj = price_cache.get(ticker_clean) if price_cache else None
    curr_price = update_obj.price if update_obj else None

    return {
        "id": item["id"],
        "ticker": ticker_clean,
        "added_at": item["added_at"],
        "current_price": curr_price,
        "price_update": update_obj.to_dict() if update_obj else None,
    }


async def remove_watchlist_item(
    ticker: str,
    user_id: str = "default",
    market_source: Optional[MarketDataSource] = None,
    db_path=None,
) -> bool:
    ticker_clean = ticker.strip().upper()
    removed = remove_watchlist_ticker(ticker_clean, user_id, db_path=db_path)

    if removed and market_source:
        pos = get_position(ticker_clean, user_id, db_path=db_path)
        if not pos:
            await market_source.remove_ticker(ticker_clean)

    return removed
