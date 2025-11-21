"""
Enhanced CORS (Cross-Origin Resource Sharing) configuration.
Provides flexible CORS settings for different environments.
"""

from typing import List
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.config import settings


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware with enhanced settings.
    
    Args:
        app: FastAPI application instance
    """
    # Get allowed origins
    origins = settings.get_cors_origins()
    
    # Parse allowed methods
    methods = [m.strip() for m in settings.CORS_ALLOW_METHODS.split(",")]
    
    # Parse allowed headers (if not wildcard)
    if settings.CORS_ALLOW_HEADERS == "*":
        headers = ["*"]
    else:
        headers = [h.strip() for h in settings.CORS_ALLOW_HEADERS.split(",")]
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=methods,
        allow_headers=headers,
        expose_headers=[
            "X-Process-Time",
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset"
        ],
        max_age=3600  # Cache preflight requests for 1 hour
    )


def get_cors_origins_for_environment() -> List[str]:
    """
    Get appropriate CORS origins based on environment.
    
    Returns:
        List[str]: List of allowed origins
    """
    if settings.DEBUG:
        # Development: allow localhost and common dev ports
        return [
            "http://localhost:3000",
            "http://localhost:3001",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001",
            "http://127.0.0.1:8080",
        ]
    else:
        # Production: use configured origins
        return settings.get_cors_origins()


# Common CORS presets
CORS_PRESETS = {
    "development": {
        "allow_origins": ["*"],
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    },
    "production_strict": {
        "allow_origins": [],  # Must be configured
        "allow_credentials": True,
        "allow_methods": ["GET", "POST"],
        "allow_headers": ["Authorization", "Content-Type"],
    },
    "production_relaxed": {
        "allow_origins": [],  # Must be configured
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["*"],
    },
}


def validate_cors_configuration() -> dict:
    """
    Validate current CORS configuration.
    
    Returns:
        dict: Validation results
    """
    issues = []
    warnings = []
    
    # Check if wildcard is used in production
    if not settings.DEBUG and "*" in settings.get_cors_origins():
        warnings.append(
            "Using wildcard (*) for CORS origins in production is not recommended"
        )
    
    # Check if credentials are enabled with wildcard
    if settings.CORS_ALLOW_CREDENTIALS and "*" in settings.get_cors_origins():
        issues.append(
            "Cannot use allow_credentials=True with allow_origins=['*']"
        )
    
    # Check if origins are configured for production
    if not settings.DEBUG and not settings.get_cors_origins():
        issues.append(
            "No CORS origins configured for production"
        )
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "current_config": {
            "origins": settings.get_cors_origins(),
            "credentials": settings.CORS_ALLOW_CREDENTIALS,
            "methods": settings.CORS_ALLOW_METHODS,
            "headers": settings.CORS_ALLOW_HEADERS,
        }
    }
