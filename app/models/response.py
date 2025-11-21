"""
Response schemas for API endpoints.
Defines standard response formats with pagination.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Generic, TypeVar

from app.models.news import NewsListItem, NewsDetail


DataT = TypeVar('DataT')


class PaginationMeta(BaseModel):
    """Pagination metadata for cursor-based pagination."""
    next_cursor: Optional[str] = Field(
        None,
        description="Cursor for next page (null if no more items)"
    )
    prev_cursor: Optional[str] = Field(
        None,
        description="Cursor for previous page (null if first page)"
    )
    has_next: bool = Field(..., description="Whether there are more items")
    has_prev: bool = Field(..., description="Whether there are previous items")
    limit: int = Field(..., description="Number of items requested")
    returned: int = Field(..., description="Number of items actually returned")
    
    class Config:
        json_schema_extra = {
            "example": {
                "next_cursor": "eyJfaWQiOiI2NWUxMjM0NTY3ODkwYWJjZGVmMDEyMzQiLCJyZWxlYXNlZEF0IjoiMjAyNS0wMi0yNlQxMjowMDowMFoifQ==",
                "prev_cursor": None,
                "has_next": True,
                "has_prev": False,
                "limit": 100,
                "returned": 100
            }
        }


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Generic paginated response."""
    data: List[DataT] = Field(..., description="List of items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")


class NewsListResponse(BaseModel):
    """Response for news list endpoint."""
    data: List[NewsListItem] = Field(..., description="List of news articles")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "slug": "bitcoin-hits-new-high",
                        "title": "Bitcoin Hits New All-Time High",
                        "subtitle": "Bitcoin surges past $50,000...",
                        "source": "coinmarketcap",
                        "sourceName": "CoinMarketCap News",
                        "sourceUrl": "https://coinmarketcap.com/...",
                        "releasedAt": "2025-02-26T12:00:00Z",
                        "assets": [
                            {
                                "name": "Bitcoin",
                                "slug": "bitcoin",
                                "symbol": "BTC"
                            }
                        ]
                    }
                ],
                "pagination": {
                    "next_cursor": "eyJ...",
                    "prev_cursor": None,
                    "has_next": True,
                    "has_prev": False,
                    "limit": 100,
                    "returned": 1
                }
            }
        }


class ErrorDetail(BaseModel):
    """Error detail schema."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    status: int = Field(..., description="HTTP status code")
    timestamp: str = Field(..., description="Error timestamp (ISO 8601)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "NEWS_NOT_FOUND",
                "message": "News article with slug 'xyz' not found",
                "status": 404,
                "timestamp": "2025-02-26T12:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: ErrorDetail = Field(..., description="Error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "Invalid query parameters",
                    "status": 400,
                    "timestamp": "2025-02-26T12:30:00Z"
                }
            }
        }
