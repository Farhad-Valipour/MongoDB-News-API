"""
Main FastAPI application.
Initializes the API, configures middleware, and includes routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.core.database import db_manager
from app.routers import news, health
from app.utils.logger import logger, log_info, log_error


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    log_info("Starting application", app_name=settings.APP_NAME, version=settings.APP_VERSION)
    
    try:
        # Connect to MongoDB
        await db_manager.connect()
        log_info("Application started successfully")
    except Exception as e:
        log_error("Failed to start application", error=str(e))
        raise
    
    yield
    
    # Shutdown
    log_info("Shutting down application")
    await db_manager.disconnect()
    log_info("Application shut down successfully")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    MongoDB News API - A REST API for accessing news articles from various sources.
    
    ## Features
    - 📰 Access news from multiple sources (CoinMarketCap, Bloomberg, Reuters, etc.)
    - 🔍 Advanced filtering and search
    - 📄 Cursor-based pagination for large datasets
    - 🔐 API Key authentication
    - 🚀 High performance with async operations
    
    ## Authentication
    All endpoints require API key authentication via:
    - **Authorization header**: `Authorization: Bearer <your-api-key>`
    - **Query parameter**: `?api_key=<your-api-key>`
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS.split(","),
    allow_headers=settings.CORS_ALLOW_HEADERS.split(",") if settings.CORS_ALLOW_HEADERS != "*" else ["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(news.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint.
    Returns basic API information.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


# Exception handlers
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.utils.exceptions import (
    NewsNotFoundException,
    InvalidCursorException,
    RateLimitExceededException
)
from datetime import datetime


@app.exception_handler(NewsNotFoundException)
async def news_not_found_handler(request: Request, exc: NewsNotFoundException):
    """Handle NewsNotFoundException."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "code": "NEWS_NOT_FOUND",
                "message": exc.message,
                "status": 404,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    )


@app.exception_handler(InvalidCursorException)
async def invalid_cursor_handler(request: Request, exc: InvalidCursorException):
    """Handle InvalidCursorException."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "INVALID_CURSOR",
                "message": exc.message,
                "status": 400,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    )


@app.exception_handler(RateLimitExceededException)
async def rate_limit_handler(request: Request, exc: RateLimitExceededException):
    """Handle RateLimitExceededException."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": exc.message,
                "status": 429,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
