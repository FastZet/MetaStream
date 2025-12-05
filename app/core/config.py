import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MetaStream"
    VERSION: str = "0.1.0"
    
    # Logging configuration
    # set to DEBUG for "painfully excessive" details
    LOG_LEVEL: str = "DEBUG" 
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Scraper settings
    # Time in seconds to wait for a specific scraper before skipping it
    SCRAPER_TIMEOUT: int = 15 
    
    # Application settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
