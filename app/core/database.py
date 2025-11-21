"""
MongoDB database connection and client management.
Handles connection pooling and provides access to database collections.
"""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

from app.config import settings


class DatabaseManager:
    """Manages MongoDB connection and provides database access."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
    
    async def connect(self):
        """
        Establish connection to MongoDB.
        Creates connection pool with configured min/max pool size.
        """
        try:
            mongodb_uri = settings.get_mongodb_uri()
            
            self.client = AsyncIOMotorClient(
                mongodb_uri,
                minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
                maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
            )
            self.db = self.client[settings.MONGODB_DB_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            print(f"✅ Connected to MongoDB: {settings.MONGODB_DB_NAME}")
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("✅ Disconnected from MongoDB")
    
    async def ping(self) -> bool:
        """
        Check if database connection is alive.
        Returns True if connected, False otherwise.
        """
        try:
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False
    
    def get_collection(self, collection_name: str = None):
        """
        Get a collection from the database.
        
        Args:
            collection_name: Name of collection. Defaults to settings.MONGODB_COLLECTION_NAME
        
        Returns:
            AsyncIOMotorCollection instance
        """
        if collection_name is None:
            collection_name = settings.MONGODB_COLLECTION_NAME
        return self.db[collection_name]


# Global database manager instance
db_manager = DatabaseManager()


async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency for getting database instance.
    Used in FastAPI dependency injection.
    """
    return db_manager.db
