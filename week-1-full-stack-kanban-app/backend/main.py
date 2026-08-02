import os
import json
import sqlite3
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
FREE_MODELS = [
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "poolside/laguna-s-2.1:free",
    "inclusionai/ling-3.0-flash:free"
]

DB_PATH = os.path.join(os.path.dirname(__file__), "kanban.db")

DEFAULT_COLUMNS = [
    {
        "id": "backlog",
        "title": "Backlog",
        "cards": [
            {
                "id": "card-1",
                "title": "Project Setup",
                "details": "NextJS 15 workspace initialization with Tailwind CSS styling."
            }
        ]
    },
    {"id": "todo", "title": "To Do", "cards": []},
    {"id": "in-progress", "title": "In Progress", "cards": []},
    {"id": "review", "title": "Review", "cards": []},
    {"id": "done", "title": "Done", "cards": []}
]

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boards (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    cursor.execute("SELECT id FROM users WHERE username = 'user'")
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (id, username, password) VALUES ('user-1', 'user', 'password')")
        cursor.execute("INSERT INTO boards (id, user_id, data) VALUES ('board-1', 'user-1', ?)", (json.dumps(DEFAULT_COLUMNS),))
    conn.commit()
    conn.close()

init_db()

app = FastAPI(title="Kanban App API")

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
    history: list[ChatMessage] = []

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/login")
def login(req: LoginRequest, response: Response):
    if req.username == "user" and req.password == "password":
        response.set_cookie(key="session_user", value="user", httponly=True)
        return {"success": True, "username": "user"}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.post("/api/logout")
def logout(response: Response):
    response.delete_cookie(key="session_user")
    return {"success": True}

@app.get("/api/me")
def get_me(request: Request):
    user = request.cookies.get("session_user")
    if user == "user":
        return {"authenticated": True, "username": "user"}
    return {"authenticated": False}

@app.get("/api/board")
def get_board(request: Request):
    user = request.cookies.get("session_user")
    if user != "user":
        # Allow fallback for MVP single user mode if unauthenticated during dev
        pass
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM boards WHERE user_id = 'user-1'")
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"columns": json.loads(row[0])}
    return {"columns": DEFAULT_COLUMNS}

@app.put("/api/board")
def update_board(req: BoardUpdateRequest, request: Request):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE boards SET data = ? WHERE user_id = 'user-1'", (json.dumps(req.columns),))
    conn.commit()
    conn.close()
    return {"success": True, "columns": req.columns}

@app.post("/api/ai/test")
async def ai_test():
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY is not set")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First try primary model
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": "What is 2+2? Answer with just the single number digit."}
            ],
        }
        response = await client.post(OPENROUTER_URL, headers=headers, json=payload)
        
        if response.status_code == 402 or "Insufficient credits" in response.text:
            # Fallback to free tier model
            payload["model"] = FALLBACK_FREE_MODEL
            response = await client.post(OPENROUTER_URL, headers=headers, json=payload)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
            
        data = response.json()
        reply = data["choices"][0]["message"]["content"].strip()
        return {"success": True, "result": reply, "model_used": payload["model"], "raw": data}

@app.post("/api/ai/chat")
async def ai_chat(req: ChatRequest, request: Request):
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY is not set")
    
    # Retrieve current board state
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM boards WHERE user_id = 'user-1'")
    row = cursor.fetchone()
    conn.close()
    current_board = json.loads(row[0]) if row else DEFAULT_COLUMNS

    system_prompt = (
        "You are an AI assistant for a Project Management Kanban App.\n"
        "You can inspect, create, edit, move, or delete cards on the Kanban board.\n\n"
        "Current Kanban Board JSON State:\n"
        f"{json.dumps(current_board, indent=2)}\n\n"
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

    messages = [{"role": "system", "content": system_prompt}]
    for msg in req.history[-6:]:
        messages.append({"role": msg.role, "content": msg.content})
    messages.append({"role": "user", "content": req.message})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    candidate_models = [MODEL_NAME] + FREE_MODELS
    last_error = ""

    async with httpx.AsyncClient(timeout=45.0) as client:
        for model in candidate_models:
            payload = {
                "model": model,
                "messages": messages,
                "response_format": {"type": "json_object"}
            }
            res = await client.post(OPENROUTER_URL, headers=headers, json=payload)
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
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("UPDATE boards SET data = ? WHERE user_id = 'user-1'", (json.dumps(updated_board),))
                    conn.commit()
                    conn.close()

                return {
                    "success": True,
                    "reply": reply,
                    "board": updated_board,
                    "model_used": model
                }
            else:
                last_error = res.text

    raise HTTPException(status_code=500, detail=f"All models failed: {last_error}")

# Static files directory location (will be populated during Docker build or local export)
static_dir = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    @app.get("/", response_class=HTMLResponse)
    def index_fallback():
        return "<html><body><h1>Hello World from FastAPI Backend!</h1></body></html>"
