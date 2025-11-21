"""
Asset model representing a cryptocurrency or financial asset.
Used within news documents.
"""

from pydantic import BaseModel, Field
from typing import Optional


class AssetBase(BaseModel):
    """Base asset schema."""
    name: Optional[str] = Field(None, description="Full name of the asset")
    slug: Optional[str] = Field(None, description="URL-friendly identifier")
    symbol: str = Field(..., description="Trading symbol (e.g., BTC, ETH, LSE:AWE)")


class Asset(AssetBase):
    """
    Asset schema for API responses.
    Represents a cryptocurrency or financial asset mentioned in news.
    """
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Bitcoin",
                "slug": "bitcoin",
                "symbol": "BTC"
            }
        }
