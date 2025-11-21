# MongoDB News API

> A high-performance REST API for accessing news articles from MongoDB with advanced filtering and cursor-based pagination.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0+-darkgreen.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Features

- 📰 **Multi-source News**: Access news from CoinMarketCap, Bloomberg, Reuters, and more
- 🔍 **Advanced Filtering**: Filter by date range, source, asset, and keywords
- 📄 **Cursor Pagination**: Efficient pagination for large datasets
- 🔐 **API Key Auth**: Secure access with API key authentication
- 🚀 **High Performance**: Async operations with Motor driver
- 📊 **RESTful API**: Standard HTTP methods and status codes
- 📖 **Auto Documentation**: Interactive API docs with Swagger UI

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MongoDB 7.0+
- pip

### Installation

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
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your MongoDB connection and API keys
# See MONGODB_CONNECTION.md for detailed MongoDB setup
```

5. **Run the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

---

## 📚 API Documentation

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
- `keyword`: Search keyword
- `limit`: Items per page (10-1000, default: 100)
- `cursor`: Pagination cursor
- `sort_by`: Sort field (releasedAt, title, createdAt)
- `order`: Sort order (asc, desc)

**Example:**
```bash
curl "http://localhost:8000/api/v1/news?source=bloomberg&limit=50" \
  -H "Authorization: Bearer your-api-key"
```

#### Get Single News
```http
GET /api/v1/news/{slug}
```

**Example:**
```bash
curl "http://localhost:8000/api/v1/news/bitcoin-hits-new-high" \
  -H "Authorization: Bearer your-api-key"
```

### Health Check
```http
GET /api/v1/health
```

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

## 🐳 Docker Support

Coming in Phase 1 completion...

---

## 🧪 Testing

Coming in Phase 3...

---

## 📝 Development Status

**Phase 1: Core & Foundation** - ✅ Complete (20 files)
- [x] Core infrastructure
- [x] Database connection
- [x] API Key authentication
- [x] News endpoints
- [x] Health check
- [x] Error handling

**Phase 2: Production Ready** - 🔄 Planned (6 files)
- [ ] Enhanced middleware
- [ ] Rate limiting
- [ ] Aggregation endpoints

**Phase 3: Testing & DX** - 📋 Planned (10 files)
- [ ] Unit tests
- [ ] Integration tests
- [ ] Documentation

**Phase 4: GitHub Ready** - 📋 Planned (10 files)
- [ ] CI/CD pipeline
- [ ] Community guidelines

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [Motor](https://motor.readthedocs.io/)
- [MongoDB](https://www.mongodb.com/)
- [Pydantic](https://docs.pydantic.dev/)

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Version**: 1.0.0  
**Status**: Phase 1 Complete ✅
