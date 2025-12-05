import random
from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional

from app.core.config import settings
from app.core.logger import setup_logging, get_logger
from app.core.engine import engine

# --- Scraper Imports ---
from app.scrapers.dinotube import DinoTubeScraper

# Setup Logging
setup_logging()
logger = get_logger("main")

# Initialize App
app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Mount Static Files (CSS/Images)
# Ensure the folder 'app/static' exists
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup Templates
templates = Jinja2Templates(directory="app/templates")

# Search Suggestions
SUGGESTIONS = [
    "stepmom", "japanese", "massage", "hentai", "milf", 
    "amateur", "ebony", "pov", "teacher", "vr", "latina", 
    "threesome", "office", "lesbian", "casting"
]

@app.on_event("startup")
async def startup_event():
    """
    Register scrapers on startup.
    """
    logger.info("Starting MetaStream Engine...")
    
    # --- Register Scrapers Here ---
    engine.register_scraper(DinoTubeScraper())
    
    logger.info("Engine initialized and ready.")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, over_18: Optional[str] = Cookie(None)):
    """
    Root route. 
    Checks for 'over_18' cookie.
    If missing -> Show Splash Screen.
    If present -> Show Home Page.
    """
    if not over_18:
        logger.info("New user detected. Showing splash screen.")
        return templates.TemplateResponse("splash.html", {"request": request})
    
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "suggestions": random.sample(SUGGESTIONS, 6)
    })

@app.post("/enter")
async def enter_site():
    """
    Sets the age verification cookie and redirects to home.
    """
    response = RedirectResponse(url="/", status_code=303)
    # Cookie lasts 30 days
    response.set_cookie(key="over_18", value="true", max_age=60*60*24*30) 
    logger.info("User verified age. Setting cookie.")
    return response

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str, page: int = 1):
    """
    Search route used by HTMX.
    Returns the 'results.html' partial fragment, not a full page.
    """
    if not q:
        return HTMLResponse("", status_code=200)

    # Execute search via the Engine
    data = await engine.search(q, page)
    
    return templates.TemplateResponse("results.html", {
        "request": request,
        "results": data["results"],
        "count": data["count"],
        "time": data["time"],
        "page": data["page"],
        "query": q
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
