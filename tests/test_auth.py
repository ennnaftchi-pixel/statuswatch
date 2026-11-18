from app.security import (
    hash_password,
    verify_password,
    create_session_token,
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


async def test_login_page_renders(client) -> None:
    response = await client.get("/admin/login")
    assert response.status_code == 200
    assert "Admin Login" in response.text
