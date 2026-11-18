from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pwdlib import PasswordHash

from app.config import settings

# 1. Password Hashing
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

# 2. Session Tokens
session_serializer = URLSafeTimedSerializer(settings.app_secret_key)

def create_session_token(email: str) -> str:
    return session_serializer.dumps({"email": email})

def verify_session_token(token: str, max_age_seconds: int = 86400) -> str | None:
    try:
        data = session_serializer.loads(token, max_age=max_age_seconds)
        return data.get("email")
    except (BadSignature, SignatureExpired):
        return None
