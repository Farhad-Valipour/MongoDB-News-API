"""
Request/Response logging middleware.
Logs all incoming requests and outgoing responses with detailed information.
"""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.utils.logger import log_info, log_error


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all requests and responses.
    Captures method, path, query params, status code, and response time.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and log details.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
        
        Returns:
            Response: HTTP response
        """
        # Start timer
        start_time = time.time()
        
        # Extract request details
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Extract API key (if present) - truncate for security
        api_key = None
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            api_key = auth_header.replace("Bearer ", "")
            api_key = api_key[:8] + "..." if len(api_key) > 8 else api_key
        elif "api_key" in query_params:
            api_key = query_params["api_key"]
            api_key = api_key[:8] + "..." if len(api_key) > 8 else api_key
        
        # Log incoming request
        log_info(
            f"Incoming request: {method} {path}",
            client_ip=client_ip,
            query_params=str(query_params) if query_params else None,
            api_key=api_key,
            user_agent=user_agent[:50] if user_agent else None  # Truncate UA
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate response time
            process_time = time.time() - start_time
            response_time_ms = round(process_time * 1000, 2)
            
            # Log response
            log_info(
                f"Response: {method} {path} → {response.status_code}",
                status_code=response.status_code,
                response_time_ms=response_time_ms,
                client_ip=client_ip
            )
            
            # Add custom header with response time
            response.headers["X-Process-Time"] = str(response_time_ms)
            
            return response
        
        except Exception as e:
            # Calculate response time even for errors
            process_time = time.time() - start_time
            response_time_ms = round(process_time * 1000, 2)
            
            # Log error
            log_error(
                f"Error processing request: {method} {path}",
                error=str(e),
                response_time_ms=response_time_ms,
                client_ip=client_ip
            )
            
            # Re-raise exception to be handled by error handler
            raise
