async def test_health(client) -> None:
    response = await client.get("/health")
    assert response.json() == {"status": "ok"}
