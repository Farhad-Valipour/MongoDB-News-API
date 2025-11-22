"""
Models package.
Exports all model classes for easy importing.
"""

from app.models.response import (
    NewsListResponse,
    NewsDetailResponse,
    AggregationResponse,
    ErrorResponse,
    PaginationMeta,
    ResponseMetadata
)
from app.models.news import NewsListItem, NewsDetail, Asset
from app.models.request import NewsQueryParams

__all__ = [
    # Response models
    "NewsListResponse",
    "NewsDetailResponse",
    "AggregationResponse",
    "ErrorResponse",
    "PaginationMeta",
    "ResponseMetadata",
    
    # News models
    "NewsListItem",
    "NewsDetail",
    "Asset",
    
    # Request models
    "NewsQueryParams",
]