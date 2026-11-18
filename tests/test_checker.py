from unittest.mock import AsyncMock, patch

import httpx
import pytest
from sqlalchemy import select

from app.checker import probe_service
from app.models import Check, Service


@pytest.mark.asyncio
async def test_probe_service_success(db_session):
    service = Service(name="Test", url="https://test.com", expected_status=200)
    db_session.add(service)
    await db_session.commit()

    mock_response = AsyncMock()
    mock_response.status_code = 200
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        async with httpx.AsyncClient() as client:
            with patch("app.checker.SessionLocal", return_value=db_session):
                await probe_service(client, service)

    checks = (await db_session.scalars(select(Check))).all()
    assert len(checks) == 1
    assert checks[0].status == "up"
    assert checks[0].http_status_code == 200


@pytest.mark.asyncio
async def test_probe_service_down(db_session):
    service = Service(name="Test", url="https://test.com", expected_status=200)
    db_session.add(service)
    await db_session.commit()

    mock_response = AsyncMock()
    mock_response.status_code = 500
    
    with patch("httpx.AsyncClient.get", return_value=mock_response):
        async with httpx.AsyncClient() as client:
            with patch("app.checker.SessionLocal", return_value=db_session):
                await probe_service(client, service)

    checks = (await db_session.scalars(select(Check))).all()
    assert len(checks) == 1
    assert checks[0].status == "down"
    assert checks[0].http_status_code == 500
