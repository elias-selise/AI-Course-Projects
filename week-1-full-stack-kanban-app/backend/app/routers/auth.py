from fastapi import APIRouter, HTTPException, Request, Response

from .. import config
from ..schemas import LoginRequest

router = APIRouter(prefix="/api", tags=["auth"])


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/login")
def login(req: LoginRequest, response: Response):
    if req.username == config.USERNAME and req.password == config.PASSWORD:
        response.set_cookie(key="session_user", value=config.USERNAME, httponly=True)
        return {"success": True, "username": config.USERNAME}
    raise HTTPException(status_code=401, detail="Invalid username or password")


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="session_user")
    return {"success": True}


@router.get("/me")
def get_me(request: Request):
    if request.cookies.get("session_user") == config.USERNAME:
        return {"authenticated": True, "username": config.USERNAME}
    return {"authenticated": False}
