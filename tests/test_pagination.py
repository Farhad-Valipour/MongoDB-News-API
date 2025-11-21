"""
Unit tests for cursor-based pagination.
Tests cursor encoding/decoding and pagination logic.
"""

import pytest
import base64
import json
from datetime import datetime, timezone, timedelta

from app.core.pagination import PaginationCursor, create_pagination_response
from app.utils.exceptions import InvalidCursorException


@pytest.mark.unit
class TestCursorEncoding:
    """Test cursor encoding functionality."""
    
    def test_encode_cursor_with_datetime(self):
        """Test encoding cursor with datetime field."""
        now = datetime.now(timezone.utc)
        cursor_data = {
            "_id": "507f1f77bcf86cd799439011",
            "releasedAt": now
        }
        
        encoded = PaginationCursor.encode(cursor_data)
        
        # Should be base64 string
        assert isinstance(encoded, str)
        assert len(encoded) > 0
        
        # Should be decodable
        decoded_str = base64.b64decode(encoded.encode()).decode()
        decoded_data = json.loads(decoded_str)
        assert "_id" in decoded_data
        assert "releasedAt" in decoded_data
    
    def test_encode_cursor_with_timezone_aware_datetime(self):
        """Test encoding timezone-aware datetime."""
        aware_dt = datetime(2025, 11, 20, 12, 0, 0, tzinfo=timezone.utc)
        cursor_data = {
            "_id": "507f1f77bcf86cd799439011",
            "releasedAt": aware_dt
        }
        
        encoded = PaginationCursor.encode(cursor_data)
        decoded_str = base64.b64decode(encoded.encode()).decode()
        decoded_data = json.loads(decoded_str)
        
        # Check that datetime was converted to ISO format
        assert "T" in decoded_data["releasedAt"]
        assert decoded_data["releasedAt"].endswith("Z") or "+00:00" in decoded_data["releasedAt"]
    
    def test_encode_cursor_with_naive_datetime(self):
        """Test encoding naive datetime (without timezone)."""
        naive_dt = datetime(2025, 11, 20, 12, 0, 0)
        cursor_data = {
            "_id": "507f1f77bcf86cd799439011",
            "releasedAt": naive_dt
        }
        
        encoded = PaginationCursor.encode(cursor_data)
        
        # Should still encode successfully
        assert isinstance(encoded, str)
        assert len(encoded) > 0
    
    def test_encode_cursor_with_multiple_fields(self):
        """Test encoding cursor with multiple fields."""
        cursor_data = {
            "_id": "507f1f77bcf86cd799439011",
            "releasedAt": datetime.now(timezone.utc),
            "title": "Test Article"
        }
        
        encoded = PaginationCursor.encode(cursor_data)
        decoded_str = base64.b64decode(encoded.encode()).decode()
        decoded_data = json.loads(decoded_str)
        
        assert len(decoded_data) == 3
        assert all(key in decoded_data for key in ["_id", "releasedAt", "title"])
    
    def test_encode_cursor_consistent_output(self):
        """Test that encoding same data produces consistent output."""
        cursor_data = {
            "_id": "507f1f77bcf86cd799439011",
            "releasedAt": datetime(2025, 11, 20, 12, 0, 0, tzinfo=timezone.utc)
        }
        
        encoded1 = PaginationCursor.encode(cursor_data)
        encoded2 = PaginationCursor.encode(cursor_data)
        
        # Should produce same encoded string
        assert encoded1 == encoded2


