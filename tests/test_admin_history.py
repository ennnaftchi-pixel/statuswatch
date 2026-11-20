
from app.models import Check, Service
from app.security import create_session_token


async def test_service_history(client, db_session) -> None:
    # 1. Setup a service and some checks
    service = Service(name="History Test", url="https://example.com")
    db_session.add(service)
    await db_session.commit()

    check1 = Check(service_id=service.id, status="up", http_status_code=200, response_time_ms=50)
    check2 = Check(service_id=service.id, status="down", http_status_code=500, response_time_ms=100, error_message="Server Error")
    db_session.add_all([check1, check2])
    await db_session.commit()

    # 2. Authenticate
    token = create_session_token("admin@example.com")
    client.cookies.set("session", token)

    # 3. Request the history page
    response = await client.get(f"/admin/services/{service.id}/history")
    
    # 4. Verify the HTML contains our data
    assert response.status_code == 200
    assert "History: History Test" in response.text
    assert "50 ms" in response.text
    assert "100 ms" in response.text
    assert "Server Error" in response.text
