"""
News router.
Handles all news-related API endpoints.
"""

from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Annotated

from app.models.news import NewsListItem, NewsDetail
from app.models.request import NewsQueryParams
from app.models.response import NewsListResponse, ErrorResponse
from app.services.news_service import NewsService, get_news_service
from app.dependencies import get_db, get_current_api_key
from app.utils.exceptions import (
    NewsNotFoundException,
    InvalidCursorException,
    news_not_found_exception,
    invalid_cursor_exception
)
from app.utils.logger import log_info, log_error


router = APIRouter(prefix="/news", tags=["News"])


@router.get(
    "",
    response_model=NewsListResponse,
    summary="Get news list",
    description="Get paginated list of news articles with optional filters",
    responses={
        200: {"description": "Successful response with news list"},
        400: {"model": ErrorResponse, "description": "Invalid request parameters"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid API key"},
    }
)
async def get_news_list(
    from_date: Annotated[str | None, Query(description="Filter from date (ISO 8601)")] = None,
    to_date: Annotated[str | None, Query(description="Filter to date (ISO 8601)")] = None,
    source: Annotated[str | None, Query(description="Filter by source (coinmarketcap, bloomberg, reuters, ...)")] = None,
    asset_slug: Annotated[str | None, Query(description="Filter by asset slug")] = None,
    keyword: Annotated[str | None, Query(description="Search keyword", min_length=2, max_length=100)] = None,
    limit: Annotated[int, Query(description="Number of items per page", ge=10, le=1000)] = 100,
    cursor: Annotated[str | None, Query(description="Pagination cursor")] = None,
    sort_by: Annotated[str, Query(description="Sort field")] = "releasedAt",
    order: Annotated[str, Query(description="Sort order (asc/desc)")] = "desc",
    db: AsyncIOMotorDatabase = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get paginated list of news articles.
    
    **Filters:**
    - `from_date`: Filter news from this date
    - `to_date`: Filter news until this date
    - `source`: Filter by news source (e.g., coinmarketcap, bloomberg, reuters)
    - `asset_slug`: Filter by asset (e.g., bitcoin, ethereum)
    - `keyword`: Search in title and content
    
    **Pagination:**
    - `limit`: Number of items to return (10-1000)
    - `cursor`: Cursor from previous response for next page
    
    **Sorting:**
    - `sort_by`: Field to sort by (releasedAt, title, createdAt)
    - `order`: Sort order (asc, desc)
    """
    try:
        # Parse query parameters
        from datetime import datetime
        params_dict = {
            "limit": limit,
            "cursor": cursor,
            "sort_by": sort_by,
            "order": order,
        }
        
        if from_date:
            try:
                # Handle different date formats
                if 'Z' in from_date:
                    params_dict["from_date"] = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                else:
                    params_dict["from_date"] = datetime.fromisoformat(from_date)
            except ValueError as e:
                log_error("Invalid from_date format", error=str(e), from_date=from_date)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": {
                            "code": "INVALID_DATE_FORMAT",
                            "message": f"Invalid from_date format. Use ISO 8601 format (e.g., 2025-11-20 or 2025-11-20T10:30:00Z)",
                            "status": 400,
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                    }
                )
        
        if to_date:
            try:
                # Handle different date formats
                if 'Z' in to_date:
                    params_dict["to_date"] = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
                else:
                    params_dict["to_date"] = datetime.fromisoformat(to_date)
            except ValueError as e:
                log_error("Invalid to_date format", error=str(e), to_date=to_date)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": {
                            "code": "INVALID_DATE_FORMAT",
                            "message": f"Invalid to_date format. Use ISO 8601 format (e.g., 2025-11-20 or 2025-11-20T10:30:00Z)",
                            "status": 400,
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                    }
                )
        
        if source:
            params_dict["source"] = source
        if asset_slug:
            params_dict["asset_slug"] = asset_slug
        if keyword:
            params_dict["keyword"] = keyword
        
        params = NewsQueryParams(**params_dict)
        
        # Get news service
        news_service = NewsService(db)
        
        # Fetch news
        news_list, pagination = await news_service.get_news_list(params)
        
        # Log request
        log_info(
            "News list fetched",
            count=len(news_list),
            source=source,
            has_cursor=bool(cursor)
        )
        
        return NewsListResponse(
            data=[NewsListItem(**item) for item in news_list],
            pagination=pagination
        )
    
    except InvalidCursorException as e:
        log_error("Invalid cursor", error=str(e))
        raise invalid_cursor_exception()
    
    except ValueError as e:
        log_error("Invalid parameters", error=str(e))
        raise invalid_cursor_exception()
    
    except Exception as e:
        log_error("Unexpected error in get_news_list", error=str(e))
        raise


@router.get(
    "/{slug}",
    response_model=NewsDetail,
    summary="Get news by slug",
    description="Get detailed information about a specific news article",
    responses={
        200: {"description": "Successful response with news details"},
        404: {"model": ErrorResponse, "description": "News not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized - Invalid API key"},
    }
)
async def get_news_by_slug(
    slug: Annotated[str, Path(description="News article slug")],
    db: AsyncIOMotorDatabase = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get detailed information about a specific news article by its slug.
    
    **Parameters:**
    - `slug`: Unique identifier for the news article
    
    **Returns:**
    - Full news article including content, metadata, and related assets
    """
    try:
        # Get news service
        news_service = NewsService(db)
        
        # Fetch news
        news = await news_service.get_news_by_slug(slug)
        
        # Log request
        log_info("News detail fetched", slug=slug)
        
        return NewsDetail(**news)
    
    except NewsNotFoundException:
        log_error("News not found", slug=slug)
        raise news_not_found_exception(slug)
    
    except Exception as e:
        log_error("Unexpected error in get_news_by_slug", slug=slug, error=str(e))
        raise
