package scrapers

import (
	"github.com/fastzet/MetaStream/models"
)

// Scraper interface that all website scrapers must implement
type Scraper interface {
	// Name returns the display name of the video site
	Name() string
	
	// Enabled returns whether this scraper is active
	Enabled() bool
	
	// SearchURL generates the search URL for a given query
	SearchURL(query string) string
	
	// Scrape performs the actual scraping and returns video results
	Scrape(query string) ([]models.Video, error)
}

// Global registry of all scrapers
var scrapers []Scraper

// Register adds a scraper to the global registry
// Called automatically by each scraper's init() function
func Register(s Scraper) {
	scrapers = append(scrapers, s)
}

// GetAll returns all registered scrapers
func GetAll() []Scraper {
	return scrapers
}

// GetEnabled returns only enabled scrapers
func GetEnabled() []Scraper {
	var enabled []Scraper
	for _, s := range scrapers {
		if s.Enabled() {
			enabled = append(enabled, s)
		}
	}
	return enabled
}
