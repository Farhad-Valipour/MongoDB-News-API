"""
Main FastAPI application.
Initializes the API, configures middleware, and includes routers.
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings
from app.core.database import db_manager
from app.routers import news, health, aggregations
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.middleware.cors import configure_cors
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
    - 📊 Analytics and aggregation endpoints
    - 🛡️ Rate limiting and security
    
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

# Configure CORS (must be first)
configure_cors(app)

# Add custom middleware (order matters - last added runs first)
app.add_middleware(ErrorHandlerMiddleware)  # Catch all errors
app.add_middleware(RateLimitMiddleware)     # Rate limiting
app.add_middleware(RequestLoggingMiddleware)  # Logging

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(news.router, prefix="/api/v1")
app.include_router(aggregations.router, prefix="/api/v1")


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
        "health": "/api/v1/health",
        "features": {
            "authentication": "API Key",
            "pagination": "Cursor-based",
            "rate_limiting": f"{settings.RATE_LIMIT_PER_HOUR} requests/hour",
            "aggregations": True
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
