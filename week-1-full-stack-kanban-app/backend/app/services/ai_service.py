import json

import httpx
from fastapi import HTTPException

from .. import config
from ..schemas import ChatRequest
from .board_service import get_board_columns, save_board_columns


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }


def _build_system_prompt(board: list) -> str:
    return (
        "You are an AI assistant for a Project Management Kanban App.\n"
        "You can inspect, create, edit, move, or delete cards on the Kanban board.\n\n"
        "Current Kanban Board JSON State:\n"
        f"{json.dumps(board, indent=2)}\n\n"
        "RULES:\n"
        "1. Respond to the user's request.\n"
        "2. If the user asks you to modify, create, delete, move, or rename cards or columns, return valid JSON in this EXACT structure:\n"
        "{\n"
        '  "reply": "Your explanation to the user",\n'
        '  "board": [ ... full updated columns array matching current board schema ... ]\n'
        "}\n"
        "3. If NO board changes are needed, return:\n"
        "{\n"
        '  "reply": "Your answer to the user",\n'
        '  "board": null\n'
        "}\n"
        "Your response MUST be raw valid JSON strictly matching the schema above without markdown surrounding text."
    )


async def ai_test() -> dict:
    if not config.OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY is not set")

    payload = {
        "model": config.MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": "What is 2+2? Answer with just the single number digit.",
            }
        ],
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            config.OPENROUTER_URL, headers=_headers(), json=payload
        )

        if response.status_code == 402 or "Insufficient credits" in response.text:
            payload["model"] = config.FREE_MODELS[0]
            response = await client.post(
                config.OPENROUTER_URL, headers=_headers(), json=payload
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, detail=response.text
            )

        data = response.json()
        reply = data["choices"][0]["message"]["content"].strip()
        return {
            "success": True,
            "result": reply,
            "model_used": payload["model"],
            "raw": data,
        }


async def ai_chat(req: ChatRequest) -> dict:
    if not config.OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY is not set")

    current_board = get_board_columns()

    messages = [{"role": "system", "content": _build_system_prompt(current_board)}]
    for msg in req.history[-6:]:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": req.message})

    candidate_models = [config.MODEL_NAME] + config.FREE_MODELS
    last_error = ""

    async with httpx.AsyncClient(timeout=45.0) as client:
        for model in candidate_models:
            payload = {
                "model": model,
                "messages": messages,
                "response_format": {"type": "json_object"},
            }
            res = await client.post(
                config.OPENROUTER_URL, headers=_headers(), json=payload
            )
            if res.status_code == 200:
                content = res.json()["choices"][0]["message"]["content"]
                try:
                    parsed = json.loads(content)
                    reply = parsed.get("reply", content)
                    updated_board = parsed.get("board")
                except Exception:
                    reply = content
                    updated_board = None

                if updated_board and isinstance(updated_board, list):
                    save_board_columns(updated_board)

                return {
                    "success": True,
                    "reply": reply,
                    "board": updated_board,
                    "model_used": model,
                }
            else:
                last_error = res.text

    raise HTTPException(status_code=500, detail=f"All models failed: {last_error}")
