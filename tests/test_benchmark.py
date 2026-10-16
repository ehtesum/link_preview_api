import time
from app.cache import CacheManager

def test_cache_throughput_benchmark():
    cache = CacheManager()
    cache.redis_client = None # In-memory benchmark

    iterations = 5000
    sample_payload = {
        "title": "Benchmark Sample Title",
        "description": "Benchmark description content",
        "image": "https://example.com/image.png",
        "cached": True
    }

    start = time.perf_counter()
    for i in range(iterations):
        cache.set(f"https://bench{i}.com", sample_payload, ttl=300)
    write_duration = time.perf_counter() - start

    start = time.perf_counter()
    for i in range(iterations):
        val = cache.get(f"https://bench{i}.com")
        assert val is not None
    read_duration = time.perf_counter() - start

    # 5,000 in-memory set/get operations should take less than 0.5s total
    assert write_duration < 0.5
    assert read_duration < 0.5
