import json
import re
from typing import Any, Dict, Union
from pydantic import ValidationError
from app.llm.models import LLMResponse


class LLMResponseParseError(Exception):
    """Custom exception raised when an LLM response cannot be parsed into LLMResponse schema."""
    def __init__(self, message: str, raw_content: str = ""):
        super().__init__(message)
        self.raw_content = raw_content


def extract_json_string(text: str) -> str:
    """Extracts JSON string from raw LLM output, removing markdown code blocks if present."""
    text = text.strip()
    
    # Check for markdown code blocks ```json ... ``` or ``` ... ```
    pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # If text starts with { and ends with }, return as is
    if text.startswith("{") and text.endswith("}"):
        return text

    # Try finding first { and last }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace:last_brace + 1]

    return text


def parse_llm_response(raw_input: Union[str, Dict[str, Any]]) -> LLMResponse:
    """
    Parses and validates raw LLM output into an LLMResponse Pydantic instance.

    :param raw_input: Raw string or dictionary output from LiteLLM.
    :return: Validated LLMResponse object.
    :raises LLMResponseParseError: If parsing or Pydantic validation fails.
    """
    if isinstance(raw_input, dict):
        parsed_dict = raw_input
        raw_str = json.dumps(raw_input)
    elif isinstance(raw_input, str):
        raw_str = raw_input
        json_str = extract_json_string(raw_input)
        try:
            parsed_dict = json.loads(json_str)
        except json.JSONDecodeError as err:
            raise LLMResponseParseError(
                f"Failed to decode JSON from LLM response: {str(err)}",
                raw_content=raw_input
            ) from err
    else:
        raise LLMResponseParseError(
            f"Unsupported response type for parsing: {type(raw_input)}",
            raw_content=str(raw_input)
        )

    if not isinstance(parsed_dict, dict):
        raise LLMResponseParseError(
            "Parsed JSON root is not a dictionary",
            raw_content=raw_str
        )

    # Ensure required 'message' key exists
    if "message" not in parsed_dict:
        # If model returned response in another field, or just text:
        if "text" in parsed_dict:
            parsed_dict["message"] = str(parsed_dict["text"])
        elif "content" in parsed_dict:
            parsed_dict["message"] = str(parsed_dict["content"])
        else:
            raise LLMResponseParseError(
                "Missing required field 'message' in structured LLM response JSON",
                raw_content=raw_str
            )

    try:
        return LLMResponse.model_validate(parsed_dict)
    except ValidationError as val_err:
        raise LLMResponseParseError(
            f"LLM response failed schema validation: {str(val_err)}",
            raw_content=raw_str
        ) from val_err
