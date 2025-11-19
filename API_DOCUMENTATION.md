# Sauti AI API Documentation

Complete API reference for the Sauti AI - Voice of the People platform.

**Base URL**: `http://localhost:8000/api/v1` (development)  
**Production URL**: `https://api.sautiai.com/api/v1`  
**API Version**: 1.0.0  
**Total Endpoints**: 50+

## 📋 Table of Contents

- [Quick Links](#quick-links)
- [Authentication](#authentication)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Data Ingestion](#data-ingestion)
- [AI Analysis](#ai-analysis)
- [Chat](#chat)
- [Dashboard](#dashboard)
- [Alerts](#alerts)
- [Crisis Detection](#crisis-detection)
- [Reports](#reports)
- [Transparency](#transparency)
- [Search](#search)
- [Rules](#rules)
- [Configuration](#configuration)
- [Jaseci Agents](#jaseci-agents)
- [Real-time](#real-time)
- [Sample Data](#sample-data)
- [SDK & Client Libraries](#sdk--client-libraries)
- [Postman Collection](#postman-collection)

## 🔗 Quick Links

- **Interactive Swagger UI**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/health

## 🔐 Authentication

Most endpoints require authentication via Supabase Auth. Include the access token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

**Getting an Access Token:**

1. Sign in via frontend (email/password or Google OAuth)
2. Extract token from Supabase session
3. Include in API requests

**Token Verification:**

```http
GET /api/v1/auth/verify?token={token}
```

**Note**: For development/testing, some endpoints may accept tokens in query parameters, but this is not recommended for production.

## 📦 Response Format

All API responses follow a standard format:

```json
{
  "success": boolean,
  "message": "string",
  "data": object | array | null,
  "timestamp": "ISO 8601 datetime"
}
```

### Success Response Example

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    "id": "uuid-here",
    "status": "active"
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Error Response Example

```json
{
  "success": false,
  "message": "Error description",
  "data": null,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## ⚠️ Error Handling

### HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required or invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service temporarily unavailable (e.g., AI features disabled)

### Error Response Format

```json
{
  "detail": "Error message or validation errors"
}
```

### Validation Errors

```json
{
  "detail": [
    {
      "type": "validation_error",
      "loc": ["body", "field_name"],
      "msg": "Error message",
      "input": "invalid_value"
    }
  ]
}
```

## 🚦 Rate Limiting

Rate limiting is enabled on selected endpoints using `slowapi`.

**Default Limits (Development):**
- Dashboard endpoints: 100 requests/minute
- AI endpoints: 50 requests/minute
- Other endpoints: 200 requests/minute

**Rate Limit Response:**

```json
{
  "detail": "Rate limit exceeded"
}
```

**Headers:**
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Time when limit resets

---

## 📡 Data Ingestion

### Ingest Twitter Data

```http
POST /api/v1/ingest/twitter
```

Ingest data from Twitter API. Tracks specified hashtags and geo-tagged posts within Kenyan boundaries.

**Request Body:**
```json
{
  "hashtags": ["#Kenya", "#Nairobi"],
  "max_results": 100,
  "geo_bounds": {
    "north": 5.5,
    "south": -4.7,
    "east": 41.9,
    "west": 33.9
  }
}
```

**Note**: Requires `TWITTER_BEARER_TOKEN` in environment. If not configured, ingestion is skipped gracefully.

**Response:**
```json
{
  "success": true,
  "message": "Twitter ingestion started for 2 hashtags",
  "data": {
    "hashtags": ["#Kenya", "#Nairobi"]
  }
}
```

### Ingest Facebook Data

```http
POST /api/v1/ingest/facebook
```

**Request Body:**
```json
{
  "page_ids": ["page_id_1", "page_id_2"],
  "max_posts": 50
}
```

**Note**: Requires `FACEBOOK_ACCESS_TOKEN` in environment.

### Ingest RSS Feeds

```http
POST /api/v1/ingest/rss
```

**Request Body:**
```json
[
  "https://www.bbc.com/news/world/africa/rss.xml",
  "https://www.theguardian.com/world/africa/rss"
]
```

**Response:**
```json
{
  "success": true,
  "message": "RSS ingestion started for 2 feeds",
  "data": {
    "feed_urls": [
      "https://www.bbc.com/news/world/africa/rss.xml",
      "https://www.theguardian.com/world/africa/rss"
    ]
  }
}
```

### Get Ingestion Status

```http
GET /api/v1/ingest/status
```

**Response:**
```json
{
  "success": true,
  "message": "Ingestion status retrieved",
  "data": {
    "sources": {
      "rss": {
        "count": 60,
        "latest": "2025-01-15T18:28:32Z"
      },
      "twitter": {
        "count": 0,
        "latest": null
      }
    },
    "total_recent": 60
  }
}
```

---

## 🤖 AI Analysis

### Analyze Sentiment

```http
POST /api/v1/ai/analyze-sentiment
```

Analyze sentiment of feedback text using Vertex AI. Automatically stores the result in the database.

**Request Body:**
```json
{
  "feedback_id": "uuid-here",
  "text": "The hospital services are excellent!",
  "language": "en"
}
```

**Fields:**
- `feedback_id` (required): UUID of the feedback item
- `text` (required): Text content to analyze
- `language` (optional, default: "en"): Language code ("en" or "sw")

**Response:**
```json
{
  "success": true,
  "message": "Sentiment analyzed",
  "data": {
    "feedback_id": "uuid-here",
    "sentiment": "positive",
    "confidence": 0.92,
    "scores": {
      "positive": 0.92,
      "negative": 0.05,
      "neutral": 0.03
    },
    "analyzed_at": "2025-01-15T19:00:00Z",
    "model_used": "vertex-ai-gemini"
  }
}
```

**Note**: Returns 503 if AI features are disabled.

### Classify Sector

```http
POST /api/v1/ai/classify-sector
```

**Request Body:**
```json
{
  "feedback_id": "uuid-here",
  "text": "The hospital in my area has long queues.",
  "language": "en"
}
```

**Available Sectors:**
- `health` - Healthcare and medical services
- `education` - Schools and educational services
- `transport` - Roads, public transport, traffic
- `governance` - Government services and administration
- `economy` - Economic issues, jobs, business
- `environment` - Climate, pollution, conservation
- `security` - Police, crime, safety
- `agriculture` - Farming, crops, livestock
- `other` - Other categories

**Response:**
```json
{
  "success": true,
  "message": "Sector classified",
  "data": {
    "feedback_id": "uuid-here",
    "primary_sector": "health",
    "confidence": 0.89,
    "classified_at": "2025-01-15T19:00:00Z",
    "model_used": "vertex-ai-gemini"
  }
}
```

### Generate Summary

```http
POST /api/v1/ai/summarize
```

**Request Body:**
```json
{
  "feedback_ids": ["uuid-1", "uuid-2", "uuid-3"],
  "language": "en"
}
```

### Generate Policy Report

```http
POST /api/v1/ai/policy-report
```

**Query Parameters:**
- `sector` (optional): Filter by sector
- `county` (optional): Filter by county

---

## 💬 Chat

### Send Chat Message

```http
POST /api/v1/chat/message
```

Send a message to the AI chat assistant for civic intelligence queries.

**Request Body:**
```json
{
  "message": "What are the top issues in Nairobi?",
  "conversation_history": [
    {
      "user": "Hello",
      "assistant": "Hello! How can I help you?"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Chat response generated",
  "data": {
    "response": "Based on recent feedback, the top issues in Nairobi are...",
    "intent": "query_issues",
    "entities": {
      "location": "Nairobi"
    },
    "data_points": {
      "summary": "..."
    },
    "follow_ups": [
      "Tell me more about health issues",
      "What about education?"
    ],
    "timestamp": "2025-01-15T19:00:00Z"
  }
}
```

**Note**: Returns 404 if AI features are disabled.

---

## 📊 Dashboard

### Get Insights

```http
GET /api/v1/dashboard/insights?days=7&county=Nairobi&sector=health
```

Get comprehensive dashboard insights including sentiment distribution, sector breakdown, top issues, and alerts.

**Query Parameters:**
- `days` (default: 7): Number of days to look back
- `county` (optional): Filter by county
- `sector` (optional): Filter by sector

**Response:**
```json
{
  "success": true,
  "message": "Insights retrieved",
  "data": {
    "total_feedback": 60,
    "sentiment_distribution": {
      "positive": 1,
      "negative": 1,
      "neutral": 48
    },
    "sector_distribution": {
      "governance": 3,
      "security": 2,
      "education": 1,
      "health": 1
    },
    "top_issues": [
      {
        "sector": "governance",
        "count": 3
      }
    ],
    "trending_complaints": [...],
    "recent_alerts": [],
    "county_heatmap": {
      "Nairobi": {
        "count": 10,
        "sentiment": {
          "positive": 2,
          "negative": 3,
          "neutral": 5
        }
      }
    },
    "generated_at": "2025-01-15T19:00:00Z"
  }
}
```

### Get Sentiment Trends

```http
GET /api/v1/dashboard/sentiment-trends?days=30
```

### Get Top Issues

```http
GET /api/v1/dashboard/top-issues?limit=10&days=7
```

### Get County Heatmap

```http
GET /api/v1/dashboard/county-heatmap?days=7
```

---

## 🚨 Alerts

### List All Alerts

```http
GET /api/v1/alerts?limit=50&severity=high
```

**Query Parameters:**
- `limit` (default: 50): Maximum number of alerts
- `severity` (optional): Filter by severity (critical/high/medium/low)

**Response:**
```json
{
  "success": true,
  "message": "Alerts retrieved",
  "data": [
    {
      "id": "alert-uuid",
      "title": "Alert title",
      "severity": "high",
      "sector": "health",
      "county": "Nairobi",
      "created_at": "2025-01-15T19:00:00Z"
    }
  ]
}
```

### Get Red Flag Alerts

```http
GET /api/v1/alerts/red-flags?limit=20
```

### Check Trending Complaints

```http
POST /api/v1/alerts/check-trending
```

**Request Body:**
```json
{
  "time_window_hours": 24,
  "min_volume": 10
}
```

### Acknowledge Alert

```http
POST /api/v1/alerts/{alert_id}/ack
```

---

## ⚠️ Crisis Detection

### Detect Crisis Signals

```http
POST /api/v1/crisis/detect?time_window_hours=24&min_volume=10
```

Detect crisis signals from recent feedback. Analyzes sentiment velocity, hashtag trends, policy-specific crises, and escalation predictions.

**Query Parameters:**
- `time_window_hours` (default: 24): Time window in hours to analyze
- `min_volume` (default: 10): Minimum feedback volume to analyze

**Response:**
```json
{
  "success": true,
  "message": "Detected 3 crisis signals",
  "data": {
    "signals": [
      {
        "type": "sentiment_velocity",
        "severity": "high",
        "description": "Rapid sentiment deterioration detected",
        "data": {
          "velocity_score": 0.85,
          "trend": "deteriorating"
        }
      }
    ],
    "time_window_hours": 24,
    "total_signals": 3,
    "critical_count": 1,
    "high_count": 2
  }
}
```

### Monitor Policy

```http
POST /api/v1/crisis/monitor-policy?policy_name=Finance%20Bill%202024&keywords=finance,bill,tax&time_window_hours=168
```

**Query Parameters:**
- `policy_name` (required): Name of policy to monitor
- `keywords` (required): Comma-separated keywords
- `time_window_hours` (default: 168): Time window in hours (7 days)

**Response:**
```json
{
  "success": true,
  "message": "Policy monitoring completed for Finance Bill 2024",
  "data": {
    "policy_name": "Finance Bill 2024",
    "signals_detected": 2,
    "sentiment_analysis": {
      "positive": 10,
      "negative": 45,
      "neutral": 15
    },
    "risk_level": "high"
  }
}
```

### Get Crisis Signals

```http
GET /api/v1/crisis/signals?limit=20&severity=high&signal_type=sentiment_velocity
```

### Get Crisis Dashboard

```http
GET /api/v1/crisis/dashboard?days=7
```

---

## 📄 Reports

### Generate Citizen Pulse Report

```http
POST /api/v1/reports/pulse?period=weekly
```

Generate a Citizen Pulse report (weekly or daily summary).

**Query Parameters:**
- `period` (default: "weekly"): Report period ("weekly" or "daily")

**Response:**
```json
{
  "success": true,
  "message": "Weekly report generated",
  "data": {
    "report_id": "report-uuid",
    "period": "weekly",
    "generated_at": "2025-01-15T19:00:00Z"
  }
}
```

**Note**: Returns 503 if AI features are disabled.

### List Reports

```http
GET /api/v1/reports/pulse?limit=20
```

### Get Report HTML

```http
GET /api/v1/reports/pulse/{report_id}/html
```

Returns HTML-formatted report for download or display.

---

## 🔍 Transparency

### Get Transparency Metrics

```http
GET /api/v1/transparency/metrics?days=30
```

**Response:**
```json
{
  "success": true,
  "message": "Transparency metrics retrieved",
  "data": {
    "total_issues": 150,
    "responded_issues": 120,
    "response_rate": 0.8,
    "average_response_time_hours": 48,
    "agencies": [
      {
        "name": "Ministry of Health",
        "response_rate": 0.9
      }
    ]
  }
}
```

### Submit Government Response

```http
POST /api/v1/transparency/response
```

**Request Body:**
```json
{
  "issue_id": "issue-uuid",
  "agency": "Ministry of Health",
  "response_text": "We have addressed this issue...",
  "response_date": "2025-01-15T19:00:00Z"
}
```

### Get Agencies

```http
GET /api/v1/transparency/agencies?days=30
```

### Get Issue Timeline

```http
GET /api/v1/transparency/timeline/{issue_id}
```

---

## 🔎 Search

### Search Feedback

```http
GET /api/v1/search/feedback?q=health&sector=health&county=Nairobi&limit=20
```

Full-text search across citizen feedback with filtering options.

**Query Parameters:**
- `q` (required): Search query
- `sector` (optional): Filter by sector
- `county` (optional): Filter by county
- `limit` (default: 20): Maximum results

**Response:**
```json
{
  "success": true,
  "message": "Found 20 feedback items",
  "data": [
    {
      "id": "feedback-uuid",
      "text": "Hospital services need improvement",
      "source": "rss",
      "location": "Nairobi",
      "created_at": "2025-01-15T18:00:00Z",
      "_score": 3.92,
      "whyMatched": {
        "termFrequency": 1,
        "recentDays": 2.08,
        "recencyBoost": 2.92
      },
      "highlights": ["health"]
    }
  ]
}
```

---

## 📋 Rules

### List Alert Rules

```http
GET /api/v1/rules
```

### Create Alert Rule

```http
POST /api/v1/rules
```

**Request Body:**
```json
{
  "name": "High volume health complaints",
  "enabled": true,
  "sector": "health",
  "county": "Nairobi",
  "min_count": 10,
  "notify_slack": true,
  "notify_webhook": false
}
```

### Update Alert Rule

```http
PATCH /api/v1/rules/{rule_id}
```

### Delete Alert Rule

```http
DELETE /api/v1/rules/{rule_id}
```

### Evaluate Rules

```http
POST /api/v1/rules:eval
```

Manually trigger rule evaluation.

---

## ⚙️ Configuration

### Get Alert Configuration

```http
GET /api/v1/config/alerts
```

### Update Alert Configuration

```http
POST /api/v1/config/alerts
```

**Request Body:**
```json
{
  "SLACK_WEBHOOK_URL": "https://hooks.slack.com/services/...",
  "ALERT_WEBHOOK_URL": "https://example.com/webhook"
}
```

---

## 🤖 Jaseci Agents

### Run Agent

```http
POST /api/v1/agents/run
```

**Request Body:**
```json
{
  "agent_type": "monitoring",
  "parameters": {
    "time_window": 24,
    "alert_threshold": 0.8
  }
}
```

**Available Agent Types:**
- `data_ingestion`: Autonomous data collection
- `preprocessing`: Text cleaning and normalization
- `language_detection`: Detect language (en/sw)
- `routing`: Route data to appropriate LLM pipeline
- `monitoring`: Monitor risks and trends

### Get Agent Status

```http
GET /api/v1/agents/status
```

### Get Available Agents

```http
GET /api/v1/agents/types
```

---

## 🔴 Real-time

### WebSocket Stream

```http
WS /api/v1/realtime/stream
```

WebSocket endpoint for real-time updates.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/realtime/stream');
```

**Message Format:**
```json
{
  "type": "update",
  "data": {
    "new_feedback": 5,
    "latest": {
      "id": "feedback-uuid",
      "source": "rss",
      "created_at": "2025-01-15T19:00:00Z"
    }
  },
  "timestamp": "2025-01-15T19:00:00Z"
}
```

**Client Messages:**
- `"ping"` - Keep-alive ping
- Server responds with `{"type": "pong"}`

**Streams:**
- New feedback ingestion
- Sentiment updates
- Alert notifications
- Dashboard updates

---

## 🧪 Sample Data

### Generate Sample Data

```http
POST /api/v1/sample/sample
```

Generate sample feedback data for testing (no API tokens required).

**Request Body:**
```json
{
  "count": 20,
  "sectors": ["health", "education", "transport"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Generated 20 sample feedback items",
  "data": {
    "count": 20,
    "sectors": ["health", "education", "transport"],
    "feedback_ids": ["uuid-1", "uuid-2", ...]
  }
}
```

**Note**: Automatically creates sentiment scores and sector classifications for generated data.

### Get Sample RSS Feeds

```http
GET /api/v1/sample/feeds
```

---

## 📚 SDK & Client Libraries

### JavaScript/TypeScript

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

// Get dashboard insights
const insights = await api.get('/dashboard/insights?days=7');

// Analyze sentiment
const sentiment = await api.post('/ai/analyze-sentiment', {
  feedback_id: 'uuid',
  text: 'Great service!',
  language: 'en'
});
```

### Python

```python
import requests

BASE_URL = 'http://localhost:8000/api/v1'
headers = {'Authorization': f'Bearer {access_token}'}

# Get dashboard insights
response = requests.get(
    f'{BASE_URL}/dashboard/insights?days=7',
    headers=headers
)
insights = response.json()

# Analyze sentiment
response = requests.post(
    f'{BASE_URL}/ai/analyze-sentiment',
    headers=headers,
    json={
        'feedback_id': 'uuid',
        'text': 'Great service!',
        'language': 'en'
    }
)
sentiment = response.json()
```

---

## 📮 Postman Collection

A Postman collection is available for testing all endpoints:

1. Import the collection from `docs/postman/SautiAI_API.postman_collection.json`
2. Set environment variables:
   - `base_url`: `http://localhost:8000/api/v1`
   - `access_token`: Your Supabase access token
3. Run requests directly from Postman

---

## 📊 Endpoint Summary

### Total: 50+ Endpoints

- **Data Ingestion**: 8 endpoints
- **AI Analysis**: 6 endpoints
- **Chat**: 1 endpoint
- **Dashboard**: 4 endpoints
- **Alerts**: 5 endpoints
- **Crisis Detection**: 4 endpoints
- **Reports**: 3 endpoints
- **Transparency**: 4 endpoints
- **Search**: 1 endpoint
- **Rules**: 5 endpoints
- **Configuration**: 2 endpoints
- **Jaseci Agents**: 3 endpoints
- **Authentication**: 2 endpoints
- **Sample Data**: 2 endpoints
- **Real-time**: 1 endpoint
- **System**: 2 endpoints

---

## 📝 Changelog

### Version 1.0.0 (2025-01-15)
- Initial API release
- All core endpoints implemented
- Vertex AI integration
- Jaseci agent support
- Real-time WebSocket streaming
- Comprehensive error handling
- Rate limiting implementation

---

**Last Updated**: 2025-01-15  
**API Version**: 1.0.0  
**Maintained by**: Sauti AI Team
