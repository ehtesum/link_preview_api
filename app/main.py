from fastapi import FastAPI, Query, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import httpx

from .schemas import LinkPreviewResponse, ErrorResponse
from .ssrf import is_safe_url
from .extractor import fetch_and_extract_metadata
from .cache import cache

app = FastAPI(
    title="LinkPreviewAPI",
    description="High-throughput OpenGraph & Twitter Card URL metadata extraction API with caching and SSRF shield.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "LinkPreviewAPI"}

@app.get(
    "/v1/preview",
    response_model=LinkPreviewResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or unsafe URL"},
        504: {"model": ErrorResponse, "description": "Target website timed out"},
    },
    tags=["Link Preview"]
)
async def get_link_preview(
    url: str = Query(..., description="Target webpage URL to extract preview metadata from")
):
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url

    if not is_safe_url(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forbidden URL target. Private and loopback IP addresses are blocked."
        )

    cached_data = cache.get(url)
    if cached_data:
        cached_data["cached"] = True
        return LinkPreviewResponse(**cached_data)

    try:
        data = await fetch_and_extract_metadata(url)
        cache.set(url, data)
        return LinkPreviewResponse(**data)
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"Target URL {url} timed out after 5.0 seconds."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to scrape URL: {str(e)}"
        )
