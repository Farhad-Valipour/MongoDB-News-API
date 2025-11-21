"""
Aggregation router.
Provides endpoints for news analytics and statistics.
"""

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Annotated, Optional
from datetime import datetime

from app.services.aggregation_service import AggregationService
from app.dependencies import get_db, get_current_api_key
from app.utils.logger import log_info


router = APIRouter(prefix="/aggregations", tags=["Aggregations"])


@router.get(
    "/stats",
    summary="Get news statistics",
    description="Get aggregated news statistics grouped by various dimensions"
)
async def get_stats(
    group_by: Annotated[str, Query(description="Group by: source, date")] = "source",
    from_date: Annotated[str | None, Query(description="Filter from date (ISO 8601)")] = None,
    to_date: Annotated[str | None, Query(description="Filter to date (ISO 8601)")] = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get aggregated news statistics.
    
    **Supported group_by values:**
    - `source`: Group by news source
    - `date`: Group by date (daily timeline)
    
    **Example:**
    ```
    GET /api/v1/aggregations/stats?group_by=source&from_date=2025-11-01&to_date=2025-11-30
    ```
    """
    # Parse dates
    parsed_from_date = None
    parsed_to_date = None
    
    if from_date:
        parsed_from_date = datetime.fromisoformat(from_date.replace('Z', '+00:00') if 'Z' in from_date else from_date)
    if to_date:
        parsed_to_date = datetime.fromisoformat(to_date.replace('Z', '+00:00') if 'Z' in to_date else to_date)
    
    # Get aggregation service
    agg_service = AggregationService(db)
    
    # Execute aggregation based on group_by
    if group_by == "source":
        data = await agg_service.get_stats_by_source(parsed_from_date, parsed_to_date)
        total = sum(item["count"] for item in data)
    elif group_by == "date":
        data = await agg_service.get_timeline("daily", parsed_from_date, parsed_to_date)
        total = sum(item["count"] for item in data)
    else:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Invalid group_by value: {group_by}")
    
    log_info("Stats aggregation completed", group_by=group_by, results=len(data))
    
    return {
        "data": data,
        "total": total,
        "filters": {
            "group_by": group_by,
            "from_date": from_date,
            "to_date": to_date
        }
    }


@router.get(
    "/top-assets",
    summary="Get top mentioned assets",
    description="Get the most frequently mentioned assets in news"
)
async def get_top_assets(
    limit: Annotated[int, Query(description="Number of top assets", ge=1, le=100)] = 10,
    from_date: Annotated[str | None, Query(description="Filter from date (ISO 8601)")] = None,
    to_date: Annotated[str | None, Query(description="Filter to date (ISO 8601)")] = None,
    source: Annotated[str | None, Query(description="Filter by source")] = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get most mentioned assets in news.
    
    Returns list of assets with their mention counts and percentages.
    
    **Example:**
    ```
    GET /api/v1/aggregations/top-assets?limit=10&source=bloomberg
    ```
    """
    # Parse dates
    parsed_from_date = None
    parsed_to_date = None
    
    if from_date:
        parsed_from_date = datetime.fromisoformat(from_date.replace('Z', '+00:00') if 'Z' in from_date else from_date)
    if to_date:
        parsed_to_date = datetime.fromisoformat(to_date.replace('Z', '+00:00') if 'Z' in to_date else to_date)
    
    # Get aggregation service
    agg_service = AggregationService(db)
    
    # Get top assets
    data = await agg_service.get_top_assets(limit, parsed_from_date, parsed_to_date, source)
    
    log_info("Top assets fetched", limit=limit, results=len(data))
    
    return {
        "data": data,
        "filters": {
            "limit": limit,
            "from_date": from_date,
            "to_date": to_date,
            "source": source
        }
    }


@router.get(
    "/timeline",
    summary="Get news timeline",
    description="Get news count over time with configurable intervals"
)
async def get_timeline(
    interval: Annotated[str, Query(description="Time interval: daily, weekly, monthly")] = "daily",
    from_date: Annotated[str | None, Query(description="Filter from date (ISO 8601)")] = None,
    to_date: Annotated[str | None, Query(description="Filter to date (ISO 8601)")] = None,
    source: Annotated[str | None, Query(description="Filter by source")] = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get news count over time.
    
    **Supported intervals:**
    - `daily`: Group by day
    - `weekly`: Group by week
    - `monthly`: Group by month
    
    **Example:**
    ```
    GET /api/v1/aggregations/timeline?interval=daily&from_date=2025-11-01&to_date=2025-11-30
    ```
    """
    # Validate interval
    if interval not in ["daily", "weekly", "monthly"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Invalid interval: {interval}")
    
    # Parse dates
    parsed_from_date = None
    parsed_to_date = None
    
    if from_date:
        parsed_from_date = datetime.fromisoformat(from_date.replace('Z', '+00:00') if 'Z' in from_date else from_date)
    if to_date:
        parsed_to_date = datetime.fromisoformat(to_date.replace('Z', '+00:00') if 'Z' in to_date else to_date)
    
    # Get aggregation service
    agg_service = AggregationService(db)
    
    # Get timeline
    data = await agg_service.get_timeline(interval, parsed_from_date, parsed_to_date, source)
    
    log_info("Timeline fetched", interval=interval, results=len(data))
    
    return {
        "data": data,
        "filters": {
            "interval": interval,
            "from_date": from_date,
            "to_date": to_date,
            "source": source
        }
    }


@router.get(
    "/source-performance",
    summary="Get source performance statistics",
    description="Get detailed performance statistics for each news source"
)
async def get_source_performance(
    from_date: Annotated[str | None, Query(description="Filter from date (ISO 8601)")] = None,
    to_date: Annotated[str | None, Query(description="Filter to date (ISO 8601)")] = None,
    db: AsyncIOMotorDatabase = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """
    Get detailed performance statistics for each source.
    
    Includes:
    - Total news count
    - Average news per day
    - Top mentioned assets
    
    **Example:**
    ```
    GET /api/v1/aggregations/source-performance?from_date=2025-11-01&to_date=2025-11-30
    ```
    """
    # Parse dates
    parsed_from_date = None
    parsed_to_date = None
    
    if from_date:
        parsed_from_date = datetime.fromisoformat(from_date.replace('Z', '+00:00') if 'Z' in from_date else from_date)
    if to_date:
        parsed_to_date = datetime.fromisoformat(to_date.replace('Z', '+00:00') if 'Z' in to_date else to_date)
    
    # Get aggregation service
    agg_service = AggregationService(db)
    
    # Get source performance
    data = await agg_service.get_source_performance(parsed_from_date, parsed_to_date)
    
    log_info("Source performance fetched", sources=len(data))
    
    return {
        "data": data,
        "filters": {
            "from_date": from_date,
            "to_date": to_date
        }
    }
