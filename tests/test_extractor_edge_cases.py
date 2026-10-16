import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from bs4 import BeautifulSoup
from app.extractor import fetch_and_extract_metadata

def test_extractor_handles_empty_html():
    async def run():
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://empty-example.com"
        mock_resp.content = b""

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            meta = await fetch_and_extract_metadata("https://empty-example.com")
            
            assert meta["title"] is None
            assert meta["description"] is None
            assert meta["image"] is None
            assert meta["domain"] == "empty-example.com"
            assert meta["favicon"] == "https://empty-example.com/favicon.ico"

    asyncio.run(run())

def test_extractor_handles_unicode_and_html_entities():
    async def run():
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta property="og:title" content="Python &amp; AI &mdash; 🚀 Future Tech">
            <meta property="og:description" content="&quot;Code is poetry&quot; &bull; 2026 Edition">
            <link rel="icon" href="/static/custom-favicon.png">
        </head>
        <body></body>
        </html>
        """.encode("utf-8")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://unicode-example.com/sub/page"
        mock_resp.content = html

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            meta = await fetch_and_extract_metadata("https://unicode-example.com/sub/page")

            assert "Python & AI — 🚀 Future Tech" in meta["title"]
            assert "\"Code is poetry\" • 2026 Edition" in meta["description"]
            assert meta["favicon"] == "https://unicode-example.com/static/custom-favicon.png"

    asyncio.run(run())

def test_extractor_relative_image_resolution():
    async def run():
        html = b"""
        <html>
        <head>
            <meta property="og:image" content="../images/hero.jpg">
        </head>
        </html>
        """
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.url = "https://media.org/articles/post-1"
        mock_resp.content = html

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_resp
            meta = await fetch_and_extract_metadata("https://media.org/articles/post-1")
            assert meta["image"] == "https://media.org/images/hero.jpg"

    asyncio.run(run())
