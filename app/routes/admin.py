from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Check, Service, User
from app.security import (
    create_session_token,
    is_rate_limited,
    is_safe_url,
    record_failed_attempt,
    verify_password,
    verify_session_token,
)
from app.templates import templates

router = APIRouter(prefix="/admin", tags=["admin"])


def get_current_user(request: Request) -> str | None:
    token = request.cookies.get("session")
    if not token:
        return None
    return verify_session_token(token)


@router.get("/", include_in_schema=False)
async def admin_root():
    return RedirectResponse(url="/admin/services", status_code=302)

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user_email: str | None = Depends(get_current_user)):
    if not user_email:
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse(request, "admin_dashboard.html", {"user_email": user_email})


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
    client_ip = request.client.host if request.client else "unknown"
    
    if is_rate_limited(client_ip):
        return templates.TemplateResponse(request, "login.html", {"error": "Too many failed attempts."})

    stmt = select(User).where(User.email == email)
    user = await session.scalar(stmt)

    if not user or not verify_password(password, user.password_hash):
        record_failed_attempt(client_ip)
        return templates.TemplateResponse(request, "login.html", {"error": "Invalid email or password"})

    token = create_session_token(user.email)
    response = RedirectResponse(url="/admin/services", status_code=302)
    response.set_cookie(key="session", value=token, httponly=True, samesite="lax", max_age=86400)
    return response


@router.post("/logout")
async def logout():
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("session")
    return response


@router.get("/services", response_class=HTMLResponse)
async def list_services(
    request: Request,
    user_email: str | None = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not user_email:
        return RedirectResponse(url="/admin/login", status_code=302)
    stmt = select(Service).order_by(Service.name)
    services = (await session.scalars(stmt)).all()
    return templates.TemplateResponse(request, "admin_services.html", {"user_email": user_email, "services": services})


@router.get("/services/new", response_class=HTMLResponse)
async def new_service_page(request: Request, user_email: str | None = Depends(get_current_user)):
    if not user_email:
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse(request, "admin_service_form.html", {"user_email": user_email, "service": None, "error": None})


@router.post("/services/new", response_class=HTMLResponse)
async def create_service(
    request: Request,
    user_email: str | None = Depends(get_current_user),
    name: str = Form(...),
    url: str = Form(...),
    expected_status: int = Form(200),
    check_interval_seconds: int = Form(30),
    session: AsyncSession = Depends(get_session),
):
    if not user_email:
        return RedirectResponse(url="/admin/login", status_code=302)

    # FIXED: Added await
    if not await is_safe_url(url):
        return templates.TemplateResponse(request, "admin_service_form.html", {"user_email": user_email, "service": None, "error": "Invalid URL."})

    new_service = Service(name=name, url=url, expected_status=expected_status, check_interval_seconds=check_interval_seconds)
    session.add(new_service)
    await session.commit()
    return RedirectResponse(url="/admin/services", status_code=302)


@router.get("/services/{service_id}/edit", response_class=HTMLResponse)
async def edit_service_page(request: Request, service_id: int, user_email: str | None = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if not user_email:
        return RedirectResponse(url="/admin/login", status_code=302)
    service = await session.get(Service, service_id)
    return templates.TemplateResponse(request, "admin_service_form.html", {"user_email": user_email, "service": service, "error": None})


@router.post("/services/{service_id}/edit", response_class=HTMLResponse)
async def update_service(
    request: Request,
    service_id: int,
    user_email: str | None = Depends(get_current_user),
    name: str = Form(...),
    url: str = Form(...),
    expected_status: int = Form(200),
    check_interval_seconds: int = Form(30),
    session: AsyncSession = Depends(get_session),
):
    if not user_email:
        return RedirectResponse(url="/admin/login", status_code=302)
    
    service = await session.get(Service, service_id)
    if not service:
        return RedirectResponse(url="/admin/services", status_code=302)

    # FIXED: Added await
    if not await is_safe_url(url):
        return templates.TemplateResponse(request, "admin_service_form.html", {"user_email": user_email, "service": service, "error": "Invalid URL."})

    service.name = name
    service.url = url
    service.expected_status = expected_status
    service.check_interval_seconds = check_interval_seconds
    await session.commit()
    return RedirectResponse(url="/admin/services", status_code=302)


@router.post("/services/{service_id}/toggle")
async def toggle_service(service_id: int, user_email: str | None = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if not user_email:
        return RedirectResponse(url="/admin/login", status_code=302)
    service = await session.get(Service, service_id)
    if service:
        service.is_active = not service.is_active
        await session.commit()
    return RedirectResponse(url="/admin/services", status_code=302)


@router.post("/services/{service_id}/toggle-public")
async def toggle_public(service_id: int, user_email: str | None = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if not user_email:
        return RedirectResponse(url="/admin/login", status_code=302)
    service = await session.get(Service, service_id)
    if service:
        service.is_public = not service.is_public
        await session.commit()
    return RedirectResponse(url="/admin/services", status_code=302)


@router.post("/services/{service_id}/delete")
async def delete_service(service_id: int, user_email: str | None = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if not user_email:
        return RedirectResponse(url="/admin/login", status_code=302)
    service = await session.get(Service, service_id)
    if service:
        await session.delete(service)
        await session.commit()
    return RedirectResponse(url="/admin/services", status_code=302)


@router.get("/services/{service_id}/history", response_class=HTMLResponse)
async def service_history(request: Request, service_id: int, user_email: str | None = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    if not user_email:
        return RedirectResponse(url="/admin/login", status_code=302)
    service = await session.get(Service, service_id)
    if not service:
        return RedirectResponse(url="/admin/services", status_code=302)
    
    stmt = select(Check).where(Check.service_id == service_id).order_by(Check.id.desc()).limit(50)
    checks = (await session.scalars(stmt)).all()
    return templates.TemplateResponse(request, "admin_history.html", {"user_email": user_email, "service": service, "checks": checks})
