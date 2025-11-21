"""
Security module for API Key authentication.
Validates API keys from Authorization header or query parameters.
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader, APIKeyQuery
from typing import Optional

from app.config import settings


# Define API Key security schemes
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)
api_key_query = APIKeyQuery(name="api_key", auto_error=False)


async def verify_api_key(
    api_key_header: Optional[str] = Security(api_key_header),
    api_key_query: Optional[str] = Security(api_key_query),
) -> str:
    """
    Verify API key from header or query parameter.
    
    Accepts API key in two formats:
    1. Authorization header: "Bearer <api_key>"
    2. Query parameter: ?api_key=<api_key>
    
    Args:
        api_key_header: API key from Authorization header
        api_key_query: API key from query parameter
    
    Returns:
        str: Validated API key
    
    Raises:
        HTTPException: If API key is missing or invalid
    """
    valid_api_keys = settings.get_api_keys()
    
    # If no API keys configured, allow all requests (development mode)
    if not valid_api_keys:
        return "development-mode"
    
    # Try to get API key from header first
    api_key = None
    if api_key_header:
        # Remove "Bearer " prefix if present
        api_key = api_key_header.replace("Bearer ", "").replace("bearer ", "")
    elif api_key_query:
        api_key = api_key_query
    
    # Check if API key is provided
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required. Provide it in Authorization header or api_key query parameter.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate API key
    if api_key not in valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return api_key


def get_api_key_info(api_key: str) -> dict:
    """
    Get information about an API key.
    Currently returns basic info, can be extended for API key metadata.
    
    Args:
        api_key: The API key
    
    Returns:
        dict: API key information
    """
    return {
        "api_key": api_key[:8] + "..." if len(api_key) > 8 else api_key,
        "valid": True,
    }
