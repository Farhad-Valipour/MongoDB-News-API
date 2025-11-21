# MongoDB News API - Development Guide

Guide for developers who want to contribute to or extend the MongoDB News API.

## Table of Contents

1. [Setup Development Environment](#setup-development-environment)
2. [Project Structure](#project-structure)
3. [Running the Application](#running-the-application)
4. [Testing](#testing)
5. [Code Style](#code-style)
6. [Adding New Features](#adding-new-features)
7. [Debugging](#debugging)
8. [Contributing](#contributing)

---

## Setup Development Environment

### Prerequisites

- Python 3.11+
- MongoDB 4.4+
- Git
- Virtual environment tool (venv or conda)

### Installation Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd mongodb-news-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt
```

4. **Setup MongoDB**

Option A - Local MongoDB:
```bash
# Install MongoDB (Ubuntu/Debian)
sudo apt-get install -y mongodb

# Start MongoDB
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

Option B - Docker:
```bash
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

5. **Configure environment variables**

Create `.env` file in project root:
```bash
# Application
APP_NAME=MongoDB News API
APP_VERSION=1.0.0
DEBUG=True
LOG_LEVEL=DEBUG

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=novoxpert
MONGODB_COLLECTION_NAME=news

# Security
API_KEYS=test-key-1,test-key-2,dev-key-12345

# Pagination
DEFAULT_PAGE_LIMIT=100
MAX_PAGE_LIMIT=1000
MIN_PAGE_LIMIT=10

# CORS
CORS_ORIGINS=*

# Rate Limiting
RATE_LIMIT_PER_HOUR=1000
```

6. **Verify installation**
```bash
python -c "import fastapi; import motor; print('✅ All dependencies installed')"
```

---

## Project Structure

```
mongodb-news-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # Dependency injection
│   │
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── database.py        # MongoDB connection
│   │   ├── pagination.py      # Cursor-based pagination
│   │   └── security.py        # API key authentication
│   │
│   ├── models/                 # Pydantic models
│   │   ├── __init__.py
│   │   ├── asset.py           # Asset model
│   │   ├── news.py            # News models
│   │   ├── request.py         # Request models
│   │   └── response.py        # Response models
│   │
│   ├── routers/                # API endpoints
│   │   ├── __init__.py
│   │   ├── aggregations.py    # Aggregation endpoints
│   │   ├── health.py          # Health check
│   │   └── news.py            # News endpoints
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── aggregation_service.py
│   │   └── news_service.py
│   │
│   ├── middleware/             # Custom middleware
│   │   ├── __init__.py
│   │   ├── cors.py            # CORS configuration
│   │   ├── error_handler.py   # Global error handler
│   │   ├── logging.py         # Request logging
│   │   └── rate_limit.py      # Rate limiting
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── exceptions.py      # Custom exceptions
│       └── logger.py          # Logging utilities
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_news.py           # News endpoint tests
│   ├── test_pagination.py     # Pagination tests
│   ├── test_aggregations.py   # Aggregation tests
│   ├── test_security.py       # Security tests
│   └── test_integration.py    # Integration tests
│
├── docs/                       # Documentation
│   ├── API_REFERENCE.md
│   ├── USAGE_EXAMPLES.md
│   └── DEVELOPMENT.md         # This file
│
├── scripts/                    # Utility scripts
│   └── __init__.py
│
├── .env                        # Environment variables (not in git)
├── .gitignore
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
└── README.md                   # Project README
```

### Architecture Layers

The application follows a layered architecture:

1. **Router Layer** (`app/routers/`): HTTP endpoint definitions
2. **Service Layer** (`app/services/`): Business logic
3. **Model Layer** (`app/models/`): Data models and validation
4. **Core Layer** (`app/core/`): Core functionality (DB, auth, pagination)
5. **Middleware Layer** (`app/middleware/`): Request/response processing

---

## Running the Application

### Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py script
python -m app.main
```

The API will be available at:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Production Server

```bash
# Using gunicorn with uvicorn workers
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_news.py

# Run specific test class
pytest tests/test_news.py::TestGetNewsList

# Run specific test
pytest tests/test_news.py::TestGetNewsList::test_get_news_without_filters

# Run with verbose output
pytest -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Test Coverage

View coverage report:
```bash
# Generate HTML coverage report
pytest --cov=app --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Writing Tests

Example test structure:

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.unit
class TestMyFeature:
    """Test suite for my feature."""
    
    async def test_basic_functionality(
        self,
        async_client,
        auth_headers,
        mock_database_manager
    ):
        """Test basic functionality."""
        # Setup
        mock_collection = mock_database_manager["collection"]
        mock_collection.find.return_value = AsyncMock()
        
        # Execute
        response = await async_client.get(
            "/api/v1/endpoint",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        assert "data" in response.json()
```

---

## Code Style

### Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (not 79)
- **Imports**: Use absolute imports
- **Docstrings**: Google style
- **Type hints**: Required for all functions

### Code Formatting

```bash
# Format code with black
black app/ tests/

# Sort imports with isort
isort app/ tests/

# Check style with flake8
flake8 app/ tests/

# Type checking with mypy
mypy app/
```

### Pre-commit Checks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
```

Install pre-commit:
```bash
pip install pre-commit
pre-commit install
```

### Docstring Example

```python
def my_function(param1: str, param2: int) -> dict:
    """
    Brief description of the function.
    
    Longer description if needed. Explain what the function does,
    any important details, and edge cases.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        dict: Description of return value
    
    Raises:
        ValueError: When param2 is negative
        
    Example:
        >>> result = my_function("test", 42)
        >>> print(result)
        {'status': 'success'}
    """
    if param2 < 0:
        raise ValueError("param2 must be positive")
    
    return {"status": "success", "param1": param1, "param2": param2}
```

---

## Adding New Features

### Adding a New Endpoint

1. **Define the model** (`app/models/`)

```python
# app/models/my_feature.py
from pydantic import BaseModel, Field

class MyFeatureRequest(BaseModel):
    """Request model for my feature."""
    name: str = Field(..., description="Feature name")
    enabled: bool = Field(True, description="Whether feature is enabled")

class MyFeatureResponse(BaseModel):
    """Response model for my feature."""
    id: str
    name: str
    enabled: bool
    created_at: datetime
```

2. **Create the service** (`app/services/`)

```python
# app/services/my_feature_service.py
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.my_feature import MyFeatureRequest, MyFeatureResponse

class MyFeatureService:
    """Business logic for my feature."""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["my_features"]
    
    async def create_feature(self, request: MyFeatureRequest) -> MyFeatureResponse:
        """Create new feature."""
        document = request.dict()
        document["created_at"] = datetime.utcnow()
        
        result = await self.collection.insert_one(document)
        document["id"] = str(result.inserted_id)
        
        return MyFeatureResponse(**document)
```

3. **Create the router** (`app/routers/`)

```python
# app/routers/my_feature.py
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.dependencies import get_db, get_current_api_key
from app.services.my_feature_service import MyFeatureService
from app.models.my_feature import MyFeatureRequest, MyFeatureResponse

router = APIRouter(prefix="/my-feature", tags=["My Feature"])

@router.post("", response_model=MyFeatureResponse)
async def create_feature(
    request: MyFeatureRequest,
    db: AsyncIOMotorDatabase = Depends(get_db),
    api_key: str = Depends(get_current_api_key),
):
    """Create new feature."""
    service = MyFeatureService(db)
    return await service.create_feature(request)
```

4. **Register the router** (`app/main.py`)

```python
from app.routers import my_feature

app.include_router(my_feature.router, prefix="/api/v1")
```

5. **Write tests** (`tests/`)

```python
# tests/test_my_feature.py
import pytest

@pytest.mark.unit
class TestMyFeature:
    async def test_create_feature(self, async_client, auth_headers):
        response = await async_client.post(
            "/api/v1/my-feature",
            json={"name": "Test Feature", "enabled": True},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Feature"
        assert data["enabled"] is True
```

---

## Debugging

### Using Python Debugger

```python
# In your code
import pdb; pdb.set_trace()  # Breakpoint

# Or use ipdb for better experience
import ipdb; ipdb.set_trace()
```

### VS Code Debug Configuration

Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": false,
      "envFile": "${workspaceFolder}/.env"
    },
    {
      "name": "Python: Pytest",
      "type": "python",
      "request": "launch",
      "module": "pytest",
      "args": ["-v"],
      "console": "integratedTerminal",
      "justMyCode": false
    }
  ]
}
```

### Logging

```python
from app.utils.logger import log_info, log_error, log_debug

# In your code
log_debug("Debugging information", extra_field="value")
log_info("Operation successful", item_id="123")
log_error("Operation failed", error=str(e))
```

View logs:
```bash
# In development (console)
tail -f logs/app.log

# With filtering
tail -f logs/app.log | grep ERROR
```

---

## Contributing

### Git Workflow

1. **Create feature branch**
```bash
git checkout -b feature/my-new-feature
```

2. **Make changes and commit**
```bash
git add .
git commit -m "feat: add new feature"
```

Commit message format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions/changes
- `refactor:` Code refactoring
- `perf:` Performance improvements
- `chore:` Maintenance tasks

3. **Push and create PR**
```bash
git push origin feature/my-new-feature
```

### Code Review Checklist

Before submitting PR:

- [ ] Code follows style guide
- [ ] All tests pass
- [ ] Coverage is maintained or improved
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance is acceptable
- [ ] Error handling is proper
- [ ] Logging is appropriate

### Running CI Checks Locally

```bash
# Run all checks
./scripts/run_checks.sh

# Or manually:
black --check app/ tests/
isort --check app/ tests/
flake8 app/ tests/
mypy app/
pytest --cov=app --cov-fail-under=80
```

---

## Useful Commands

### Database Management

```bash
# MongoDB shell
mongo

# Check collections
use novoxpert
show collections

# Query data
db.news.find().limit(5)

# Create index
db.news.createIndex({"releasedAt": -1})

# Database stats
db.stats()
```

### Performance Testing

```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py --host=http://localhost:8000
```

### Generate OpenAPI Schema

```bash
# Get OpenAPI schema
curl http://localhost:8000/openapi.json > openapi.json
```

---

## Troubleshooting

### Common Issues

**MongoDB connection fails**
```bash
# Check MongoDB is running
sudo systemctl status mongodb

# Check connection
mongo --eval "db.stats()"
```

**Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
echo $PYTHONPATH
```

**Tests fail**
```bash
# Clear pytest cache
pytest --cache-clear

# Run with verbose output
pytest -vv
```

**Port already in use**
```bash
# Find process using port 8000
lsof -ti:8000

# Kill process
kill -9 $(lsof -ti:8000)
```

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Motor Documentation](https://motor.readthedocs.io/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Pytest Documentation](https://docs.pytest.org/)
- [MongoDB Documentation](https://docs.mongodb.com/)

---

## Getting Help

- Check existing issues on GitHub
- Review documentation
- Ask in discussions
- Contact maintainers

---

**Happy coding! 🚀**
