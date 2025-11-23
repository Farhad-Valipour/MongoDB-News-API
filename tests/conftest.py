"""
Pytest configuration and shared fixtures.
Provides mock database, test client, and sample data for all tests.
"""

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator, Dict, List
from unittest.mock import MagicMock, AsyncMock
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import db_manager
from app.config import settings


# ==================== Event Loop Configuration ====================

@pytest.fixture(scope="session")
def event_loop():
    """
    Create event loop for async tests.
    Session-scoped to reuse across all tests.
    """
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
    """
    Mock settings for all tests.
    Automatically applied to every test.
    """
    monkeypatch.setattr(settings, "API_KEYS", test_api_key)
    monkeypatch.setattr(settings, "RATE_LIMIT_PER_HOUR", 1000)
    monkeypatch.setattr(settings, "MONGODB_DB_NAME", "test_db")
    monkeypatch.setattr(settings, "MONGODB_COLLECTION_NAME", "test_news")
    return settings


# ==================== Database Fixtures ====================

@pytest.fixture
async def mock_db():
    """
    Mock MongoDB database for unit tests.
    Does not require actual MongoDB connection.
    """
    mock_db = AsyncMock()
    mock_collection = AsyncMock()
    
    # Setup mock collection
    mock_db.__getitem__.return_value = mock_collection
    
    return {
        "db": mock_db,
        "collection": mock_collection
    }


@pytest.fixture
async def mock_database_manager(mock_db):
    """
    Mock the global database manager.
    Replaces real database with mock.
    """
    original_db = db_manager.db
    original_client = db_manager.client
    
    # Replace with mock
    db_manager.db = mock_db["db"]
    db_manager.client = AsyncMock()
    
    yield mock_db
    
    # Restore original
    db_manager.db = original_db
    db_manager.client = original_client


# ==================== HTTP Client Fixtures ====================

@pytest.fixture
def test_client():
    """
    Synchronous test client for FastAPI.
    Use for simple sync tests.
    """
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Async HTTP client for FastAPI.
    Use for async tests and better performance.
    """
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
    """
    Multiple sample news items with different sources and dates.
    Useful for pagination and filtering tests.
    """
    base_time = datetime.now(timezone.utc)
    
    news_items = []
    sources = ["coinmarketcap", "bloomberg", "reuters", "coindesk"]
    
    for i in range(20):
        released_at = base_time - timedelta(hours=i)
        news_items.append({
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
    """Sample Bloomberg news for source filtering tests."""
    base_time = datetime.now(timezone.utc)
    return [
        {
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
    """Sample news about Bitcoin for asset filtering tests."""
    base_time = datetime.now(timezone.utc)
    return [
        {
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
    """Valid base64-encoded cursor for pagination tests."""
    from app.core.pagination import encode_cursor
    timestamp = datetime.now(timezone.utc)
    return encode_cursor(timestamp)


@pytest.fixture
def invalid_cursor() -> str:
    """Invalid cursor for negative tests."""
    return "invalid-cursor-format"


# ==================== Helper Functions ====================

@pytest.fixture
def create_mock_cursor_result():
    """
    Factory function to create mock cursor result from MongoDB.
    Returns a function that accepts a list and returns AsyncMock with to_list method.
    """
    def _create_mock(data: List[Dict]) -> AsyncMock:
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=data)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
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
    """Sample aggregation statistics results."""
    return [
        {"_id": "coinmarketcap", "count": 150},
        {"_id": "bloomberg", "count": 120},
        {"_id": "reuters", "count": 100},
        {"_id": "coindesk", "count": 80}
    ]


@pytest.fixture
def sample_top_assets() -> List[Dict]:
    """Sample top assets aggregation results."""
    return [
        {
            "_id": "bitcoin",
            "name": "Bitcoin",
            "symbol": "BTC",
            "count": 250,
            "percentage": 35.7
        },
        {
            "_id": "ethereum",
            "name": "Ethereum",
            "symbol": "ETH",
            "count": 180,
            "percentage": 25.7
        },
        {
            "_id": "cardano",
            "name": "Cardano",
            "symbol": "ADA",
            "count": 120,
            "percentage": 17.1
        }
    ]


@pytest.fixture
def sample_timeline_data() -> List[Dict]:
    """Sample timeline aggregation results."""
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
