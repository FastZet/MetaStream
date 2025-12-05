from pydantic import BaseModel, Field
from typing import List, Optional

class VideoResult(BaseModel):
    """
    Standardized data structure for a single video result.
    All scrapers must return data mapped to this schema.
    """
    title: str
    url: str
    thumbnail: str
    source: str  # The name of the site (e.g., "Site A")
    
    # Optional Metadata
    duration: Optional[str] = "N/A"
    views: Optional[str] = "N/A"
    rating: Optional[str] = "N/A"
    uploader: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    # Internal usage for sorting
    score: float = 0.0

class SearchQuery(BaseModel):
    """
    Structure for an incoming user search request.
    """
    query: str
    page: int = 1

class ScraperResponse(BaseModel):
    """
    What a specific scraper module returns to the main engine.
    """
    results: List[VideoResult]
    scraper_name: str
    count: int
    error: Optional[str] = None
  
