import abc
import json
import logging
import re
from typing import List, Dict, Any, Optional
from app.config import Settings

logger = logging.getLogger("finally.llm")


class BaseLLMProvider(abc.ABC):
    """Abstract base class for LLM completion providers."""

    @abc.abstractmethod
    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate raw completion string from list of message dictionaries."""
        pass


class OpenRouterLiteLLMProvider(BaseLLMProvider):
    """OpenRouter provider implementation utilizing LiteLLM SDK or direct HTTP client."""

    def __init__(self, api_key: str, model_name: str = "openrouter/openai/gpt-oss-120b"):
        self.api_key = api_key
        self.model_name = model_name

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        try:
            import litellm
            response = await litellm.acompletion(
                model=self.model_name,
                api_key=self.api_key,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
                timeout=30.0
            )
            return response.choices[0].message.content
        except ImportError:
            # Fallback to direct httpx async client if litellm is not installed
            import httpx
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://finally.local",
                "X-Title": "FinAlly AI Trading Workstation",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "openai/gpt-oss-120b",
                "messages": messages,
                "response_format": {"type": "json_object"},
                "temperature": 0.2
            }
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error calling OpenRouter LLM provider: {e}")
            raise RuntimeError(f"LLM Provider Error: {e}")


class MockLLMProvider(BaseLLMProvider):
    """Deterministic local mock LLM provider for fast zero-cost testing."""

    async def generate_response(self, messages: List[Dict[str, str]]) -> str:
        # Find user message content from messages list (last user turn)
        last_message = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_message = m.get("content", "").lower()
                break
        if not last_message and messages:
            last_message = messages[-1].get("content", "").lower()

        trades = []
        watchlist_changes = []
        message_text = "I have analyzed your request and updated your workstation state."

        # Regex intent detection
        buy_match = re.search(r"buy\s+(\d+(?:\.\d+)?)\s*(?:shares\s+of\s+)?([a-zA-Z]{1,5})", last_message)
        sell_match = re.search(r"sell\s+(\d+(?:\.\d+)?)\s*(?:shares\s+of\s+)?([a-zA-Z]{1,5})", last_message)
        add_watch_match = re.search(r"add\s+([a-zA-Z]{1,5})\s+to\s+watchlist", last_message)
        rem_watch_match = re.search(r"(?:remove|delete)\s+([a-zA-Z]{1,5})\s+from\s+watchlist", last_message)

        if buy_match:
            qty = float(buy_match.group(1))
            ticker = buy_match.group(2).upper()
            trades.append({"ticker": ticker, "side": "buy", "quantity": qty})
            message_text = f"Executed market buy order for {qty} shares of {ticker}."
        elif sell_match:
            qty = float(sell_match.group(1))
            ticker = sell_match.group(2).upper()
            trades.append({"ticker": ticker, "side": "sell", "quantity": qty})
            message_text = f"Executed market sell order for {qty} shares of {ticker}."
        elif add_watch_match:
            ticker = add_watch_match.group(1).upper()
            watchlist_changes.append({"action": "add", "ticker": ticker})
            message_text = f"Added {ticker} to your watchlist."
        elif rem_watch_match:
            ticker = rem_watch_match.group(1).upper()
            watchlist_changes.append({"action": "remove", "ticker": ticker})
            message_text = f"Removed {ticker} from your watchlist."
        elif "status" in last_message or "portfolio" in last_message or "hello" in last_message or "how" in last_message:
            message_text = "Your portfolio is in good standing. Let me know if you would like to buy or sell any positions or update your watchlist."

        payload = {
            "message": message_text,
            "trades": trades,
            "watchlist_changes": watchlist_changes
        }
        return json.dumps(payload)


def get_llm_provider(settings: Settings) -> BaseLLMProvider:
    """Factory function returning active LLM provider based on application configuration."""
    if settings.LLM_MOCK or not settings.OPENROUTER_API_KEY:
        logger.info("Using MockLLMProvider for AI Copilot (LLM_MOCK=True or API key absent).")
        return MockLLMProvider()
    return OpenRouterLiteLLMProvider(api_key=settings.OPENROUTER_API_KEY)
