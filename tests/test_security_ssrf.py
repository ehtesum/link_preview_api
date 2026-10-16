import pytest
from app.ssrf import is_safe_url

@pytest.mark.parametrize("malicious_url", [
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://127.0.0.2",
    "http://localhost",
    "http://localhost:3000",
    "http://0.0.0.0",
    "http://10.0.0.1",
    "http://10.255.255.254",
    "http://172.16.0.1",
    "http://172.31.255.255",
    "http://192.168.1.1",
    "http://192.168.100.50",
    "http://169.254.169.254",  # AWS/GCP metadata service
    "http://169.254.169.254/latest/meta-data/",
    "http://[::1]",             # IPv6 loopback
    "file:///etc/passwd",
    "file:///C:/Windows/System32/drivers/etc/hosts",
    "gopher://127.0.0.1:6379/_PING",
    "ftp://example.com/test",
    "javascript:alert('xss')",
    "http://",
    "http:///index.html",
])
def test_ssrf_rejects_dangerous_targets(malicious_url):
    assert is_safe_url(malicious_url) is False

def test_ssrf_allows_standard_public_web_domains():
    assert is_safe_url("https://www.google.com") is True
    assert is_safe_url("https://github.com/torvalds/linux") is True
    assert is_safe_url("http://example.com/page?id=123") is True
