import asyncio
import time
from typing import List, Dict
from app.core.logger import get_logger
from app.core.models import VideoResult
from app.core.scoring import rank_results
from app.scrapers.base import BaseScraper

# Initialize logger
logger = get_logger("core.engine")

class SearchEngine:
    """
    The central controller that dispatches queries to all registered scrapers,
    collects the results, and applies the ranking algorithm.
    """
    def __init__(self):
        self.scrapers: List[BaseScraper] = []

    def register_scraper(self, scraper: BaseScraper):
        """
        Adds a new scraper module to the engine.
        """
        self.scrapers.append(scraper)
        logger.info(f"Registered scraper module: {scraper.name}")

    async def search(self, query: str, page: int = 1) -> Dict:
        """
        Executes the search across all registered scrapers in parallel.
        """
        start_time = time.time()
        logger.info(f"=== Starting search for '{query}' (Page {page}) across {len(self.scrapers)} sources ===")

        if not self.scrapers:
            logger.warning("No scrapers registered! Returning empty results.")
            return {"results": [], "count": 0, "time": 0.0}

        # Create a list of async tasks (one for each scraper)
        tasks = [scraper.search(query, page) for scraper in self.scrapers]

        # Run all tasks simultaneously
        # return_exceptions=True prevents one failed scraper from crashing the whole search
        results_list = await asyncio.gather(*tasks, return_exceptions=True)

        aggregated_results: List[VideoResult] = []

        # Process results from each task
        for i, result in enumerate(results_list):
            scraper_name = self.scrapers[i].name
            
            if isinstance(result, Exception):
                # Log the error but continue with other results
                logger.error(f"Scraper '{scraper_name}' failed with error: {str(result)}")
            elif isinstance(result, list):
                logger.debug(f"Scraper '{scraper_name}' returned {len(result)} videos.")
                aggregated_results.extend(result)
            else:
                logger.warning(f"Scraper '{scraper_name}' returned unexpected data type: {type(result)}")

        # Rank the combined results
        sorted_results = rank_results(aggregated_results, query)
        
        elapsed_time = time.time() - start_time
        logger.info(f"=== Search completed in {elapsed_time:.2f}s. Total valid results: {len(sorted_results)} ===")

        return {
            "results": sorted_results,
            "count": len(sorted_results),
            "time": round(elapsed_time, 2),
            "page": page
        }

# Global Engine Instance
engine = SearchEngine()
