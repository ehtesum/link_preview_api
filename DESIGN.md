# Design Specification (DESIGN) — LinkPreviewAPI

## 1. RESTful Endpoint Specification

### 1.1 `GET /v1/preview`
**Request Parameters:**
- `url` (string, required): The target webpage URL to parse.
- `refresh` (boolean, optional, default: false): If true, bypasses Redis cache and forces a fresh scrape.

**Success Response (HTTP 200 OK):**
```json
{
  "status": "success",
  "url": "https://github.com/ehtesum/localforge_ai_code",
  "domain": "github.com",
  "title": "ehtesum/localforge_ai_code: Private on-device coding assistant",
  "description": "Private, air-gapped developer copilot server & VS Code extension running local quantized code LLMs.",
  "image": "https://opengraph.githubassets.com/1/ehtesum/localforge_ai_code",
  "favicon": "https://github.githubassets.com/favicons/favicon.svg",
  "site_name": "GitHub",
  "author": "ehtesum",
  "reading_time_minutes": 2,
  "cached": true,
  "fetched_at": "2026-10-16T14:30:00Z"
}
```

**Error Response (HTTP 400 Bad Request):**
```json
{
  "status": "error",
  "code": "INVALID_URL",
  "message": "Target URL resolves to private loopback address (SSRF blocked)."
}
```

---

## 2. Interactive Swagger Documentation (`/docs`)
- Full OpenAPI 3.1 interactive interface allowing developers to test links live in the browser with parameter validation and cURL snippets.
