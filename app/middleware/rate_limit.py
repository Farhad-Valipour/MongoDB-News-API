"""
Rate limiting middleware.
Limits the number of requests per API key or IP address.
"""

import time
from typing import Callable, Dict, Optional
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings
from app.utils.exceptions import RateLimitExceededException
from app.utils.logger import log_warning


class RateLimiter:
    """
    Simple in-memory rate limiter.
    Tracks request counts per identifier (API key or IP).
    """
    
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store: {identifier: [(timestamp1, timestamp2, ...)]}
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed for given identifier.
        
        Args:
            identifier: Unique identifier (API key or IP)
        
        Returns:
            tuple: (is_allowed, retry_after_seconds)
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Get requests for this identifier
        requests = self.requests[identifier]
        
        # Remove old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in requests
            if req_time > window_start
        ]
        
        # Check if limit exceeded
        current_count = len(self.requests[identifier])
        
        if current_count >= self.max_requests:
            # Calculate retry after time
            oldest_request = min(self.requests[identifier])
            retry_after = int(oldest_request + self.window_seconds - now)
            return False, max(retry_after, 1)
        
        # Add current request
        self.requests[identifier].append(now)
        return True, None
    
    def get_usage(self, identifier: str) -> dict:
        """
        Get current usage statistics for identifier.
        
        Args:
            identifier: Unique identifier
        
        Returns:
            dict: Usage statistics
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        requests = [
            req_time for req_time in self.requests.get(identifier, [])
            if req_time > window_start
        ]
        
        return {
            "used": len(requests),
            "limit": self.max_requests,
            "remaining": max(0, self.max_requests - len(requests)),
            "reset_at": int(now + self.window_seconds) if requests else None
        }


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting requests.
    Limits requests per API key or IP address.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Rate limiter: 1000 requests per hour (3600 seconds)
        self.limiter = RateLimiter(
            max_requests=settings.RATE_LIMIT_PER_HOUR,
            window_seconds=3600
        )
    
    def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.
        Prefers API key, falls back to IP address.
        
        Args:
            request: Incoming request
        
        Returns:
            str: Unique identifier
        """
        # Try to get API key from header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            api_key = auth_header.replace("Bearer ", "")
            return f"api_key:{api_key}"
        
        # Try to get API key from query params
        query_params = dict(request.query_params)
        if "api_key" in query_params:
            return f"api_key:{query_params['api_key']}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check rate limit before processing request.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
        
        Returns:
            Response: HTTP response or 429 if rate limit exceeded
        """
        # Skip rate limiting for health check endpoints
        if request.url.path.startswith("/api/v1/health"):
            return await call_next(request)
        
        # Get identifier
        identifier = self._get_identifier(request)
        
        # Check rate limit
        is_allowed, retry_after = self.limiter.is_allowed(identifier)
        
        if not is_allowed:
            # Log rate limit exceeded
            log_warning(
                "Rate limit exceeded",
                identifier=identifier,
                retry_after=retry_after
            )
            
            # Return 429 response
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": f"Rate limit exceeded. Try again in {retry_after} seconds.",
                        "retry_after": retry_after,
                        "limit": settings.RATE_LIMIT_PER_HOUR,
                        "window": "1 hour",
                        "status": 429,
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_HOUR),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after)
                }
            )
        
        # Get usage stats
        usage = self.limiter.get_usage(identifier)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to response
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_HOUR)
        response.headers["X-RateLimit-Remaining"] = str(usage["remaining"])
        if usage["reset_at"]:
            response.headers["X-RateLimit-Reset"] = str(usage["reset_at"])
        
        return response
