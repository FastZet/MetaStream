import logging
import sys
from app.core.config import settings

def setup_logging():
    """
    Configures the root logger based on settings.
    Ensures logs are output to stdout for Docker capture.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.DEBUG)
    
    # Create a handler that writes to stdout (standard output)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # Define the log format
    formatter = logging.Formatter(settings.LOG_FORMAT)
    handler.setFormatter(formatter)
    
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers to avoid duplicates if re-initialized
    if root_logger.handlers:
        root_logger.handlers = []
        
    root_logger.addHandler(handler)
    
    # Explicitly set levels for third-party libraries to match our verbosity
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("httpx").setLevel(log_level)
    logging.getLogger("fastapi").setLevel(log_level)

def get_logger(name: str) -> logging.Logger:
    """
    Utility to get a logger with a specific name.
    Usage: logger = get_logger(__name__)
    """
    return logging.getLogger(name)
