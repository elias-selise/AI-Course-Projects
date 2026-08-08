import json
from typing import List
from fastapi import APIRouter, Request, HTTPException, status

from app.config import get_settings
from app.db.database import get_db
from app.schemas.chat import ChatRequest, ChatResponse, ChatMessageResponse
from app.services.chat_service import process_chat_message
from app.services.llm_provider import get_llm_provider

router = APIRouter(prefix="/api/chat", tags=["AI Copilot"])


@router.post("", response_model=ChatResponse)
async def send_chat_message(chat_req: ChatRequest, request: Request):
    """Submit prompt to AI copilot, parse actions, auto-execute, and record chat log."""
    settings = getattr(request.app.state, "settings", None) or get_settings()
    cache = getattr(request.app.state, "price_cache", None)
    market_source = getattr(request.app.state, "market_source", None)
    provider = get_llm_provider(settings)

    async with get_db(settings.DB_PATH) as db:
        try:
            return await process_chat_message(
                db=db,
                cache=cache,
                provider=provider,
                user_message=chat_req.message,
                market_source=market_source
            )
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/history", response_model=List[ChatMessageResponse])
async def get_chat_history(request: Request):
    """Fetch persistent chat history logs from database."""
    settings = getattr(request.app.state, "settings", None) or get_settings()
    async with get_db(settings.DB_PATH) as db:
        async with db.execute(
            "SELECT id, role, content, actions, created_at FROM chat_messages WHERE user_id = 'default' ORDER BY created_at ASC"
        ) as cursor:
            rows = await cursor.fetchall()
            result = []
            for item_id, role, content, actions_str, created_at in rows:
                actions_obj = json.loads(actions_str) if actions_str else None
                result.append(
                    ChatMessageResponse(
                        id=item_id,
                        role=role,
                        content=content,
                        actions=actions_obj,
                        created_at=created_at
                    )
                )
            return result


@router.delete("/history")
async def clear_chat_history(request: Request):
    """Clear chat history logs from database."""
    settings = getattr(request.app.state, "settings", None) or get_settings()
    async with get_db(settings.DB_PATH) as db:
        await db.execute("DELETE FROM chat_messages WHERE user_id = 'default'")
        await db.commit()
        return {"status": "success", "message": "Chat history cleared."}
