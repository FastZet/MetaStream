package scrapers

// This file exists to ensure all scrapers are imported and registered.
// Add new scraper .go files to this import list.

import (
	_ "github.com/fastzet/MetaStream/scrapers/example_scraper" // Import example scraper

	// Add imports for your other scrapers here:
	// _ "github.com/YOUR_USERNAME/MetaStream/scrapers/another_scraper"
)
