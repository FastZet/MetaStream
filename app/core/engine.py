import asyncio
import time
from typing import List, Dict, Any
from app.core.logger import get_logger
from app.core.models import VideoResult
from app.core.scoring import rank_results
from app.scrapers.base import BaseScraper

logger = get_logger("core.engine")

class SearchEngine:
    def __init__(self):
        self.scrapers: List[BaseScraper] = []
        
        # Cache Structure:
        # {
        #   "current_query": "creampie",
        #   "context": { "dinotube_url": "..." },
        #   "pages": { 
        #       1: [VideoResult, ...], 
        #       2: [VideoResult, ...] 
        #   }
        # }
        self.cache: Dict[str, Any] = {
            "current_query": "",
            "context": {},
            "pages": {}
        }

    def register_scraper(self, scraper: BaseScraper):
        self.scrapers.append(scraper)
        logger.info(f"Registered scraper: {scraper.name}")

    async def search(self, query: str, page: int = 1) -> Dict:
        start_time = time.time()
        
        # 1. Check if Query Changed -> Clear Cache
        if self.cache["current_query"] != query:
            logger.info(f"New query detected. Clearing cache for '{query}'")
            self.cache["current_query"] = query
            self.cache["context"] = {} # Reset scraping context (redirects)
            self.cache["pages"] = {}

        # 2. Check Cache for this Page
        if page in self.cache["pages"]:
            logger.info(f"Serving Page {page} from Cache")
            results = self.cache["pages"][page]
            
            # Trigger prefetch for next page (if not cached)
            if (page + 1) not in self.cache["pages"]:
                asyncio.create_task(self._fetch_and_cache(query, page + 1))
                
            return {
                "results": results,
                "count": len(results),
                "time": 0.01,
                "page": page
            }

        # 3. Live Fetch (if not in cache)
        logger.info(f"Fetching Page {page} live...")
        results = await self._fetch_and_cache(query, page)
        
        # Trigger prefetch for next page
        asyncio.create_task(self._fetch_and_cache(query, page + 1))

        elapsed_time = time.time() - start_time
        return {
            "results": results,
            "count": len(results),
            "time": round(elapsed_time, 2),
            "page": page
        }

    async def _fetch_and_cache(self, query: str, page: int) -> List[VideoResult]:
        """
        Internal method to run scrapers, rank, and store in cache.
        """
        if not self.scrapers:
            return []

        # Pass the shared context (e.g. for DinoTube redirects)
        tasks = [scraper.search(query, page, self.cache["context"]) for scraper in self.scrapers]
        
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        aggregated_results: List[VideoResult] = []

        for result in results_list:
            if isinstance(result, list):
                aggregated_results.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraper error: {result}")

        # Rank
        sorted_results = rank_results(aggregated_results, query)
        
        # Store in Cache
        if sorted_results:
            self.cache["pages"][page] = sorted_results
            logger.info(f"Cached {len(sorted_results)} results for Page {page}")
        
        return sorted_results

engine = SearchEngine()
