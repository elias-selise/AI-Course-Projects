import os
import logging
from typing import List, Optional
import litellm
from app.llm.models import LLMResponse, PortfolioContext, ChatMessageContext
from app.llm.prompt_builder import build_messages
from app.llm.parser import parse_llm_response, LLMResponseParseError
from app.llm.mock_provider import MockLLMProvider

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "openrouter/openai/gpt-oss-120b"


class LLMClient:
    """
    LLM Client integrating LiteLLM with OpenRouter / Cerebras provider.
    Supports deterministic mock mode when LLM_MOCK=true.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        mock_mode: Optional[bool] = None,
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.model = model or os.getenv("LLM_MODEL", DEFAULT_MODEL)
        
        if mock_mode is not None:
            self.mock_mode = mock_mode
        else:
            env_mock = os.getenv("LLM_MOCK", "false").lower()
            self.mock_mode = env_mock in ("true", "1", "t", "yes")

        self.mock_provider = MockLLMProvider()

    def generate_response(self,
                          user_message: str,
                          context: Optional[PortfolioContext] = None,
                          history: Optional[List[ChatMessageContext]] = None) -> LLMResponse:
        """
        Synchronous call to generate structured response from LLM or mock provider.
        """
        portfolio_ctx = context or PortfolioContext()

        if self.mock_mode:
            logger.info("LLM_MOCK mode active: Returning mock response")
            return self.mock_provider.generate_response(user_message, portfolio_ctx)

        messages = build_messages(user_message, portfolio_ctx, history)

        try:
            response = litellm.completion(
                model=self.model,
                api_key=self.api_key,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw_content = response.choices[0].message.content
            return parse_llm_response(raw_content)

        except LLMResponseParseError:
            raise
        except Exception as e:
            logger.error(f"LiteLLM completion error: {e}", exc_info=True)
            raise RuntimeError(f"LLM service error: {str(e)}") from e

    async def generate_response_async(self,
                                      user_message: str,
                                      context: Optional[PortfolioContext] = None,
                                      history: Optional[List[ChatMessageContext]] = None) -> LLMResponse:
        """
        Asynchronous call to generate structured response from LLM or mock provider.
        """
        portfolio_ctx = context or PortfolioContext()

        if self.mock_mode:
            logger.info("LLM_MOCK mode active: Returning mock response")
            return self.mock_provider.generate_response(user_message, portfolio_ctx)

        messages = build_messages(user_message, portfolio_ctx, history)

        try:
            response = await litellm.acompletion(
                model=self.model,
                api_key=self.api_key,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            raw_content = response.choices[0].message.content
            return parse_llm_response(raw_content)

        except LLMResponseParseError:
            raise
        except Exception as e:
            logger.error(f"LiteLLM acompletion error: {e}", exc_info=True)
            raise RuntimeError(f"LLM service error: {str(e)}") from e
