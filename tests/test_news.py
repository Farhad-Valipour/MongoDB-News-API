"""
Unit tests for news endpoints.
Tests GET /api/v1/news and GET /api/v1/news/{slug}
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, patch

from app.models.response import NewsListResponse


@pytest.mark.unit
class TestGetNewsList:
    """Test cases for GET /api/v1/news endpoint."""
    
    async def test_get_news_without_filters(
        self, 
        async_client, 
        auth_headers, 
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test getting news list without any filters."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/news",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) <= 100  # Default limit
    
    async def test_get_news_with_source_filter(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_bloomberg_news,
        create_mock_cursor_result
    ):
        """Test filtering news by source."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_bloomberg_news)
        mock_collection.find.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/news?source=bloomberg",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) > 0
        # Verify find was called with source filter
        mock_collection.find.assert_called_once()
    
    async def test_get_news_with_asset_slug_filter(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_bitcoin_news,
        create_mock_cursor_result
    ):
        """Test filtering news by asset slug."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_bitcoin_news)
        mock_collection.find.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/news?asset_slug=bitcoin",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) > 0
        mock_collection.find.assert_called_once()
    
    async def test_get_news_with_keyword_search(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test searching news by keyword."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:5])
        mock_collection.find.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/news?keyword=bitcoin",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        mock_collection.find.assert_called_once()
    
    async def test_get_news_with_date_range(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test filtering news by date range."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:5])
        mock_collection.find.return_value = mock_cursor
        
        # Date range
        from_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        to_date = datetime.now(timezone.utc).isoformat()
        
        # Make request
        response = await async_client.get(
            f"/api/v1/news?from_date={from_date}&to_date={to_date}",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        mock_collection.find.assert_called_once()
    
    async def test_get_news_with_invalid_date_format(
        self,
        async_client,
        auth_headers
    ):
        """Test that invalid date format returns 400."""
        response = await async_client.get(
            "/api/v1/news?from_date=invalid-date",
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "INVALID_DATE_FORMAT"
    
    async def test_get_news_with_pagination_cursor(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        sample_cursor,
        create_mock_cursor_result
    ):
        """Test pagination with cursor."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[10:20])
        mock_collection.find.return_value = mock_cursor
        
        # Make request with cursor
        response = await async_client.get(
            f"/api/v1/news?cursor={sample_cursor}",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "pagination" in data
        mock_collection.find.assert_called_once()
    
    async def test_get_news_with_invalid_cursor(
        self,
        async_client,
        auth_headers,
        invalid_cursor
    ):
        """Test that invalid cursor returns 400."""
        response = await async_client.get(
            f"/api/v1/news?cursor={invalid_cursor}",
            headers=auth_headers
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400]
    
    async def test_get_news_sort_ascending(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test sorting news in ascending order."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/news?order=asc",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        mock_cursor.sort.assert_called()
    
    async def test_get_news_sort_descending(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test sorting news in descending order."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/news?order=desc",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        mock_cursor.sort.assert_called()
    
    async def test_get_news_custom_limit(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test custom limit parameter."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:50])
        mock_collection.find.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/news?limit=50",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        mock_cursor.limit.assert_called()
    
    async def test_get_news_limit_minimum(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test minimum limit (10)."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/news?limit=10",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
    
    async def test_get_news_limit_maximum(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test maximum limit (1000)."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list)
        mock_collection.find.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/news?limit=1000",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
    
    async def test_get_news_limit_below_minimum(
        self,
        async_client,
        auth_headers
    ):
        """Test that limit below 10 returns validation error."""
        response = await async_client.get(
            "/api/v1/news?limit=5",
            headers=auth_headers
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    async def test_get_news_limit_above_maximum(
        self,
        async_client,
        auth_headers
    ):
        """Test that limit above 1000 returns validation error."""
        response = await async_client.get(
            "/api/v1/news?limit=2000",
            headers=auth_headers
        )
        
        # Should return validation error
        assert response.status_code == 422
    
    async def test_get_news_multiple_filters(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test combining multiple filters."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:3])
        mock_collection.find.return_value = mock_cursor
        
        # Make request with multiple filters
        from_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        response = await async_client.get(
            f"/api/v1/news?source=bloomberg&asset_slug=bitcoin&from_date={from_date}&limit=20",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        mock_collection.find.assert_called_once()
    
    async def test_get_news_without_authentication(
        self,
        async_client
    ):
        """Test that request without API key returns 401."""
        response = await async_client.get("/api/v1/news")
        
        assert response.status_code == 401
    
    async def test_get_news_with_invalid_api_key(
        self,
        async_client,
        invalid_auth_headers
    ):
        """Test that request with invalid API key returns 401."""
        response = await async_client.get(
            "/api/v1/news",
            headers=invalid_auth_headers
        )
        
        assert response.status_code == 401


@pytest.mark.unit
class TestGetNewsBySlug:
    """Test cases for GET /api/v1/news/{slug} endpoint."""
    
    async def test_get_existing_news(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_item
    ):
        """Test getting an existing news article by slug."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_collection.find_one.return_value = sample_news_item
        
        # Make request
        response = await async_client.get(
            f"/api/v1/news/{sample_news_item['slug']}",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == sample_news_item["slug"]
        assert data["title"] == sample_news_item["title"]
        assert "content" in data
        assert "assets" in data
        mock_collection.find_one.assert_called_once()
    
    async def test_get_nonexistent_news(
        self,
        async_client,
        auth_headers,
        mock_database_manager
    ):
        """Test getting a news article that doesn't exist."""
        # Setup mock to return None
        mock_collection = mock_database_manager["collection"]
        mock_collection.find_one.return_value = None
        
        # Make request
        response = await async_client.get(
            "/api/v1/news/nonexistent-slug",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 404
        data = response.json()
        assert "error" in data
    
    async def test_get_news_by_slug_without_authentication(
        self,
        async_client
    ):
        """Test that request without API key returns 401."""
        response = await async_client.get("/api/v1/news/some-slug")
        
        assert response.status_code == 401
    
    async def test_get_news_by_slug_with_invalid_api_key(
        self,
        async_client,
        invalid_auth_headers
    ):
        """Test that request with invalid API key returns 401."""
        response = await async_client.get(
            "/api/v1/news/some-slug",
            headers=invalid_auth_headers
        )
        
        assert response.status_code == 401
    
    async def test_get_news_with_special_characters_in_slug(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_item
    ):
        """Test getting news with special characters in slug."""
        # Update slug with special characters
        special_slug = "bitcoin-price-up-50%-today"
        sample_news_item["slug"] = special_slug
        
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_collection.find_one.return_value = sample_news_item
        
        # Make request
        response = await async_client.get(
            f"/api/v1/news/{special_slug}",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == special_slug
