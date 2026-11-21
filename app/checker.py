import asyncio
import time
from datetime import UTC, datetime, timedelta

import httpx
from sqlalchemy import select

from app.alerts import send_telegram_alert
from app.db import SessionLocal
from app.metrics import CHECKS_TOTAL, RESPONSE_TIME, SERVICE_UP
from app.models import Alert, Check, Service

# Track services currently being probed to prevent race conditions
_pending_probes: set[int] = set()

async def _probe_and_release(client: httpx.AsyncClient, service: Service) -> None:
    try:
        await probe_service(client, service)
    finally:
        _pending_probes.discard(service.id)


async def probe_service(client: httpx.AsyncClient, service: Service) -> None:
    start_time = time.perf_counter()
    status = "down"
    http_status = None
    error_msg = None

    try:
        response = await client.get(service.url, timeout=10.0, follow_redirects=False)
        http_status = response.status_code
        
        if http_status == service.expected_status:
            status = "up"
        else:
            error_msg = f"Expected {service.expected_status}, got {http_status}"
            
    except httpx.RequestError as exc:
        error_msg = f"Request failed: {exc!s}"
    except Exception as exc:
        error_msg = f"Unknown error: {exc!s}"

    response_time_ms = int((time.perf_counter() - start_time) * 1000)

    CHECKS_TOTAL.labels(service_name=service.name, status=status).inc()
    SERVICE_UP.labels(service_name=service.name).set(1 if status == "up" else 0)
    RESPONSE_TIME.labels(service_name=service.name).observe(response_time_ms / 1000.0)

    async with SessionLocal() as session:
        new_check = Check(
            service_id=service.id,
            status=status,
            http_status_code=http_status,
            response_time_ms=response_time_ms,
            error_message=error_msg,
            checked_at=datetime.now(UTC)
        )
        session.add(new_check)
        await session.commit()

        stmt = select(Check).where(Check.service_id == service.id).order_by(Check.id.desc()).limit(3)
        recent_checks = (await session.scalars(stmt)).all()

        # New outage
        if (
            len(recent_checks) >= 2
            and recent_checks[0].status == "down"
            and recent_checks[1].status == "down"
            and (len(recent_checks) < 3 or recent_checks[2].status == "up")
        ):
            print(f"[ALERT] {service.name} is officially DOWN")
            session.add(Alert(service_id=service.id, kind="down"))
            await session.commit()
            await send_telegram_alert(service.name, "down", service.url)

        # Recovery alert
        if (
            len(recent_checks) >= 2
            and recent_checks[0].status == "up"
            and recent_checks[1].status == "down"
        ):
            alert_stmt = select(Alert).where(Alert.service_id == service.id, Alert.kind == "down").order_by(Alert.id.desc()).limit(1)
            last_down_alert = await session.scalar(alert_stmt)
            if last_down_alert:
                print(f"[RECOVERY] {service.name} is back UP")
                await session.delete(last_down_alert) 
                session.add(Alert(service_id=service.id, kind="recovery"))
                await session.commit()
                await send_telegram_alert(service.name, "up", service.url)


async def checker_loop() -> None:
    print("Starting background checker loop...")
    async with httpx.AsyncClient() as client:
        while True:
            try:
                async with SessionLocal() as session:
                    stmt = select(Service).where(Service.is_active.is_(True))
                    services = (await session.scalars(stmt)).all()

                    for service in services:
                        check_stmt = select(Check.checked_at).where(Check.service_id == service.id).order_by(Check.id.desc()).limit(1)
                        last_check_time = await session.scalar(check_stmt)
                        
                        should_check = False
                        if not last_check_time:
                            should_check = True
                        else:
                            if last_check_time.tzinfo is None:
                                last_check_time = last_check_time.replace(tzinfo=UTC)
                            if datetime.now(UTC) - last_check_time >= timedelta(seconds=service.check_interval_seconds):
                                should_check = True
                                
                        # THE FIX: Check if it's already pending
                        if should_check and service.id not in _pending_probes:
                            _pending_probes.add(service.id)
                            asyncio.create_task(_probe_and_release(client, service))

            except Exception as exc:
                print(f"[ERROR] Error in checker loop: {exc}")

            await asyncio.sleep(5)
