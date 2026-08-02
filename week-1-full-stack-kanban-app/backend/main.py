import os
import json
import sqlite3
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

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

# Static files directory location (will be populated during Docker build or local export)
static_dir = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    @app.get("/", response_class=HTMLResponse)
    def index_fallback():
        return "<html><body><h1>Hello World from FastAPI Backend!</h1></body></html>"
