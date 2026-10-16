import time
from urllib.parse import urlparse, urljoin
from typing import Dict, Any, Optional
import httpx
from bs4 import BeautifulSoup

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
MAX_BYTES = 1024 * 1024 # 1 MB maximum response size to parse

async def fetch_and_extract_metadata(target_url: str) -> Dict[str, Any]:
    start_time = time.perf_counter()
    parsed_domain = urlparse(target_url).netloc

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

    async with httpx.AsyncClient(follow_redirects=True, timeout=5.0) as client:
        response = await client.get(target_url, headers=headers)
        status_code = response.status_code

        # Read only up to MAX_BYTES
        content = response.content[:MAX_BYTES]

    soup = BeautifulSoup(content, "html.parser")

    # Title: og:title -> twitter:title -> <title>
    title = None
    og_title = soup.find("meta", property="og:title") or soup.find("meta", attrs={"name": "og:title"})
    tw_title = soup.find("meta", attrs={"name": "twitter:title"})
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()
    elif tw_title and tw_title.get("content"):
        title = tw_title["content"].strip()
    elif soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Description: og:description -> twitter:description -> meta description
    description = None
    og_desc = soup.find("meta", property="og:description") or soup.find("meta", attrs={"name": "og:description"})
    tw_desc = soup.find("meta", attrs={"name": "twitter:description"})
    meta_desc = soup.find("meta", attrs={"name": "description"})
    if og_desc and og_desc.get("content"):
        description = og_desc["content"].strip()
    elif tw_desc and tw_desc.get("content"):
        description = tw_desc["content"].strip()
    elif meta_desc and meta_desc.get("content"):
        description = meta_desc["content"].strip()

    # Image: og:image -> twitter:image
    image = None
    og_img = soup.find("meta", property="og:image") or soup.find("meta", attrs={"name": "og:image"}) or soup.find("meta", property="og:image:url")
    tw_img = soup.find("meta", attrs={"name": "twitter:image"})
    if og_img and og_img.get("content"):
        image = og_img["content"].strip()
    elif tw_img and tw_img.get("content"):
        image = tw_img["content"].strip()

    if image:
        image = urljoin(str(response.url), image)

    # Favicon
    favicon = None
    icon_link = soup.find("link", rel=lambda r: r and "icon" in r.lower())
    if icon_link and icon_link.get("href"):
        favicon = urljoin(str(response.url), icon_link["href"].strip())
    else:
        favicon = urljoin(str(response.url), "/favicon.ico")

    # Site name
    og_site = soup.find("meta", property="og:site_name")
    site_name = og_site["content"].strip() if og_site and og_site.get("content") else parsed_domain

    elapsed_ms = int((time.perf_counter() - start_time) * 1000)

    return {
        "url": str(response.url),
        "domain": parsed_domain,
        "title": title,
        "description": description,
        "image": image,
        "favicon": favicon,
        "site_name": site_name,
        "status_code": status_code,
        "response_time_ms": elapsed_ms,
        "cached": False,
    }
