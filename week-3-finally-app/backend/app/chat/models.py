from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Chat message text")


class ChatMessageResponse(BaseModel):
    message: str
    trades_executed: List[Dict[str, Any]] = []
    watchlist_changes: List[Dict[str, Any]] = []
    chat_message_id: str
