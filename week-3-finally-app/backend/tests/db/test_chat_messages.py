"""Unit tests for chat messages repository operations."""

import pytest
from app.db import ChatMessage, DatabaseRepository


def test_add_chat_message_user_and_assistant(repo: DatabaseRepository):
    """Test inserting user and assistant chat messages with actions."""
    # 1. User message
    msg1 = repo.add_chat_message("default", "user", "Buy 10 shares of AAPL")
    assert isinstance(msg1, ChatMessage)
    assert msg1.role == "user"
    assert msg1.content == "Buy 10 shares of AAPL"
    assert msg1.actions is None

    # 2. Assistant message with JSON actions
    actions_payload = {
        "trades": [{"ticker": "AAPL", "side": "buy", "quantity": 10}],
        "watchlist_changes": [],
    }
    msg2 = repo.add_chat_message(
        "default",
        "assistant",
        "Executed buy order for 10 AAPL shares.",
        actions=actions_payload,
    )
    assert msg2.role == "assistant"
    assert msg2.actions == actions_payload


def test_get_chat_messages_ordering(repo: DatabaseRepository):
    """Test retrieving chat message history in chronological order."""
    repo.add_chat_message("default", "user", "Hello")
    repo.add_chat_message("default", "assistant", "Hi! How can I help you?")

    messages = repo.get_chat_messages("default")
    assert len(messages) == 2
    assert messages[0].content == "Hello"
    assert messages[1].content == "Hi! How can I help you?"


def test_clear_chat_messages(repo: DatabaseRepository):
    """Test clearing chat message history."""
    repo.add_chat_message("default", "user", "Test")
    assert len(repo.get_chat_messages("default")) == 1

    cleared = repo.clear_chat_messages("default")
    assert cleared is True
    assert len(repo.get_chat_messages("default")) == 0


def test_add_chat_message_invalid_role_raises(repo: DatabaseRepository):
    """Test that invalid chat role raises ValueError."""
    with pytest.raises(ValueError, match="Invalid role"):
        repo.add_chat_message("default", "system", "System prompt")
