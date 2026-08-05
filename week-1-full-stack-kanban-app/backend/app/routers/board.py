from fastapi import APIRouter, Request

from ..schemas import BoardUpdateRequest
from ..services import board_service

router = APIRouter(prefix="/api", tags=["board"])


@router.get("/board")
def get_board(request: Request):
    return {"columns": board_service.get_board_columns()}


@router.put("/board")
def update_board(req: BoardUpdateRequest, request: Request):
    return {"success": True, "columns": board_service.save_board_columns(req.columns)}
