from sqlalchemy import select

from app.models import Service
from app.security import create_session_token


async def test_create_service_and_list(client, db_session) -> None:
    # Generate a valid session cookie
    token = create_session_token("admin@example.com")
    client.cookies.set("session", token)

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
