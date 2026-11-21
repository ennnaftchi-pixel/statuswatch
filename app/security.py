import asyncio
import ipaddress
import time
from urllib.parse import urlparse

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from pwdlib import PasswordHash

from app.config import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

session_serializer = URLSafeTimedSerializer(settings.app_secret_key)

def create_session_token(email: str) -> str:
    return session_serializer.dumps({"email": email})

def verify_session_token(token: str, max_age_seconds: int = 86400) -> str | None:
    try:
        data = session_serializer.loads(token, max_age=max_age_seconds)
        return data.get("email")
    except (BadSignature, SignatureExpired):
        return None

# Fix Bug 6: Use async getaddrinfo instead of blocking socket
async def is_safe_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        hostname = parsed.hostname
        if not hostname:
            return False

        loop = asyncio.get_running_loop()
        results = await loop.getaddrinfo(hostname, None)
        for res in results:
            ip = res[4][0]
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                return False
        return True
    except Exception:
        return False

login_attempts: dict[str, list[float]] = {}
MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60

def is_rate_limited(ip: str) -> bool:
    now = time.time()
    if ip in login_attempts:
        login_attempts[ip] = [t for t in login_attempts[ip] if now - t < WINDOW_SECONDS]
        if len(login_attempts[ip]) >= MAX_ATTEMPTS:
            return True
    return False

def record_failed_attempt(ip: str) -> None:
    if ip not in login_attempts:
        login_attempts[ip] = []
    login_attempts[ip].append(time.time())
