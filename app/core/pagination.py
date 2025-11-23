"""
Cursor-based pagination logic.
Handles encoding/decoding of cursors and building MongoDB queries for pagination.
"""

import base64
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.utils.exceptions import InvalidCursorException


class PaginationCursor:
    """Handles cursor encoding and decoding for pagination."""
    
    @staticmethod
    def encode(cursor_data: Dict[str, Any]) -> str:
        """
        Encode cursor data to base64 string.
        
        Args:
            cursor_data: Dictionary containing cursor information (e.g., _id, releasedAt)
        
        Returns:
            str: Base64 encoded cursor string
        """
        try:
            # Convert datetime to ISO format string for JSON serialization
            serializable_data = {}
            for key, value in cursor_data.items():
                if isinstance(value, datetime):
                    # Convert to ISO format, handle timezone-aware and naive datetimes
                    iso_string = value.isoformat()
                    # Ensure consistent format by replacing +00:00 with Z
                    if iso_string.endswith('+00:00'):
                        iso_string = iso_string.replace('+00:00', 'Z')
                    serializable_data[key] = iso_string
                else:
                    serializable_data[key] = str(value)
            
            json_str = json.dumps(serializable_data, sort_keys=True)
            encoded = base64.b64encode(json_str.encode()).decode()
            return encoded
        except Exception as e:
            raise InvalidCursorException(f"Failed to encode cursor: {str(e)}")
    
    @staticmethod
    def decode(cursor: str) -> Dict[str, Any]:
        """
        Decode base64 cursor string to dictionary.
        
        Args:
            cursor: Base64 encoded cursor string
        
        Returns:
            dict: Decoded cursor data
        
        Raises:
            InvalidCursorException: If cursor format is invalid
        """
        try:
            decoded = base64.b64decode(cursor.encode()).decode()
            cursor_data = json.loads(decoded)
            return cursor_data
        except Exception as e:
            raise InvalidCursorException(f"Invalid cursor format: {str(e)}")
    
    @staticmethod
    def build_cursor_query(
        cursor_data: Dict[str, Any],
        sort_field: str,
        sort_order: str
    ) -> Dict[str, Any]:
        """
        Build MongoDB query for cursor-based pagination.
        
        Args:
            cursor_data: Decoded cursor data containing _id and sort field value
            sort_field: Field to sort by (e.g., 'releasedAt')
            sort_order: Sort order ('asc' or 'desc')
        
        Returns:
            dict: MongoDB query for pagination
        """
        if not cursor_data:
            return {}
        
        cursor_id = cursor_data.get("_id")
        cursor_value = cursor_data.get(sort_field)
        
        if not cursor_id or cursor_value is None:
            return {}
        
        # Convert ISO string back to datetime if needed
        if sort_field in ["releasedAt", "createdAt", "updatedAt"]:
            try:
                # Handle both Z and +00:00 formats
                if isinstance(cursor_value, str):
                    if cursor_value.endswith('Z'):
                        cursor_value = datetime.fromisoformat(cursor_value.replace('Z', '+00:00'))
                    else:
                        cursor_value = datetime.fromisoformat(cursor_value)
            except ValueError:
                # If parsing fails, keep as string
                pass
        
        # Build query based on sort order
        if sort_order == "desc":
            # For descending order: find documents with value less than cursor
            query = {
                "$or": [
                    {sort_field: {"$lt": cursor_value}},
                    {
                        sort_field: cursor_value,
                        "_id": {"$lt": cursor_id}
                    }
                ]
            }
        else:
            # For ascending order: find documents with value greater than cursor
            query = {
                "$or": [
                    {sort_field: {"$gt": cursor_value}},
                    {
                        sort_field: cursor_value,
                        "_id": {"$gt": cursor_id}
                    }
                ]
            }
        
        return query


def create_pagination_response(
    items: List[Dict[str, Any]],
    limit: int,
    sort_field: str,
    has_prev: bool = False
) -> Dict[str, Any]:
    """
    Create pagination response with cursors.
    
    Args:
        items: List of items returned from database (may include +1 extra item)
        limit: Requested limit
        sort_field: Field used for sorting
        has_prev: Whether there are previous items
    
    Returns:
        dict: Pagination metadata with cursors
    """
    has_next = len(items) > limit
    
    # Remove extra item if exists
    if has_next:
        items = items[:limit]
    
    # Create cursors
    next_cursor = None
    prev_cursor = None
    
    if has_next and items:
        last_item = items[-1]
        next_cursor = PaginationCursor.encode({
            "_id": str(last_item["_id"]),
            sort_field: last_item.get(sort_field)
        })
    
    if has_prev and items:
        first_item = items[0]
        prev_cursor = PaginationCursor.encode({
            "_id": str(first_item["_id"]),
            sort_field: first_item.get(sort_field)
        })
    
    return {
        "next_cursor": next_cursor,
        "prev_cursor": prev_cursor,
        "has_next": has_next,
        "has_prev": has_prev,
        "limit": limit,
        "returned": len(items)
    }


# FIXED: Export encode_cursor function for backward compatibility with tests
def encode_cursor(cursor_data: Dict[str, Any]) -> str:
    """
    Legacy function for encoding cursors.
    Wrapper around PaginationCursor.encode() for backward compatibility.
    
    Args:
        cursor_data: Dictionary containing cursor information
    
    Returns:
        str: Base64 encoded cursor string
    """
    return PaginationCursor.encode(cursor_data)


# FIXED: Export decode_cursor function for backward compatibility with tests
def decode_cursor(cursor: str) -> Dict[str, Any]:
    """
    Legacy function for decoding cursors.
    Wrapper around PaginationCursor.decode() for backward compatibility.
    
    Args:
        cursor: Base64 encoded cursor string
    
    Returns:
        dict: Decoded cursor data
    """
    return PaginationCursor.decode(cursor)
