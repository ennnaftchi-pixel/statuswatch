from httpx import ASGITransport, AsyncClient

from app.main import app
from app.security import (
    create_session_token,
    hash_password,
    verify_password,
    verify_session_token,
)


def test_password_hashing() -> None:
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_session_token() -> None:
    token = create_session_token("test@example.com")
    assert verify_session_token(token) == "test@example.com"
    
    # Tampered token should fail
    assert verify_session_token("invalid.token.string") is None


async def test_login_page_renders() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/admin/login")
        assert response.status_code == 200
        assert "Admin Login" in response.text
