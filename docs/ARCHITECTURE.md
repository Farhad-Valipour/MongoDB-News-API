# Architecture Documentation

Complete system architecture and design decisions for MongoDB News API.

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Technology Stack](#technology-stack)
4. [Layer Architecture](#layer-architecture)
5. [Data Flow](#data-flow)
6. [Database Design](#database-design)
7. [API Design](#api-design)
8. [Security Architecture](#security-architecture)
9. [Performance Considerations](#performance-considerations)
10. [Design Decisions](#design-decisions)

---

## System Overview

MongoDB News API is a high-performance REST API built to aggregate and serve cryptocurrency news from multiple sources. The system is designed with scalability, performance, and maintainability in mind.

### Key Characteristics

- **Async-first**: All I/O operations are asynchronous
- **Stateless**: Each request is independent
- **Horizontally Scalable**: Can run multiple instances
- **Database-agnostic**: Loosely coupled with MongoDB
- **API-first**: RESTful design with OpenAPI documentation

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
│  (Web Apps, Mobile Apps, Third-party Services, CLI Tools)      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTPS/HTTP
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    Load Balancer / Reverse Proxy                │
│                    (Nginx, AWS ALB, CloudFlare)                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │
        ┌────────────────┴────────────────┐
        │                                  │
        ▼                                  ▼
┌───────────────┐                  ┌───────────────┐
│  API Instance │                  │  API Instance │
│   (Container) │  ◄──────────►   │   (Container) │
└───────┬───────┘                  └───────┬───────┘
        │                                  │
        │         FastAPI Application     │
        │                                  │
        │   ┌──────────────────────────┐  │
        │   │   Middleware Layer       │  │
        │   │  ┌──────────────────┐   │  │
        │   │  │ CORS             │   │  │
        │   │  │ Rate Limiting    │   │  │
        │   │  │ Logging          │   │  │
        │   │  │ Error Handling   │   │  │
        │   │  └──────────────────┘   │  │
        │   └──────────────────────────┘  │
        │                                  │
        │   ┌──────────────────────────┐  │
        │   │   Router Layer           │  │
        │   │  ┌──────────────────┐   │  │
        │   │  │ /news            │   │  │
        │   │  │ /aggregations    │   │  │
        │   │  │ /health          │   │  │
        │   │  └──────────────────┘   │  │
        │   └──────────────────────────┘  │
        │                                  │
        │   ┌──────────────────────────┐  │
        │   │   Service Layer          │  │
        │   │  ┌──────────────────┐   │  │
        │   │  │ NewsService      │   │  │
        │   │  │ AggregationSvc   │   │  │
        │   │  └──────────────────┘   │  │
        │   └──────────────────────────┘  │
        │                                  │
        │   ┌──────────────────────────┐  │
        │   │   Core Layer             │  │
        │   │  ┌──────────────────┐   │  │
        │   │  │ Database Manager │   │  │
        │   │  │ Authentication   │   │  │
        │   │  │ Pagination       │   │  │
        │   │  └──────────────────┘   │  │
        │   └──────────────────────────┘  │
        │                                  │
        └────────────┬─────────────────────┘
                     │
                     │ Motor (Async Driver)
                     │
        ┌────────────▼─────────────────────┐
        │      MongoDB Database            │
        │                                  │
        │  ┌────────────────────────────┐ │
        │  │   news Collection          │ │
        │  │  • Indexes                 │ │
        │  │  • Sharding (optional)     │ │
        │  └────────────────────────────┘ │
        └───────────────────────────────────┘
```

---

## Technology Stack

### Backend Framework
- **FastAPI 0.109+**: Modern, fast web framework
  - Async/await support
  - Automatic API documentation
  - Pydantic integration
  - Type hints

### Database
- **MongoDB 7.0+**: NoSQL document database
  - Flexible schema
  - Horizontal scaling
  - Rich query capabilities
  - Aggregation pipeline

### Database Driver
- **Motor 3.3+**: Async MongoDB driver
  - Non-blocking I/O
  - Connection pooling
  - High throughput

### Server
- **Uvicorn 0.27+**: ASGI server
  - High performance
  - WebSocket support
  - Multiple workers

### Data Validation
- **Pydantic 2.5+**: Data validation
  - Type validation
  - Serialization
  - Configuration management

### Development Tools
- **Pytest**: Testing framework
- **Black**: Code formatter
- **MyPy**: Type checker
- **Flake8**: Linter

### Deployment
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **GitHub Actions**: CI/CD pipeline

---

## Layer Architecture

### 1. Presentation Layer (Routers)

**Purpose**: Handle HTTP requests and responses

**Responsibilities**:
- Route management
- Request validation
- Response formatting
- HTTP status codes
- OpenAPI documentation

**Location**: `app/routers/`

**Example**:
```python
@router.get("/news", response_model=NewsListResponse)
async def get_news_list(
    source: str = None,
    limit: int = 100,
    db: Database = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    service = NewsService(db)
    return await service.get_news_list(source, limit)
```

### 2. Business Logic Layer (Services)

**Purpose**: Implement business rules and logic

**Responsibilities**:
- Data processing
- Business rules
- External service integration
- Aggregation logic
- Data transformation

**Location**: `app/services/`

**Example**:
```python
class NewsService:
    def __init__(self, db: Database):
        self.db = db
        self.collection = db["news"]
    
    async def get_news_list(self, filters, pagination):
        query = self._build_query(filters)
        cursor = self.collection.find(query)
        return await cursor.to_list(length=pagination.limit)
```

### 3. Data Access Layer (Core)

**Purpose**: Interact with database

**Responsibilities**:
- Database connection management
- Query execution
- Connection pooling
- Transaction handling (if needed)

**Location**: `app/core/database.py`

**Example**:
```python
class DatabaseManager:
    async def connect(self):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        await self.client.admin.command('ping')
```

### 4. Cross-Cutting Concerns (Middleware)

**Purpose**: Handle system-wide concerns

**Responsibilities**:
- Authentication
- Rate limiting
- Logging
- Error handling
- CORS

**Location**: `app/middleware/`

---

## Data Flow

### Request Flow

```
1. Client Request
   │
   ▼
2. Load Balancer
   │
   ▼
3. Middleware Stack
   ├─► CORS Check
   ├─► Authentication
   ├─► Rate Limiting
   └─► Request Logging
   │
   ▼
4. Router
   │
   ▼
5. Service Layer
   ├─► Validate Input
   ├─► Build Query
   └─► Process Business Logic
   │
   ▼
6. Database Layer
   ├─► Execute Query
   └─► Fetch Data
   │
   ▼
7. Response Processing
   ├─► Transform Data
   ├─► Apply Pagination
   └─► Format Response
   │
   ▼
8. Middleware Stack (Response)
   ├─► Response Logging
   ├─► Add Headers
   └─► Error Handling
   │
   ▼
9. Client Response
```

### Pagination Flow

```
User Request (Page 1)
   │
   ▼
[No Cursor] ──► Query: {}, Sort: releasedAt, Limit: 101
   │
   ▼
Database Returns: 101 items
   │
   ▼
Return: 100 items + next_cursor (encoded from item 100)
   │
   ▼
User Request (Page 2 with cursor)
   │
   ▼
[Decode Cursor] ──► Query: {releasedAt: {$lt: cursor_date}}, Limit: 101
   │
   ▼
Database Returns: Next 101 items
   │
   ▼
Return: 100 items + next_cursor
```

---

## Database Design

### Collections

#### news Collection

```javascript
{
  _id: ObjectId("..."),
  slug: "bitcoin-hits-50k",          // Unique identifier
  title: "Bitcoin Hits $50,000",     // Article title
  subtitle: "BTC surges...",         // Short summary
  content: "<p>Full content...</p>", // HTML content
  source: "bloomberg",               // Source identifier
  sourceName: "Bloomberg",           // Display name
  sourceUrl: "https://...",          // Original URL
  releasedAt: ISODate("..."),       // Publication date
  assets: [                          // Related cryptocurrencies
    {
      name: "Bitcoin",
      slug: "bitcoin",
      symbol: "BTC"
    }
  ],
  createdAt: ISODate("..."),        // Database timestamp
  updatedAt: ISODate("...")         // Last update
}
```

### Indexes

```javascript
// Performance indexes
db.news.createIndex({ slug: 1 }, { unique: true })
db.news.createIndex({ releasedAt: -1 })
db.news.createIndex({ source: 1, releasedAt: -1 })
db.news.createIndex({ "assets.slug": 1, releasedAt: -1 })

// Text search index (optional)
db.news.createIndex({ 
  title: "text", 
  subtitle: "text", 
  content: "text" 
})
```

### Query Patterns

**Most Recent News**:
```javascript
db.news.find()
  .sort({ releasedAt: -1 })
  .limit(100)
```

**Filtered by Source**:
```javascript
db.news.find({ source: "bloomberg" })
  .sort({ releasedAt: -1 })
  .limit(100)
```

**Aggregation - Top Assets**:
```javascript
db.news.aggregate([
  { $unwind: "$assets" },
  { $group: { 
      _id: "$assets.slug", 
      count: { $sum: 1 },
      name: { $first: "$assets.name" }
  }},
  { $sort: { count: -1 } },
  { $limit: 10 }
])
```

---

## API Design

### RESTful Principles

1. **Resource-based URLs**
   - `/api/v1/news` (collection)
   - `/api/v1/news/{slug}` (specific item)

2. **HTTP Methods**
   - `GET`: Retrieve data
   - `POST`: Create (future)
   - `PUT`: Update (future)
   - `DELETE`: Delete (future)

3. **Status Codes**
   - `200`: Success
   - `400`: Bad request
   - `401`: Unauthorized
   - `404`: Not found
   - `429`: Rate limit exceeded
   - `500`: Server error

4. **Consistent Response Format**
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "...",
    "has_next": true,
    "returned": 100
  }
}
```

### Versioning

- URL-based versioning: `/api/v1/`
- Allows multiple versions simultaneously
- Clear migration path

### Pagination Strategy

**Cursor-based pagination**:
- Better performance for large datasets
- Consistent results even with data changes
- No page number calculations
- Encoded cursor contains timestamp and ID

---

## Security Architecture

### Authentication

**API Key Authentication**:
```
Authorization: Bearer <api-key>
```

**Process**:
1. Extract API key from header or query
2. Validate against configured keys
3. Reject if invalid (401)
4. Proceed if valid

### Rate Limiting

**Implementation**:
- In-memory counter per API key
- Sliding window algorithm
- 1000 requests per hour default
- Returns 429 with Retry-After header

**Formula**:
```python
allowed = requests_in_window < max_requests
retry_after = oldest_request + window_size - now
```

### Data Security

1. **Input Validation**: Pydantic models
2. **SQL Injection**: MongoDB driver handles
3. **XSS Prevention**: Content sanitization
4. **CORS**: Configurable origins
5. **HTTPS**: Enforced in production

---

## Performance Considerations

### Async Operations

All I/O operations are async:
```python
async def get_news():
    # Non-blocking database call
    result = await collection.find().to_list()
    return result
```

### Connection Pooling

```python
AsyncIOMotorClient(
    uri,
    minPoolSize=10,
    maxPoolSize=50
)
```

### Database Indexes

- Query optimization
- Sort operations
- Aggregation performance

### Caching Strategy

**Future improvements**:
- Redis for rate limiting
- Cache frequently accessed data
- Cache aggregation results

### Query Optimization

1. **Limit results**: Max 1000 items
2. **Cursor pagination**: No skip operations
3. **Projection**: Return only needed fields
4. **Indexes**: All filter fields indexed

---

## Design Decisions

### Why FastAPI?

1. **Performance**: Comparable to Node.js
2. **Type Safety**: Built-in with Pydantic
3. **Documentation**: Auto-generated OpenAPI
4. **Modern**: Async/await support
5. **Developer Experience**: Type hints, IDE support

### Why MongoDB?

1. **Flexible Schema**: News structure varies by source
2. **Horizontal Scaling**: Sharding support
3. **Rich Queries**: Aggregation pipeline
4. **JSON Native**: No ORM needed
5. **Performance**: Fast reads

### Why Cursor-based Pagination?

1. **Performance**: No skip operations
2. **Consistency**: Stable results
3. **Scalability**: Works with large datasets
4. **Real-time**: Handles data changes

### Why Async?

1. **Concurrency**: Handle multiple requests
2. **Efficiency**: Non-blocking I/O
3. **Scalability**: Better resource utilization
4. **Modern**: Python 3.11+ optimizations

### Why Layered Architecture?

1. **Separation of Concerns**: Each layer has one job
2. **Testability**: Easy to mock dependencies
3. **Maintainability**: Clear structure
4. **Flexibility**: Easy to swap implementations

---

## Scalability Patterns

### Horizontal Scaling

```
Load Balancer
    │
    ├─► API Instance 1
    ├─► API Instance 2
    ├─► API Instance 3
    └─► API Instance N
         │
         └─► MongoDB (Replica Set / Sharded)
```

### Stateless Design

- No session storage
- Each request is independent
- Can run multiple instances
- Easy to scale up/down

### Database Scaling

1. **Replica Sets**: Read scalability
2. **Sharding**: Write scalability
3. **Indexes**: Query performance
4. **Caching**: Reduce database load

---

## Future Improvements

### Phase 5 Enhancements

1. **WebSocket Support**: Real-time updates
2. **GraphQL API**: Flexible queries
3. **Redis Caching**: Improved performance
4. **Message Queue**: Async processing
5. **Elasticsearch**: Full-text search
6. **Admin Dashboard**: Management UI

### Architecture Evolution

```
Current:
Client → API → MongoDB

Future:
Client → API Gateway → [
    REST API,
    GraphQL API,
    WebSocket API
] → [
    Cache (Redis),
    Database (MongoDB),
    Search (Elasticsearch),
    Queue (RabbitMQ)
]
```

---

## Monitoring & Observability

### Logging Levels

- **DEBUG**: Development
- **INFO**: Production default
- **WARNING**: Issues
- **ERROR**: Failures

### Metrics to Track

1. **API Metrics**:
   - Request rate
   - Response time
   - Error rate
   - Status code distribution

2. **Database Metrics**:
   - Query time
   - Connection pool usage
   - Index usage

3. **System Metrics**:
   - CPU usage
   - Memory usage
   - Network I/O

---

## Conclusion

MongoDB News API is built with modern best practices:

- ✅ Clean architecture
- ✅ Async operations
- ✅ Type safety
- ✅ Comprehensive testing
- ✅ Production-ready
- ✅ Scalable design
- ✅ Well documented

The architecture supports current needs while remaining flexible for future enhancements.

---

**Questions?** Open an issue on [GitHub](https://github.com/yourusername/mongodb-news-api/issues)
