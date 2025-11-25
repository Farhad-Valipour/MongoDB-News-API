"""
Aggregation router.
Provides endpoints for news analytics and statistics.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Annotated, Optional
from datetime import datetime
import time

from app.services.aggregation_service import AggregationService
from app.dependencies import get_db, get_current_api_key
from app.models.response import AggregationResponse, ResponseMetadata
from app.utils.logger import log_info


router = APIRouter(prefix="/aggregations", tags=["Aggregations"])


@router.get(
    "/stats",
    response_model=AggregationResponse,
    summary="Get news statistics",
    description="Get aggregated news statistics grouped by various dimensions"
)
async def get_stats(
    group_by: Annotated[str, Query(description="Group by: source, date")] = "source",
    start: Annotated[str | None, Query(description="Filter from date (ISO 8601)")] = None,
    end: Annotated[str | None, Query(description="Filter to date (ISO 8601)")] = None,
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
    GET /api/v1/aggregations/stats?group_by=source&start=2025-11-01&end=2025-11-30
    ```
    """
    # Start timer
    start_time = time.time()
    
    # Parse dates
    parsed_start = None
    parsed_end = None
    
    if start:
        parsed_start = datetime.fromisoformat(start.replace('Z', '+00:00') if 'Z' in start else start)
    if end:
        parsed_end = datetime.fromisoformat(end.replace('Z', '+00:00') if 'Z' in end else end)
    
    # Get aggregation service
    agg_service = AggregationService(db)
    
    # Execute aggregation based on group_by
    if group_by == "source":
        data = await agg_service.get_stats_by_source(parsed_start, parsed_end)
        total = sum(item["count"] for item in data)
    elif group_by == "date":
        data = await agg_service.get_timeline("daily", parsed_start, parsed_end)
        total = sum(item["count"] for item in data)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid group_by value: {group_by}")
    
    # Calculate query time
    query_time_ms = (time.time() - start_time) * 1000
    
    # Add filters and total to each result
    result_data = [{
        **item,
        "filters": {
            "group_by": group_by,
            "start": start,
            "end": end
        },
        "total": total
    } for item in data]
    
    log_info(
        "Stats aggregation completed",
        group_by=group_by,
        results=len(data),
        query_time_ms=round(query_time_ms, 2)
    )
    
    return AggregationResponse(
        success=True,
        data=result_data,
        metadata=ResponseMetadata(
            query_time_ms=round(query_time_ms, 2),
            timestamp=datetime.utcnow().isoformat(),
            api_version="1.0.0"
        )
    )


