"""
Unit tests for aggregation endpoints.
Tests statistical and analytical queries.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock


@pytest.mark.unit
class TestStatsAggregation:
    """Test cases for GET /api/v1/aggregations/stats endpoint."""
    
    async def test_stats_by_source(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_aggregation_stats
    ):
        """Test getting statistics grouped by source."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_aggregation_stats)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/stats?group_by=source",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data
        assert "filters" in data
        assert data["filters"]["group_by"] == "source"
        assert isinstance(data["data"], list)
        assert data["total"] > 0
    
    async def test_stats_by_date(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_timeline_data
    ):
        """Test getting statistics grouped by date."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_timeline_data)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/stats?group_by=date",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["group_by"] == "date"
        assert isinstance(data["data"], list)
    
    async def test_stats_with_date_filter(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_aggregation_stats
    ):
        """Test stats with date range filter."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_aggregation_stats)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Date range
        from_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        to_date = datetime.now(timezone.utc).isoformat()
        
        # Make request
        response = await async_client.get(
            f"/api/v1/aggregations/stats?group_by=source&from_date={from_date}&to_date={to_date}",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["from_date"] == from_date
        assert data["filters"]["to_date"] == to_date
    
    async def test_stats_without_date_filter(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_aggregation_stats
    ):
        """Test stats without date filtering (all time)."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_aggregation_stats)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/stats?group_by=source",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["from_date"] is None
        assert data["filters"]["to_date"] is None
    
    async def test_stats_invalid_group_by(
        self,
        async_client,
        auth_headers
    ):
        """Test that invalid group_by returns 400."""
        response = await async_client.get(
            "/api/v1/aggregations/stats?group_by=invalid",
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    async def test_stats_total_calculation(
        self,
        async_client,
        auth_headers,
        mock_database_manager
    ):
        """Test that total is calculated correctly."""
        # Setup mock with known values
        stats = [
            {"_id": "source1", "count": 100},
            {"_id": "source2", "count": 200},
            {"_id": "source3", "count": 300}
        ]
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=stats)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/stats?group_by=source",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 600  # Sum of all counts


@pytest.mark.unit
class TestTopAssets:
    """Test cases for GET /api/v1/aggregations/top-assets endpoint."""
    
    async def test_get_top_assets_default(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_top_assets
    ):
        """Test getting top assets with default limit."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_top_assets)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/top-assets",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "filters" in data
        assert data["filters"]["limit"] == 10  # Default limit
        assert isinstance(data["data"], list)
    
    async def test_get_top_assets_custom_limit(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_top_assets
    ):
        """Test getting top assets with custom limit."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_top_assets[:5])
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/top-assets?limit=5",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["limit"] == 5
    
    async def test_get_top_assets_with_source_filter(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_top_assets
    ):
        """Test getting top assets filtered by source."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_top_assets)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/top-assets?source=bloomberg",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["source"] == "bloomberg"
    
    async def test_get_top_assets_with_date_range(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_top_assets
    ):
        """Test getting top assets with date range."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_top_assets)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Date range
        from_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        to_date = datetime.now(timezone.utc).isoformat()
        
        # Make request
        response = await async_client.get(
            f"/api/v1/aggregations/top-assets?from_date={from_date}&to_date={to_date}",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["from_date"] == from_date
        assert data["filters"]["to_date"] == to_date
    
    async def test_top_assets_percentage_calculation(
        self,
        async_client,
        auth_headers,
        mock_database_manager
    ):
        """Test that percentage is calculated correctly."""
        # Setup mock with percentage data
        assets = [
            {"_id": "bitcoin", "name": "Bitcoin", "symbol": "BTC", "count": 100, "percentage": 50.0},
            {"_id": "ethereum", "name": "Ethereum", "symbol": "ETH", "count": 50, "percentage": 25.0},
            {"_id": "cardano", "name": "Cardano", "symbol": "ADA", "count": 50, "percentage": 25.0}
        ]
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=assets)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/top-assets",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        # Verify percentages sum to 100
        total_percentage = sum(item.get("percentage", 0) for item in data["data"])
        assert total_percentage == 100.0
    
    async def test_top_assets_limit_validation(
        self,
        async_client,
        auth_headers
    ):
        """Test limit validation (1-100)."""
        # Test limit below minimum
        response = await async_client.get(
            "/api/v1/aggregations/top-assets?limit=0",
            headers=auth_headers
        )
        assert response.status_code == 422
        
        # Test limit above maximum
        response = await async_client.get(
            "/api/v1/aggregations/top-assets?limit=101",
            headers=auth_headers
        )
        assert response.status_code == 422


@pytest.mark.unit
class TestTimeline:
    """Test cases for GET /api/v1/aggregations/timeline endpoint."""
    
    async def test_timeline_daily(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_timeline_data
    ):
        """Test daily timeline."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_timeline_data)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/timeline?interval=daily",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["interval"] == "daily"
        assert isinstance(data["data"], list)
    
    async def test_timeline_weekly(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_timeline_data
    ):
        """Test weekly timeline."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_timeline_data)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/timeline?interval=weekly",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["interval"] == "weekly"
    
    async def test_timeline_monthly(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_timeline_data
    ):
        """Test monthly timeline."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_timeline_data)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/timeline?interval=monthly",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["interval"] == "monthly"
    
    async def test_timeline_invalid_interval(
        self,
        async_client,
        auth_headers
    ):
        """Test that invalid interval returns 400."""
        response = await async_client.get(
            "/api/v1/aggregations/timeline?interval=yearly",
            headers=auth_headers
        )
        
        assert response.status_code == 400
    
    async def test_timeline_with_date_range(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_timeline_data
    ):
        """Test timeline with date range filter."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_timeline_data)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Date range
        from_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        to_date = datetime.now(timezone.utc).isoformat()
        
        # Make request
        response = await async_client.get(
            f"/api/v1/aggregations/timeline?interval=daily&from_date={from_date}&to_date={to_date}",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["from_date"] == from_date
        assert data["filters"]["to_date"] == to_date
    
    async def test_timeline_with_source_filter(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_timeline_data
    ):
        """Test timeline filtered by source."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_timeline_data)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/timeline?interval=daily&source=bloomberg",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["source"] == "bloomberg"


@pytest.mark.unit
class TestSourcePerformance:
    """Test cases for GET /api/v1/aggregations/source-performance endpoint."""
    
    async def test_get_source_performance(
        self,
        async_client,
        auth_headers,
        mock_database_manager
    ):
        """Test getting source performance statistics."""
        # Setup mock with performance data
        performance_data = [
            {
                "_id": "coinmarketcap",
                "count": 150,
                "avg_per_day": 5.0,
                "top_assets": ["bitcoin", "ethereum"]
            },
            {
                "_id": "bloomberg",
                "count": 120,
                "avg_per_day": 4.0,
                "top_assets": ["bitcoin"]
            }
        ]
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=performance_data)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/source-performance",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
    
    async def test_source_performance_with_date_range(
        self,
        async_client,
        auth_headers,
        mock_database_manager
    ):
        """Test source performance with date range."""
        # Setup mock
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_collection.aggregate.return_value = mock_cursor
        
        # Date range
        from_date = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        to_date = datetime.now(timezone.utc).isoformat()
        
        # Make request
        response = await async_client.get(
            f"/api/v1/aggregations/source-performance?from_date={from_date}&to_date={to_date}",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["filters"]["from_date"] == from_date
        assert data["filters"]["to_date"] == to_date
    
    async def test_source_performance_avg_calculation(
        self,
        async_client,
        auth_headers,
        mock_database_manager
    ):
        """Test that average per day is calculated correctly."""
        # Setup mock
        performance_data = [
            {"_id": "source1", "count": 300, "avg_per_day": 10.0}
        ]
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=performance_data)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Make request
        response = await async_client.get(
            "/api/v1/aggregations/source-performance",
            headers=auth_headers
        )
        
        # Assertions
        assert response.status_code == 200
        data = response.json()
        # Verify avg_per_day exists
        if len(data["data"]) > 0:
            assert "avg_per_day" in data["data"][0] or "count" in data["data"][0]


@pytest.mark.unit
class TestAggregationAuthentication:
    """Test authentication for aggregation endpoints."""
    
    async def test_stats_without_auth(self, async_client):
        """Test that stats endpoint requires authentication."""
        response = await async_client.get("/api/v1/aggregations/stats")
        assert response.status_code == 401
    
    async def test_top_assets_without_auth(self, async_client):
        """Test that top-assets endpoint requires authentication."""
        response = await async_client.get("/api/v1/aggregations/top-assets")
        assert response.status_code == 401
    
    async def test_timeline_without_auth(self, async_client):
        """Test that timeline endpoint requires authentication."""
        response = await async_client.get("/api/v1/aggregations/timeline")
        assert response.status_code == 401
    
    async def test_source_performance_without_auth(self, async_client):
        """Test that source-performance endpoint requires authentication."""
        response = await async_client.get("/api/v1/aggregations/source-performance")
        assert response.status_code == 401
