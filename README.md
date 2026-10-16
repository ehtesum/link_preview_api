# LinkPreviewAPI 🔗

> High-throughput, SSRF-shielded OpenGraph and Twitter Card URL preview metadata extraction API with caching.

Building rich link previews (like those in Discord, Slack, iMessage, or Notion) sounds simple until you actually deploy it:
- Naive URL scrapers introduce severe **Server-Side Request Forgery (SSRF)** vulnerabilities (attackers feed `http://169.254.169.254` to steal AWS/GCP cloud instance credentials or port-scan your internal network).
- Target servers hang or send 100MB video files that exhaust your server RAM.
- Popular links get scraped hundreds of times redundantly.

**LinkPreviewAPI** is a production-ready, standalone microservice built with **FastAPI** that fetches, validates, and caches structured metadata (title, description, hero image, favicon, domain, and response time) in under 40 milliseconds.

---

## Key Features

- 🛡️ **Zero-Trust SSRF Shield**: Resolves hostnames to underlying IP addresses before connecting. Automatically blocks private subnets (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopbacks (`127.0.0.1`, `[::1]`), and cloud metadata services (`169.254.169.254`).
- ⚡ **Multi-Tier Caching**: Integrates with Redis (with automatic in-memory fallback when Redis is absent) for sub-1ms cached responses.
- 🎯 **Cascading Metadata Extraction**:
  - **Title**: `og:title` ➔ `twitter:title` ➔ HTML `<title>`
  - **Description**: `og:description` ➔ `twitter:description` ➔ `<meta name="description">`
  - **Image**: `og:image` ➔ `twitter:image` (auto-resolves relative URLs to absolute links)
  - **Favicon**: `<link rel="icon">` ➔ fallback to `/favicon.ico`
- 🔒 **Resource Safety Bounds**: Enforces a strict 5.0-second network timeout and limits response body ingestion to the first 1 MB to prevent RAM exhaustion.
- 📖 **Self-Documenting**: Auto-generates interactive Swagger and ReDoc documentation at `/docs`.

---

## API Reference

### `GET /v1/preview`

Extracts OpenGraph and social preview metadata for a given URL.

**Query Parameters:**
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `url` | `string` | **Yes** | Target webpage URL (e.g. `https://github.com/torvalds/linux`) |

#### Sample Request

```bash
curl -X GET "http://localhost:8000/v1/preview?url=https://github.com/torvalds/linux"
```

#### Sample Response (HTTP 200 OK)

```json
{
  "url": "https://github.com/torvalds/linux",
  "domain": "github.com",
  "title": "torvalds/linux: Linux kernel source tree",
  "description": "Linux kernel source tree. Contribute to torvalds/linux development by creating an account on GitHub.",
  "image": "https://opengraph.githubassets.com/1/torvalds/linux",
  "favicon": "https://github.githubassets.com/favicons/favicon.svg",
  "site_name": "GitHub",
  "status_code": 200,
  "response_time_ms": 38,
  "cached": false
}
```

---

## Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Framework** | FastAPI (ASGI) |
| **Async HTTP Client** | HTTPX (with connection pooling and redirect following) |
| **HTML Parser** | BeautifulSoup4 (using Python's fast native html.parser) |
| **Cache Layer** | Redis 5+ with in-memory TTL dictionary fallback |
| **Validation** | Pydantic v2 |
| **ASGI Server** | Uvicorn |

---

## Quickstart

### 1. Installation

```bash
git clone https://github.com/your-username/link_preview_api.git
cd link_preview_api

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run API Server

```bash
# Start development server
python run.py
```

The API will be live at `http://localhost:8000`. Open `http://localhost:8000/docs` in your browser for the interactive Swagger playground.

---

## Automated Test Suite

The test suite covers:
1. **SSRF Penetration Tests**: Verifies rejection of 20+ attack strings (hex notation, loopbacks, internal IPs, cloud metadata endpoints, `file:///` protocols).
2. **Edge-Case Parsing**: Malformed HTML, missing metadata tags, HTML entities, and relative path resolutions.
3. **Throughput Benchmarking**: Verifies that 5,000 in-memory cache operations execute in under 0.5 seconds.
4. **Endpoint Integration**: Tests `/health` and `/v1/preview` caching behavior via the FastAPI TestClient.

```bash
# Run all tests
python -m pytest

# Run with verbose output
python -m pytest -v
```

---

## Known Limitations

1. **Client-Rendered (SPA) Webpages**: Websites that generate all `<meta>` tags purely via client-side JavaScript (without SSR) will only yield the initial static HTML title/metadata.
2. **Aggressive Bot Protection**: Sites with strict Cloudflare Under Attack mode or Akamai bot walls may block requests despite standard User-Agent headers.
3. **Video Stream Previews**: Currently extracts static thumbnail images (`og:image`); does not extract embedded video streams (`og:video`).

---

## Future Work & Roadmap

- [ ] **Headless Browser Fallback**: Optional Playwright / Puppeteer worker pool to render heavy client-side React/Vue pages when static metadata is absent.
- [ ] **Image Dimension Verification**: Inspect extracted image URLs to ensure thumbnails meet minimum resolution standards (e.g., minimum 200x200 px).
- [ ] **Webhook / Batch Extraction**: Endpoint to accept a list of 50 URLs and return previews in parallel via background task workers.
- [ ] **oEmbed Support**: Native parser for YouTube, Twitter/X, and Spotify oEmbed JSON responses.

---

## License

MIT License. Built for developers needing reliable, secure link metadata.