@router.get(
    "/top-assets",
    response_model=AggregationResponse,
    summary="Get top mentioned assets",
    description="Get the most frequently mentioned assets in news"
)
async def get_top_assets(
    limit: Annotated[int, Query(description="Number of top assets", ge=1, le=100)] = 10,
    start: Annotated[str | None, Query(description="Filter from date (ISO 8601)")] = None,
    end: Annotated[str | None, Query(description="Filter to date (ISO 8601)")] = None,
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
    # Start timer
    start_time = time.time()
    
    # Parse dates
    parsed_start = None
    parsed_end = None
    
    if start:
        parsed_start = datetime.fromisoformat(start.replace('Z', '+00:00') if 'Z' in start else start)
    if end:
        parsed_end = datetime.fromisoformat(end.replace('Z', '+00:00') if 'Z' in end else end)
    
    # Get aggregation service
    agg_service = AggregationService(db)
    
    # Get top assets
    data = await agg_service.get_top_assets(limit, parsed_start, parsed_end, source)
    
    # Calculate query time
    query_time_ms = (time.time() - start_time) * 1000
    
    # Add filters to each result
    result_data = [{
        **item,
        "filters": {
            "limit": limit,
            "start": start,
            "end": end,
            "source": source
        }
    } for item in data]
    
    log_info(
        "Top assets fetched",
        limit=limit,
        results=len(data),
        query_time_ms=round(query_time_ms, 2)
    )
    
    return AggregationResponse(
        success=True,
        data=result_data,
        metadata=ResponseMetadata(
            query_time_ms=round(query_time_ms, 2),
            timestamp=datetime.utcnow().isoformat(),
            api_version="1.0.0"
        )
    )


@router.get(
    "/timeline",
    response_model=AggregationResponse,
    summary="Get news timeline",
    description="Get news count over time with configurable intervals"
)
async def get_timeline(
    interval: Annotated[str, Query(description="Time interval: daily, weekly, monthly")] = "daily",
    start: Annotated[str | None, Query(description="Filter from date (ISO 8601)")] = None,
    end: Annotated[str | None, Query(description="Filter to date (ISO 8601)")] = None,
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
    GET /api/v1/aggregations/timeline?interval=daily&start=2025-11-01&end=2025-11-30
    ```
    """
    # Start timer
    start_time = time.time()
    
    # Validate interval
    if interval not in ["daily", "weekly", "monthly"]:
        raise HTTPException(status_code=400, detail=f"Invalid interval: {interval}")
    
    # Parse dates
    parsed_start = None
    parsed_end = None
    
    if start:
        parsed_start = datetime.fromisoformat(start.replace('Z', '+00:00') if 'Z' in start else start)
    if end:
        parsed_end = datetime.fromisoformat(end.replace('Z', '+00:00') if 'Z' in end else end)
    
    # Get aggregation service
    agg_service = AggregationService(db)
    
    # Get timeline
    data = await agg_service.get_timeline(interval, parsed_start, parsed_end, source)
    
    # Calculate query time
    query_time_ms = (time.time() - start_time) * 1000
    
    # Add filters to each result
    result_data = [{
        **item,
        "filters": {
            "interval": interval,
            "start": start,
            "end": end,
            "source": source
        }
    } for item in data]
    
    log_info(
        "Timeline fetched",
        interval=interval,
        results=len(data),
        query_time_ms=round(query_time_ms, 2)
    )
    
    return AggregationResponse(
        success=True,
        data=result_data,
        metadata=ResponseMetadata(
            query_time_ms=round(query_time_ms, 2),
            timestamp=datetime.utcnow().isoformat(),
            api_version="1.0.0"
        )
    )


@router.get(
    "/source-performance",
    response_model=AggregationResponse,
    summary="Get source performance statistics",
    description="Get detailed performance statistics for each news source"
)
async def get_source_performance(
    start: Annotated[str | None, Query(description="Filter from date (ISO 8601)")] = None,
    end: Annotated[str | None, Query(description="Filter to date (ISO 8601)")] = None,
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
    GET /api/v1/aggregations/source-performance?start=2025-11-01&end=2025-11-30
    ```
    """
    # Start timer
    start_time = time.time()
    
    # Parse dates
    parsed_start = None
    parsed_end = None
    
    if start:
        parsed_start = datetime.fromisoformat(start.replace('Z', '+00:00') if 'Z' in start else start)
    if end:
        parsed_end = datetime.fromisoformat(end.replace('Z', '+00:00') if 'Z' in end else end)
    
    # Get aggregation service
    agg_service = AggregationService(db)
    
    # Get source performance
    data = await agg_service.get_source_performance(parsed_start, parsed_end)
    
    # Calculate query time
    query_time_ms = (time.time() - start_time) * 1000
    
    # Add filters to each result
    result_data = [{
        **item,
        "filters": {
            "start": start,
            "end": end
        }
    } for item in data]
    
    log_info(
        "Source performance fetched",
        sources=len(data),
        query_time_ms=round(query_time_ms, 2)
    )
    
    return AggregationResponse(
        success=True,
        data=result_data,
        metadata=ResponseMetadata(
            query_time_ms=round(query_time_ms, 2),
            timestamp=datetime.utcnow().isoformat(),
            api_version="1.0.0"
        )
    )
