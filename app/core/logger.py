import logging
import sys
from app.core.config import settings

class EndpointFilter(logging.Filter):
    """
    Filter to exclude specific endpoints from logs (e.g., health checks).
    """
    def filter(self, record: logging.LogRecord) -> bool:
        return record.getMessage().find("/healthz") == -1

def setup_logging():
    """
    Configures the root logger based on settings.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.DEBUG)
    
    # Create a handler that writes to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Define the log format
    formatter = logging.Formatter(settings.LOG_FORMAT)
    handler.setFormatter(formatter)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clean up existing handlers
    if root_logger.handlers:
        root_logger.handlers = []
        
    root_logger.addHandler(handler)
    
    # Set levels for libraries
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("httpx").setLevel(log_level)
    logging.getLogger("fastapi").setLevel(log_level)

    # --- SUPPRESS HEALTH LOGS ---
    # Get the uvicorn access logger and add the filter
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_access_logger.addFilter(EndpointFilter())

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
