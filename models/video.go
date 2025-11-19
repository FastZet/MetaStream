package models

import "time"

// Video represents a single video result from any site
type Video struct {
	Site        string    `json:"site"`         // Name of the video site
	Title       string    `json:"title"`        // Video title
	URL         string    `json:"url"`          // Direct link to video
	Thumbnail   string    `json:"thumbnail"`    // Thumbnail image URL
	Duration    string    `json:"duration"`     // Video length (e.g., "12:34")
	Views       string    `json:"views"`        // View count
	UploadDate  string    `json:"upload_date"`  // When video was uploaded
	Uploader    string    `json:"uploader"`     // Channel/user name
	Description string    `json:"description"`  // Short description
	ScrapedAt   time.Time `json:"scraped_at"`   // When we scraped this
}

// SearchResult represents the complete search response
type SearchResult struct {
	Query         string   `json:"query"`           // Search term used
	Videos        []Video  `json:"videos"`          // All video results
	TotalResults  int      `json:"total_results"`   // Number of videos found
	ScrapedSites  int      `json:"scraped_sites"`   // Number of sites searched
	FailedSites   []string `json:"failed_sites"`    // Sites that had errors
	SearchTimeMs  int64    `json:"search_time_ms"`  // How long search took
}
