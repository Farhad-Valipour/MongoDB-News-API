"""
Unit tests for security features.
Tests API key authentication and rate limiting.
"""

import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock

from app.core.security import verify_api_key
from app.middleware.rate_limit import RateLimiter


def assert_valid_metadata(metadata):
    """Helper to validate metadata structure"""
    assert "query_time_ms" in metadata
    assert "timestamp" in metadata
    assert "api_version" in metadata
    assert metadata["api_version"] == "1.0.0"
    assert isinstance(metadata["query_time_ms"], (int, float))
    assert metadata["query_time_ms"] > 0


@pytest.mark.unit
@pytest.mark.security
class TestAPIKeyAuthentication:
    """Test API key authentication functionality."""
    
    async def test_valid_api_key_header(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test request with valid API key in Authorization header."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Make request with valid API key
        response = await async_client.get(
            "/api/v1/news",
            headers=auth_headers
        )
        
        # Should be successful
        assert response.status_code == 200
        result = response.json()
        
        # Check new structure
        assert result["success"] == True
        assert "metadata" in result
        assert_valid_metadata(result["metadata"])
    
    async def test_valid_api_key_query_param(
        self,
        async_client,
        test_api_key,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test request with valid API key in query parameter."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Make request with API key in query
        response = await async_client.get(
            f"/api/v1/news?api_key={test_api_key}"
        )
        
        # Should be successful
        assert response.status_code == 200
        result = response.json()
        
        # Check new structure
        assert result["success"] == True
        assert "metadata" in result
        assert_valid_metadata(result["metadata"])
    
    async def test_missing_api_key(
        self,
        async_client
    ):
        """Test request without API key returns 401."""
        response = await async_client.get("/api/v1/news")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "API key" in data["detail"]
    
    async def test_invalid_api_key_header(
        self,
        async_client,
        invalid_auth_headers
    ):
        """Test request with invalid API key in header."""
        response = await async_client.get(
            "/api/v1/news",
            headers=invalid_auth_headers
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "Invalid API key" in data["detail"]
    
    async def test_invalid_api_key_query_param(
        self,
        async_client,
        invalid_api_key
    ):
        """Test request with invalid API key in query parameter."""
        response = await async_client.get(
            f"/api/v1/news?api_key={invalid_api_key}"
        )
        
        assert response.status_code == 401
    
    async def test_api_key_bearer_prefix(
        self,
        async_client,
        test_api_key,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test that Bearer prefix is properly handled."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Test with Bearer prefix
        response = await async_client.get(
            "/api/v1/news",
            headers={"Authorization": f"Bearer {test_api_key}"}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
        
        # Test with bearer prefix (lowercase)
        response = await async_client.get(
            "/api/v1/news",
            headers={"Authorization": f"bearer {test_api_key}"}
        )
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
    
    async def test_api_key_without_bearer_prefix(
        self,
        async_client,
        test_api_key,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test API key without Bearer prefix."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Make request without Bearer prefix
        response = await async_client.get(
            "/api/v1/news",
            headers={"Authorization": test_api_key}
        )
        
        # Should still work
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
    
    async def test_api_key_priority_header_over_query(
        self,
        async_client,
        test_api_key,
        invalid_api_key,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test that header API key takes priority over query parameter."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Valid key in header, invalid in query
        response = await async_client.get(
            f"/api/v1/news?api_key={invalid_api_key}",
            headers={"Authorization": f"Bearer {test_api_key}"}
        )
        
        # Should use header key and succeed
        assert response.status_code == 200
        result = response.json()
        assert result["success"] == True
    
    async def test_empty_api_key_header(
        self,
        async_client
    ):
        """Test request with empty Authorization header."""
        response = await async_client.get(
            "/api/v1/news",
            headers={"Authorization": "Bearer "}
        )
        
        assert response.status_code == 401
    
    async def test_malformed_authorization_header(
        self,
        async_client
    ):
        """Test request with malformed Authorization header."""
        response = await async_client.get(
            "/api/v1/news",
            headers={"Authorization": "InvalidFormat"}
        )
        
        assert response.status_code == 401


@pytest.mark.unit
@pytest.mark.security
class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limiter_allows_within_limit(self):
        """Test that requests within limit are allowed."""
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        identifier = "test-user"
        
        # Make 10 requests
        for i in range(10):
            is_allowed, retry_after = limiter.is_allowed(identifier)
            assert is_allowed is True
            assert retry_after is None
    
    def test_rate_limiter_blocks_over_limit(self):
        """Test that requests over limit are blocked."""
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        identifier = "test-user"
        
        # Make 5 requests (within limit)
        for i in range(5):
            is_allowed, _ = limiter.is_allowed(identifier)
            assert is_allowed is True
        
        # 6th request should be blocked
        is_allowed, retry_after = limiter.is_allowed(identifier)
        assert is_allowed is False
        assert retry_after is not None
        assert retry_after > 0
    
    def test_rate_limiter_retry_after(self):
        """Test that retry_after is calculated correctly."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        identifier = "test-user"
        
        # Use up the limit
        limiter.is_allowed(identifier)
        limiter.is_allowed(identifier)
        
        # Next request should be blocked with retry_after
        is_allowed, retry_after = limiter.is_allowed(identifier)
        assert is_allowed is False
        assert retry_after <= 60
        assert retry_after >= 1
    
    def test_rate_limiter_window_expiration(self):
        """Test that old requests are removed after window expires."""
        limiter = RateLimiter(max_requests=2, window_seconds=1)  # 1 second window
        identifier = "test-user"
        
        # Use up the limit
        limiter.is_allowed(identifier)
        limiter.is_allowed(identifier)
        
        # Should be blocked
        is_allowed, _ = limiter.is_allowed(identifier)
        assert is_allowed is False
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be allowed again
        is_allowed, _ = limiter.is_allowed(identifier)
        assert is_allowed is True
    
    def test_rate_limiter_different_identifiers(self):
        """Test that different identifiers have separate limits."""
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        
        # User 1 uses their limit
        limiter.is_allowed("user1")
        limiter.is_allowed("user1")
        
        # User 1 should be blocked
        is_allowed, _ = limiter.is_allowed("user1")
        assert is_allowed is False
        
        # User 2 should still be allowed
        is_allowed, _ = limiter.is_allowed("user2")
        assert is_allowed is True
    
    def test_rate_limiter_usage_stats(self):
        """Test getting usage statistics."""
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        identifier = "test-user"
        
        # Initial usage
        usage = limiter.get_usage(identifier)
        assert usage["used"] == 0
        assert usage["limit"] == 10
        assert usage["remaining"] == 10
        
        # After some requests
        limiter.is_allowed(identifier)
        limiter.is_allowed(identifier)
        limiter.is_allowed(identifier)
        
        usage = limiter.get_usage(identifier)
        assert usage["used"] == 3
        assert usage["remaining"] == 7
    
    async def test_rate_limit_headers_present(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test that rate limit headers are included in response."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/news",
            headers=auth_headers
        )
        
        # Check headers
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        
        # Check response structure
        result = response.json()
        assert result["success"] == True
        assert "metadata" in result
        assert_valid_metadata(result["metadata"])
    
    async def test_rate_limit_headers_values(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result,
        mock_settings
    ):
        """Test that rate limit header values are correct."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/news",
            headers=auth_headers
        )
        
        # Check header values
        assert response.status_code == 200
        limit = int(response.headers.get("X-RateLimit-Limit", 0))
        remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        
        assert limit == mock_settings.RATE_LIMIT_PER_HOUR
        assert remaining <= limit


@pytest.mark.unit
@pytest.mark.security
class TestCORSHeaders:
    """Test CORS (Cross-Origin Resource Sharing) functionality."""
    
    async def test_cors_preflight_request(
        self,
        async_client
    ):
        """Test CORS preflight OPTIONS request."""
        response = await async_client.options(
            "/api/v1/news",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization"
            }
        )
        
        # Preflight should return 200
        assert response.status_code == 200
    
    async def test_cors_headers_in_response(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test that CORS headers are included in actual requests."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Make request with Origin header
        response = await async_client.get(
            "/api/v1/news",
            headers={
                **auth_headers,
                "Origin": "http://example.com"
            }
        )
        
        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers or \
               "Access-Control-Allow-Origin" in response.headers


@pytest.mark.unit
@pytest.mark.security
class TestAuthenticationEndToEnd:
    """End-to-end authentication tests."""
    
    async def test_full_request_with_auth(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_item
    ):
        """Test complete authenticated request flow."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_collection.find_one.return_value = sample_news_item
        
        # Make authenticated request
        response = await async_client.get(
            f"/api/v1/news/{sample_news_item['slug']}",
            headers=auth_headers
        )
        
        # Should succeed
        assert response.status_code == 200
        result = response.json()
        
        # Check new structure
        assert result["success"] == True
        assert "data" in result
        assert "metadata" in result
        assert_valid_metadata(result["metadata"])
        
        # Check data
        assert result["data"]["slug"] == sample_news_item["slug"]
    
    async def test_multiple_endpoints_with_same_key(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        sample_news_item,
        create_mock_cursor_result
    ):
        """Test using same API key across multiple endpoints."""
        # Setup mocks
        mock_collection = mock_database_manager["collection"]
        
        # Mock for list endpoint
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Mock for detail endpoint
        mock_collection.find_one.return_value = sample_news_item
        
        # Test multiple endpoints
        response1 = await async_client.get("/api/v1/news", headers=auth_headers)
        assert response1.status_code == 200
        result1 = response1.json()
        assert result1["success"] == True
        
        response2 = await async_client.get(
            f"/api/v1/news/{sample_news_item['slug']}",
            headers=auth_headers
        )
        assert response2.status_code == 200
        result2 = response2.json()
        assert result2["success"] == True
        
        # Mock for aggregations
        mock_cursor2 = AsyncMock()
        mock_cursor2.to_list = AsyncMock(return_value=[])
        mock_collection.aggregate.return_value = mock_cursor2
        
        response3 = await async_client.get(
            "/api/v1/aggregations/stats",
            headers=auth_headers
        )
        assert response3.status_code == 200
        result3 = response3.json()
        assert result3["success"] == True
    
    async def test_auth_error_format(
        self,
        async_client,
        invalid_auth_headers
    ):
        """Test that authentication errors have proper format."""
        response = await async_client.get(
            "/api/v1/news",
            headers=invalid_auth_headers
        )
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
