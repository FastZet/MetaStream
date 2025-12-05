# MetaStream

MetaStream is a specialized meta-search engine and video aggregator designed to provide a unified interface for searching content across multiple adult video streaming platforms. 

Unlike traditional indexers, MetaStream operates on a **Live Search** architecture. It does not maintain a local database of videos. Instead, it utilizes high-concurrency asynchronous scrapers to fetch, parse, and rank results from target websites in real-time when a user queries the system.

## 🚀 Key Features

*   **Live Aggregation:** Real-time scraping of target sources ensures results are always up-to-date. No dead links from old database entries.
*   **Modular Scraper Architecture:** Each target website is handled by an isolated scraper module. This ensures that if one site updates its HTML structure, only that specific module needs maintenance, without affecting the rest of the application.
*   **Smart Scoring System:** Results are not just listed; they are ranked based on a custom scoring algorithm that weighs metadata such as view count, rating, duration, and relevance.
*   **Privacy Focused:** No user tracking, no search history logging, and no persistent database.
*   **Single Container Deployment:** The entire application (Frontend + Backend) is packaged into a single Docker container for effortless deployment on any VPS or local machine.
*   **Modern Lightweight UI:** Built with **FastAPI**, **Jinja2**, **HTMX**, and **TailwindCSS** to provide a Single-Page-Application (SPA) feel without the overhead of heavy JavaScript frameworks.
*   **Compliance:** Includes a mandatory age-verification splash screen (18+).

## 🛠 Technology Stack

*   **Language:** Python 3.11+
*   **Web Framework:** FastAPI
*   **Concurrency:** Python `asyncio` & `httpx` (for parallel execution of scrapers)
*   **Parsing:** BeautifulSoup4 & lxml
*   **Frontend:** HTML5, Jinja2 Templates, HTMX, TailwindCSS via CDN
*   **Containerization:** Docker

## 📂 Project Structure

```text
metastream/
├── app/
│   ├── main.py              # Application entry point
│   ├── core/                # Core logic (Config, Scoring, Engine)
│   ├── scrapers/            # Isolated scraper modules for each site
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # Static assets (CSS/Images)
├── Dockerfile               # Container definition
└── requirements.txt         # Python dependencies
```

## ⚡ Quick Start (Docker)

This is the recommended way to run MetaStream.

1.  **Build the Image:**
    ```bash
    docker build -t metastream .
    ```

2.  **Run the Container:**
    ```bash
    docker run -d -p 8000:8000 --name metastream-app metastream
    ```

3.  **Access the App:**
    Open your browser and navigate to `http://localhost:8000`.

## 🔧 Development Setup (Local)

If you wish to contribute or develop new scraper modules locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/MetaStream.git
    cd MetaStream
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Server:**
    ```bash
    uvicorn app.main:app --reload
    ```

## 🧩 Adding New Scrapers

MetaStream is designed to be easily extensible. To add a new site:

1.  Create a new file in `app/scrapers/` (e.g., `site_x.py`).
2.  Inherit from the `BaseScraper` class found in `app/scrapers/base.py`.
3.  Implement the `search` method to parse HTML from the new site.
4.  Register the scraper in the main engine.

## ⚠️ Disclaimer

This application is intended for educational purposes regarding web scraping, asynchronous programming, and data aggregation. The developers are not responsible for the content hosted on the third-party websites accessed by this tool.
