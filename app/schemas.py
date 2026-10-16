from typing import Optional
from pydantic import BaseModel, HttpUrl

class LinkPreviewResponse(BaseModel):
    url: str
    domain: str
    title: Optional[str] = None
    description: Optional[str] = None
    image: Optional[str] = None
    favicon: Optional[str] = None
    site_name: Optional[str] = None
    status_code: int = 200
    response_time_ms: int
    cached: bool = False

class ErrorResponse(BaseModel):
    detail: str
    url: Optional[str] = None