@pytest.mark.unit
class TestCursorDecoding:
    """Test cursor decoding functionality."""
    
    def test_decode_valid_cursor(self):
        """Test decoding a valid cursor."""
        # Create valid cursor
        original_data = {
            "_id": "507f1f77bcf86cd799439011",
            "releasedAt": "2025-11-20T12:00:00Z"
        }
        json_str = json.dumps(original_data)
        encoded = base64.b64encode(json_str.encode()).decode()
        
        # Decode
        decoded = PaginationCursor.decode(encoded)
        
        assert decoded["_id"] == original_data["_id"]
        assert decoded["releasedAt"] == original_data["releasedAt"]
    
    def test_decode_invalid_base64(self):
        """Test that invalid base64 raises exception."""
        invalid_cursor = "not-valid-base64!@#$"
        
        with pytest.raises(InvalidCursorException):
            PaginationCursor.decode(invalid_cursor)
    
    def test_decode_invalid_json(self):
        """Test that invalid JSON raises exception."""
        # Valid base64 but invalid JSON
        invalid_json = base64.b64encode(b"not-json").decode()
        
        with pytest.raises(InvalidCursorException):
            PaginationCursor.decode(invalid_json)
    
    def test_decode_empty_cursor(self):
        """Test decoding empty cursor."""
        with pytest.raises(InvalidCursorException):
            PaginationCursor.decode("")
    
    def test_encode_decode_roundtrip(self):
        """Test that encode -> decode returns original data."""
        original = {
            "_id": "507f1f77bcf86cd799439011",
            "releasedAt": datetime(2025, 11, 20, 12, 0, 0, tzinfo=timezone.utc)
        }
        
        encoded = PaginationCursor.encode(original)
        decoded = PaginationCursor.decode(encoded)
        
        # _id should match
        assert decoded["_id"] == original["_id"]
        # releasedAt should be ISO string after encoding
        assert "releasedAt" in decoded
        assert isinstance(decoded["releasedAt"], str)


@pytest.mark.unit
class TestCursorQuery:
    """Test cursor query building for MongoDB."""
    
    def test_build_query_descending_order(self):
        """Test building query for descending order pagination."""
        cursor_data = {
            "_id": "507f1f77bcf86cd799439011",
            "releasedAt": "2025-11-20T12:00:00Z"
        }
        
        query = PaginationCursor.build_cursor_query(
            cursor_data,
            sort_field="releasedAt",
            sort_order="desc"
        )
        
        # Should have $or query with $lt operator
        assert "$or" in query
        assert len(query["$or"]) == 2
    
    def test_build_query_ascending_order(self):
        """Test building query for ascending order pagination."""
        cursor_data = {
            "_id": "507f1f77bcf86cd799439011",
            "releasedAt": "2025-11-20T12:00:00Z"
        }
        
        query = PaginationCursor.build_cursor_query(
            cursor_data,
            sort_field="releasedAt",
            sort_order="asc"
        )
        
        # Should have $or query with $gt operator
        assert "$or" in query
        assert len(query["$or"]) == 2
    
    def test_build_query_empty_cursor(self):
        """Test building query with empty cursor data."""
        query = PaginationCursor.build_cursor_query(
            {},
            sort_field="releasedAt",
            sort_order="desc"
        )
        
        # Should return empty query
        assert query == {}
    
    def test_build_query_missing_id(self):
        """Test building query when _id is missing."""
        cursor_data = {
            "releasedAt": "2025-11-20T12:00:00Z"
        }
        
        query = PaginationCursor.build_cursor_query(
            cursor_data,
            sort_field="releasedAt",
            sort_order="desc"
        )
        
        # Should return empty query
        assert query == {}
    
    def test_build_query_missing_sort_field(self):
        """Test building query when sort field is missing."""
        cursor_data = {
            "_id": "507f1f77bcf86cd799439011"
        }
        
        query = PaginationCursor.build_cursor_query(
            cursor_data,
            sort_field="releasedAt",
            sort_order="desc"
        )
        
        # Should return empty query
        assert query == {}
    
    def test_build_query_with_datetime_field(self):
        """Test building query with datetime sort field."""
        cursor_data = {
            "_id": "507f1f77bcf86cd799439011",
            "createdAt": "2025-11-20T12:00:00Z"
        }
        
        query = PaginationCursor.build_cursor_query(
            cursor_data,
            sort_field="createdAt",
            sort_order="desc"
        )
        
        assert "$or" in query
        # The datetime string should be converted back to datetime object
        assert "createdAt" in query["$or"][0]


