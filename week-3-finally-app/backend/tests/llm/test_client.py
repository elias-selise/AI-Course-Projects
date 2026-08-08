import pytest
from unittest.mock import patch, MagicMock
from app.llm.client import LLMClient
from app.llm.models import LLMResponse, PortfolioContext


def test_client_mock_mode_flag():
    client = LLMClient(mock_mode=True)
    assert client.mock_mode is True
    resp = client.generate_response("Buy 10 AAPL")
    assert len(resp.trades) == 1
    assert resp.trades[0].ticker == "AAPL"


@pytest.mark.asyncio
async def test_client_mock_mode_async():
    client = LLMClient(mock_mode=True)
    resp = await client.generate_response_async("Buy 5 MSFT")
    assert len(resp.trades) == 1
    assert resp.trades[0].ticker == "MSFT"


@patch("litellm.completion")
def test_client_litellm_sync_call(mock_completion):
    mock_choice = MagicMock()
    mock_choice.message.content = '{"message": "LLM response", "trades": [], "watchlist_changes": []}'
    mock_completion.return_value = MagicMock(choices=[mock_choice])

    client = LLMClient(api_key="fake-key", mock_mode=False)
    resp = client.generate_response("Analyze portfolio")

    assert resp.message == "LLM response"
    mock_completion.assert_called_once()
    call_kwargs = mock_completion.call_args.kwargs
    assert call_kwargs["api_key"] == "fake-key"
    assert call_kwargs["model"] == "openrouter/openai/gpt-oss-120b"


@pytest.mark.asyncio
@patch("litellm.acompletion")
async def test_client_litellm_async_call(mock_acompletion):
    mock_choice = MagicMock()
    mock_choice.message.content = '{"message": "Async LLM response", "trades": [], "watchlist_changes": []}'
    mock_acompletion.return_value = MagicMock(choices=[mock_choice])

    client = LLMClient(api_key="fake-key", mock_mode=False)
    resp = await client.generate_response_async("Analyze portfolio")

    assert resp.message == "Async LLM response"
    mock_acompletion.assert_called_once()
