import httpx
import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional
from bs4 import BeautifulSoup
from app.core.config import settings
from app.core.models import VideoResult
from app.core.logger import get_logger

class BaseScraper(ABC):
    """
    Abstract Base Class for all Video Scrapers.
    Handles HTTP requests, logging, and error management.
    """

    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.logger = get_logger(f"scraper.{name}")
        
        # Standard headers to mimic a real browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """
        Fetches the URL and returns a BeautifulSoup object.
        Includes excessive logging for debugging.
        """
        self.logger.debug(f"Initiating HTTP GET request to: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=settings.SCRAPER_TIMEOUT, follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers)
                
                self.logger.debug(f"Received response from {url}. Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    self.logger.error(f"Failed to fetch {url}. Status: {response.status_code}. Response: {response.text[:200]}...")
                    return None
                
                self.logger.debug(f"Successfully fetched {len(response.text)} bytes from {url}. Parsing HTML...")
                return BeautifulSoup(response.text, "lxml")

        except httpx.TimeoutException:
            self.logger.error(f"Timeout exceeded ({settings.SCRAPER_TIMEOUT}s) while connecting to {url}")
            return None
        except httpx.RequestError as e:
            self.logger.error(f"Network error while connecting to {url}: {str(e)}")
            return None
        except Exception as e:
            self.logger.exception(f"Unexpected error in get_soup for {url}: {str(e)}")
            return None

    @abstractmethod
    async def search(self, query: str, page: int = 1) -> List[VideoResult]:
        """
        Abstract method. Must be implemented by child classes.
        Should return a list of VideoResult objects.
        """
        pass
