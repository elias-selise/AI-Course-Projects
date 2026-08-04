from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class BoardUpdateRequest(BaseModel):
    columns: list


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = Field(default_factory=list)
