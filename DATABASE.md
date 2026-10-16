# Database & Cache Specification (DATABASE) — LinkPreviewAPI

## 1. Storage Architecture
- **Primary Cache Engine**: Redis 7+ (in-memory key-value store with LRU memory eviction).
- **Secondary Persistent DB (Optional)**: SQLite 3 for tracking developer API keys and usage rate limit quotas.

---

## 2. Redis Key Hierarchy & Data Modeling

### 2.1 Preview Cache Entries
- **Key Pattern**: `linkpreview:cache:<sha256(normalized_url)>`
- **Data Type**: String (JSON-encoded payload).
- **TTL**: 86,400 seconds (24 hours).

```redis
SET linkpreview:cache:a1b2c3... '{"title":"...","image":"..."}' EX 86400
```

### 2.2 Sliding-Window Rate Limit Entries
- **Key Pattern**: `linkpreview:ratelimit:<client_ip>:<minute_timestamp>`
- **Data Type**: Integer (Atomic increment counter).
- **TTL**: 120 seconds.

```redis
INCR linkpreview:ratelimit:203.0.113.19:29864230
EXPIRE linkpreview:ratelimit:203.0.113.19:29864230 120
```

---

## 3. Eviction & Memory Policies
- Redis `maxmemory-policy` set to `allkeys-lru` guaranteeing the database never crashes due to memory limits, automatically evicting oldest cached previews when memory ceiling is reached.
