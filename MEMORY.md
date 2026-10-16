# Memory & Performance Specification (MEMORY) — LinkPreviewAPI

## 1. Process Memory Footprint
- **Uvicorn Worker Baseline**: ~30 MB RAM per async worker process.
- **Maximum Ceiling**: Capped at 60 MB RAM under concurrent 500-request bursts.

---

## 2. Resource Optimization Strategy
- **Shared Async Client**: Maintains a single persistent `httpx.AsyncClient` with connection pooling (max 100 keep-alive connections) across the process lifecycle rather than instantiating client sessions per request.
- **Streaming HTML Head Parser**: Uses `lxml` / `BeautifulSoup` parsing with an early exit parser: reads only the `<head>...</head>` section of incoming HTML pages, closing the socket stream as soon as metadata is extracted without buffering the full page body.
