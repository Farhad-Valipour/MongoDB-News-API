"""
Logging configuration.
Sets up structured logging for the application.
"""

import logging
import sys
from typing import Any

from app.config import settings


def setup_logger() -> logging.Logger:
    """
    Setup and configure application logger.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("news_api")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Create formatter
    if settings.DEBUG:
        # Detailed format for development
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        # JSON-like format for production
        formatter = logging.Formatter(
            fmt='{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":"%(message)s"}',
            datefmt="%Y-%m-%dT%H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


# Global logger instance
logger = setup_logger()


def log_info(message: str, **kwargs: Any):
    """Log info message with optional context."""
    extra_info = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    full_message = f"{message} | {extra_info}" if extra_info else message
    logger.info(full_message)


def log_error(message: str, **kwargs: Any):
    """Log error message with optional context."""
    extra_info = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    full_message = f"{message} | {extra_info}" if extra_info else message
    logger.error(full_message)


def log_warning(message: str, **kwargs: Any):
    """Log warning message with optional context."""
    extra_info = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    full_message = f"{message} | {extra_info}" if extra_info else message
    logger.warning(full_message)


def log_debug(message: str, **kwargs: Any):
    """Log debug message with optional context."""
    extra_info = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    full_message = f"{message} | {extra_info}" if extra_info else message
    logger.debug(full_message)
