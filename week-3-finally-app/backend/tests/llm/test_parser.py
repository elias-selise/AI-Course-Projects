import pytest
from app.llm.parser import parse_llm_response, extract_json_string, LLMResponseParseError
from app.llm.models import LLMResponse


def test_extract_json_string_markdown_blocks():
    raw_markdown = """Here is the response:
```json
{
  "message": "Buying AAPL",
  "trades": [{"ticker": "AAPL", "side": "buy", "quantity": 10}],
  "watchlist_changes": []
}
```
Hope this helps!"""
    extracted = extract_json_string(raw_markdown)
    assert extracted.startswith("{") and extracted.endswith("}")
    assert '"message": "Buying AAPL"' in extracted


def test_parse_valid_json_string():
    raw_json = '{"message": "Portfolio looks fine.", "trades": [], "watchlist_changes": []}'
    parsed = parse_llm_response(raw_json)
    assert isinstance(parsed, LLMResponse)
    assert parsed.message == "Portfolio looks fine."
    assert parsed.trades == []
    assert parsed.watchlist_changes == []


def test_parse_dictionary_input():
    data = {
        "message": "Executed sell.",
        "trades": [{"ticker": "NVDA", "side": "sell", "quantity": 5.0}],
        "watchlist_changes": [{"ticker": "AMD", "action": "add"}]
    }
    parsed = parse_llm_response(data)
    assert parsed.message == "Executed sell."
    assert len(parsed.trades) == 1
    assert parsed.trades[0].ticker == "NVDA"
    assert parsed.trades[0].side == "sell"
    assert parsed.trades[0].quantity == 5.0
    assert len(parsed.watchlist_changes) == 1
    assert parsed.watchlist_changes[0].ticker == "AMD"


def test_parse_malformed_json_raises_error():
    malformed = '{"message": "Hello", "trades": [unclosed array'
    with pytest.raises(LLMResponseParseError) as exc_info:
        parse_llm_response(malformed)
    assert "Failed to decode JSON" in str(exc_info.value)
    assert exc_info.value.raw_content == malformed


def test_parse_missing_message_field():
    no_message = '{"trades": []}'
    with pytest.raises(LLMResponseParseError) as exc_info:
        parse_llm_response(no_message)
    assert "Missing required field 'message'" in str(exc_info.value)


def test_parse_fallback_fields():
    alt = '{"text": "Fallback message", "trades": []}'
    parsed = parse_llm_response(alt)
    assert parsed.message == "Fallback message"


def test_parse_schema_validation_failure():
    # Invalid side "hold"
    bad_schema = '{"message": "invalid", "trades": [{"ticker": "AAPL", "side": "hold", "quantity": 5}]}'
    with pytest.raises(LLMResponseParseError) as exc_info:
        parse_llm_response(bad_schema)
    assert "LLM response failed schema validation" in str(exc_info.value)
