"""
Cursor service for encoding/decoding pagination cursors.
Wraps PaginationCursor class for service layer use.
"""

from typing import Dict, Any, Optional

from app.core.pagination import PaginationCursor as CorePaginationCursor
from app.utils.exceptions import InvalidCursorException


class CursorService:
    """Service for managing pagination cursors."""
    
    @staticmethod
    def encode_cursor(cursor_data: Dict[str, Any]) -> str:
        """
        Encode cursor data to base64 string.
        
        Args:
            cursor_data: Dictionary with _id and sort field value
        
        Returns:
            str: Encoded cursor
        """
        return CorePaginationCursor.encode(cursor_data)
    
    @staticmethod
    def decode_cursor(cursor: Optional[str]) -> Dict[str, Any]:
        """
        Decode cursor string to dictionary.
        
        Args:
            cursor: Base64 encoded cursor string
        
        Returns:
            dict: Decoded cursor data (empty dict if cursor is None)
        
        Raises:
            InvalidCursorException: If cursor is invalid
        """
        if not cursor:
            return {}
        
        return CorePaginationCursor.decode(cursor)
    
    @staticmethod
    def build_cursor_query(
        cursor: Optional[str],
        sort_field: str,
        sort_order: str
    ) -> Dict[str, Any]:
        """
        Build MongoDB query for cursor-based pagination.
        
        Args:
            cursor: Base64 encoded cursor string
            sort_field: Field to sort by
            sort_order: 'asc' or 'desc'
        
        Returns:
            dict: MongoDB query filter
        """
        if not cursor:
            return {}
        
        cursor_data = CorePaginationCursor.decode(cursor)
        return CorePaginationCursor.build_cursor_query(
            cursor_data, sort_field, sort_order
        )


# Global cursor service instance
cursor_service = CursorService()
