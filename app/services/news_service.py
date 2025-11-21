"""
News service containing business logic for news operations.
Handles database queries, filtering, sorting, and pagination.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.models.news import NewsListItem, NewsDetail
from app.models.request import NewsQueryParams
from app.services.cursor_service import cursor_service
from app.core.pagination import create_pagination_response
from app.utils.exceptions import NewsNotFoundException
from app.config import settings


class NewsService:
    """Service for news-related operations."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db[settings.MONGODB_COLLECTION_NAME]
    
    async def get_news_list(
        self,
        params: NewsQueryParams
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Get paginated list of news with filters.
        
        Args:
            params: Query parameters including filters, sorting, and pagination
        
        Returns:
            Tuple of (news_list, pagination_meta)
        """
        # Build base query
        query = self._build_query(params)
        
        # Add cursor-based pagination query
        cursor_query = cursor_service.build_cursor_query(
            params.cursor,
            params.sort_by.value,
            params.order.value
        )
        if cursor_query:
            query = {"$and": [query, cursor_query]} if query else cursor_query
        
        # Build sort criteria
        sort_criteria = self._build_sort_criteria(params.sort_by.value, params.order.value)
        
        # Query with limit + 1 to check if there are more items
        cursor = self.collection.find(
            query,
            projection=self._get_list_projection()
        ).sort(sort_criteria).limit(params.limit + 1)
        
        # Fetch results
        items = await cursor.to_list(length=params.limit + 1)
        
        # Convert ObjectId to string
        for item in items:
            item["_id"] = str(item["_id"])
        
        # Create pagination response
        pagination = create_pagination_response(
            items,
            params.limit,
            params.sort_by.value,
            has_prev=bool(params.cursor)
        )
        
        # Return actual items (without the +1 extra)
        actual_items = items[:params.limit]
        
        return actual_items, pagination
    
    async def get_news_by_slug(self, slug: str) -> Dict[str, Any]:
        """
        Get a single news article by slug.
        
        Args:
            slug: News article slug
        
        Returns:
            dict: News article data
        
        Raises:
            NewsNotFoundException: If news not found
        """
        news = await self.collection.find_one(
            {"slug": slug},
            projection=self._get_detail_projection()
        )
        
        if not news:
            raise NewsNotFoundException(f"News with slug '{slug}' not found")
        
        # Convert ObjectId to string
        news["_id"] = str(news["_id"])
        
        return news
    
    def _build_query(self, params: NewsQueryParams) -> Dict[str, Any]:
        """
        Build MongoDB query from parameters.
        
        Args:
            params: Query parameters
        
        Returns:
            dict: MongoDB query
        """
        query = {}
        
        # Date range filter
        if params.from_date or params.to_date:
            date_filter = {}
            if params.from_date:
                date_filter["$gte"] = params.from_date
            if params.to_date:
                date_filter["$lte"] = params.to_date
            query["releasedAt"] = date_filter
        
        # Source filter
        if params.source:
            query["source"] = params.source
        
        # Asset filter
        if params.asset_slug:
            query["assets.slug"] = params.asset_slug
        
        # Keyword search (text search in title and content)
        if params.keyword:
            # Use regex for flexible search
            keyword_regex = {"$regex": params.keyword, "$options": "i"}
            query["$or"] = [
                {"title": keyword_regex},
                {"content": keyword_regex},
                {"subtitle": keyword_regex}
            ]
        
        return query
    
    def _build_sort_criteria(self, sort_field: str, sort_order: str) -> List[Tuple[str, int]]:
        """
        Build MongoDB sort criteria.
        
        Args:
            sort_field: Field to sort by
            sort_order: 'asc' or 'desc'
        
        Returns:
            list: MongoDB sort criteria [(field, direction), ...]
        """
        direction = 1 if sort_order == "asc" else -1
        
        # Always include _id as secondary sort for consistency
        return [
            (sort_field, direction),
            ("_id", direction)
        ]
    
    def _get_list_projection(self) -> Dict[str, int]:
        """
        Get projection for list queries (excludes full content).
        
        Returns:
            dict: MongoDB projection
        """
        # MongoDB projection: use only inclusion OR only exclusion, not both
        # For list view, we exclude only the content field
        return {
            "content": 0  # Exclude only content field (exclusion projection)
        }
    
    def _get_detail_projection(self) -> Dict[str, int]:
        """
        Get projection for detail queries (includes everything).
        
        Returns:
            dict: MongoDB projection
        """
        return {}  # Include all fields


async def get_news_service(db: AsyncIOMotorDatabase) -> NewsService:
    """
    Get news service instance.
    Used as a dependency in FastAPI endpoints.
    
    Args:
        db: Database instance
    
    Returns:
        NewsService: News service instance
    """
    return NewsService(db)
