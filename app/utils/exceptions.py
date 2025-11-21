"""
Custom exceptions for the application.
Provides specific error types for better error handling.
"""

from fastapi import HTTPException, status


class NewsAPIException(Exception):
    """Base exception for News API."""
    pass


class NewsNotFoundException(NewsAPIException):
    """Exception raised when a news article is not found."""
    
    def __init__(self, message: str = "News article not found"):
        self.message = message
        super().__init__(self.message)


class InvalidCursorException(NewsAPIException):
    """Exception raised when a pagination cursor is invalid."""
    
    def __init__(self, message: str = "Invalid cursor format"):
        self.message = message
        super().__init__(self.message)


class DatabaseConnectionException(NewsAPIException):
    """Exception raised when database connection fails."""
    
    def __init__(self, message: str = "Failed to connect to database"):
        self.message = message
        super().__init__(self.message)


class RateLimitExceededException(NewsAPIException):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        self.message = message
        super().__init__(self.message)


def create_http_exception(
    status_code: int,
    error_code: str,
    message: str
) -> HTTPException:
    """
    Create a formatted HTTP exception.
    
    Args:
        status_code: HTTP status code
        error_code: Application-specific error code
        message: Human-readable error message
    
    Returns:
        HTTPException: Formatted exception
    """
    from datetime import datetime
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error": {
                "code": error_code,
                "message": message,
                "status": status_code,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    )


def news_not_found_exception(slug: str) -> HTTPException:
    """Create a 404 exception for news not found."""
    return create_http_exception(
        status_code=status.HTTP_404_NOT_FOUND,
        error_code="NEWS_NOT_FOUND",
        message=f"News article with slug '{slug}' not found"
    )


def invalid_cursor_exception() -> HTTPException:
    """Create a 400 exception for invalid cursor."""
    return create_http_exception(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_code="INVALID_CURSOR",
        message="Invalid pagination cursor format"
    )


def rate_limit_exception() -> HTTPException:
    """Create a 429 exception for rate limit exceeded."""
    return create_http_exception(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        error_code="RATE_LIMIT_EXCEEDED",
        message="Too many requests. Please try again later."
    )
