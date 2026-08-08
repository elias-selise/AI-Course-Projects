import re
from typing import Optional
from app.llm.models import LLMResponse, TradeAction, WatchlistAction, PortfolioContext


class MockLLMProvider:
    """
    Deterministic mock provider for LLM integration.
    Used when LLM_MOCK=true for fast, free, predictable offline testing and Playwright E2E suites.
    """

    def generate_response(self, user_message: str, context: Optional[PortfolioContext] = None) -> LLMResponse:
        """
        Generates a deterministic LLMResponse based on keywords in the user's message.
        """
        msg_lower = user_message.lower()

        # 1. Check for trade commands: e.g. "buy 10 AAPL", "sell 5 MSFT", "buy 5 shares of MSFT"
        buy_match = re.search(r"buy\s+(\d+(?:\.\d+)?)\s+(?:shares?\s+(?:of\s+)?)?([a-zA-Z]{1,5})\b", user_message, re.IGNORECASE)
        if buy_match:
            qty = float(buy_match.group(1))
            ticker = buy_match.group(2).upper()
            if ticker not in ("SHARES", "SHARE", "THE", "FOR", "OF", "MY", "ME"):
                return LLMResponse(
                    message=f"I have placed an order to buy {qty} shares of {ticker}.",
                    trades=[TradeAction(ticker=ticker, side="buy", quantity=qty)],
                    watchlist_changes=[]
                )

        sell_match = re.search(r"sell\s+(\d+(?:\.\d+)?)\s+(?:shares?\s+(?:of\s+)?)?([a-zA-Z]{1,5})\b", user_message, re.IGNORECASE)
        if sell_match:
            qty = float(sell_match.group(1))
            ticker = sell_match.group(2).upper()
            if ticker not in ("SHARES", "SHARE", "THE", "FOR", "OF", "MY", "ME"):
                return LLMResponse(
                    message=f"I have placed an order to sell {qty} shares of {ticker}.",
                    trades=[TradeAction(ticker=ticker, side="sell", quantity=qty)],
                    watchlist_changes=[]
                )

        # Simple buy/sell without quantity (default quantity 10 or 5)
        simple_buy = re.search(r"buy\s+([a-zA-Z]{1,5})\b", user_message, re.IGNORECASE)
        if simple_buy and simple_buy.group(1).lower() not in ("some", "shares", "share", "a", "the", "for", "of", "my", "me"):
            ticker = simple_buy.group(1).upper()
            return LLMResponse(
                message=f"Executing order to buy 10 shares of {ticker}.",
                trades=[TradeAction(ticker=ticker, side="buy", quantity=10.0)],
                watchlist_changes=[]
            )

        simple_sell = re.search(r"sell\s+([a-zA-Z]{1,5})\b", user_message, re.IGNORECASE)
        if simple_sell and simple_sell.group(1).lower() not in ("some", "shares", "share", "a", "the", "for", "of", "my", "me"):
            ticker = simple_sell.group(1).upper()
            return LLMResponse(
                message=f"Executing order to sell 5 shares of {ticker}.",
                trades=[TradeAction(ticker=ticker, side="sell", quantity=5.0)],
                watchlist_changes=[]
            )

        # 2. Check for watchlist commands: "add PYPL", "watch PYPL", "remove TSLA", "unwatch TSLA"
        add_match = re.search(r"(?:add|watch)\s+([a-zA-Z]{1,5})\b", user_message, re.IGNORECASE)
        if add_match and add_match.group(1).lower() not in ("to", "watchlist", "the", "a"):
            ticker = add_match.group(1).upper()
            return LLMResponse(
                message=f"Added {ticker} to your watchlist.",
                trades=[],
                watchlist_changes=[WatchlistAction(ticker=ticker, action="add")]
            )

        rem_match = re.search(r"(?:remove|unwatch|delete)\s+([a-zA-Z]{1,5})\b", user_message, re.IGNORECASE)
        if rem_match and rem_match.group(1).lower() not in ("from", "watchlist", "the", "a"):
            ticker = rem_match.group(1).upper()
            return LLMResponse(
                message=f"Removed {ticker} from your watchlist.",
                trades=[],
                watchlist_changes=[WatchlistAction(ticker=ticker, action="remove")]
            )

        # 3. Default portfolio analysis response
        cash = context.cash_balance if context else 10000.0
        val = context.total_value if context else 10000.0
        pos_count = len(context.positions) if context else 0
        return LLMResponse(
            message=(
                f"Your portfolio currently has a total value of ${val:,.2f} with ${cash:,.2f} in cash "
                f"and {pos_count} active position(s). How can I assist you with your trades today?"
            ),
            trades=[],
            watchlist_changes=[]
        )
