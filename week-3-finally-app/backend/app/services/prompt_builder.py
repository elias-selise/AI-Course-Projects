from typing import List
from app.schemas.portfolio import PortfolioResponse, WatchlistItemResponse
from app.market.cache import PriceCache


def build_system_prompt(
    portfolio: PortfolioResponse,
    watchlist: List[WatchlistItemResponse],
    cache: PriceCache
) -> str:
    """Construct real-time system prompt with live portfolio, position, and pricing context."""
    
    positions_str = ""
    if portfolio.positions:
        for p in portfolio.positions:
            positions_str += f"  - {p.ticker}: {p.quantity} shares @ ${p.avg_cost:.2f} avg cost | Current: ${p.current_price:.2f} | Market Val: ${p.market_value:.2f} | Unrealized PnL: ${p.unrealized_pnl:.2f} ({p.unrealized_pnl_percent:.2f}%)\n"
    else:
        positions_str = "  (No current open positions)\n"

    watchlist_str = ""
    if watchlist:
        for w in watchlist:
            watchlist_str += f"  - {w.ticker}: ${w.price:.2f} (change: {w.change:+.2f})\n"
    else:
        watchlist_str = "  (Watchlist is empty)\n"

    all_prices = cache.get_all()
    cached_prices_str = ", ".join([f"{ticker}: ${update.price:.2f}" for ticker, update in all_prices.items()])

    prompt = f"""You are FinAlly, an elite AI Trading Assistant and Copilot integrated into a high-performance trading workstation.
Your task is to analyze user requests, provide concise financial analysis, and output structured trade or watchlist execution commands.

=== CURRENT PORTFOLIO & WORKSTATION STATE ===
• Cash Balance: ${portfolio.cash_balance:,.2f}
• Total Positions Value: ${portfolio.positions_value:,.2f}
• Total Portfolio Value: ${portfolio.total_value:,.2f}
• Total Unrealized P&L: ${portfolio.total_unrealized_pnl:,.2f} ({portfolio.total_unrealized_pnl_percent:+.2f}%)

• Open Positions:
{positions_str}
• Active Watchlist:
{watchlist_str}
• Live Asset Prices in Stream Cache:
  {cached_prices_str if cached_prices_str else "No active price ticks"}

=== INSTRUCTIONS & AGENTIC EXECUTION RULES ===
1. Analyze the user prompt in the context of the portfolio state above.
2. You CAN execute market trades (`buy` or `sell`) and modify the user's `watchlist` (`add` or `remove`).
3. You MUST ALWAYS respond ONLY with a valid JSON object matching the schema below. Do not wrap JSON in markdown block fences or commentary.

=== REQUIRED JSON OUTPUT SCHEMA ===
{{
  "message": "Concise natural language explanation of your response, recommendations, or actions taken.",
  "trades": [
    {{
      "ticker": "AAPL",
      "side": "buy",
      "quantity": 10.0
    }}
  ],
  "watchlist_changes": [
    {{
      "action": "add",
      "ticker": "NVDA"
    }}
  ]
}}

If no trades or watchlist changes are requested by the user, return empty arrays `[]` for "trades" and "watchlist_changes".
Ensure all tickers are uppercase. All trades execute as immediate market orders at current live prices.
"""
    return prompt
