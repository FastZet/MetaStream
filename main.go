package main

import (
	"log"
	"os"
	"strconv"

	"github.com/fastzet/MetaStream/server"
)

func main() {
	// Default server port
	port := 8080

	// Override port from environment variable if set
	if p := os.Getenv("PORT"); p != "" {
		if parsed, err := strconv.Atoi(p); err == nil {
			port = parsed
		}
	}

	log.Println("Starting MetaStream server...")
	server.Run(port)
}
