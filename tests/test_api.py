import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from bs4 import BeautifulSoup

from app.main import app
from app.ssrf import is_safe_url
from app.cache import CacheManager
from app.extractor import fetch_and_extract_metadata

client = TestClient(app)

def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_ssrf_blocks_private_and_loopback_ips():
    assert is_safe_url("http://127.0.0.1") is False
    assert is_safe_url("http://localhost") is False
    assert is_safe_url("http://10.0.0.1") is False
    assert is_safe_url("http://192.168.1.1") is False
    assert is_safe_url("http://169.254.169.254/latest/meta-data") is False
    assert is_safe_url("ftp://example.com") is False

def test_ssrf_allows_public_domain():
    # Public domains like google.com or github.com should be safe
    assert is_safe_url("https://github.com") is True

def test_preview_endpoint_blocks_ssrf():
    res = client.get("/v1/preview?url=http://127.0.0.1:8080/admin")
    assert res.status_code == 400
    assert "Forbidden URL target" in res.json()["detail"]

def test_cache_manager():
    cache = CacheManager()
    cache.redis_client = None  # Ensure in-memory fallback is active
    
    test_url = "https://example.com/page"
    sample_data = {"url": test_url, "title": "Example Page"}
    
    assert cache.get(test_url) is None
    cache.set(test_url, sample_data, ttl=60)
    
    cached = cache.get(test_url)
    assert cached is not None
    assert cached["title"] == "Example Page"

def test_preview_endpoint_success_and_caching():
    sample_meta = {
        "url": "https://example.com",
        "domain": "example.com",
        "title": "Example Domain",
        "description": "Example description",
        "image": "https://example.com/og.png",
        "favicon": "https://example.com/favicon.ico",
        "site_name": "Example",
        "status_code": 200,
        "response_time_ms": 42,
        "cached": False,
    }

    with patch("app.main.is_safe_url", return_value=True):
        with patch("app.main.fetch_and_extract_metadata", new_callable=AsyncMock) as mock_fetch:
            mock_fetch.return_value = sample_meta

            # First fetch (cache miss)
            res = client.get("/v1/preview?url=https://example.com")
            assert res.status_code == 200
            data = res.json()
            assert data["title"] == "Example Domain"
            assert data["cached"] is False

            # Second fetch (should hit cache)
            res2 = client.get("/v1/preview?url=https://example.com")
            assert res2.status_code == 200
            data2 = res2.json()
            assert data2["cached"] is True
