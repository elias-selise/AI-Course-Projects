from fastapi import APIRouter, Request

from ..schemas import ChatRequest
from ..services import ai_service

router = APIRouter(prefix="/api", tags=["ai"])


@router.post("/ai/test")
async def ai_test():
    return await ai_service.ai_test()


@router.post("/ai/chat")
async def ai_chat(req: ChatRequest, request: Request):
    return await ai_service.ai_chat(req)
