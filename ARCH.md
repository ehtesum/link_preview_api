# Architecture Specification (ARCH) — LinkPreviewAPI

## 1. High-Level System Architecture

```
+--------------------------------------------------------------------------+
|                     Client Applications & Developers                     |
|           (Web Apps, Chat Clients, CMS, Mobile Applications)             |
+--------------------------------------------------------------------------+
                                     │ HTTP GET /v1/preview?url=...
                                     ▼
+--------------------------------------------------------------------------+
|                       FastAPI Asynchronous Gateway                       |
|                                                                          |
|  +---------------------+   +---------------------+   +----------------+  |
|  | URL Validator &     |──▶| Redis Cache Layer   |──▶| Response       |  |
|  | SSRF Shield         |   | (Check SHA-256 Key) |   | Serializer     |  |
|  +---------------------+   +---------------------+   +----------------+  |
|                                       │ (Cache Miss)          ▲          |
|                                       ▼                       │          |
|                            +---------------------+            │          |
|                            | Async HTTP Scraper  |────────────┘          |
|                            | (httpx connection   |                       |
|                            |  pool + early exit) |                       |
|                            +---------------------+                       |
+--------------------------------------------------------------------------+
             │                                              │
             ▼                                              ▼
+--------------------------+                  +----------------------------+
| Redis Cache (Port 6379)  |                  | Target Webpage Server      |
| - 24hr TTL Cache Entries |                  | (External Internet Host)   |
| - Rate Limiting Windows  |                  +----------------------------+
+--------------------------+
```

---

## 2. Request Lifecycle Sequence

```
1. Client sends GET `/v1/preview?url=https://news.ycombinator.com`
2. Rate-Limiting middleware checks client IP in Redis (rejects if > 60 req/min)
3. SSRF Shield resolves DNS and verifies IP is public
4. Redis Cache Check:
   - Key: `linkpreview:cache:<hash>`
   - If HIT: Return cached JSON immediately (Latency ~10ms)
5. If MISS:
   - Async HTTP request sent with connection pool & 4s timeout
   - Reads HTML stream until `</head>` is parsed
   - Extracts OpenGraph, Twitter, and standard meta tags
   - Resolves relative URLs into absolute URLs
   - Writes result to Redis with 24h TTL
   - Returns JSON response with `X-Cache: MISS` header (Latency ~80-350ms)
```
