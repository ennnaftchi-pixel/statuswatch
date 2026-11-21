from unittest.mock import AsyncMock, patch

from sqlalchemy import select

from app.models import Service
from app.security import create_session_token


async def test_create_service_and_list(client, db_session) -> None:
    token = create_session_token("admin@example.com")
    client.cookies.set("session", token)

    # We use AsyncMock here because is_safe_url is now async
    with patch("app.routes.admin.is_safe_url", new_callable=AsyncMock, return_value=True):
        response = await client.post(
            "/admin/services/new",
            data={"name": "Test API", "url": "https://api.test.com", "expected_status": 200, "check_interval_seconds": 60},
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/services"

    stmt = select(Service).where(Service.name == "Test API")
    service = await db_session.scalar(stmt)
    assert service is not None
    assert service.url == "https://api.test.com"
    assert service.is_active is True


async def test_unauthorized_access_redirects(client) -> None:
    response = await client.get("/admin/services", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/admin/login"


async def test_ssrf_blocked_url(client) -> None:
    token = create_session_token("admin@example.com")
    client.cookies.set("session", token)

    # No mock here, the real async function runs
    response = await client.post(
        "/admin/services/new",
        data={"name": "Internal DB", "url": "http://localhost:5432", "expected_status": 200, "check_interval_seconds": 60},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert "Invalid URL" in response.text
