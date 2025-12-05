import httpx
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from bs4 import BeautifulSoup
from app.core.config import settings
from app.core.models import VideoResult
from app.core.logger import get_logger

class BaseScraper(ABC):
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.logger = get_logger(f"scraper.{name}")
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def get_soup(self, url: str) -> tuple[Optional[BeautifulSoup], str]:
        """
        Fetches the URL and returns (BeautifulSoup, Final_URL).
        Returns (None, "") on failure.
        """
        self.logger.debug(f"Initiating HTTP GET request to: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=settings.SCRAPER_TIMEOUT, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                
                # Check for redirects or success
                self.logger.debug(f"Response: {response.status_code} | URL: {response.url}")
                
                if response.status_code != 200:
                    self.logger.error(f"Failed {url} - {response.status_code}")
                    return None, ""
                
                return BeautifulSoup(response.text, "lxml"), str(response.url)

        except Exception as e:
            self.logger.exception(f"Error fetching {url}: {str(e)}")
            return None, ""

    @abstractmethod
    async def search(self, query: str, page: int = 1, context: Dict[str, Any] = None) -> List[VideoResult]:
        pass
