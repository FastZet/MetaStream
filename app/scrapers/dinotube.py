import asyncio
from typing import List
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.core.models import VideoResult

class DinoTubeScraper(BaseScraper):
    def __init__(self):
        super().__init__(name="DinoTube", base_url="https://www.dinotube.com")

    async def search(self, query: str, page: int = 1) -> List[VideoResult]:
        # DinoTube search URL format: /search/{query}?page={page}
        # Note: They use hyphens for spaces usually, but URL encoding works too.
        formatted_query = query.replace(" ", "+")
        if page > 1:
            url = f"{self.base_url}/search/{formatted_query}?page={page}"
        else:
            url = f"{self.base_url}/search/{formatted_query}"

        soup = await self.get_soup(url)
        if not soup:
            return []

        results = []
        
        # The container for results
        container = soup.select_one(".cards-container")
        if not container:
            self.logger.warning(f"No card container found for query: {query}")
            return []

        # Find all individual video cards
        cards = container.select(".card")
        
        for card in cards:
            try:
                # 1. Title and URL
                link_tag = card.select_one("a.item-link")
                if not link_tag:
                    continue
                
                title = link_tag.get("title", "Unknown Title")
                href = link_tag.get("href", "")
                
                # Handle relative URLs
                if href.startswith("/"):
                    video_url = f"{self.base_url}{href}"
                else:
                    video_url = href

                # 2. Thumbnail
                img_tag = card.select_one("img.item-image")
                thumbnail = "https://via.placeholder.com/320x180?text=No+Image"
                if img_tag:
                    thumbnail = img_tag.get("src") or img_tag.get("data-src") or thumbnail

                # 3. Duration
                # The badge might contain "HD" or "4K" text as well, so we clean it.
                duration_tag = card.select_one(".badge.float-right")
                duration = "N/A"
                if duration_tag:
                    # Get text, strip whitespace
                    raw_text = duration_tag.get_text(separator=" ", strip=True)
                    # Simple cleanup: remove "HD" or "4K" if present to just get time
                    clean_text = raw_text.replace("HD", "").replace("4K", "").replace("VR", "").strip()
                    if clean_text:
                        duration = clean_text

                # 4. Rating
                rating_tag = card.select_one(".item-score")
                rating = "N/A"
                if rating_tag:
                    rating = rating_tag.get_text(strip=True)

                # 5. Source (The site hosting the video, e.g., Eporner)
                # It's usually in the footer area
                source_tag = card.select_one(".item-source")
                video_source = "DinoTube"
                if source_tag:
                    text = source_tag.get_text(strip=True)
                    # Sometimes text implies date "4 days ago", we want the one that isn't a date
                    # But usually the site name is the anchor tag inside .item-source-rating-container
                    # Let's try to be specific:
                    source_link = card.select_one("a.item-source")
                    if source_link:
                        video_source = source_link.get_text(strip=True)

                # 6. Views
                # DinoTube search cards don't explicitly show view counts in the provided HTML.
                # We will leave it as N/A or try to parse if we find it later.
                views = "N/A"

                video = VideoResult(
                    title=title,
                    url=video_url,
                    thumbnail=thumbnail,
                    duration=duration,
                    rating=rating,
                    source=video_source,
                    views=views
                )
                results.append(video)

            except Exception as e:
                self.logger.error(f"Error parsing card: {e}")
                continue

        self.logger.info(f"Parsed {len(results)} videos from DinoTube")
        return results
