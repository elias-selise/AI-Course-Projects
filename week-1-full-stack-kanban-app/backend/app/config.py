import os

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-120b")
FREE_MODELS = [
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "poolside/laguna-s-2.1:free",
    "inclusionai/ling-3.0-flash:free",
]

DB_PATH = os.getenv("KANBAN_DB_PATH", os.path.join(BASE_DIR, "kanban.db"))

USERNAME = os.getenv("KANBAN_USERNAME", "user")
PASSWORD = os.getenv("KANBAN_PASSWORD", "password")

DEFAULT_COLUMNS = [
    {
        "id": "backlog",
        "title": "Backlog",
        "cards": [
            {
                "id": "card-1",
                "title": "Project Setup",
                "details": "NextJS 15 workspace initialization with Tailwind CSS styling.",
            }
        ],
    },
    {"id": "todo", "title": "To Do", "cards": []},
    {"id": "in-progress", "title": "In Progress", "cards": []},
    {"id": "review", "title": "Review", "cards": []},
    {"id": "done", "title": "Done", "cards": []},
]
