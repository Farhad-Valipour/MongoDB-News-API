"""Services module initialization."""

from app.services.news_service import NewsService, get_news_service
from app.services.cursor_service import cursor_service
from app.services.aggregation_service import AggregationService, get_aggregation_service

__all__ = [
    "NewsService",
    "get_news_service",
    "cursor_service",
    "AggregationService",
    "get_aggregation_service",
]
