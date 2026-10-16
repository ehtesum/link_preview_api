# Project Work Definition (PWD) — LinkPreviewAPI

## 1. Executive Summary & Vision
LinkPreviewAPI is a high-throughput, low-latency URL metadata extraction, link validation, and OpenGraph enrichment REST API built with FastAPI and Redis. Modern web and chat applications (like Discord, Slack, Notion, and Twitter/X) rely heavily on rich preview cards (website title, summary description, hero image, favicon, domain, and author). Building custom scrapers for every project is error-prone, slow, and frequently blocked by anti-bot measures. LinkPreviewAPI provides a unified, cached endpoint that ingests any URL and returns structured social preview metadata in under 40 ms.

---

## 2. Core Value Proposition
- **Sub-50ms Cached Responses**: In-memory Redis caching prevents redundant external fetches for popular URLs.
- **Resilient Fallback Parsing**: Extracts metadata in priority order: OpenGraph (`og:*`), Twitter Cards (`twitter:*`), standard HTML `<meta>`, and Schema.org JSON-LD microdata.
- **Smart Asset Normalization**: Resolves relative image/favicon paths (e.g. `/assets/logo.png`) into absolute URLs automatically.
- **Dead Link & Safety Check**: Verifies HTTP response codes and flags broken redirects or malicious targets.
- **Developer-Friendly API**: Simple JSON response schema with built-in CORS support and API key rate limiting.

---

## 3. Target User Personas
- **Frontend & Mobile Developers**: Building chat apps, bookmark managers, social feeds, or CMS editors needing instant link previews.
- **Newsletter & Content Curators**: Automating link digests with pre-extracted titles, descriptions, and thumbnail graphics.
- **Internal Tool Builders**: Verifying partner links and tracking article publication metadata.

---

## 4. MVP Feature Scope
1. Primary endpoint: `GET /v1/preview?url=<target_url>`.
2. Metadata extraction: Title, Description, Image URL, Favicon URL, Site Name, Author, and Estimated Reading Time.
3. Redis caching layer with configurable Time-To-Live (TTL default: 24 hours).
4. Automatic timeout and User-Agent rotation to bypass basic scraper blocks.
5. Interactive Swagger / OpenAPI documentation UI at `/docs`.
