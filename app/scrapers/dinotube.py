import asyncio
from typing import List, Dict, Any
from app.scrapers.base import BaseScraper
from app.core.models import VideoResult

class DinoTubeScraper(BaseScraper):
    def __init__(self):
        super().__init__(name="DinoTube", base_url="https://www.dinotube.com")

    async def search(self, query: str, page: int = 1, context: Dict[str, Any] = None) -> List[VideoResult]:
        if context is None:
            context = {}

        # --- SMART URL HANDLING ---
        # 1. If Page 1, we construct the default search URL.
        # 2. If Page > 1, we check if we have a 'resolved_url' in context from the previous page.
        
        url = ""
        
        if page == 1:
            # Initial Search
            formatted_query = query.replace(" ", "+")
            url = f"{self.base_url}/search/{formatted_query}"
        else:
            # Pagination
            if "dinotube_url" in context:
                # We have a saved pattern from Page 1 (e.g. https://www.dinotube.com/category/creampie)
                base = context["dinotube_url"]
                # Append page param. DinoTube usually handles ?page=X correctly on all resolved paths
                url = f"{base}?page={page}"
            else:
                # Fallback if cache missed or restarted
                formatted_query = query.replace(" ", "+")
                url = f"{self.base_url}/search/{formatted_query}?page={page}"

        # Fetch with redirect following enabled
        soup, final_url = await self.get_soup(url)
        
        if not soup:
            return []

        # SAVE CONTEXT
        # If we are on page 1, the 'final_url' is the source of truth for categories/stars.
        # We strip any existing query params to get the clean base.
        if page == 1 and final_url:
            clean_base = final_url.split('?')[0]
            context["dinotube_url"] = clean_base
            self.logger.info(f"Resolved DinoTube path for '{query}' -> {clean_base}")

        # --- PARSING LOGIC (Same as before) ---
        results = []
        container = soup.select_one(".cards-container")
        if not container:
            return []

        cards = container.select(".card")
        
        for card in cards:
            try:
                link_tag = card.select_one("a.item-link")
                if not link_tag: continue
                
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

                # Duration & Quality
                duration = "N/A"
                quality = None
                badge_tag = card.select_one(".badge.float-right")
                if badge_tag:
                    quality_span = badge_tag.select_one("span")
                    if quality_span:
                        quality = quality_span.get_text(strip=True)
                        full_text = badge_tag.get_text(separator=" ", strip=True)
                        duration = full_text.replace(quality, "").strip()
                    else:
                        duration = badge_tag.get_text(strip=True)

                # Rating
                rating = "N/A"
                rating_tag = card.select_one(".item-score")
                if rating_tag:
                    raw_rating = rating_tag.get_text(strip=True)
                    rating = raw_rating.replace("%", "")

                # Source
                source_link = card.select_one("a.item-source")
                video_source = "DinoTube"
                if source_link:
                    video_source = source_link.get_text(strip=True)

                video = VideoResult(
                    title=title, url=video_url, thumbnail=thumbnail,
                    duration=duration, rating=rating, quality=quality,
                    source=video_source, views="N/A"
                )
                results.append(video)

            except Exception as e:
                continue

        return results
