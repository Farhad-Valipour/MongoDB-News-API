"""Utils module initialization."""

from app.utils.exceptions import (
    NewsAPIException,
    NewsNotFoundException,
    InvalidCursorException,
    DatabaseConnectionException,
    RateLimitExceededException,
    create_http_exception,
    news_not_found_exception,
    invalid_cursor_exception,
    rate_limit_exception,
)
from app.utils.logger import logger, log_info, log_error, log_warning, log_debug

__all__ = [
    "NewsAPIException",
    "NewsNotFoundException",
    "InvalidCursorException",
    "DatabaseConnectionException",
    "RateLimitExceededException",
    "create_http_exception",
    "news_not_found_exception",
    "invalid_cursor_exception",
    "rate_limit_exception",
    "logger",
    "log_info",
    "log_error",
    "log_warning",
    "log_debug",
]
