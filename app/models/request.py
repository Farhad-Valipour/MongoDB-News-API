"""
Request schemas for API endpoints.
Defines query parameters and validation rules.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

from app.config import settings


class SortOrder(str, Enum):
    """Sort order enum."""
    ASC = "asc"
    DESC = "desc"


class SortField(str, Enum):
    """Available fields for sorting."""
    RELEASED_AT = "releasedAt"
    TITLE = "title"
    CREATED_AT = "createdAt"


class NewsQueryParams(BaseModel):
    """
    Query parameters for news list endpoint.
    Supports filtering, sorting, and pagination.
    """
    # Filters
    from_date: Optional[datetime] = Field(
        None,
        description="Filter news from this date (ISO 8601 format)"
    )
    to_date: Optional[datetime] = Field(
        None,
        description="Filter news until this date (ISO 8601 format)"
    )
    source: Optional[str] = Field(
        None,
        description="Filter by news source (e.g., coinmarketcap, bloomberg, reuters)"
    )
    asset_slug: Optional[str] = Field(
        None,
        description="Filter by asset slug (e.g., bitcoin, ethereum)"
    )
    keyword: Optional[str] = Field(
        None,
        description="Search keyword in title and content",
        min_length=2,
        max_length=100
    )
    
    # Pagination
    limit: int = Field(
        default=settings.DEFAULT_PAGE_LIMIT,
        ge=settings.MIN_PAGE_LIMIT,
        le=settings.MAX_PAGE_LIMIT,
        description=f"Number of items to return ({settings.MIN_PAGE_LIMIT}-{settings.MAX_PAGE_LIMIT})"
    )
    cursor: Optional[str] = Field(
        None,
        description="Cursor for next page (from previous response)"
    )
    
    # Sorting
    sort_by: SortField = Field(
        default=SortField.RELEASED_AT,
        description="Field to sort by"
    )
    order: SortOrder = Field(
        default=SortOrder.DESC,
        description="Sort order (asc or desc)"
    )
    
    @field_validator("from_date", "to_date")
    @classmethod
    def validate_dates(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure dates are not in the future."""
        if v:
            # Handle both timezone-aware and timezone-naive datetimes
            from datetime import timezone
            now = datetime.now(timezone.utc)
            
            # Make v timezone-aware if it's naive
            if v.tzinfo is None:
                # Assume UTC for naive datetimes
                v = v.replace(tzinfo=timezone.utc)
            
            if v > now:
                raise ValueError("Date cannot be in the future")
        return v
    
    @field_validator("to_date")
    @classmethod
    def validate_date_range(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Ensure to_date is after from_date."""
        from_date = info.data.get("from_date")
        if v and from_date and v < from_date:
            raise ValueError("to_date must be after from_date")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "from_date": "2025-01-01T00:00:00Z",
                "to_date": "2025-02-01T23:59:59Z",
                "source": "bloomberg",
                "asset_slug": "bitcoin",
                "keyword": "regulation",
                "limit": 50,
                "cursor": None,
                "sort_by": "releasedAt",
                "order": "desc"
            }
        }
