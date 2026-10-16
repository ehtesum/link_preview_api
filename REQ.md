# Requirements Specification (REQ) — LinkPreviewAPI

## 1. Functional Requirements (FR)

### FR-01: Metadata Ingestion & Parsing
- The API MUST accept a URL query parameter (`url`) via HTTP GET.
- The scraper MUST validate URL schemes (only `http://` and `https://` permitted; private IPs `127.0.0.1`, `10.0.0.0/8`, `192.168.0.0/16` blocked to prevent SSRF).
- The parser MUST extract:
  - `title`: `og:title` -> `twitter:title` -> `<title>` tag.
  - `description`: `og:description` -> `twitter:description` -> `meta[name="description"]`.
  - `image`: `og:image` -> `twitter:image` -> first salient `<img>` in body.
  - `favicon`: `link[rel="icon"]` -> `link[rel="shortcut icon"]` -> `/favicon.ico`.
  - `site_name`: `og:site_name` -> domain hostname.

### FR-02: Caching & Latency Constraints
- Extracted payloads MUST be cached in Redis with a 24-hour expiration TTL.
- Cache hits MUST respond with HTTP header `X-Cache: HIT` and complete in < 20 ms.
- Cache misses MUST respond with `X-Cache: MISS` and enforce a hard 4.0-second timeout on external target requests.

### FR-03: Rate Limiting
- The API MUST enforce sliding-window rate limiting per client IP or API key (e.g. 60 requests/minute for unauthenticated requests).

---

## 2. Non-Functional Requirements (NFR)

### NFR-01: Concurrency & Async I/O
- Built on asynchronous ASGI (FastAPI + `httpx.AsyncClient` with connection pooling) capable of handling 500 concurrent in-flight requests on 1 CPU core.

### NFR-02: Security & SSRF Protection
- Target URLs MUST be checked against private/loopback IP address ranges prior to socket connection to prevent Server-Side Request Forgery (SSRF) against internal VPC services.
