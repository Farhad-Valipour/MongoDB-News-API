# MongoDB News API

<div align="center">

![MongoDB News API](https://img.shields.io/badge/MongoDB-News_API-success?style=for-the-badge&logo=mongodb)

**A high-performance REST API for accessing cryptocurrency news from multiple sources**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat-square&logo=python)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-darkgreen.svg?style=flat-square&logo=mongodb)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

[![Tests](https://img.shields.io/badge/tests-117%20passed-success?style=flat-square)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-80%25+-brightgreen?style=flat-square)](tests/)
[![Code Style](https://img.shields.io/badge/code%20style-black-black?style=flat-square)](https://github.com/psf/black)
[![Docker](https://img.shields.io/badge/docker-ready-blue?style=flat-square&logo=docker)](Dockerfile)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [API Reference](#-api-endpoints) • [Contributing](#-contributing)

</div>

---

## 🎯 Features

### Core Functionality
- 📰 **Multi-source News**: Access news from CoinMarketCap, Bloomberg, Reuters, CoinDesk, and more
- 🔍 **Advanced Filtering**: Filter by date range, source, asset slug, and keywords
- 📄 **Cursor-based Pagination**: Efficient pagination for datasets of any size
- 🔐 **API Key Authentication**: Secure access with Bearer token or query parameter
- 🚀 **High Performance**: Async operations with Motor (async MongoDB driver)

### Analytics & Aggregations
- 📊 **Statistics**: Get news count grouped by source or date
- 🏆 **Top Assets**: Most frequently mentioned cryptocurrencies
- 📈 **Timeline**: News distribution over time (daily/weekly/monthly)
- 📉 **Source Performance**: Detailed metrics for each news source

### Developer Experience
- 📖 **Auto Documentation**: Interactive Swagger UI and ReDoc
- 🧪 **Comprehensive Tests**: 117+ tests with 80%+ coverage
- 📚 **Complete Documentation**: API reference, usage examples, and development guide
- 🐳 **Docker Ready**: Production-ready containerization
- 🔄 **CI/CD**: Automated testing and deployment

### Production Features
- 🛡️ **Rate Limiting**: 1000 requests/hour per API key
- 📝 **Request Logging**: Structured logging with context
- ⚠️ **Error Handling**: Consistent error responses across all endpoints
- 🌐 **CORS Support**: Configurable cross-origin requests
- 🔒 **Security**: Input validation, SQL injection prevention

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/mongodb-news-api.git
cd mongodb-news-api

# Start with Docker Compose
docker-compose up -d

# API will be available at http://localhost:8000
```

### Option 2: Local Installation

#### Prerequisites

- Python 3.11+
- MongoDB 7.0+
- pip

#### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/mongodb-news-api.git
cd mongodb-news-api
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your MongoDB connection and API keys
```

5. **Run the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

### Verify Installation

```bash
# Check health
curl http://localhost:8000/api/v1/health

# Test with API key
curl -H "Authorization: Bearer your-api-key" http://localhost:8000/api/v1/news?limit=5
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [API Reference](docs/API_REFERENCE.md) | Complete API documentation with examples |
| [Usage Examples](docs/USAGE_EXAMPLES.md) | Practical usage scenarios and client libraries |
| [Development Guide](docs/DEVELOPMENT.md) | Setup and contribution guidelines |
| [Deployment Guide](docs/DEPLOYMENT.md) | Production deployment instructions |
| [Architecture](docs/ARCHITECTURE.md) | System architecture and design decisions |

### Interactive API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔑 Authentication

All endpoints require API key authentication. Provide your API key via:

**Option 1: Authorization Header**
```bash
curl -H "Authorization: Bearer your-api-key" http://localhost:8000/api/v1/news
```

**Option 2: Query Parameter**
```bash
curl http://localhost:8000/api/v1/news?api_key=your-api-key
```

---

## 📖 API Endpoints

### News Endpoints

#### Get News List
```http
GET /api/v1/news
```

**Query Parameters:**
- `from_date`: Filter from date (ISO 8601)
- `to_date`: Filter to date (ISO 8601)
- `source`: Filter by source (coinmarketcap, bloomberg, reuters, ...)
- `asset_slug`: Filter by asset (bitcoin, ethereum, ...)
- `keyword`: Search keyword (min 2 chars)
- `limit`: Items per page (10-1000, default: 100)
- `cursor`: Pagination cursor
- `sort_by`: Sort field (releasedAt, title, createdAt)
- `order`: Sort order (asc, desc)

**Example:**
```bash
curl "http://localhost:8000/api/v1/news?source=bloomberg&limit=20" \
  -H "Authorization: Bearer your-api-key"
```

#### Get Single News Article
```http
GET /api/v1/news/{slug}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/news/bitcoin-hits-new-high" \
  -H "Authorization: Bearer your-api-key"
```

### Aggregation Endpoints

#### Get Statistics
```http
GET /api/v1/aggregations/stats?group_by=source
```

#### Get Top Assets
```http
GET /api/v1/aggregations/top-assets?limit=10
```

#### Get Timeline
```http
GET /api/v1/aggregations/timeline?interval=daily
```

#### Get Source Performance
```http
GET /api/v1/aggregations/source-performance
```

### Health Check
```http
GET /api/v1/health
```

> 📖 For complete API documentation, see [API Reference](docs/API_REFERENCE.md)

---

## 🗄️ Database Schema

### Collection: `news`

```javascript
{
  "_id": ObjectId,
  "slug": "unique-article-slug",
  "title": "Article Title",
  "subtitle": "Article subtitle",
  "content": "<p>Full content...</p>",
  "source": "bloomberg",  // coinmarketcap, bloomberg, reuters, ...
  "sourceName": "Bloomberg",
  "sourceUrl": "https://...",
  "releasedAt": ISODate("2025-02-26T12:00:00Z"),
  "assets": [
    {
      "name": "Bitcoin",
      "slug": "bitcoin",
      "symbol": "BTC"
    }
  ],
  "createdAt": ISODate("..."),
  "updatedAt": ISODate("...")
}
```

---

## ⚙️ Configuration

Edit `.env` file:

```env
# MongoDB (with authentication)
MONGODB_URI=mongodb://localhost:27017
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_AUTH_SOURCE=admin
MONGODB_DB_NAME=novoxpert

# Security
API_KEYS=key1,key2,key3

# Server
DEBUG=false
LOG_LEVEL=INFO
```

📖 **For detailed MongoDB connection options, see [MONGODB_CONNECTION.md](MONGODB_CONNECTION.md)**

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Using Docker Only

```bash
# Build image
docker build -t mongodb-news-api .

# Run container
docker run -d \
  -p 8000:8000 \
  -e MONGODB_URI=mongodb://your-mongodb:27017 \
  -e API_KEYS=your-api-key \
  --name news-api \
  mongodb-news-api
```

> 📖 For detailed deployment instructions, see [Deployment Guide](docs/DEPLOYMENT.md)

---

## 🧪 Testing

### Run Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m security      # Security tests only
```

### Test Coverage

- **Total Tests**: 117+
- **Coverage**: 80%+
- **Test Files**: 6 (unit, integration, security, pagination, aggregations, news)

> 📖 For more details, see [tests/README.md](tests/README.md)

---

## 📝 Project Status

| Phase | Status | Files | Description |
|-------|--------|-------|-------------|
| **Phase 1: Core & Foundation** | ✅ Complete | 20 files | Core infrastructure, database, authentication, endpoints |
| **Phase 2: Production Ready** | ✅ Complete | 6 files | Logging, rate limiting, CORS, error handling, aggregations |
| **Phase 3: Testing & DX** | ✅ Complete | 13 files | Unit tests, integration tests, documentation |
| **Phase 4: GitHub Ready** | ✅ Complete | 23 files | CI/CD, Docker, deployment guides, community files |

### Key Metrics

- **Total Lines of Code**: ~10,000+
- **Test Coverage**: 80%+
- **API Endpoints**: 10+
- **Documentation Pages**: 8+

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   Client                        │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│              FastAPI Application                │
│  ┌──────────────────────────────────────────┐  │
│  │         Middleware Layer                 │  │
│  │  • CORS  • Rate Limiting  • Logging      │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │           Router Layer                   │  │
│  │  • News  • Aggregations  • Health        │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │          Service Layer                   │  │
│  │  • Business Logic  • Data Processing     │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │           Core Layer                     │  │
│  │  • Database  • Auth  • Pagination        │  │
│  └──────────────────────────────────────────┘  │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│              MongoDB Database                   │
│         (news collection with indexes)          │
└─────────────────────────────────────────────────┘
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please read [CONTRIBUTING.md](.github/CONTRIBUTING.md) for detailed guidelines.

### Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](.github/CODE_OF_CONDUCT.md).

---

## 🛡️ Security

Found a security vulnerability? Please read our [Security Policy](.github/SECURITY.md) for responsible disclosure.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with amazing open-source tools:

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Motor](https://motor.readthedocs.io/) - Async MongoDB driver
- [MongoDB](https://www.mongodb.com/) - Database
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Uvicorn](https://www.uvicorn.org/) - ASGI server

---

## 📊 Statistics

![GitHub stars](https://img.shields.io/github/stars/yourusername/mongodb-news-api?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/mongodb-news-api?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/mongodb-news-api)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/mongodb-news-api)

---

## 📞 Support

- 📫 **Email**: support@example.com
- 💬 **Issues**: [GitHub Issues](https://github.com/yourusername/mongodb-news-api/issues)
- 📖 **Documentation**: [Full Documentation](docs/)
- 💡 **Discussions**: [GitHub Discussions](https://github.com/yourusername/mongodb-news-api/discussions)

---

## 🗺️ Roadmap

- [ ] WebSocket support for real-time updates
- [ ] GraphQL API
- [ ] Admin dashboard
- [ ] Machine learning-based recommendations
- [ ] Multi-language support
- [ ] Advanced caching with Redis

---

<div align="center">

**Made with ❤️ by the MongoDB News API Team**

[⬆ Back to Top](#mongodb-news-api)

</div>
