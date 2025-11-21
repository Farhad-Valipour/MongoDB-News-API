# MongoDB News API - Usage Examples

Practical examples for common use cases.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Operations](#basic-operations)
3. [Filtering and Searching](#filtering-and-searching)
4. [Pagination](#pagination)
5. [Analytics and Aggregations](#analytics-and-aggregations)
6. [Error Handling](#error-handling)
7. [Client Libraries](#client-libraries)

---

## Getting Started

### Setting Up Authentication

Store your API key securely:

```bash
# In your environment
export NEWS_API_KEY="your-api-key-here"
```

---

## Basic Operations

### 1. Get Latest News

Get the most recent news articles:

```bash
curl -X GET "http://localhost:8000/api/v1/news?limit=10&order=desc" \
  -H "Authorization: Bearer $NEWS_API_KEY"
```

### 2. Get Specific Article

Retrieve details of a specific news article:

```bash
curl -X GET "http://localhost:8000/api/v1/news/bitcoin-hits-new-high" \
  -H "Authorization: Bearer $NEWS_API_KEY"
```

### 3. Check API Health

Verify API status (no authentication required):

```bash
curl -X GET "http://localhost:8000/api/v1/health"
```

---

## Filtering and Searching

### 1. Filter by Source

Get news from specific source (e.g., Bloomberg):

```bash
curl -X GET "http://localhost:8000/api/v1/news?source=bloomberg&limit=20" \
  -H "Authorization: Bearer $NEWS_API_KEY"
```

### 2. Filter by Asset

Get news about a specific cryptocurrency:

```bash
curl -X GET "http://localhost:8000/api/v1/news?asset_slug=bitcoin&limit=20" \
  -H "Authorization: Bearer $NEWS_API_KEY"
```

### 3. Search by Keyword

Search for news containing specific keywords:

```bash
curl -X GET "http://localhost:8000/api/v1/news?keyword=regulation&limit=20" \
  -H "Authorization: Bearer $NEWS_API_KEY"
```

### 4. Date Range Filter

Get news within a specific date range:

```bash
curl -X GET "http://localhost:8000/api/v1/news?from_date=2025-11-01&to_date=2025-11-30" \
  -H "Authorization: Bearer $NEWS_API_KEY"
```

### 5. Combined Filters

Combine multiple filters for precise results:

```bash
curl -X GET "http://localhost:8000/api/v1/news?source=bloomberg&asset_slug=bitcoin&from_date=2025-11-01&limit=10" \
  -H "Authorization: Bearer $NEWS_API_KEY"
```

---

## Pagination

### Navigate Through Large Datasets

#### Step 1: Get First Page

```bash
curl -X GET "http://localhost:8000/api/v1/news?limit=10" \
  -H "Authorization: Bearer $NEWS_API_KEY" \
  | jq '.pagination.next_cursor'
```

#### Step 2: Get Next Page

Use the cursor from the previous response:

```bash
NEXT_CURSOR="eyJfaWQiOiI2NTRhZjgxYjc4..."

curl -X GET "http://localhost:8000/api/v1/news?limit=10&cursor=$NEXT_CURSOR" \
  -H "Authorization: Bearer $NEWS_API_KEY"
```

#### Step 3: Iterate Until End

```bash
#!/bin/bash
API_KEY="your-api-key"
CURSOR=""

while true; do
  if [ -z "$CURSOR" ]; then
    RESPONSE=$(curl -s "http://localhost:8000/api/v1/news?limit=10" \
      -H "Authorization: Bearer $API_KEY")
  else
    RESPONSE=$(curl -s "http://localhost:8000/api/v1/news?limit=10&cursor=$CURSOR" \
      -H "Authorization: Bearer $API_KEY")
  fi
  
  # Process data
  echo "$RESPONSE" | jq '.data'
  
  # Check if more pages
  HAS_NEXT=$(echo "$RESPONSE" | jq -r '.pagination.has_next')
  if [ "$HAS_NEXT" != "true" ]; then
    break
  fi
  
  # Get next cursor
  CURSOR=$(echo "$RESPONSE" | jq -r '.pagination.next_cursor')
done
```

---

## Analytics and Aggregations

### 1. Get News Count by Source

```bash
curl -X GET "http://localhost:8000/api/v1/aggregations/stats?group_by=source" \
  -H "Authorization: Bearer $NEWS_API_KEY"
```

**Response**:
```json
{
  "data": [
    {"_id": "coinmarketcap", "count": 150},
    {"_id": "bloomberg", "count": 120},
    {"_id": "reuters", "count": 100}
  ],
  "total": 370
}
```

### 2. Get Top 10 Most Mentioned Assets

```bash
curl -X GET "http://localhost:8000/api/v1/aggregations/top-assets?limit=10" \
  -H "Authorization: Bearer $NEWS_API_KEY"
```

**Response**:
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
  ]
}
```

### 3. Get Daily Timeline for Last Week

```bash
# Calculate dates
FROM_DATE=$(date -d '7 days ago' '+%Y-%m-%d')
TO_DATE=$(date '+%Y-%m-%d')

curl -X GET "http://localhost:8000/api/v1/aggregations/timeline?interval=daily&from_date=$FROM_DATE&to_date=$TO_DATE" \
  -H "Authorization: Bearer $NEWS_API_KEY"
```

### 4. Get Source Performance Metrics

```bash
curl -X GET "http://localhost:8000/api/v1/aggregations/source-performance" \
  -H "Authorization: Bearer $NEWS_API_KEY"
```

**Response**:
```json
{
  "data": [
    {
      "_id": "coinmarketcap",
      "count": 150,
      "avg_per_day": 5.0,
      "top_assets": ["bitcoin", "ethereum"]
    }
  ]
}
```

---

## Error Handling

### Handling Rate Limits

```bash
RESPONSE=$(curl -s -w "\n%{http_code}" "http://localhost:8000/api/v1/news" \
  -H "Authorization: Bearer $NEWS_API_KEY")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" -eq 429 ]; then
  RETRY_AFTER=$(echo "$BODY" | jq -r '.error.retry_after')
  echo "Rate limit exceeded. Retry after $RETRY_AFTER seconds"
  sleep $RETRY_AFTER
fi
```

### Handling Invalid Dates

```bash
# Try with invalid date
curl -X GET "http://localhost:8000/api/v1/news?from_date=invalid-date" \
  -H "Authorization: Bearer $NEWS_API_KEY"

# Response: 400 Bad Request
{
  "error": {
    "code": "INVALID_DATE_FORMAT",
    "message": "Invalid from_date format. Use ISO 8601 format",
    "status": 400
  }
}
```

### Handling Missing Articles

```bash
curl -X GET "http://localhost:8000/api/v1/news/nonexistent-slug" \
  -H "Authorization: Bearer $NEWS_API_KEY"

# Response: 404 Not Found
{
  "error": {
    "code": "NEWS_NOT_FOUND",
    "message": "News article not found: nonexistent-slug",
    "status": 404
  }
}
```

---

## Client Libraries

### Python Client

```python
import requests
from datetime import datetime, timedelta

class NewsAPIClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8000/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def get_news(self, source=None, asset_slug=None, keyword=None, 
                 from_date=None, to_date=None, limit=100):
        """Get news with filters."""
        params = {"limit": limit}
        if source:
            params["source"] = source
        if asset_slug:
            params["asset_slug"] = asset_slug
        if keyword:
            params["keyword"] = keyword
        if from_date:
            params["from_date"] = from_date.isoformat()
        if to_date:
            params["to_date"] = to_date.isoformat()
        
        response = self.session.get(f"{self.base_url}/news", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_news_by_slug(self, slug: str):
        """Get specific news article."""
        response = self.session.get(f"{self.base_url}/news/{slug}")
        response.raise_for_status()
        return response.json()
    
    def get_all_news(self, **kwargs):
        """Get all news using pagination."""
        all_news = []
        cursor = None
        
        while True:
            params = {**kwargs, "limit": 100}
            if cursor:
                params["cursor"] = cursor
            
            response = self.session.get(f"{self.base_url}/news", params=params)
            response.raise_for_status()
            data = response.json()
            
            all_news.extend(data["data"])
            
            if not data["pagination"]["has_next"]:
                break
            
            cursor = data["pagination"]["next_cursor"]
        
        return all_news
    
    def get_top_assets(self, limit=10, from_date=None, to_date=None):
        """Get top mentioned assets."""
        params = {"limit": limit}
        if from_date:
            params["from_date"] = from_date.isoformat()
        if to_date:
            params["to_date"] = to_date.isoformat()
        
        response = self.session.get(f"{self.base_url}/aggregations/top-assets", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_timeline(self, interval="daily", from_date=None, to_date=None):
        """Get news timeline."""
        params = {"interval": interval}
        if from_date:
            params["from_date"] = from_date.isoformat()
        if to_date:
            params["to_date"] = to_date.isoformat()
        
        response = self.session.get(f"{self.base_url}/aggregations/timeline", params=params)
        response.raise_for_status()
        return response.json()


# Usage example
if __name__ == "__main__":
    client = NewsAPIClient(api_key="your-api-key")
    
    # Get latest Bitcoin news from Bloomberg
    news = client.get_news(source="bloomberg", asset_slug="bitcoin", limit=10)
    print(f"Found {len(news['data'])} articles")
    
    # Get specific article
    article = client.get_news_by_slug("bitcoin-hits-new-high")
    print(f"Title: {article['title']}")
    
    # Get all news from last week
    from_date = datetime.now() - timedelta(days=7)
    all_news = client.get_all_news(from_date=from_date)
    print(f"Total articles: {len(all_news)}")
    
    # Get top 5 assets
    top_assets = client.get_top_assets(limit=5)
    for asset in top_assets['data']:
        print(f"{asset['name']}: {asset['count']} mentions ({asset['percentage']}%)")
```

### JavaScript/Node.js Client

```javascript
const axios = require('axios');

class NewsAPIClient {
  constructor(apiKey, baseURL = 'http://localhost:8000/api/v1') {
    this.apiKey = apiKey;
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: baseURL,
      headers: {
        'Authorization': `Bearer ${apiKey}`
      }
    });
  }

  async getNews(options = {}) {
    const { source, assetSlug, keyword, fromDate, toDate, limit = 100 } = options;
    const params = { limit };
    
    if (source) params.source = source;
    if (assetSlug) params.asset_slug = assetSlug;
    if (keyword) params.keyword = keyword;
    if (fromDate) params.from_date = fromDate.toISOString();
    if (toDate) params.to_date = toDate.toISOString();
    
    const response = await this.client.get('/news', { params });
    return response.data;
  }

  async getNewsBySlug(slug) {
    const response = await this.client.get(`/news/${slug}`);
    return response.data;
  }

  async* getAllNews(options = {}) {
    let cursor = null;
    
    while (true) {
      const params = { ...options, limit: 100 };
      if (cursor) params.cursor = cursor;
      
      const response = await this.client.get('/news', { params });
      const data = response.data;
      
      yield* data.data;
      
      if (!data.pagination.has_next) break;
      cursor = data.pagination.next_cursor;
    }
  }

  async getTopAssets(limit = 10, fromDate, toDate) {
    const params = { limit };
    if (fromDate) params.from_date = fromDate.toISOString();
    if (toDate) params.to_date = toDate.toISOString();
    
    const response = await this.client.get('/aggregations/top-assets', { params });
    return response.data;
  }

  async getTimeline(interval = 'daily', fromDate, toDate) {
    const params = { interval };
    if (fromDate) params.from_date = fromDate.toISOString();
    if (toDate) params.to_date = toDate.toISOString();
    
    const response = await this.client.get('/aggregations/timeline', { params });
    return response.data;
  }
}

// Usage example
(async () => {
  const client = new NewsAPIClient('your-api-key');
  
  // Get latest Bitcoin news
  const news = await client.getNews({ 
    source: 'bloomberg', 
    assetSlug: 'bitcoin', 
    limit: 10 
  });
  console.log(`Found ${news.data.length} articles`);
  
  // Get all news using async generator
  const allNews = [];
  for await (const article of client.getAllNews({ source: 'coinmarketcap' })) {
    allNews.push(article);
  }
  console.log(`Total articles: ${allNews.length}`);
  
  // Get top assets
  const topAssets = await client.getTopAssets(5);
  topAssets.data.forEach(asset => {
    console.log(`${asset.name}: ${asset.count} mentions (${asset.percentage}%)`);
  });
})();
```

---

## Advanced Scenarios

### Building a News Dashboard

```python
from news_api_client import NewsAPIClient
from datetime import datetime, timedelta
import pandas as pd

client = NewsAPIClient(api_key="your-api-key")

# Get data for last 30 days
from_date = datetime.now() - timedelta(days=30)
to_date = datetime.now()

# 1. Get timeline data
timeline = client.get_timeline(interval="daily", from_date=from_date, to_date=to_date)
timeline_df = pd.DataFrame(timeline['data'])

# 2. Get top assets
top_assets = client.get_top_assets(limit=10, from_date=from_date, to_date=to_date)
assets_df = pd.DataFrame(top_assets['data'])

# 3. Get source performance
response = requests.get(
    "http://localhost:8000/api/v1/aggregations/source-performance",
    headers={"Authorization": f"Bearer {client.api_key}"},
    params={"from_date": from_date.isoformat(), "to_date": to_date.isoformat()}
)
sources_df = pd.DataFrame(response.json()['data'])

# Create visualizations
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Timeline chart
axes[0].plot(timeline_df['_id'], timeline_df['count'])
axes[0].set_title('News Timeline')
axes[0].set_xlabel('Date')
axes[0].set_ylabel('Count')

# Top assets bar chart
axes[1].barh(assets_df['name'], assets_df['count'])
axes[1].set_title('Top 10 Assets')
axes[1].set_xlabel('Mentions')

# Source distribution pie chart
axes[2].pie(sources_df['count'], labels=sources_df['_id'], autopct='%1.1f%%')
axes[2].set_title('News by Source')

plt.tight_layout()
plt.savefig('news_dashboard.png')
```

### Real-time Monitoring

```python
import time
from news_api_client import NewsAPIClient

client = NewsAPIClient(api_key="your-api-key")
seen_slugs = set()

while True:
    # Get latest news
    news = client.get_news(limit=10, order="desc")
    
    for article in news['data']:
        if article['slug'] not in seen_slugs:
            print(f"NEW: {article['title']} - {article['source']}")
            seen_slugs.add(article['slug'])
    
    # Wait 60 seconds before next check
    time.sleep(60)
```

---

## Tips and Best Practices

1. **Use Pagination**: Always use cursor-based pagination for large datasets
2. **Cache Results**: Cache aggregation results that don't change frequently
3. **Handle Rate Limits**: Implement exponential backoff when hitting rate limits
4. **Use Date Filters**: Narrow down results with date ranges for better performance
5. **Monitor Usage**: Track your API usage with the rate limit headers
6. **Error Handling**: Always handle errors gracefully in production code
7. **Connection Pooling**: Reuse HTTP connections for better performance
