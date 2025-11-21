"""
Dependency injection utilities.
Provides reusable dependencies for FastAPI endpoints.
"""

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database
from app.core.security import verify_api_key


async def get_db() -> AsyncIOMotorDatabase:
    """
    Get database dependency.
    Used in endpoint dependency injection.
    """
    return await get_database()


async def get_current_api_key(
    api_key: str = Depends(verify_api_key)
) -> str:
    """
    Get current validated API key.
    Used in endpoint dependency injection for authentication.
    """
    return api_key
