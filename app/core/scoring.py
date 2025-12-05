import re
from typing import List
from app.core.models import VideoResult
from app.core.logger import get_logger

logger = get_logger("core.scoring")

def parse_views(view_str: str) -> int:
    """
    Converts view strings (e.g., '1.2k', '1M', '500') into integers.
    """
    if not view_str or view_str == "N/A":
        return 0
    
    s = view_str.lower().replace(',', '').strip()
    try:
        if 'k' in s:
            return int(float(s.replace('k', '')) * 1000)
        elif 'm' in s:
            return int(float(s.replace('m', '')) * 1000000)
        elif 'b' in s: # Billions, rare but possible
            return int(float(s.replace('b', '')) * 1000000000)
        else:
            # Extract only digits just in case text surrounds it "500 views"
            digits = re.findall(r'\d+', s)
            return int(''.join(digits)) if digits else 0
    except Exception as e:
        logger.warning(f"Failed to parse view count '{view_str}': {e}")
        return 0

def parse_rating(rating_str: str) -> float:
    """
    Converts rating strings (e.g., '95%', '4.5', '9/10') into a 0-100 float.
    """
    if not rating_str or rating_str == "N/A":
        return 50.0  # Default neutral rating

    s = rating_str.replace('%', '').strip()
    
    try:
        # Handle "4.5/5" format
        if '/' in s:
            parts = s.split('/')
            return (float(parts[0]) / float(parts[1])) * 100
        
        val = float(s)
        
        # If value is small (e.g. 4.5), assume it is out of 5, scale to 100
        # If value is > 10, assume it is percentage
        if val <= 10:
            return val * 10  # 8.5 -> 85
            
        return val
    except Exception as e:
        logger.warning(f"Failed to parse rating '{rating_str}': {e}")
        return 50.0

def parse_duration_seconds(duration_str: str) -> int:
    """
    Converts duration (e.g. '10:05', '1h 20m', '5 min') to seconds.
    """
    if not duration_str or duration_str == "N/A":
        return 0
        
    try:
        # Simple case: MM:SS or HH:MM:SS
        if ':' in duration_str:
            parts = duration_str.split(':')
            if len(parts) == 2: # MM:SS
                return int(parts[0]) * 60 + int(parts[1])
            elif len(parts) == 3: # HH:MM:SS
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        
        # Text case: "5 min"
        nums = re.findall(r'\d+', duration_str)
        if nums:
            return int(nums[0]) * 60
            
        return 0
    except Exception:
        return 0

def calculate_score(video: VideoResult, query_terms: List[str]) -> float:
    """
    Main logic to assign a score to a video.
    """
    logger.debug(f"Scoring video: {video.title}")
    
    # 1. View Score (Logarithmic-ish cap)
    views = parse_views(video.views)
    # Cap at 1M views = 100 points
    view_score = min(views / 1000000, 1.0) * 100
    
    # 2. Rating Score
    rating_score = parse_rating(video.rating)
    
    # 3. Duration Score
    seconds = parse_duration_seconds(video.duration)
    duration_score = 0
    if seconds < 120: # < 2 mins
        duration_score = 20
    elif seconds < 600: # 2-10 mins
        duration_score = 60
    else: # > 10 mins
        duration_score = 100

    # 4. Title Relevance Bonus
    title_lower = video.title.lower()
    bonus = 0
    for term in query_terms:
        if term in title_lower:
            bonus += 5

    # Weights
    # Views: 40%, Rating: 40%, Duration: 20%
    final_score = (view_score * 0.4) + (rating_score * 0.4) + (duration_score * 0.2) + bonus
    
    logger.debug(f"Calculated Score: {final_score:.2f} (Views: {view_score}, Rating: {rating_score}, Dur: {duration_score}, Bonus: {bonus})")
    
    return final_score

def rank_results(results: List[VideoResult], query: str) -> List[VideoResult]:
    """
    Takes a list of raw results, calculates scores, and sorts them.
    """
    logger.info(f"Ranking {len(results)} videos for query: '{query}'")
    
    query_terms = query.lower().split()
    
    for video in results:
        video.score = calculate_score(video, query_terms)
        
    # Sort descending by score
    sorted_results = sorted(results, key=lambda x: x.score, reverse=True)
    
    return sorted_results
