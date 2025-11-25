"""
Aggregation service for news analytics and statistics.
Provides aggregated data for reporting and dashboards.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config import settings
from app.utils.logger import log_info


class AggregationService:
    """Service for news aggregation and analytics."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[settings.MONGODB_COLLECTION_NAME]
    
    async def get_stats_by_source(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get news count grouped by source.
        
        Args:
            start: Start date filter
            end: End date filter
        
        Returns:
            List of source statistics
        """
        # Build match stage
        match_stage = {}
        if start or end:
            date_filter = {}
            if start:
                date_filter["$gte"] = start
            if end:
                date_filter["$lte"] = end
            match_stage["releasedAt"] = date_filter
        
        # Aggregation pipeline
        pipeline = []
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        pipeline.extend([
            {
                "$group": {
                    "_id": "$source",
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "source": "$_id",
                    "count": 1
                }
            },
            {"$sort": {"count": -1}}
        ])
        
        # Execute aggregation
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        log_info("Stats by source fetched", count=len(results))
        
        return results
    
    async def get_top_assets(
        self,
        limit: int = 10,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get most mentioned assets.
        
        Args:
            limit: Number of top assets to return
            start: Start date filter
            end: End date filter
            source: Filter by specific source
        
        Returns:
            List of top assets with counts
        """
        # Build match stage
        match_stage = {}
        
        if start or end:
            date_filter = {}
            if start:
                date_filter["$gte"] = start
            if end:
                date_filter["$lte"] = end
            match_stage["releasedAt"] = date_filter
        
        if source:
            match_stage["source"] = source
        
        # Aggregation pipeline
        pipeline = []
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        pipeline.extend([
            # Unwind assets array
            {"$unwind": "$assets"},
            # Filter out assets without slug
            {"$match": {"assets.slug": {"$exists": True, "$ne": None}}},
            # Group by asset
            {
                "$group": {
                    "_id": "$assets.slug",
                    "name": {"$first": "$assets.name"},
                    "symbol": {"$first": "$assets.symbol"},
                    "count": {"$sum": 1}
                }
            },
            # Sort by count
            {"$sort": {"count": -1}},
            # Limit results
            {"$limit": limit},
            # Format output
            {
                "$project": {
                    "_id": 0,
                    "asset": {
                        "name": "$name",
                        "slug": "$_id",
                        "symbol": "$symbol"
                    },
                    "count": 1
                }
            }
        ])
        
        # Execute aggregation
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=limit)
        
        # Calculate total for percentages
        total_pipeline = []
        if match_stage:
            total_pipeline.append({"$match": match_stage})
        total_pipeline.append({"$count": "total"})
        
        total_cursor = self.collection.aggregate(total_pipeline)
        total_results = await total_cursor.to_list(length=1)
        total_news = total_results[0]["total"] if total_results else 0
        
        # Add percentages
        for item in results:
            item["percentage"] = round((item["count"] / total_news * 100), 2) if total_news > 0 else 0
        
        log_info("Top assets fetched", count=len(results), total_news=total_news)
        
        return results
    
    async def get_timeline(
        self,
        interval: str = "daily",
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get news count over time.
        
        Args:
            interval: Time interval (daily, weekly, monthly)
            start: Start date
            end: End date
            source: Filter by source
        
        Returns:
            List of time periods with counts
        """
        # Build match stage
        match_stage = {}
        
        if start or end:
            date_filter = {}
            if start:
                date_filter["$gte"] = start
            if end:
                date_filter["$lte"] = end
            match_stage["releasedAt"] = date_filter
        
        if source:
            match_stage["source"] = source
        
        # Determine date format based on interval
        date_format = {
            "daily": "%Y-%m-%d",
            "weekly": "%Y-W%U",  # Year-Week
            "monthly": "%Y-%m"
        }.get(interval, "%Y-%m-%d")
        
        # Aggregation pipeline
        pipeline = []
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        pipeline.extend([
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": date_format,
                            "date": "$releasedAt"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "date": "$_id",
                    "count": 1
                }
            },
            {"$sort": {"date": 1}}
        ])
        
        # Execute aggregation
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        log_info("Timeline fetched", interval=interval, count=len(results))
        
        return results
    
    async def get_source_performance(
        self,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get detailed performance stats for each source.
        
        Args:
            start: Start date
            end: End date
        
        Returns:
            List of source performance statistics
        """
        # Build match stage
        match_stage = {}
        if start or end:
            date_filter = {}
            if start:
                date_filter["$gte"] = start
            if end:
                date_filter["$lte"] = end
            match_stage["releasedAt"] = date_filter
        
        # Aggregation pipeline
        pipeline = []
        
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        pipeline.extend([
            {
                "$group": {
                    "_id": "$source",
                    "total_news": {"$sum": 1},
                    "assets": {"$push": "$assets"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "source": "$_id",
                    "total_news": 1,
                    "assets": 1
                }
            },
            {"$sort": {"total_news": -1}}
        ])
        
        # Execute aggregation
        cursor = self.collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)
        
        # Calculate days if date range provided
        if start and end:
            days = (end - start).days + 1
            for item in results:
                item["avg_per_day"] = round(item["total_news"] / days, 2) if days > 0 else 0
        
        log_info("Source performance fetched", sources=len(results))
        
        return results


async def get_aggregation_service(db: AsyncIOMotorDatabase) -> AggregationService:
    """
    Get aggregation service instance.
    
    Args:
        db: Database instance
    
    Returns:
        AggregationService: Aggregation service
    """
    return AggregationService(db)
