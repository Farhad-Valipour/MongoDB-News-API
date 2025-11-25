"""
Integration tests for complete workflows.
Tests end-to-end scenarios combining multiple components.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock


def assert_valid_metadata(metadata):
    """Helper to validate metadata structure"""
    assert "query_time_ms" in metadata
    assert "timestamp" in metadata
    assert "api_version" in metadata
    assert metadata["api_version"] == "1.0.0"
    assert isinstance(metadata["query_time_ms"], (int, float))
    assert metadata["query_time_ms"] > 0


@pytest.mark.integration
class TestNewsWorkflow:
    """Test complete news browsing workflow."""
    
    async def test_browse_news_workflow(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """
        Test complete workflow:
        1. Get first page of news
        2. Navigate to second page using cursor
        3. Get details of specific article
        """
        mock_collection = mock_database_manager["collection"]
        
        # Step 1: Get first page
        first_page = sample_news_list[:11]  # 11 to indicate has_next
        mock_cursor1 = create_mock_cursor_result(first_page)
        mock_collection.find.return_value = mock_cursor1
        
        response1 = await async_client.get(
            "/api/v1/news?limit=10",
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        result1 = response1.json()
        
        # Check new structure
        assert result1["success"] == True
        assert "data" in result1
        assert "pagination" in result1
        assert "metadata" in result1
        assert_valid_metadata(result1["metadata"])
        
        # Check pagination
        assert len(result1["data"]) <= 10
        assert result1["pagination"]["has_next"] is True
        next_cursor = result1["pagination"]["next_cursor"]
        
        # Step 2: Get second page
        second_page = sample_news_list[10:20]
        mock_cursor2 = create_mock_cursor_result(second_page)
        mock_collection.find.return_value = mock_cursor2
        
        response2 = await async_client.get(
            f"/api/v1/news?limit=10&cursor={next_cursor}",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        result2 = response2.json()
        
        # Check new structure
        assert result2["success"] == True
        assert "metadata" in result2
        assert_valid_metadata(result2["metadata"])
        
        assert len(result2["data"]) > 0
        
        # Step 3: Get article detail
        article_slug = result2["data"][0]["slug"]
        mock_collection.find_one.return_value = sample_news_list[10]
        
        response3 = await async_client.get(
            f"/api/v1/news/{article_slug}",
            headers=auth_headers
        )
        
        assert response3.status_code == 200
        result3 = response3.json()
        
        # Check new structure for detail
        assert result3["success"] == True
        assert "data" in result3
        assert "metadata" in result3
        assert_valid_metadata(result3["metadata"])
        
        # Data is now wrapped in object
        detail = result3["data"]
        assert detail["slug"] == article_slug
        assert "content" in detail
    
    async def test_filtered_news_workflow(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_bloomberg_news,
        create_mock_cursor_result
    ):
        """
        Test filtered news workflow:
        1. Get news from specific source
        2. Filter by asset
        3. Get article details
        """
        mock_collection = mock_database_manager["collection"]
        
        # Step 1: Filter by source
        mock_cursor1 = create_mock_cursor_result(sample_bloomberg_news)
        mock_collection.find.return_value = mock_cursor1
        
        response1 = await async_client.get(
            "/api/v1/news?source=bloomberg",
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        result1 = response1.json()
        
        # Check new structure
        assert result1["success"] == True
        assert "metadata" in result1
        assert_valid_metadata(result1["metadata"])
        
        assert len(result1["data"]) > 0
        
        # Step 2: Filter by asset
        mock_cursor2 = create_mock_cursor_result(sample_bloomberg_news[:3])
        mock_collection.find.return_value = mock_cursor2
        
        response2 = await async_client.get(
            "/api/v1/news?source=bloomberg&asset_slug=bitcoin",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        result2 = response2.json()
        
        # Check new structure
        assert result2["success"] == True
        assert "metadata" in result2
        assert_valid_metadata(result2["metadata"])
        
        # Step 3: Get details
        if len(result2["data"]) > 0:
            slug = result2["data"][0]["slug"]
            mock_collection.find_one.return_value = sample_bloomberg_news[0]
            
            response3 = await async_client.get(
                f"/api/v1/news/{slug}",
                headers=auth_headers
            )
            
            assert response3.status_code == 200
            result3 = response3.json()
            
            # Check new structure
            assert result3["success"] == True
            assert "metadata" in result3
            assert_valid_metadata(result3["metadata"])


@pytest.mark.integration
class TestAnalyticsWorkflow:
    """Test analytics and aggregation workflow."""
    
    async def test_analytics_dashboard_workflow(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_aggregation_stats,
        sample_top_assets,
        sample_timeline_data
    ):
        """
        Test complete analytics workflow:
        1. Get stats by source
        2. Get top assets
        3. Get timeline
        4. Get source performance
        """
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        
        # Step 1: Stats by source
        mock_cursor.to_list = AsyncMock(return_value=sample_aggregation_stats)
        mock_collection.aggregate.return_value = mock_cursor
        
        response1 = await async_client.get(
            "/api/v1/aggregations/stats?group_by=source",
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        result1 = response1.json()
        
        # Check new structure
        assert result1["success"] == True
        assert "data" in result1
        assert "metadata" in result1
        assert_valid_metadata(result1["metadata"])
        
        # Check that data items have filters and total
        for item in result1["data"]:
            assert "total" in item
        
        # Step 2: Top assets
        mock_cursor.to_list = AsyncMock(return_value=sample_top_assets)
        mock_collection.aggregate.return_value = mock_cursor
        
        response2 = await async_client.get(
            "/api/v1/aggregations/top-assets?limit=5",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        result2 = response2.json()
        
        # Check new structure
        assert result2["success"] == True
        assert "data" in result2
        assert "metadata" in result2
        assert_valid_metadata(result2["metadata"])
        
        # Step 3: Timeline
        mock_cursor.to_list = AsyncMock(return_value=sample_timeline_data)
        mock_collection.aggregate.return_value = mock_cursor
        
        response3 = await async_client.get(
            "/api/v1/aggregations/timeline?interval=daily",
            headers=auth_headers
        )
        
        assert response3.status_code == 200
        result3 = response3.json()
        
        # Check new structure
        assert result3["success"] == True
        assert "data" in result3
        assert "metadata" in result3
        assert_valid_metadata(result3["metadata"])
        
        # Step 4: Source performance
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_collection.aggregate.return_value = mock_cursor
        
        response4 = await async_client.get(
            "/api/v1/aggregations/source-performance",
            headers=auth_headers
        )
        
        assert response4.status_code == 200
        result4 = response4.json()
        
        # Check new structure
        assert result4["success"] == True
        assert "data" in result4
        assert "metadata" in result4
        assert_valid_metadata(result4["metadata"])
    
    async def test_time_filtered_analytics(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_timeline_data
    ):
        """Test analytics with time range filtering."""
        mock_collection = mock_database_manager["collection"]
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=sample_timeline_data)
        mock_collection.aggregate.return_value = mock_cursor
        
        # Define date range
        start = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        end = datetime.now(timezone.utc).isoformat()
        
        # Get stats with date filter
        response1 = await async_client.get(
            f"/api/v1/aggregations/stats?group_by=date&start={start}&end={end}",
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        result1 = response1.json()
        
        # Check new structure
        assert result1["success"] == True
        assert "metadata" in result1
        assert_valid_metadata(result1["metadata"])
        
        # Get timeline with date filter
        response2 = await async_client.get(
            f"/api/v1/aggregations/timeline?interval=daily&start={start}&end={end}",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        result2 = response2.json()
        
        # Check new structure
        assert result2["success"] == True
        assert "metadata" in result2
        assert_valid_metadata(result2["metadata"])


@pytest.mark.integration
class TestErrorHandlingWorkflow:
    """Test error handling across different scenarios."""
    
    async def test_invalid_authentication_flow(
        self,
        async_client,
        invalid_auth_headers
    ):
        """Test that all endpoints properly reject invalid auth."""
        endpoints = [
            "/api/v1/news",
            "/api/v1/news/some-slug",
            "/api/v1/aggregations/stats?group_by=source",
            "/api/v1/aggregations/top-assets",
            "/api/v1/aggregations/timeline?interval=daily",
            "/api/v1/aggregations/source-performance"
        ]
        
        for endpoint in endpoints:
            response = await async_client.get(
                endpoint,
                headers=invalid_auth_headers
            )
            assert response.status_code == 401, f"Endpoint {endpoint} did not return 401"
    
    async def test_not_found_flow(
        self,
        async_client,
        auth_headers,
        mock_database_manager
    ):
        """Test 404 error handling."""
        # Setup mock to return None
        mock_collection = mock_database_manager["collection"]
        mock_collection.find_one.return_value = None
        
        # Request nonexistent news
        response = await async_client.get(
            "/api/v1/news/nonexistent-slug",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        result = response.json()
        assert "error" in result
    
    async def test_validation_error_flow(
        self,
        async_client,
        auth_headers
    ):
        """Test validation error handling."""
        # Invalid limit (too low)
        response1 = await async_client.get(
            "/api/v1/news?limit=5",
            headers=auth_headers
        )
        assert response1.status_code == 422
        
        # Invalid limit (too high)
        response2 = await async_client.get(
            "/api/v1/news?limit=2000",
            headers=auth_headers
        )
        assert response2.status_code == 422


@pytest.mark.integration
class TestSearchWorkflow:
    """Test search and filtering workflows."""
    
    async def test_keyword_search_workflow(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """
        Test search workflow:
        1. Search by keyword
        2. Refine with source filter
        3. Get article details
        """
        mock_collection = mock_database_manager["collection"]
        
        # Step 1: Search by keyword
        search_results = sample_news_list[:5]
        mock_cursor1 = create_mock_cursor_result(search_results)
        mock_collection.find.return_value = mock_cursor1
        
        response1 = await async_client.get(
            "/api/v1/news?keyword=bitcoin",
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        result1 = response1.json()
        
        # Check new structure
        assert result1["success"] == True
        assert "metadata" in result1
        assert_valid_metadata(result1["metadata"])
        
        # Step 2: Refine with source
        mock_cursor2 = create_mock_cursor_result(search_results[:3])
        mock_collection.find.return_value = mock_cursor2
        
        response2 = await async_client.get(
            "/api/v1/news?keyword=bitcoin&source=bloomberg",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        result2 = response2.json()
        
        # Check new structure
        assert result2["success"] == True
        assert "metadata" in result2
        assert_valid_metadata(result2["metadata"])
        
        # Step 3: Get details
        if len(result2["data"]) > 0:
            slug = result2["data"][0]["slug"]
            mock_collection.find_one.return_value = search_results[0]
            
            response3 = await async_client.get(
                f"/api/v1/news/{slug}",
                headers=auth_headers
            )
            
            assert response3.status_code == 200
            result3 = response3.json()
            
            # Check new structure
            assert result3["success"] == True
            assert "metadata" in result3
            assert_valid_metadata(result3["metadata"])
    
    async def test_complex_filtering_workflow(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test complex filtering with multiple parameters."""
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:5])
        mock_collection.find.return_value = mock_cursor
        
        # Complex query with multiple filters
        start = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        end = datetime.now(timezone.utc).isoformat()
        
        response = await async_client.get(
            f"/api/v1/news?source=bloomberg&asset_slug=bitcoin&keyword=price&start={start}&end={end}&limit=20",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Check new structure
        assert result["success"] == True
        assert "data" in result
        assert "pagination" in result
        assert "metadata" in result
        assert_valid_metadata(result["metadata"])


@pytest.mark.integration
class TestPaginationWorkflow:
    """Test complete pagination scenarios."""
    
    async def test_full_pagination_cycle(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """
        Test full pagination cycle:
        1. Get page 1
        2. Get page 2
        3. Get page 3
        4. Verify no more pages
        """
        mock_collection = mock_database_manager["collection"]
        
        # Page 1
        page1 = sample_news_list[:11]
        mock_cursor1 = create_mock_cursor_result(page1)
        mock_collection.find.return_value = mock_cursor1
        
        response1 = await async_client.get(
            "/api/v1/news?limit=10",
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        result1 = response1.json()
        
        # Check new structure
        assert result1["success"] == True
        assert "pagination" in result1
        assert "metadata" in result1
        assert_valid_metadata(result1["metadata"])
        
        assert result1["pagination"]["has_next"] is True
        cursor1 = result1["pagination"]["next_cursor"]
        
        # Page 2
        page2 = sample_news_list[10:20]
        mock_cursor2 = create_mock_cursor_result(page2)
        mock_collection.find.return_value = mock_cursor2
        
        response2 = await async_client.get(
            f"/api/v1/news?limit=10&cursor={cursor1}",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        result2 = response2.json()
        
        # Check new structure
        assert result2["success"] == True
        assert "metadata" in result2
        assert_valid_metadata(result2["metadata"])
        
        # Page 3 (last page)
        page3 = sample_news_list[20:25]  # Only 5 items, less than limit
        mock_cursor3 = create_mock_cursor_result(page3)
        mock_collection.find.return_value = mock_cursor3
        
        if result2["pagination"]["has_next"]:
            cursor2 = result2["pagination"]["next_cursor"]
            response3 = await async_client.get(
                f"/api/v1/news?limit=10&cursor={cursor2}",
                headers=auth_headers
            )
            
            assert response3.status_code == 200
            result3 = response3.json()
            
            # Check new structure
            assert result3["success"] == True
            assert "metadata" in result3
            assert_valid_metadata(result3["metadata"])
            
            # Last page should have has_next = false
            assert result3["pagination"]["has_next"] is False
    
    async def test_pagination_with_sorting(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test pagination with different sort orders."""
        mock_collection = mock_database_manager["collection"]
        
        # Ascending order
        mock_cursor1 = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor1
        
        response1 = await async_client.get(
            "/api/v1/news?order=asc&limit=10",
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        result1 = response1.json()
        
        # Check new structure
        assert result1["success"] == True
        assert "metadata" in result1
        assert_valid_metadata(result1["metadata"])
        
        # Descending order
        mock_cursor2 = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor2
        
        response2 = await async_client.get(
            "/api/v1/news?order=desc&limit=10",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        result2 = response2.json()
        
        # Check new structure
        assert result2["success"] == True
        assert "metadata" in result2
        assert_valid_metadata(result2["metadata"])


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceWorkflow:
    """Test performance-related scenarios."""
    
    async def test_large_result_set_handling(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test handling of large result sets."""
        mock_collection = mock_database_manager["collection"]
        
        # Request maximum limit
        large_result = sample_news_list * 50  # Large dataset
        mock_cursor = create_mock_cursor_result(large_result[:1000])
        mock_collection.find.return_value = mock_cursor
        
        response = await async_client.get(
            "/api/v1/news?limit=1000",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        
        # Check new structure
        assert result["success"] == True
        assert "metadata" in result
        assert_valid_metadata(result["metadata"])
        
        assert len(result["data"]) <= 1000
    
    async def test_concurrent_requests_simulation(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Simulate concurrent requests (basic test)."""
        mock_collection = mock_database_manager["collection"]
        mock_cursor = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor
        
        # Make multiple requests
        responses = []
        for _ in range(5):
            response = await async_client.get(
                "/api/v1/news",
                headers=auth_headers
            )
            responses.append(response)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)
        
        # All should have valid structure
        for r in responses:
            result = r.json()
            assert result["success"] == True
            assert "metadata" in result
            assert_valid_metadata(result["metadata"])


@pytest.mark.integration
class TestHealthCheckWorkflow:
    """Test health check and monitoring endpoints."""
    
    async def test_health_check_flow(
        self,
        async_client,
        mock_database_manager
    ):
        """Test health check endpoints."""
        # Mock database ping
        mock_client = mock_database_manager["db"].__class__
        
        # Health check should work without auth
        response = await async_client.get("/api/v1/health")
        
        # Should return status
        assert response.status_code == 200
        result = response.json()
        assert "status" in result
