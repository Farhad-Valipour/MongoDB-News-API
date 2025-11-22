"""
Response schemas for API endpoints.
Defines standard response formats with pagination and metadata.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Generic, TypeVar
from datetime import datetime

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


class ResponseMetadata(BaseModel):
    """Response metadata with query performance and timestamp."""
    query_time_ms: float = Field(
        ...,
        description="Query execution time in milliseconds"
    )
    timestamp: str = Field(
        ...,
        description="Response timestamp (ISO 8601)"
    )
    api_version: str = Field(
        default="1.0.0",
        description="API version"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_time_ms": 45.32,
                "timestamp": "2025-11-22T00:15:23.445678",
                "api_version": "1.0.0"
            }
        }


class StandardResponse(BaseModel, Generic[DataT]):
    """Standard API response with success flag, data, pagination, and metadata."""
    success: bool = Field(
        True,
        description="Whether the request was successful"
    )
    data: List[DataT] = Field(..., description="Response data")
    pagination: Optional[PaginationMeta] = Field(
        None,
        description="Pagination metadata (for paginated endpoints)"
    )
    metadata: ResponseMetadata = Field(..., description="Response metadata")


class NewsListResponse(BaseModel):
    """Response for news list endpoint."""
    success: bool = Field(
        True,
        description="Whether the request was successful"
    )
    data: List[NewsListItem] = Field(..., description="List of news articles")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
    metadata: ResponseMetadata = Field(..., description="Response metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
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
                },
                "metadata": {
                    "query_time_ms": 45.32,
                    "timestamp": "2025-11-22T00:15:23.445678",
                    "api_version": "1.0.0"
                }
            }
        }


class NewsDetailResponse(BaseModel):
    """Response for single news detail endpoint."""
    success: bool = Field(
        True,
        description="Whether the request was successful"
    )
    data: NewsDetail = Field(..., description="News article details")
    metadata: ResponseMetadata = Field(..., description="Response metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "data": {
                    "slug": "bitcoin-hits-new-high",
                    "title": "Bitcoin Hits New All-Time High",
                    "subtitle": "Bitcoin surges past $50,000...",
                    "content": "<p>Full article content...</p>",
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
                    ],
                    "createdAt": "2025-02-26T12:05:00Z",
                    "updatedAt": "2025-02-26T12:05:00Z"
                },
                "metadata": {
                    "query_time_ms": 12.45,
                    "timestamp": "2025-11-22T00:15:23.445678",
                    "api_version": "1.0.0"
                }
            }
        }


class AggregationResponse(BaseModel):
    """Response for aggregation endpoints."""
    success: bool = Field(
        True,
        description="Whether the request was successful"
    )
    data: List[dict] = Field(..., description="Aggregation results")
    metadata: ResponseMetadata = Field(..., description="Response metadata")


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
    success: bool = Field(
        False,
        description="Always false for errors"
    )
    error: ErrorDetail = Field(..., description="Error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "Invalid query parameters",
                    "status": 400,
                    "timestamp": "2025-02-26T12:30:00Z"
                }
            }
        }
