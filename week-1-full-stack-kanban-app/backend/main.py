import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import auth, board, ai

init_db()

app = FastAPI(title="Kanban App API")

app.include_router(auth.router)
app.include_router(board.router)
app.include_router(ai.router)

static_dir = os.path.join(os.path.dirname(__file__), "static")

if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
else:
    @app.get("/", response_class=HTMLResponse)
    def index_fallback():
        return "<html><body><h1>Hello World from FastAPI Backend!</h1></body></html>"