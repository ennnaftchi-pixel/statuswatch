from unittest.mock import patch

from sqlalchemy import select

from app.models import Service
from app.security import create_session_token


async def test_create_service_and_list(client, db_session) -> None:
    # Generate a valid session cookie
    token = create_session_token("admin@example.com")
    client.cookies.set("session", token)

    # We mock 'is_safe_url' so it doesn't try to resolve the fake domain via DNS
    with patch("app.routes.admin.is_safe_url", return_value=True):
        # 1. Create a service via POST
        response = await client.post(
            "/admin/services/new",
            data={
                "name": "Test API",
                "url": "https://api.test.com",
                "expected_status": 200,
                "check_interval_seconds": 60,
            },
            follow_redirects=False,
        )
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/services"

    # 2. Verify it exists in the SQLite database
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

    # Here we do NOT mock it, so it should genuinely block 'localhost'
    response = await client.post(
        "/admin/services/new",
        data={
            "name": "Internal DB",
            "url": "http://localhost:5432",
            "expected_status": 200,
            "check_interval_seconds": 60,
        },
        follow_redirects=False,
    )
    assert response.status_code == 200
    # We just check for "Invalid URL" to avoid whitespace/HTML escaping issues
    assert "Invalid URL" in response.text
