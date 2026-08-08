import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent

# Database configuration
# Look for DATABASE_PATH env var first, otherwise check /app/db/finally.db, project_root/db/finally.db, or local finally.db
env_db_path = os.getenv("DATABASE_PATH")
if env_db_path:
    DATABASE_PATH = Path(env_db_path)
elif Path("/app/db").exists():
    DATABASE_PATH = Path("/app/db/finally.db")
else:
    DATABASE_PATH = PROJECT_ROOT / "db" / "finally.db"

# API Keys & Flags
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY", "")
LLM_MOCK = os.getenv("LLM_MOCK", "false").lower() in ("true", "1", "yes")

# Static frontend directory
FRONTEND_STATIC_DIR = PROJECT_ROOT / "frontend" / "out"
