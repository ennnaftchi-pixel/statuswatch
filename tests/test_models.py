from sqlalchemy import select

from app.models import Alert, Check, Service, User


async def test_user_defaults(session) -> None:
    user = User(email="admin@example.com", password_hash="x")
    session.add(user)
    await session.commit()
    await session.refresh(user)
    assert user.id is not None
    assert user.role == "admin"
    assert user.is_active is True
    assert user.created_at is not None


async def test_service_defaults(session) -> None:
    svc = Service(name="Example", url="https://example.com")
    session.add(svc)
    await session.commit()
    await session.refresh(svc)
    assert svc.expected_status == 200
    assert svc.check_interval_seconds == 30
    assert svc.is_active is True
    assert svc.is_public is True


async def test_check_belongs_to_service(session) -> None:
    svc = Service(name="Example", url="https://example.com")
    session.add(svc)
    await session.commit()

    check = Check(
        service_id=svc.id, status="up", http_status_code=200, response_time_ms=42
    )
    session.add(check)
    await session.commit()

    result = await session.scalar(select(Check).where(Check.id == check.id))
    assert result is not None
    assert result.status == "up"
    assert result.http_status_code == 200


async def test_alert_links_to_service(session) -> None:
    svc = Service(name="Example", url="https://example.com")
    session.add(svc)
    await session.commit()

    alert = Alert(service_id=svc.id, kind="down")
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    assert alert.id is not None
    assert alert.kind == "down"
    assert alert.sent_at is not None
