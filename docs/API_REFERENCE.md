# MongoDB News API - API Reference

Complete reference documentation for all API endpoints.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints require API key authentication. You can provide the API key in two ways:

### Option 1: Authorization Header (Recommended)
```bash
Authorization: Bearer YOUR_API_KEY
```

### Option 2: Query Parameter
```bash
?api_key=YOUR_API_KEY
```

## Rate Limiting

- **Limit**: 1000 requests per hour per API key
- **Headers**: All responses include rate limit information:
  - `X-RateLimit-Limit`: Maximum requests per hour
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Unix timestamp when the limit resets

When rate limit is exceeded, you'll receive a `429 Too Many Requests` response with a `Retry-After` header.

---

## Endpoints

### Root Endpoint

#### `GET /`

Get basic API information.

**Authentication**: Not required

**Response**:
```json
{
  "name": "MongoDB News API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "health": "/api/v1/health",
  "features": {
    "authentication": "API Key",
    "pagination": "Cursor-based",
    "rate_limiting": "1000 requests/hour",
    "aggregations": true
  }
}
```

---

### Health Check

#### `GET /api/v1/health`

Check API and database health status.

**Authentication**: Not required

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-20T12:00:00Z"
}
```

---

## News Endpoints

### Get News List

#### `GET /api/v1/news`

Get paginated list of news articles with optional filters.

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `from_date` | string (ISO 8601) | No | - | Filter news from this date |
| `to_date` | string (ISO 8601) | No | - | Filter news until this date |
| `source` | string | No | - | Filter by news source (coinmarketcap, bloomberg, reuters, etc.) |
| `asset_slug` | string | No | - | Filter by asset slug (bitcoin, ethereum, etc.) |
| `keyword` | string | No | - | Search keyword in title and content (2-100 chars) |
| `limit` | integer | No | 100 | Number of items per page (10-1000) |
| `cursor` | string | No | - | Pagination cursor from previous response |
| `sort_by` | string | No | releasedAt | Field to sort by (releasedAt, title, createdAt) |
| `order` | string | No | desc | Sort order (asc, desc) |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/news?source=bloomberg&limit=20" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Success Response** (200 OK):
```json
{
  "data": [
    {
      "slug": "bitcoin-hits-new-high",
      "title": "Bitcoin Hits New All-Time High",
      "subtitle": "Bitcoin surges past $50,000...",
      "source": "coinmarketcap",
      "sourceName": "CoinMarketCap News",
      "sourceUrl": "https://coinmarketcap.com/...",
      "releasedAt": "2025-11-20T12:00:00Z",
      "assets": [
        {
          "name": "Bitcoin",
          "slug": "bitcoin",
          "symbol": "BTC"
        }
      ]
    }
  ],
  "pagination": {
    "next_cursor": "eyJfaWQiOiI2NTRh...",
    "prev_cursor": null,
    "has_next": true,
    "has_prev": false,
    "limit": 20,
    "returned": 20
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid parameters (e.g., invalid date format)
- `401 Unauthorized`: Missing or invalid API key
- `422 Unprocessable Entity`: Validation error (e.g., limit out of range)

---

### Get News by Slug

#### `GET /api/v1/news/{slug}`

Get detailed information about a specific news article.

**Authentication**: Required

**Path Parameters**:
- `slug` (string, required): Unique identifier for the news article

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/news/bitcoin-hits-new-high" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Success Response** (200 OK):
```json
{
  "slug": "bitcoin-hits-new-high",
  "title": "Bitcoin Hits New All-Time High",
  "subtitle": "Bitcoin surges past $50,000...",
  "content": "<p>Full article content with HTML...</p>",
  "source": "coinmarketcap",
  "sourceName": "CoinMarketCap News",
  "sourceUrl": "https://coinmarketcap.com/...",
  "releasedAt": "2025-11-20T12:00:00Z",
  "assets": [
    {
      "name": "Bitcoin",
      "slug": "bitcoin",
      "symbol": "BTC"
    }
  ],
  "createdAt": "2025-11-20T12:05:00Z",
  "updatedAt": "2025-11-20T12:05:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing or invalid API key
- `404 Not Found`: News article not found

---

## Aggregation Endpoints

### Get Statistics

#### `GET /api/v1/aggregations/stats`

Get aggregated news statistics grouped by source or date.

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `group_by` | string | No | source | Group by: source, date |
| `from_date` | string (ISO 8601) | No | - | Filter from this date |
| `to_date` | string (ISO 8601) | No | - | Filter until this date |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/aggregations/stats?group_by=source" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Success Response** (200 OK):
```json
{
  "data": [
    {
      "_id": "coinmarketcap",
      "count": 150
    },
    {
      "_id": "bloomberg",
      "count": 120
    }
  ],
  "total": 270,
  "filters": {
    "group_by": "source",
    "from_date": null,
    "to_date": null
  }
}
```

---

### Get Top Assets

#### `GET /api/v1/aggregations/top-assets`

Get the most frequently mentioned assets in news.

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | 10 | Number of top assets (1-100) |
| `from_date` | string (ISO 8601) | No | - | Filter from this date |
| `to_date` | string (ISO 8601) | No | - | Filter until this date |
| `source` | string | No | - | Filter by source |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/aggregations/top-assets?limit=5" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Success Response** (200 OK):
```json
{
  "data": [
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
    }
  ],
  "filters": {
    "limit": 5,
    "from_date": null,
    "to_date": null,
    "source": null
  }
}
```

---

### Get Timeline

#### `GET /api/v1/aggregations/timeline`

Get news count over time with configurable intervals.

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `interval` | string | No | daily | Time interval: daily, weekly, monthly |
| `from_date` | string (ISO 8601) | No | - | Filter from this date |
| `to_date` | string (ISO 8601) | No | - | Filter until this date |
| `source` | string | No | - | Filter by source |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/aggregations/timeline?interval=daily" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Success Response** (200 OK):
```json
{
  "data": [
    {
      "_id": "2025-11-20",
      "count": 45
    },
    {
      "_id": "2025-11-19",
      "count": 52
    }
  ],
  "filters": {
    "interval": "daily",
    "from_date": null,
    "to_date": null,
    "source": null
  }
}
```

---

### Get Source Performance

#### `GET /api/v1/aggregations/source-performance`

Get detailed performance statistics for each news source.

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `from_date` | string (ISO 8601) | No | - | Filter from this date |
| `to_date` | string (ISO 8601) | No | - | Filter until this date |

**Example Request**:
```bash
curl -X GET "http://localhost:8000/api/v1/aggregations/source-performance" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

**Success Response** (200 OK):
```json
{
  "data": [
    {
      "_id": "coinmarketcap",
      "count": 150,
      "avg_per_day": 5.0,
      "top_assets": ["bitcoin", "ethereum"]
    },
    {
      "_id": "bloomberg",
      "count": 120,
      "avg_per_day": 4.0,
      "top_assets": ["bitcoin"]
    }
  ],
  "filters": {
    "from_date": null,
    "to_date": null
  }
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "status": 400,
    "timestamp": "2025-11-20T12:00:00Z"
  }
}
```

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INVALID_DATE_FORMAT` | 400 | Invalid date format in request |
| `INVALID_CURSOR` | 400 | Invalid or expired pagination cursor |
| `NEWS_NOT_FOUND` | 404 | Requested news article not found |
| `VALIDATION_ERROR` | 422 | Request validation failed |

---

## Date Format

All dates should be in ISO 8601 format:

**Examples**:
- `2025-11-20` (date only)
- `2025-11-20T12:00:00Z` (with time, UTC)
- `2025-11-20T12:00:00+00:00` (with timezone)

---

## Pagination

This API uses **cursor-based pagination** for efficient navigation through large datasets.

### How It Works

1. First request: Don't include a cursor parameter
2. Response includes `pagination.next_cursor` if more items exist
3. Use that cursor in the next request: `?cursor=eyJfaWQi...`
4. Repeat until `pagination.has_next` is `false`

### Benefits

- Consistent results even when data changes
- Efficient for large datasets
- No page number calculations needed

### Example Flow

```bash
# Page 1
GET /api/v1/news?limit=10

# Response includes next_cursor
# Page 2
GET /api/v1/news?limit=10&cursor=eyJfaWQiOiI2NTRh...

# Continue until has_next is false
```

---

## Interactive Documentation

Visit these URLs for interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`
