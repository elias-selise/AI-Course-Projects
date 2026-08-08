from app.llm.models import (
    PortfolioContext,
    PositionContext,
    WatchlistPriceContext,
    ChatMessageContext,
)
from app.llm.prompt_builder import (
    build_context_prompt,
    build_messages,
    SYSTEM_PROMPT,
)


def test_build_context_prompt_formatting():
    ctx = PortfolioContext(
        cash_balance=8500.0,
        total_value=11500.0,
        total_pnl=1500.0,
        total_pnl_pct=15.0,
        positions=[
            PositionContext(
                ticker="AAPL",
                quantity=10.0,
                avg_cost=150.0,
                current_price=180.0,
                market_value=1800.0,
                unrealized_pnl=300.0,
                unrealized_pnl_pct=20.0,
            )
        ],
        watchlist=[
            WatchlistPriceContext(ticker="MSFT", price=400.0, direction="up")
        ]
    )

    prompt = build_context_prompt(ctx)

    assert "Cash Balance: $8,500.00" in prompt
    assert "Total Portfolio Value: $11,500.00" in prompt
    assert "Total Unrealized P&L: +$1,500.00 (+15.00%)" in prompt
    assert "AAPL: Qty=10.00, AvgCost=$150.00, Price=$180.00" in prompt
    assert "MSFT: $400.00 (up)" in prompt


def test_build_context_prompt_empty_positions():
    ctx = PortfolioContext(cash_balance=10000.0, total_value=10000.0)
    prompt = build_context_prompt(ctx)

    assert "Current Positions: None (100% Cash)" in prompt
    assert "Watchlist & Live Prices: None" in prompt


def test_build_messages_structure():
    ctx = PortfolioContext(cash_balance=5000.0)
    history = [
        ChatMessageContext(role="user", content="What is my cash balance?"),
        ChatMessageContext(role="assistant", content="Your cash balance is $5,000.00."),
    ]

    messages = build_messages(
        user_message="Should I buy AAPL?",
        context=ctx,
        history=history,
    )

    assert len(messages) == 4
    assert messages[0]["role"] == "system"
    assert SYSTEM_PROMPT in messages[0]["content"]
    assert "Cash Balance: $5,000.00" in messages[0]["content"]

    assert messages[1] == {"role": "user", "content": "What is my cash balance?"}
    assert messages[2] == {"role": "assistant", "content": "Your cash balance is $5,000.00."}
    assert messages[3] == {"role": "user", "content": "Should I buy AAPL?"}
