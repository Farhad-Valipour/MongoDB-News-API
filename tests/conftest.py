"""
Pytest configuration with PROPERLY FIXED mock cursor.
"""
import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator, Dict, List
from unittest.mock import MagicMock
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import db_manager
from app.config import settings


# ==================== Event Loop Configuration ====================

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== Configuration Fixtures ====================

@pytest.fixture
def test_api_key() -> str:
    """Valid test API key."""
    return "test-api-key-12345"


@pytest.fixture
def invalid_api_key() -> str:
    """Invalid API key for negative tests."""
    return "invalid-key-xyz"


@pytest.fixture(autouse=True)
def mock_settings(monkeypatch, test_api_key):
    """Mock settings for all tests."""
    monkeypatch.setattr(settings, "API_KEYS", test_api_key)
    monkeypatch.setattr(settings, "RATE_LIMIT_PER_HOUR", 1000)
    monkeypatch.setattr(settings, "MONGODB_DB_NAME", "test_db")
    monkeypatch.setattr(settings, "MONGODB_COLLECTION_NAME", "test_news")
    return settings


# ==================== Database Fixtures ====================

@pytest.fixture
async def mock_db():
    """Mock MongoDB database for unit tests."""
    # Create a proper mock that mimics Motor's AsyncIOMotorCollection
    mock_collection = MagicMock()
    
    # Mock find_one - returns awaitable
    async def mock_find_one(filter_dict, projection=None):
        return None  # Will be overridden in tests
    
    mock_collection.find_one = mock_find_one
    
    # Mock find - returns a cursor-like object
    def mock_find(filter_dict, projection=None):
        # Create a mock cursor
        mock_cursor = MagicMock()
        
        # to_list is async
        async def mock_to_list(length=None):
            return []  # Will be overridden in tests
        
        mock_cursor.to_list = mock_to_list
        
        # Chain methods return self
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        
        return mock_cursor
    
    mock_collection.find = mock_find
    
    # Create mock database
    mock_db_instance = MagicMock()
    mock_db_instance.__getitem__ = MagicMock(return_value=mock_collection)
    
    return {
        "db": mock_db_instance,
        "collection": mock_collection
    }


@pytest.fixture
async def mock_database_manager(mock_db):
    """Mock the global database manager."""
    original_db = db_manager.db
    original_client = db_manager.client
    
    db_manager.db = mock_db["db"]
    db_manager.client = MagicMock()  # Not AsyncMock!
    
    yield mock_db
    
    db_manager.db = original_db
    db_manager.client = original_client


# ==================== HTTP Client Fixtures ====================

@pytest.fixture
def test_client():
    """Synchronous test client for FastAPI."""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client for FastAPI."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ==================== Sample Data Fixtures ====================

@pytest.fixture
def sample_asset() -> Dict:
    """Single sample asset/cryptocurrency."""
    return {
        "name": "Bitcoin",
        "slug": "bitcoin",
        "symbol": "BTC"
    }


@pytest.fixture
def sample_assets() -> List[Dict]:
    """Multiple sample assets."""
    return [
        {"name": "Bitcoin", "slug": "bitcoin", "symbol": "BTC"},
        {"name": "Ethereum", "slug": "ethereum", "symbol": "ETH"},
        {"name": "Cardano", "slug": "cardano", "symbol": "ADA"}
    ]


@pytest.fixture
def sample_news_item(sample_asset) -> Dict:
    """Single sample news item."""
    now = datetime.now(timezone.utc)
    return {
        "_id": "507f1f77bcf86cd799439011",
        "slug": "bitcoin-hits-50k",
        "title": "Bitcoin Hits $50,000 Milestone",
        "subtitle": "BTC reaches new all-time high amid institutional adoption",
        "content": "<p>Bitcoin has reached $50,000 for the first time...</p>",
        "source": "coinmarketcap",
        "sourceName": "CoinMarketCap News",
        "sourceUrl": "https://coinmarketcap.com/news/bitcoin-50k",
        "releasedAt": now,
        "assets": [sample_asset],
        "createdAt": now,
        "updatedAt": now
    }


@pytest.fixture
def sample_news_list(sample_assets) -> List[Dict]:
    """Multiple sample news items."""
    base_time = datetime.now(timezone.utc)
    
    news_items = []
    sources = ["coinmarketcap", "bloomberg", "reuters", "coindesk"]
    
    for i in range(20):
        released_at = base_time - timedelta(hours=i)
        news_items.append({
            "_id": f"507f1f77bcf86cd79943{i:04d}",
            "slug": f"news-article-{i}",
            "title": f"News Article {i}",
            "subtitle": f"Subtitle for article {i}",
            "content": f"<p>Content for article {i}</p>",
            "source": sources[i % len(sources)],
            "sourceName": sources[i % len(sources)].title(),
            "sourceUrl": f"https://{sources[i % len(sources)]}.com/article-{i}",
            "releasedAt": released_at,
            "assets": [sample_assets[i % len(sample_assets)]],
            "createdAt": released_at,
            "updatedAt": released_at
        })
    
    return news_items


