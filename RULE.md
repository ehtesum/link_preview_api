# Engineering Rules & Guidelines (RULE) — LinkPreviewAPI

## 1. Network & SSRF Security Guardrails
- **RULE-01: Strict SSRF Filtering**: Before initiating any HTTP request, the target hostname MUST be resolved via DNS and checked against private/reserved IP blocks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.0/8`, `169.254.0.0/16`, `::1`). If matching, the request MUST be rejected immediately with HTTP 400.
- **RULE-02: Content-Length Cap**: Scraper requests MUST abort downloading if the response body exceeds 2.5 MB (HTML documents should never exceed this threshold) to prevent Zip-bomb / payload memory attacks.

---

## 2. Scraping Hygiene & Etiquette
- **RULE-03: Respectful User-Agent**: The HTTP client MUST declare an informative User-Agent (`LinkPreviewBot/1.0 (+https://github.com/ehtesum/link_preview_api)`) rather than generic bot strings.
- **RULE-04: Strict External Timeouts**: Target URL requests MUST enforce a connection timeout of 2.0 seconds and a read timeout of 3.0 seconds to prevent slowloris resource exhaustion.

---

## 3. Data Integrity Rules
- **RULE-05: Absolute URL Resolution**: All relative image links (`/banner.jpg`) MUST be resolved to absolute URLs (`https://example.com/banner.jpg`) using `urllib.parse.urljoin` before responding to clients.
