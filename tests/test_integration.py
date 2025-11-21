"""
Integration tests for complete workflows.
Tests end-to-end scenarios combining multiple components.
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock


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
        data1 = response1.json()
        assert len(data1["data"]) <= 10
        assert data1["pagination"]["has_next"] is True
        next_cursor = data1["pagination"]["next_cursor"]
        
        # Step 2: Get second page
        second_page = sample_news_list[10:20]
        mock_cursor2 = create_mock_cursor_result(second_page)
        mock_collection.find.return_value = mock_cursor2
        
        response2 = await async_client.get(
            f"/api/v1/news?limit=10&cursor={next_cursor}",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["data"]) > 0
        
        # Step 3: Get article detail
        article_slug = data2["data"][0]["slug"]
        mock_collection.find_one.return_value = sample_news_list[10]
        
        response3 = await async_client.get(
            f"/api/v1/news/{article_slug}",
            headers=auth_headers
        )
        
        assert response3.status_code == 200
        detail = response3.json()
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
        data1 = response1.json()
        assert len(data1["data"]) > 0
        
        # Step 2: Filter by asset
        mock_cursor2 = create_mock_cursor_result(sample_bloomberg_news[:3])
        mock_collection.find.return_value = mock_cursor2
        
        response2 = await async_client.get(
            "/api/v1/news?source=bloomberg&asset_slug=bitcoin",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Step 3: Get details
        if len(data2["data"]) > 0:
            slug = data2["data"][0]["slug"]
            mock_collection.find_one.return_value = sample_bloomberg_news[0]
            
            response3 = await async_client.get(
                f"/api/v1/news/{slug}",
                headers=auth_headers
            )
            
            assert response3.status_code == 200


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
        stats = response1.json()
        assert "data" in stats
        assert "total" in stats
        
        # Step 2: Top assets
        mock_cursor.to_list = AsyncMock(return_value=sample_top_assets)
        mock_collection.aggregate.return_value = mock_cursor
        
        response2 = await async_client.get(
            "/api/v1/aggregations/top-assets?limit=5",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        top_assets = response2.json()
        assert "data" in top_assets
        
        # Step 3: Timeline
        mock_cursor.to_list = AsyncMock(return_value=sample_timeline_data)
        mock_collection.aggregate.return_value = mock_cursor
        
        response3 = await async_client.get(
            "/api/v1/aggregations/timeline?interval=daily",
            headers=auth_headers
        )
        
        assert response3.status_code == 200
        timeline = response3.json()
        assert "data" in timeline
        
        # Step 4: Source performance
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_collection.aggregate.return_value = mock_cursor
        
        response4 = await async_client.get(
            "/api/v1/aggregations/source-performance",
            headers=auth_headers
        )
        
        assert response4.status_code == 200
        performance = response4.json()
        assert "data" in performance
    
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
        from_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        to_date = datetime.now(timezone.utc).isoformat()
        
        # Get stats with date filter
        response1 = await async_client.get(
            f"/api/v1/aggregations/stats?group_by=date&from_date={from_date}&to_date={to_date}",
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        
        # Get timeline with date filter
        response2 = await async_client.get(
            f"/api/v1/aggregations/timeline?interval=daily&from_date={from_date}&to_date={to_date}",
            headers=auth_headers
        )
        
        assert response2.status_code == 200


@pytest.mark.integration
class TestErrorHandlingWorkflow:
    """Test error handling across different scenarios."""
    
    async def test_invalid_authentication_flow(
        self,
        async_client,
        invalid_auth_headers
    ):
        """Test that all endpoints properly reject invalid auth."""
        # News list
        response1 = await async_client.get(
            "/api/v1/news",
            headers=invalid_auth_headers
        )
        assert response1.status_code == 401
        
        # News detail
        response2 = await async_client.get(
            "/api/v1/news/some-slug",
            headers=invalid_auth_headers
        )
        assert response2.status_code == 401
        
        # Aggregations
        response3 = await async_client.get(
            "/api/v1/aggregations/stats",
            headers=invalid_auth_headers
        )
        assert response3.status_code == 401
    
    async def test_invalid_parameters_flow(
        self,
        async_client,
        auth_headers
    ):
        """Test handling of invalid parameters."""
        # Invalid date format
        response1 = await async_client.get(
            "/api/v1/news?from_date=invalid-date",
            headers=auth_headers
        )
        assert response1.status_code == 400
        
        # Invalid limit
        response2 = await async_client.get(
            "/api/v1/news?limit=5000",
            headers=auth_headers
        )
        assert response2.status_code == 422
        
        # Invalid group_by
        response3 = await async_client.get(
            "/api/v1/aggregations/stats?group_by=invalid",
            headers=auth_headers
        )
        assert response3.status_code == 400
    
    async def test_not_found_flow(
        self,
        async_client,
        auth_headers,
        mock_database_manager
    ):
        """Test 404 handling."""
        # Setup mock to return None
        mock_collection = mock_database_manager["collection"]
        mock_collection.find_one.return_value = None
        
        # Try to get non-existent article
        response = await async_client.get(
            "/api/v1/news/nonexistent-article",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data


@pytest.mark.integration
class TestSearchWorkflow:
    """Test search and filtering workflow."""
    
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
        data1 = response1.json()
        
        # Step 2: Refine with source
        mock_cursor2 = create_mock_cursor_result(search_results[:3])
        mock_collection.find.return_value = mock_cursor2
        
        response2 = await async_client.get(
            "/api/v1/news?keyword=bitcoin&source=bloomberg",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Step 3: Get details
        if len(data2["data"]) > 0:
            slug = data2["data"][0]["slug"]
            mock_collection.find_one.return_value = search_results[0]
            
            response3 = await async_client.get(
                f"/api/v1/news/{slug}",
                headers=auth_headers
            )
            
            assert response3.status_code == 200
    
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
        from_date = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        to_date = datetime.now(timezone.utc).isoformat()
        
        response = await async_client.get(
            f"/api/v1/news?source=bloomberg&asset_slug=bitcoin&keyword=price&from_date={from_date}&to_date={to_date}&limit=20",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data


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
        data1 = response1.json()
        assert data1["pagination"]["has_next"] is True
        cursor1 = data1["pagination"]["next_cursor"]
        
        # Page 2
        page2 = sample_news_list[10:20]
        mock_cursor2 = create_mock_cursor_result(page2)
        mock_collection.find.return_value = mock_cursor2
        
        response2 = await async_client.get(
            f"/api/v1/news?limit=10&cursor={cursor1}",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Page 3 (last page)
        page3 = sample_news_list[20:25]  # Only 5 items, less than limit
        mock_cursor3 = create_mock_cursor_result(page3)
        mock_collection.find.return_value = mock_cursor3
        
        if data2["pagination"]["has_next"]:
            cursor2 = data2["pagination"]["next_cursor"]
            response3 = await async_client.get(
                f"/api/v1/news?limit=10&cursor={cursor2}",
                headers=auth_headers
            )
            
            assert response3.status_code == 200
            data3 = response3.json()
            # Last page should have has_next = false
            assert data3["pagination"]["has_next"] is False
    
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
        
        # Descending order
        mock_cursor2 = create_mock_cursor_result(sample_news_list[:10])
        mock_collection.find.return_value = mock_cursor2
        
        response2 = await async_client.get(
            "/api/v1/news?order=desc&limit=10",
            headers=auth_headers
        )
        
        assert response2.status_code == 200


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
        data = response.json()
        assert len(data["data"]) <= 1000
    
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
        data = response.json()
        assert "status" in data
