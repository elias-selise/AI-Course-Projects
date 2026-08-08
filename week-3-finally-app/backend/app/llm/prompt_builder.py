from typing import List, Dict, Any
from app.llm.models import PortfolioContext, ChatMessageContext

SYSTEM_PROMPT = """You are FinAlly, an expert AI trading assistant on the FinAlly AI Trading Workstation platform.

Your mission:
1. Provide concise, professional, data-driven analysis of the user's trading portfolio, market positions, risk concentration, and unrealized P&L.
2. Suggest trades with clear financial reasoning when requested or appropriate.
3. Automatically trigger trades ("buy" or "sell") and watchlist modifications ("add" or "remove") when the user instructs or confirms an action.
4. Manage the watchlist proactively when requested.

STRICT RESPONSE FORMAT REQUIREMENTS:
You MUST ALWAYS respond with a SINGLE valid JSON object matching this schema EXACTLY:
{
  "message": "<Your markdown conversational response to the user>",
  "trades": [
    {
      "ticker": "<TICKER>",
      "side": "buy" | "sell",
      "quantity": <float_gt_0>
    }
  ],
  "watchlist_changes": [
    {
      "ticker": "<TICKER>",
      "action": "add" | "remove"
    }
  ]
}

CRITICAL RULES:
- `message` (string, required): Your conversational response to the user.
- `trades` (array, optional): Fill with trade objects ONLY if executing trades now based on user intent/request. If no trades, use an empty array `[]`.
- `watchlist_changes` (array, optional): Fill with watchlist changes ONLY if modifying watchlist now based on user intent/request. If no changes, use an empty array `[]`.
- Always verify the user has sufficient cash for buys or sufficient shares for sells according to the provided Portfolio Context.
- Output ONLY the JSON block. Do NOT include extraneous text outside the JSON.
"""


def build_context_prompt(context: PortfolioContext) -> str:
    """Formats portfolio context, cash balance, positions, P&L, and watchlist into a clear prompt string."""
    lines = ["=== CURRENT PORTFOLIO CONTEXT ==="]
    lines.append(f"Cash Balance: ${context.cash_balance:,.2f}")
    lines.append(f"Total Portfolio Value: ${context.total_value:,.2f}")
    lines.append(f"Total Unrealized P&L: ${context.total_pnl:+,.2f} ({context.total_pnl_pct:+.2f}%)")
    lines.append("")

    if context.positions:
        lines.append("Current Positions:")
        for pos in context.positions:
            lines.append(
                f"  - {pos.ticker}: Qty={pos.quantity:.2f}, AvgCost=${pos.avg_cost:,.2f}, "
                f"Price=${pos.current_price:,.2f}, Value=${pos.market_value:,.2f}, "
                f"P&L=${pos.unrealized_pnl:+,.2f} ({pos.unrealized_pnl_pct:+.2f}%)"
            )
    else:
        lines.append("Current Positions: None (100% Cash)")

    lines.append("")
    if context.watchlist:
        lines.append("Watchlist & Live Prices:")
        for item in context.watchlist:
            dir_str = f"({item.direction})" if item.direction else ""
            lines.append(f"  - {item.ticker}: ${item.price:,.2f} {dir_str}")
    else:
        lines.append("Watchlist & Live Prices: None")

    lines.append("================================")
    return "\n".join(lines)


def build_messages(
    user_message: str,
    context: PortfolioContext,
    history: List[ChatMessageContext] = None
) -> List[Dict[str, Any]]:
    """
    Constructs the list of message objects for the LiteLLM API call,
    incorporating System Prompt, Portfolio Context, Conversation History, and the user's latest query.
    """
    context_str = build_context_prompt(context)
    full_system = f"{SYSTEM_PROMPT}\n\n{context_str}"

    messages: List[Dict[str, Any]] = [{"role": "system", "content": full_system}]

    # Include past history turns if provided
    history_items = history if history is not None else context.history
    if history_items:
        for msg in history_items[-10:]:  # Keep recent 10 turns for context efficiency
            if msg.role in ("user", "assistant"):
                messages.append({"role": msg.role, "content": msg.content})

    # Add the current user query
    messages.append({"role": "user", "content": user_message})

    return messages
