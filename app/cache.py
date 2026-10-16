import os
import json
import time
import hashlib
from typing import Optional, Dict, Any

REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
DEFAULT_TTL = 86400 # 24 hours

class CacheManager:
    def __init__(self):
        self.redis_client = None
        self.memory_store: Dict[str, tuple[float, str]] = {} # key -> (expiry, data)

        try:
            import redis
            client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=1)
            client.ping()
            self.redis_client = client
        except Exception:
            # Fallback to internal memory cache
            self.redis_client = None

    def _hash_key(self, url: str) -> str:
        return f"linkpreview:{hashlib.sha256(url.encode()).hexdigest()}"

    def get(self, url: str) -> Optional[Dict[str, Any]]:
        key = self._hash_key(url)

        if self.redis_client:
            try:
                cached = self.redis_client.get(key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
        else:
            if key in self.memory_store:
                expiry, val = self.memory_store[key]
                if time.time() < expiry:
                    return json.loads(val)
                del self.memory_store[key]

        return None

    def set(self, url: str, data: Dict[str, Any], ttl: int = DEFAULT_TTL) -> None:
        key = self._hash_key(url)
        val = json.dumps(data)

        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, val)
                return
            except Exception:
                pass

        # In-memory store
        self.memory_store[key] = (time.time() + ttl, val)

cache = CacheManager()
