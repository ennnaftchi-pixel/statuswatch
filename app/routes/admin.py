from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.security import create_session_token, verify_password, verify_session_token
from app.templates import templates

router = APIRouter(prefix="/admin", tags=["admin"])


def get_current_user(request: Request) -> str | None:
    token = request.cookies.get("session")
    if not token:
        return None
    return verify_session_token(token)


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    session: AsyncSession = Depends(get_session),
):
    stmt = select(User).where(User.email == email)
    user = await session.scalar(stmt)

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request, "login.html", {"error": "Invalid email or password"}
        )

    token = create_session_token(user.email)
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(key="session", value=token, httponly=True, max_age=86400)
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user_email: str | None = Depends(get_current_user)):
    if not user_email:
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse(request, "admin_dashboard.html", {"user_email": user_email})


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("session")
    return response
