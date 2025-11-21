"""
Health check router.
Provides endpoints for monitoring API health and database connectivity.
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

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
    - `status`: Overall health status (healthy/unhealthy)
    - `timestamp`: Current server timestamp
    - `database`: Database connection status
    - `version`: API version
    """
    try:
        # Check database connection
        start_time = datetime.utcnow()
        is_connected = await db_manager.ping()
        ping_duration = (datetime.utcnow() - start_time).total_microseconds() / 1000
        
        if not is_connected:
            log_error("Database connection failed")
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "database": {
                    "connected": False,
                    "error": "Failed to ping database"
                },
                "version": settings.APP_VERSION
            }
        
        log_info("Health check successful", ping_ms=ping_duration)
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "database": {
                "connected": True,
                "ping_ms": round(ping_duration, 2)
            },
            "version": settings.APP_VERSION
        }
    
    except Exception as e:
        log_error("Health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "database": {
                "connected": False,
                "error": str(e)
            },
            "version": settings.APP_VERSION
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
            "ready": False,
            "reason": "Database not initialized"
        }
    
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat() + "Z"
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
        "alive": True,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
