import random
from fastapi import FastAPI, Request, Response, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
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

# Mount Static Files
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
    engine.register_scraper(DinoTubeScraper())
    logger.info("Engine initialized and ready.")

# --- NEW: Health Check for Render ---
@app.get("/healthz")
@app.head("/")
async def health_check():
    return JSONResponse(content={"status": "ok"}, status_code=200)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, over_18: Optional[str] = Cookie(None)):
    if not over_18:
        logger.info("New user detected. Showing splash screen.")
        return templates.TemplateResponse("splash.html", {"request": request})
    
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "suggestions": random.sample(SUGGESTIONS, 6)
    })

@app.post("/enter")
async def enter_site():
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="over_18", value="true", max_age=60*60*24*30) 
    logger.info("User verified age. Setting cookie.")
    return response

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str, page: int = 1):
    if not q:
        return HTMLResponse("", status_code=200)

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