@pytest.mark.unit
class TestPaginationResponse:
    """Test pagination response creation."""
    
    def test_create_response_with_next(self):
        """Test creating response when there are more items."""
        items = [
            {
                "_id": f"id{i}",
                "releasedAt": datetime.now(timezone.utc) - timedelta(hours=i),
                "title": f"Article {i}"
            }
            for i in range(11)  # 11 items, limit 10
        ]
        
        pagination = create_pagination_response(
            items=items,
            limit=10,
            sort_field="releasedAt",
            has_prev=False
        )
        
        assert pagination["has_next"] is True
        assert pagination["next_cursor"] is not None
        assert pagination["returned"] == 10
        assert pagination["limit"] == 10
    
    def test_create_response_without_next(self):
        """Test creating response when no more items."""
        items = [
            {
                "_id": f"id{i}",
                "releasedAt": datetime.now(timezone.utc) - timedelta(hours=i),
                "title": f"Article {i}"
            }
            for i in range(5)  # 5 items, limit 10
        ]
        
        pagination = create_pagination_response(
            items=items,
            limit=10,
            sort_field="releasedAt",
            has_prev=False
        )
        
        assert pagination["has_next"] is False
        assert pagination["next_cursor"] is None
        assert pagination["returned"] == 5
    
    def test_create_response_with_prev(self):
        """Test creating response with previous cursor."""
        items = [
            {
                "_id": f"id{i}",
                "releasedAt": datetime.now(timezone.utc) - timedelta(hours=i),
                "title": f"Article {i}"
            }
            for i in range(10)
        ]
        
        pagination = create_pagination_response(
            items=items,
            limit=10,
            sort_field="releasedAt",
            has_prev=True
        )
        
        assert pagination["has_prev"] is True
        assert pagination["prev_cursor"] is not None
    
    def test_create_response_first_page(self):
        """Test creating response for first page (no prev)."""
        items = [
            {
                "_id": f"id{i}",
                "releasedAt": datetime.now(timezone.utc) - timedelta(hours=i),
                "title": f"Article {i}"
            }
            for i in range(11)
        ]
        
        pagination = create_pagination_response(
            items=items,
            limit=10,
            sort_field="releasedAt",
            has_prev=False
        )
        
        assert pagination["has_prev"] is False
        assert pagination["prev_cursor"] is None
        assert pagination["has_next"] is True
    
    def test_create_response_exact_limit(self):
        """Test response when items exactly match limit."""
        items = [
            {
                "_id": f"id{i}",
                "releasedAt": datetime.now(timezone.utc) - timedelta(hours=i),
                "title": f"Article {i}"
            }
            for i in range(10)
        ]
        
        pagination = create_pagination_response(
            items=items,
            limit=10,
            sort_field="releasedAt",
            has_prev=False
        )
        
        assert pagination["has_next"] is False
        assert pagination["returned"] == 10
    
    def test_create_response_empty_items(self):
        """Test response with empty items list."""
        pagination = create_pagination_response(
            items=[],
            limit=10,
            sort_field="releasedAt",
            has_prev=False
        )
        
        assert pagination["has_next"] is False
        assert pagination["next_cursor"] is None
        assert pagination["prev_cursor"] is None
        assert pagination["returned"] == 0
    
    def test_create_response_removes_extra_item(self):
        """Test that extra item is removed from response."""
        items = [
            {
                "_id": f"id{i}",
                "releasedAt": datetime.now(timezone.utc) - timedelta(hours=i),
                "title": f"Article {i}"
            }
            for i in range(11)  # 11 items but limit is 10
        ]
        
        # Items list should be modified
        pagination = create_pagination_response(
            items=items,
            limit=10,
            sort_field="releasedAt",
            has_prev=False
        )
        
        # Returned count should be limit, not limit+1
        assert pagination["returned"] == 10
        assert pagination["has_next"] is True


@pytest.mark.unit  
class TestPaginationIntegration:
    """Integration tests for full pagination workflow."""
    
    async def test_pagination_workflow(
        self,
        async_client,
        auth_headers,
        mock_database_manager,
        sample_news_list,
        create_mock_cursor_result
    ):
        """Test complete pagination workflow: page 1 -> page 2."""
        # Setup mock for first page
        mock_collection = mock_database_manager["collection"]
        first_page = sample_news_list[:11]  # Return 11 to indicate more items
        mock_cursor = create_mock_cursor_result(first_page)
        mock_collection.find.return_value = mock_cursor
        
        # Get first page
        response1 = await async_client.get(
            "/api/v1/news?limit=10",
            headers=auth_headers
        )
        
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["pagination"]["has_next"] is True
        assert data1["pagination"]["next_cursor"] is not None
        
        # Setup mock for second page
        next_cursor = data1["pagination"]["next_cursor"]
        second_page = sample_news_list[10:20]
        mock_cursor2 = create_mock_cursor_result(second_page)
        mock_collection.find.return_value = mock_cursor2
        
        # Get second page with cursor
        response2 = await async_client.get(
            f"/api/v1/news?limit=10&cursor={next_cursor}",
            headers=auth_headers
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["data"]) > 0