@pytest.fixture
def sample_bloomberg_news() -> List[Dict]:
    """Sample Bloomberg news."""
    base_time = datetime.now(timezone.utc)
    return [
        {
            "_id": f"507f1f77bcf86cd79944{i:04d}",
            "slug": f"bloomberg-{i}",
            "title": f"Bloomberg Article {i}",
            "subtitle": "Bloomberg subtitle",
            "content": "<p>Bloomberg content</p>",
            "source": "bloomberg",
            "sourceName": "Bloomberg",
            "sourceUrl": f"https://bloomberg.com/article-{i}",
            "releasedAt": base_time - timedelta(hours=i),
            "assets": [{"name": "Bitcoin", "slug": "bitcoin", "symbol": "BTC"}],
            "createdAt": base_time - timedelta(hours=i),
            "updatedAt": base_time - timedelta(hours=i)
        }
        for i in range(5)
    ]


@pytest.fixture
def sample_bitcoin_news(sample_asset) -> List[Dict]:
    """Sample news about Bitcoin."""
    base_time = datetime.now(timezone.utc)
    return [
        {
            "_id": f"507f1f77bcf86cd79945{i:04d}",
            "slug": f"bitcoin-news-{i}",
            "title": f"Bitcoin News {i}",
            "subtitle": "Bitcoin analysis",
            "content": "<p>Bitcoin content</p>",
            "source": "coinmarketcap",
            "sourceName": "CoinMarketCap",
            "sourceUrl": f"https://coinmarketcap.com/bitcoin-{i}",
            "releasedAt": base_time - timedelta(days=i),
            "assets": [sample_asset],
            "createdAt": base_time - timedelta(days=i),
            "updatedAt": base_time - timedelta(days=i)
        }
        for i in range(10)
    ]


# ==================== Pagination Fixtures ====================

@pytest.fixture
def sample_cursor() -> str:
    """Valid base64-encoded cursor."""
    from app.core.pagination import encode_cursor
    timestamp = datetime.now(timezone.utc)
    cursor_data = {
        "_id": "507f1f77bcf86cd799439011",
        "releasedAt": timestamp
    }
    return encode_cursor(cursor_data)


@pytest.fixture
def invalid_cursor() -> str:
    """Invalid cursor."""
    return "invalid-cursor-format"


# ==================== Helper Functions ====================

@pytest.fixture
def create_mock_cursor_result():
    """
    CORRECTED VERSION - Returns a function that creates a proper mock cursor.
    
    CRITICAL: Motor cursor methods return self (NOT async), only to_list() is async!
    """
    def _create_mock(data: List[Dict]):
        """Create a properly mocked Motor cursor."""
        # Create mock cursor - NOT AsyncMock!
        mock_cursor = MagicMock()
        
        # to_list is async and returns data
        async def mock_to_list(length=None):
            return data
        
        mock_cursor.to_list = mock_to_list
        
        # Chain methods return self (synchronous!)
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        
        return mock_cursor
    
    return _create_mock


@pytest.fixture
def auth_headers(test_api_key) -> Dict[str, str]:
    """Authentication headers with valid API key."""
    return {
        "Authorization": f"Bearer {test_api_key}"
    }


@pytest.fixture
def invalid_auth_headers(invalid_api_key) -> Dict[str, str]:
    """Authentication headers with invalid API key."""
    return {
        "Authorization": f"Bearer {invalid_api_key}"
    }


# ==================== Aggregation Test Data ====================

@pytest.fixture
def sample_aggregation_stats() -> List[Dict]:
    """Sample aggregation statistics."""
    return [
        {"_id": "coinmarketcap", "count": 150},
        {"_id": "bloomberg", "count": 120},
        {"_id": "reuters", "count": 100},
        {"_id": "coindesk", "count": 80}
    ]


@pytest.fixture
def sample_top_assets() -> List[Dict]:
    """Sample top assets aggregation."""
    return [
        {"_id": "bitcoin", "name": "Bitcoin", "symbol": "BTC", "count": 250, "percentage": 35.7},
        {"_id": "ethereum", "name": "Ethereum", "symbol": "ETH", "count": 180, "percentage": 25.7},
        {"_id": "cardano", "name": "Cardano", "symbol": "ADA", "count": 120, "percentage": 17.1}
    ]


@pytest.fixture
def sample_timeline_data() -> List[Dict]:
    """Sample timeline aggregation."""
    base_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return [
        {
            "_id": (base_date - timedelta(days=i)).strftime("%Y-%m-%d"),
            "count": 50 - i * 5
        }
        for i in range(7)
    ]


# ==================== Test Markers ====================

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "security: Security related tests")
