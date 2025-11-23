package server

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"path/filepath"

	"github.com/gorilla/mux"
	"github.com/fastzet/MetaStream/server/handlers"
)

// Serve static frontend and API
func Run(port int) {
	r := mux.NewRouter()

	// API endpoint
	r.HandleFunc("/api/search", handlers.SearchHandler).Methods("GET")

	// Serve static files from /web
	webDir := "./web"
	fs := http.FileServer(http.Dir(webDir))
	r.PathPrefix("/").Handler(http.StripPrefix("/", fs))

	addr := fmt.Sprintf(":%d", port)
	log.Printf("MetaStream server running at http://localhost%s ...", addr)

	// Try binding, fallback to port 0 if failed
	err := http.ListenAndServe(addr, r)
	if err != nil {
		log.Printf("Failed to bind on port %d: %v", port, err)
		log.Println("Trying random available port ...")
		addr2 := ":0"
		log.Fatal(http.ListenAndServe(addr2, r))
	}
}
