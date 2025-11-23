package handlers

import (
	"encoding/json"
	"net/http"
	"strings"
	"time"

	"github.com/fastzet/MetaStream/models"
	"github.com/fastzet/MetaStream/scrapers"
)

// SearchHandler serves /api/search?query=video_term
func SearchHandler(w http.ResponseWriter, r *http.Request) {
	q := strings.TrimSpace(r.URL.Query().Get("query"))
	start := time.Now()

	result := models.SearchResult{
		Query: q,
	}

	if q == "" {
		http.Error(w, "Missing ?query=", http.StatusBadRequest)
		return
	}

	found := []models.Video{}
	failedSites := []string{}

	// Query all enabled scrapers (run sequentially for simplicity)
	for _, scraper := range scrapers.GetEnabled() {
		videos, err := scraper.Scrape(q)
		if err != nil {
			failedSites = append(failedSites, scraper.Name())
			continue
		}
		found = append(found, videos...)
	}

	result.Videos = found
	result.TotalResults = len(found)
	result.ScrapedSites = len(scrapers.GetEnabled())
	result.FailedSites = failedSites
	result.SearchTimeMs = time.Since(start).Milliseconds()

	// Return as JSON
	w.Header().Set("Content-Type", "application/json")
	_ = json.NewEncoder(w).Encode(result)
}
