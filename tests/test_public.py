async def test_public_page_empty(client) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert "No public services are currently being monitored." in response.text


async def test_public_page_with_services(client, db_session) -> None:
    from app.models import Service
    
    # Add a public service
    service = Service(
        name="Public API", 
        url="https://api.public.com", 
        is_public=True
    )
    db_session.add(service)
    await db_session.commit()

    response = await client.get("/")
    assert response.status_code == 200
    assert "Public API" in response.text
    assert "Wait for check" in response.text # Because we haven't created any Checks yet
