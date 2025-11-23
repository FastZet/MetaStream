package scrapers

import (
	"fmt"
	"github.com/fastzet/MetaStream/models"
	"github.com/PuerkitoBio/goquery"
	"net/http"
	"net/url"
	"time"
)

// ExampleScraper - This is a template showing how to create scrapers
// Copy this file and modify for each video site you want to add
type ExampleScraper struct{}

// Name returns the display name shown in search results
func (s ExampleScraper) Name() string {
	return "Example Site"
}

// Enabled controls whether this scraper runs
// Set to false to temporarily disable without deleting the file
func (s ExampleScraper) Enabled() bool {
	return false // Set to true when you customize this for a real site
}

// SearchURL builds the search URL with the user's query
func (s ExampleScraper) SearchURL(query string) string {
	// CUSTOMIZE: Replace with actual site's search URL pattern
	return "https://example.com/search?q=" + url.QueryEscape(query)
}

// Scrape fetches and parses video results
func (s ExampleScraper) Scrape(query string) ([]models.Video, error) {
	var videos []models.Video
	
	// Make HTTP request
	searchURL := s.SearchURL(query)
	resp, err := http.Get(searchURL)
	if err != nil {
		return nil, fmt.Errorf("failed to fetch %s: %v", s.Name(), err)
	}
	defer resp.Body.Close()
	
	// Parse HTML
	doc, err := goquery.NewDocumentFromReader(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to parse HTML from %s: %v", s.Name(), err)
	}
	
	// Extract video data from search results
	// CUSTOMIZE: Change CSS selectors to match the actual site's HTML structure
	doc.Find(".video-item").Each(func(i int, sel *goquery.Selection) {
		// Extract each field using CSS selectors
		title := sel.Find(".video-title").Text()
		videoURL, _ := sel.Find("a.video-link").Attr("href")
		thumbnail, _ := sel.Find("img.thumbnail").Attr("src")
		duration := sel.Find(".duration").Text()
		views := sel.Find(".view-count").Text()
		uploader := sel.Find(".channel-name").Text()
		uploadDate := sel.Find(".upload-date").Text()
		
		// Only add if we got at least a title and URL
		if title != "" && videoURL != "" {
			video := models.Video{
				Site:        s.Name(),
				Title:       title,
				URL:         videoURL,
				Thumbnail:   thumbnail,
				Duration:    duration,
				Views:       views,
				Uploader:    uploader,
				UploadDate:  uploadDate,
				Description: "", // Add if site provides it
				ScrapedAt:   time.Now(),
			}
			videos = append(videos, video)
		}
	})
	
	return videos, nil
}

// Auto-register this scraper when package loads
func init() {
	Register(ExampleScraper{})
}
