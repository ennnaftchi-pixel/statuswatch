async def test_metrics_endpoint(client) -> None:
    response = await client.get("/metrics")
    assert response.status_code == 200
    # Check that our custom metric is in the response payload
    assert "statuswatch_service_up" in response.text
    assert "statuswatch_checks_total" in response.text
