import pytest

from app.security import is_rate_limited, is_safe_url, record_failed_attempt


@pytest.mark.asyncio
async def test_ssrf_valid_urls():
    assert await is_safe_url("https://google.com") is True
    assert await is_safe_url("http://example.com/api") is True

@pytest.mark.asyncio
async def test_ssrf_invalid_schemes():
    assert await is_safe_url("file:///etc/passwd") is False
    assert await is_safe_url("ftp://example.com") is False

@pytest.mark.asyncio
async def test_ssrf_internal_ips():
    assert await is_safe_url("http://localhost:8000") is False
    assert await is_safe_url("http://127.0.0.1") is False
    assert await is_safe_url("http://192.168.1.1") is False
    assert await is_safe_url("http://172.17.0.1") is False
    assert await is_safe_url("http://169.254.169.254") is False

def test_rate_limiting():
    test_ip = "1.2.3.4"
    assert is_rate_limited(test_ip) is False
    for _ in range(5):
        record_failed_attempt(test_ip)
    assert is_rate_limited(test_ip) is True
