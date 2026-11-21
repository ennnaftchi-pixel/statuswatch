from datetime import UTC, datetime, timedelta

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

    # Calculate the timestamp for 24 hours ago
    time_24h_ago = datetime.now(UTC) - timedelta(hours=24)

    status_data = []
    for service in services:
        # 2. Get the latest check (for current status)
        latest_check = await session.scalar(
            select(Check)
            .where(Check.service_id == service.id)
            .order_by(Check.id.desc())
            .limit(1)
        )

        # 3. Get the history for the last 24 hours (ordered oldest to newest for the UI chart)
        history_stmt = (
            select(Check)
            .where(Check.service_id == service.id)
            .where(Check.checked_at >= time_24h_ago)
            .order_by(Check.checked_at.asc())
        )
        history = (await session.scalars(history_stmt)).all()

        status_data.append({
            "service": service,
            "latest_check": latest_check,
            "history": history
        })

    return templates.TemplateResponse(
        request, "public_status.html", {"status_data": status_data}
    )
