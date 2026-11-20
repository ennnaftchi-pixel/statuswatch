from app.security import is_rate_limited, is_safe_url, record_failed_attempt


def test_ssrf_valid_urls():
    assert is_safe_url("https://google.com") is True
    assert is_safe_url("http://example.com/api") is True

def test_ssrf_invalid_schemes():
    assert is_safe_url("file:///etc/passwd") is False
    assert is_safe_url("ftp://example.com") is False

def test_ssrf_internal_ips():
    assert is_safe_url("http://localhost:8000") is False
    assert is_safe_url("http://127.0.0.1") is False
    assert is_safe_url("http://192.168.1.1") is False
    assert is_safe_url("http://172.17.0.1") is False
    assert is_safe_url("http://169.254.169.254") is False # AWS metadata IP

def test_rate_limiting():
    test_ip = "1.2.3.4"
    # Not limited initially
    assert is_rate_limited(test_ip) is False
    
    # Record 5 failed attempts
    for _ in range(5):
        record_failed_attempt(test_ip)
        
    # Now it should be limited
    assert is_rate_limited(test_ip) is True
