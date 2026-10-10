from .base import BaseScraperPlugin
from backend.src.schemas.scrapers import RawPost
from.loader import load_sources
import httpx
import asyncio
import selectolax
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
class WebScraperPlugin(BaseScraperPlugin):
    async def fetch(self) -> list[RawPost]:
        sources = load_sources("web")
        async with httpx.AsyncClient(headers=HEADERS, timeout=15.0) as client:
          response = client.get(sources[0].url)
          response.raise_for_status()
          


        return []
