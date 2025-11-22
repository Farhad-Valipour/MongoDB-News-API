"""
Health check router.
Provides endpoints for monitoring API health and database connectivity.
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
import time

from app.dependencies import get_db
from app.config import settings
from app.core.database import db_manager
from app.utils.logger import log_info, log_error


router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    summary="Health check",
    description="Check API and database health status",
    responses={
        200: {"description": "API is healthy"},
        503: {"description": "API is unhealthy"},
    }
)
async def health_check(db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Check the health status of the API and database connection.
    
    **Returns:**
    - `success`: Whether the health check passed
    - `status`: Overall health status (healthy/unhealthy)
    - `timestamp`: Current server timestamp
    - `database`: Database connection status
    - `version`: API version
    - `query_time_ms`: Health check execution time
    """
    start_time = time.time()
    
    try:
        # Check database connection
        db_start = datetime.utcnow()
        is_connected = await db_manager.ping()
        ping_duration = (datetime.utcnow() - db_start).total_microseconds() / 1000
        
        # Calculate total query time
        query_time_ms = (time.time() - start_time) * 1000
        
        if not is_connected:
            log_error("Database connection failed")
            return {
                "success": False,
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": {
                    "connected": False,
                    "error": "Failed to ping database"
                },
                "version": settings.APP_VERSION,
                "query_time_ms": round(query_time_ms, 2)
            }
        
        log_info("Health check successful", ping_ms=round(ping_duration, 2))
        
        return {
            "success": True,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "connected": True,
                "ping_ms": round(ping_duration, 2)
            },
            "version": settings.APP_VERSION,
            "query_time_ms": round(query_time_ms, 2)
        }
    
    except Exception as e:
        query_time_ms = (time.time() - start_time) * 1000
        log_error("Health check failed", error=str(e))
        return {
            "success": False,
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "connected": False,
                "error": str(e)
            },
            "version": settings.APP_VERSION,
            "query_time_ms": round(query_time_ms, 2)
        }


@router.get(
    "/ready",
    summary="Readiness check",
    description="Check if API is ready to handle requests",
)
async def readiness_check():
    """
    Check if the API is ready to handle requests.
    Used by orchestration systems like Kubernetes.
    """
    # Check if database manager is initialized
    if db_manager.client is None:
        return {
            "success": False,
            "ready": False,
            "reason": "Database not initialized",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return {
        "success": True,
        "ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/live",
    summary="Liveness check",
    description="Check if API is alive",
)
async def liveness_check():
    """
    Check if the API is alive.
    Used by orchestration systems like Kubernetes.
    """
    return {
        "success": True,
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }
