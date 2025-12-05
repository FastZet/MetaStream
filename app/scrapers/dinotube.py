import asyncio
from typing import List
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper
from app.core.models import VideoResult

class DinoTubeScraper(BaseScraper):
    def __init__(self):
        super().__init__(name="DinoTube", base_url="https://www.dinotube.com")

    async def search(self, query: str, page: int = 1) -> List[VideoResult]:
        formatted_query = query.replace(" ", "+")
        if page > 1:
            url = f"{self.base_url}/search/{formatted_query}?page={page}"
        else:
            url = f"{self.base_url}/search/{formatted_query}"

        soup = await self.get_soup(url)
        if not soup:
            return []

        results = []
        container = soup.select_one(".cards-container")
        if not container:
            return []

        cards = container.select(".card")
        
        for card in cards:
            try:
                link_tag = card.select_one("a.item-link")
                if not link_tag:
                    continue
                
                title = link_tag.get("title", "Unknown Title")
                href = link_tag.get("href", "")
                if href.startswith("/"):
                    video_url = f"{self.base_url}{href}"
                else:
                    video_url = href

                img_tag = card.select_one("img.item-image")
                thumbnail = "https://via.placeholder.com/320x180?text=No+Image"
                if img_tag:
                    thumbnail = img_tag.get("src") or img_tag.get("data-src") or thumbnail

                # --- NEW LOGIC FOR DURATION & QUALITY ---
                duration = "N/A"
                quality = None
                
                badge_tag = card.select_one(".badge.float-right")
                if badge_tag:
                    # Check for nested span (usually holds the 'HD' or '4K' text)
                    quality_span = badge_tag.select_one("span")
                    if quality_span:
                        quality = quality_span.get_text(strip=True)
                        # Remove the quality text from the full text to get just duration
                        # badge text: "4K 26:48" -> "26:48"
                        full_text = badge_tag.get_text(separator=" ", strip=True)
                        duration = full_text.replace(quality, "").strip()
                    else:
                        duration = badge_tag.get_text(strip=True)

                # --- NEW LOGIC FOR RATING ---
                rating = "N/A"
                rating_tag = card.select_one(".item-score")
                if rating_tag:
                    raw_rating = rating_tag.get_text(strip=True)
                    # Remove % sign so we just store the number (e.g. "54")
                    rating = raw_rating.replace("%", "")

                source_link = card.select_one("a.item-source")
                video_source = "DinoTube"
                if source_link:
                    video_source = source_link.get_text(strip=True)

                video = VideoResult(
                    title=title,
                    url=video_url,
                    thumbnail=thumbnail,
                    duration=duration,
                    rating=rating,
                    quality=quality, # Pass the quality
                    source=video_source,
                    views="N/A" # DinoTube search doesn't show views
                )
                results.append(video)

            except Exception as e:
                self.logger.error(f"Error parsing card: {e}")
                continue

        return results
