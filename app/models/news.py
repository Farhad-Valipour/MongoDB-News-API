"""
News document model.
Represents news articles from various sources (CoinMarketCap, Bloomberg, Reuters, etc.)
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.models.asset import Asset


class NewsBase(BaseModel):
    """Base news schema with common fields."""
    slug: str = Field(..., description="Unique identifier for the news article")
    title: str = Field(..., description="Article title")
    subtitle: Optional[str] = Field(None, description="Article subtitle or summary")
    content: str = Field(..., description="Full article content (may contain HTML)")
    source: str = Field(..., description="News source (e.g., coinmarketcap, bloomberg, reuters)")
    sourceName: str = Field(..., description="Human-readable source name")
    sourceUrl: str = Field(..., description="Original article URL")
    releasedAt: datetime = Field(..., description="Article publication date")
    assets: List[Asset] = Field(default=[], description="Related assets/cryptocurrencies")


class NewsInDB(NewsBase):
    """
    News schema as stored in MongoDB.
    Includes database-specific fields.
    """
    createdAt: Optional[datetime] = Field(None, description="Database creation timestamp")
    updatedAt: Optional[datetime] = Field(None, description="Database update timestamp")
    
    class Config:
        from_attributes = True


class NewsListItem(BaseModel):
    """
    Simplified news schema for list responses.
    Excludes full content to reduce response size.
    """
    slug: str
    title: str
    subtitle: Optional[str] = None
    source: str
    sourceName: str
    sourceUrl: str
    releasedAt: datetime
    assets: List[Asset] = []
    
    class Config:
        json_schema_extra = {
            "example": {
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
        }


class NewsDetail(NewsInDB):
    """
    Detailed news schema for single item responses.
    Includes full content and all metadata.
    """
    
    class Config:
        json_schema_extra = {
            "example": {
                "slug": "bitcoin-hits-new-high",
                "title": "Bitcoin Hits New All-Time High",
                "subtitle": "Bitcoin surges past $50,000...",
                "content": "<p>Full article content with HTML...</p>",
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
            }
        }
