from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Check, Service
from app.templates import templates

router = APIRouter(tags=["public"])


@router.get("/", response_class=HTMLResponse)
async def public_status_page(
    request: Request, session: AsyncSession = Depends(get_session)
):
    # 1. Fetch only services that are marked as public and active
    stmt = (
        select(Service)
        .where(Service.is_public.is_(True))
        .where(Service.is_active.is_(True))
        .order_by(Service.name)
    )
    services = (await session.scalars(stmt)).all()

    # 2. For each service, find its most recent check
    status_data = []
    for service in services:
        latest_check = await session.scalar(
            select(Check)
            .where(Check.service_id == service.id)
            .order_by(Check.id.desc())
            .limit(1)
        )
        status_data.append({"service": service, "latest_check": latest_check})

    return templates.TemplateResponse(
        request, "public_status.html", {"status_data": status_data}
    )
