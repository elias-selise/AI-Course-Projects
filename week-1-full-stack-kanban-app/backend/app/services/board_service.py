import json

from .. import config
from ..database import get_connection


def get_board_columns() -> list:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT data FROM boards WHERE user_id = 'user-1'"
        ).fetchone()
    finally:
        conn.close()
    if row:
        return json.loads(row["data"])
    return config.DEFAULT_COLUMNS


def save_board_columns(columns: list) -> list:
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE boards SET data = ? WHERE user_id = 'user-1'",
            (json.dumps(columns),),
        )
        conn.commit()
    finally:
        conn.close()
    return columns
