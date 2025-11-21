"""
Global error handler middleware.
Catches all unhandled exceptions and returns consistent error responses.
"""

import traceback
import uuid
from typing import Callable
from datetime import datetime
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from pydantic import ValidationError

from app.utils.logger import log_error
from app.utils.exceptions import (
    NewsNotFoundException,
    InvalidCursorException,
    RateLimitExceededException,
)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling all application errors.
    Provides consistent error response format.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and handle any errors.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
        
        Returns:
            Response: HTTP response or error response
        """
        # Generate unique request ID for tracking
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        try:
            response = await call_next(request)
            return response
        
        except NewsNotFoundException as e:
            # 404 Not Found
            return self._create_error_response(
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="NEWS_NOT_FOUND",
                message=str(e),
                request_id=request_id
            )
        
        except InvalidCursorException as e:
            # 400 Bad Request - Invalid Cursor
            return self._create_error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="INVALID_CURSOR",
                message=str(e),
                request_id=request_id
            )
        
        except RateLimitExceededException as e:
            # 429 Too Many Requests
            return self._create_error_response(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                error_code="RATE_LIMIT_EXCEEDED",
                message=str(e),
                request_id=request_id
            )
        
        except ValidationError as e:
            # 422 Validation Error (Pydantic)
            return self._create_validation_error_response(e, request_id)
        
        except ValueError as e:
            # 400 Bad Request - Invalid Value
            return self._create_error_response(
                status_code=status.HTTP_400_BAD_REQUEST,
                error_code="INVALID_VALUE",
                message=str(e),
                request_id=request_id
            )
        
        except Exception as e:
            # 500 Internal Server Error - Unexpected
            return self._handle_unexpected_error(e, request, request_id)
    
    def _create_error_response(
        self,
        status_code: int,
        error_code: str,
        message: str,
        request_id: str,
        details: dict = None
    ) -> JSONResponse:
        """
        Create standardized error response.
        
        Args:
            status_code: HTTP status code
            error_code: Application error code
            message: Human-readable error message
            request_id: Unique request identifier
            details: Additional error details
        
        Returns:
            JSONResponse: Error response
        """
        error_data = {
            "error": {
                "code": error_code,
                "message": message,
                "status": status_code,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "request_id": request_id
            }
        }
        
        if details:
            error_data["error"]["details"] = details
        
        return JSONResponse(
            status_code=status_code,
            content=error_data
        )
    
    def _create_validation_error_response(
        self,
        error: ValidationError,
        request_id: str
    ) -> JSONResponse:
        """
        Create response for Pydantic validation errors.
        
        Args:
            error: Pydantic validation error
            request_id: Unique request identifier
        
        Returns:
            JSONResponse: Validation error response
        """
        # Extract validation errors
        details = []
        for err in error.errors():
            field = " -> ".join(str(loc) for loc in err["loc"])
            details.append({
                "field": field,
                "message": err["msg"],
                "type": err["type"]
            })
        
        return self._create_error_response(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            request_id=request_id,
            details=details
        )
    
    def _handle_unexpected_error(
        self,
        error: Exception,
        request: Request,
        request_id: str
    ) -> JSONResponse:
        """
        Handle unexpected errors (500 Internal Server Error).
        
        Args:
            error: The exception that occurred
            request: The request that caused the error
            request_id: Unique request identifier
        
        Returns:
            JSONResponse: Internal server error response
        """
        # Log full error with traceback
        error_trace = traceback.format_exc()
        log_error(
            "Unexpected error occurred",
            error=str(error),
            error_type=type(error).__name__,
            path=request.url.path,
            method=request.method,
            request_id=request_id,
            traceback=error_trace
        )
        
        # Return generic error (don't expose internal details)
        return self._create_error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred. Please try again later.",
            request_id=request_id,
            details={
                "support": "If this error persists, please contact support with the request ID"
            }
        )


def format_error_response(
    status_code: int,
    error_code: str,
    message: str,
    details: dict = None
) -> dict:
    """
    Helper function to format error responses consistently.
    
    Args:
        status_code: HTTP status code
        error_code: Application error code
        message: Human-readable message
        details: Additional details
    
    Returns:
        dict: Formatted error response
    """
    response = {
        "error": {
            "code": error_code,
            "message": message,
            "status": status_code,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return response
