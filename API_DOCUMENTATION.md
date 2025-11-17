# Sauti AI API Documentation

Complete API reference for the Sauti AI - Voice of the People platform.

**Base URL**: `http://localhost:8000/api/v1`  
**API Version**: 1.0.0  
**Total Endpoints**: 50+

## 🔗 Quick Links

- **Interactive Swagger UI**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **API Testing**: See [Testing Guide](./TESTING.md#api-testing)

## 📚 Table of Contents

- [Authentication](#authentication)
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
- [Response Format](#response-format)
- [Error Handling](#error-handling)

---

## Authentication

### Get User Profile
```http
GET /api/v1/auth/profile?token={token}
```

Get user profile from Supabase Auth token.

**Query Parameters:**
- `token` (required): Supabase authentication token

**Response:**
```json
{
  "success": true,
  "message": "Profile retrieved",
  "data": {
    "id": "user-uuid",
    "email": "user@example.com",
    "created_at": "2025-01-01T00:00:00Z"
  }
}
```

### Verify Token
```http
GET /api/v1/auth/verify?token={token}
```

Verify if an authentication token is valid.

**Query Parameters:**
- `token` (required): Token to verify

**Response:**
```json
{
  "success": true,
  "message": "Token verified"
}
```

---

## Data Ingestion

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

Ingest data from Facebook Graph API. Monitors public pages.

**Request Body:**
```json
{
  "page_ids": ["page_id_1", "page_id_2"],
  "max_posts": 50
}
```

**Note**: Requires `FACEBOOK_ACCESS_TOKEN` in environment. If not configured, ingestion is skipped gracefully.

**Response:**
```json
{
  "success": true,
  "message": "Facebook ingestion started for 2 pages",
  "data": {
    "page_ids": ["page_id_1", "page_id_2"]
  }
}
```

### Ingest RSS Feeds
```http
POST /api/v1/ingest/rss
```

Ingest data from RSS feeds (news sources, government portals).

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

Get status of recent ingestion jobs.

**Response:**
```json
{
  "success": true,
  "message": "Ingestion status retrieved",
  "data": {
    "sources": {
      "rss": {
        "count": 60,
        "latest": "2025-11-14T18:28:32.268755+00:00"
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

## AI Analysis

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
    "analyzed_at": "2025-11-14T19:00:00Z",
    "model_used": "vertex-ai-gemini"
  }
}
```

### Classify Sector
```http
POST /api/v1/ai/classify-sector
```

Classify feedback into a sector using Vertex AI. Automatically stores the result in the database.

**Request Body:**
```json
{
  "feedback_id": "uuid-here",
  "text": "The hospital in my area has long queues.",
  "language": "en"
}
```

**Fields:**
- `feedback_id` (required): UUID of the feedback item
- `text` (required): Text content to classify
- `language` (optional, default: "en"): Language code ("en" or "sw")

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
    "classified_at": "2025-11-14T19:00:00Z",
    "model_used": "vertex-ai-gemini"
  }
}
```

### Generate Summary
```http
POST /api/v1/ai/summarize
```

Generate AI summary for a batch of feedback using Vertex AI.

**Request Body:**
```json
{
  "feedback_ids": ["uuid-1", "uuid-2", "uuid-3"],
  "language": "en"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Summary generated",
  "data": {
    "id": "summary-uuid",
    "batch_id": "batch_2025-11-14T19:00:00",
    "summary_text": "Summary of feedback...",
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "language": "en",
    "generated_at": "2025-11-14T19:00:00Z",
    "model_used": "vertex-ai"
  }
}
```

### Generate Policy Report
```http
POST /api/v1/ai/policy-report
```

Generate policy recommendation report using Vertex AI + ADK.

**Query Parameters:**
- `sector` (optional): Filter by sector
- `county` (optional): Filter by county

**Response:**
```json
{
  "success": true,
  "message": "Policy report generated",
  "data": {
    "recommendations": [
      {
        "sector": "health",
        "title": "Improve Hospital Infrastructure",
        "description": "Detailed recommendation...",
        "urgency": "high",
        "priority": 8,
        "county": "Nairobi",
        "generated_at": "2025-11-14T19:00:00Z"
      }
    ],
    "analysis": "Policy analysis report..."
  }
}
```

### Get Summaries
```http
GET /api/v1/ai/summaries?limit=10&offset=0
```

Get recent AI-generated summaries.

**Query Parameters:**
- `limit` (default: 10): Number of summaries to return
- `offset` (default: 0): Pagination offset

**Response:**
```json
{
  "success": true,
  "message": "Summaries retrieved",
  "data": [
    {
      "id": "summary-uuid",
      "batch_id": "batch_2025-11-14",
      "summary_text": "Summary text...",
      "key_points": ["Point 1", "Point 2"],
      "language": "en",
      "generated_at": "2025-11-14T19:00:00Z"
    }
  ]
}
```

### Get Recommendations
```http
GET /api/v1/ai/recommendations?sector=health&limit=10
```

Get policy recommendations.

**Query Parameters:**
- `sector` (optional): Filter by sector
- `limit` (default: 10): Number of recommendations to return

**Response:**
```json
{
  "success": true,
  "message": "Recommendations retrieved",
  "data": [
    {
      "id": "rec-uuid",
      "sector": "health",
      "title": "Recommendation title",
      "description": "Detailed description",
      "urgency": "high",
      "priority": 8,
      "county": "Nairobi",
      "generated_at": "2025-11-14T19:00:00Z"
    }
  ]
}
```

---

## Dashboard

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
    "trending_complaints": [
      {
        "id": "feedback-uuid",
        "text": "Feedback text...",
        "created_at": "2025-11-14T18:28:32Z",
        "source": "rss"
      }
    ],
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
    "generated_at": "2025-11-14T19:00:00Z"
  }
}
```

### Get Sentiment Trends
```http
GET /api/v1/dashboard/sentiment-trends?days=30
```

Get sentiment trends over time.

**Query Parameters:**
- `days` (default: 30): Number of days to analyze

**Response:**
```json
{
  "success": true,
  "message": "Sentiment trends retrieved",
  "data": {
    "trends": {
      "2025-11-14": {
        "positive": 5,
        "negative": 3,
        "neutral": 12
      },
      "2025-11-13": {
        "positive": 4,
        "negative": 2,
        "neutral": 10
      }
    },
    "period_days": 30
  }
}
```

### Get Top Issues
```http
GET /api/v1/dashboard/top-issues?limit=10&days=7
```

Get top issues by volume and urgency.

**Query Parameters:**
- `limit` (default: 10): Number of issues to return
- `days` (default: 7): Number of days to look back

**Response:**
```json
{
  "success": true,
  "message": "Top issues retrieved",
  "data": [
    {
      "sector": "governance",
      "count": 3
    },
    {
      "sector": "security",
      "count": 2
    }
  ]
}
```

### Get County Heatmap
```http
GET /api/v1/dashboard/county-heatmap?days=7
```

Get county-level sentiment and issue heatmap.

**Query Parameters:**
- `days` (default: 7): Number of days to analyze

**Response:**
```json
{
  "success": true,
  "message": "County heatmap retrieved",
  "data": {
    "Nairobi": {
      "count": 10,
      "sentiment": {
        "positive": 2,
        "negative": 3,
        "neutral": 5
      }
    },
    "Mombasa": {
      "count": 5,
      "sentiment": {
        "positive": 1,
        "negative": 1,
        "neutral": 3
      }
    }
  }
}
```

---

## Alerts

### Check Trending Complaints
```http
POST /api/v1/alerts/check-trending
```

Check for trending complaints that may require attention.

**Request Body:**
```json
{
  "time_window_hours": 24,
  "min_volume": 10
}
```

**Response:**
```json
{
  "success": true,
  "message": "Trending complaints checked",
  "data": {
    "trending": [
      {
        "id": "alert-uuid",
        "title": "Alert title",
        "severity": "high",
        "count": 15
      }
    ]
  }
}
```

### Get Red Flag Alerts
```http
GET /api/v1/alerts/red-flags?limit=20
```

Get red flag alerts that require immediate attention.

**Query Parameters:**
- `limit` (default: 20): Maximum number of alerts to return

**Response:**
```json
{
  "success": true,
  "message": "Red flag alerts retrieved",
  "data": [
    {
      "id": "alert-uuid",
      "title": "Red flag alert",
      "severity": "critical",
      "description": "Alert description",
      "created_at": "2025-11-14T19:00:00Z"
    }
  ]
}
```

### List All Alerts
```http
GET /api/v1/alerts?limit=50&severity=high
```

Get all alerts with optional filtering.

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
      "created_at": "2025-11-14T19:00:00Z"
    }
  ]
}
```

### Acknowledge Alert
```http
POST /api/v1/alerts/{alert_id}/ack
```

Acknowledge an alert.

**Response:**
```json
{
  "success": true,
  "message": "Alert acknowledged",
  "data": {
    "alert_id": "alert-uuid",
    "acknowledged_at": "2025-11-14T19:00:00Z"
  }
}
```

---

## Crisis Detection

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

Monitor a specific policy, bill, or public issue for crisis signals.

**Query Parameters:**
- `policy_name` (required): Name of policy to monitor (e.g., "Finance Bill 2024", "Healthcare Act")
- `keywords` (required): Comma-separated keywords related to the policy
- `time_window_hours` (default: 168): Time window in hours (default: 7 days)

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

Get recent crisis signals with optional filtering.

**Query Parameters:**
- `limit` (default: 20): Maximum number of signals
- `severity` (optional): Filter by severity (critical/high/medium)
- `signal_type` (optional): Filter by signal type

**Response:**
```json
{
  "success": true,
  "message": "Retrieved 5 crisis signals",
  "data": [
    {
      "id": "signal-uuid",
      "type": "sentiment_velocity",
      "severity": "high",
      "description": "Rapid sentiment deterioration",
      "created_at": "2025-11-14T19:00:00Z"
    }
  ]
}
```

### Get Crisis Dashboard
```http
GET /api/v1/crisis/dashboard?days=7
```

Get comprehensive crisis monitoring dashboard data.

**Query Parameters:**
- `days` (default: 7): Number of days to analyze

**Response:**
```json
{
  "success": true,
  "message": "Crisis dashboard data retrieved",
  "data": {
    "crisis_signals": [...],
    "sentiment_velocity": {...},
    "hashtag_intelligence": {...},
    "escalation_prediction": {...},
    "recent_alerts": [...],
    "total_feedback_analyzed": 161,
    "time_period_days": 7
  }
}
```

---

## Chat

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
    "timestamp": "2025-11-14T19:00:00Z"
  }
}
```

---

## Reports

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
    "generated_at": "2025-11-14T19:00:00Z"
  }
}
```

### List Reports
```http
GET /api/v1/reports/pulse?limit=20
```

Get list of generated reports.

**Query Parameters:**
- `limit` (default: 20): Maximum number of reports

**Response:**
```json
{
  "success": true,
  "message": "Reports retrieved",
  "data": [
    {
      "id": "report-uuid",
      "period": "weekly",
      "generated_at": "2025-11-14T19:00:00Z",
      "summary": "Report summary..."
    }
  ]
}
```

### Get Report HTML
```http
GET /api/v1/reports/pulse/{report_id}/html
```

Get HTML-formatted report for download or display.

**Response:**
```html
<!DOCTYPE html>
<html>
  <head>...</head>
  <body>...</body>
</html>
```

---

## Transparency

### Get Transparency Metrics
```http
GET /api/v1/transparency/metrics?days=30
```

Get government transparency metrics including response rates and performance.

**Query Parameters:**
- `days` (default: 30): Number of days to analyze

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

Submit a government response to an issue.

**Request Body:**
```json
{
  "issue_id": "issue-uuid",
  "agency": "Ministry of Health",
  "response_text": "We have addressed this issue...",
  "response_date": "2025-11-14T19:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Response submitted",
  "data": {
    "issue_id": "issue-uuid",
    "response_id": "response-uuid"
  }
}
```

### Get Agencies
```http
GET /api/v1/transparency/agencies?days=30
```

Get list of government agencies with performance metrics.

**Query Parameters:**
- `days` (default: 30): Number of days to analyze

**Response:**
```json
{
  "success": true,
  "message": "Agencies retrieved",
  "data": [
    {
      "name": "Ministry of Health",
      "response_rate": 0.9,
      "average_response_time_hours": 24,
      "total_issues": 50
    }
  ]
}
```

### Get Issue Timeline
```http
GET /api/v1/transparency/timeline/{issue_id}
```

Get timeline of events for a specific issue.

**Response:**
```json
{
  "success": true,
  "message": "Timeline retrieved",
  "data": {
    "issue_id": "issue-uuid",
    "events": [
      {
        "type": "created",
        "timestamp": "2025-11-10T10:00:00Z",
        "description": "Issue reported"
      },
      {
        "type": "response",
        "timestamp": "2025-11-12T14:00:00Z",
        "description": "Government response received"
      }
    ]
  }
}
```

---

## Search

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
      "created_at": "2025-11-14T18:00:00Z",
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

## Rules

### List Alert Rules
```http
GET /api/v1/rules
```

Get all alert rules.

**Response:**
```json
{
  "success": true,
  "message": "Rules retrieved",
  "data": [
    {
      "id": "rule-uuid",
      "name": "High volume health complaints",
      "enabled": true,
      "sector": "health",
      "min_count": 10,
      "notify_slack": true
    }
  ]
}
```

### Create Alert Rule
```http
POST /api/v1/rules
```

Create a new alert rule.

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

**Response:**
```json
{
  "success": true,
  "message": "Rule created",
  "data": {
    "id": "rule-uuid",
    "name": "High volume health complaints"
  }
}
```

### Update Alert Rule
```http
PATCH /api/v1/rules/{rule_id}
```

Update an existing alert rule.

**Request Body:**
```json
{
  "enabled": false,
  "min_count": 15
}
```

**Response:**
```json
{
  "success": true,
  "message": "Rule updated",
  "data": {
    "id": "rule-uuid",
    "enabled": false
  }
}
```

### Delete Alert Rule
```http
DELETE /api/v1/rules/{rule_id}
```

Delete an alert rule.

**Response:**
```json
{
  "success": true,
  "message": "Rule deleted"
}
```

### Evaluate Rules
```http
POST /api/v1/rules:eval
```

Manually trigger rule evaluation.

**Response:**
```json
{
  "success": true,
  "message": "Rules evaluated",
  "data": {
    "rules_checked": 5,
    "alerts_generated": 2
  }
}
```

---

## Configuration

### Get Alert Configuration
```http
GET /api/v1/config/alerts
```

Get current alert configuration (webhooks, etc.).

**Response:**
```json
{
  "success": true,
  "message": "Alerts config",
  "data": {
    "SLACK_WEBHOOK_URL": "https://hooks.slack.com/...",
    "ALERT_WEBHOOK_URL": "https://example.com/webhook"
  }
}
```

### Update Alert Configuration
```http
POST /api/v1/config/alerts
```

Update alert configuration.

**Request Body:**
```json
{
  "SLACK_WEBHOOK_URL": "https://hooks.slack.com/...",
  "ALERT_WEBHOOK_URL": "https://example.com/webhook"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Alerts config saved",
  "data": {
    "SLACK_WEBHOOK_URL": "https://hooks.slack.com/...",
    "ALERT_WEBHOOK_URL": "https://example.com/webhook"
  }
}
```

---

## Jaseci Agents

### Run Agent
```http
POST /api/v1/agents/run
```

Run a Jaseci OSP agent.

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

**Response:**
```json
{
  "success": true,
  "message": "Agent monitoring started",
  "data": {
    "agent_type": "monitoring"
  }
}
```

### Get Agent Status
```http
GET /api/v1/agents/status
```

Get status of running agents.

**Response:**
```json
{
  "success": true,
  "message": "Agent status retrieved",
  "data": {
    "active_agents": [],
    "status": "operational"
  }
}
```

### Get Available Agents
```http
GET /api/v1/agents/types
```

Get list of available agent types.

**Response:**
```json
{
  "success": true,
  "message": "Available agents retrieved",
  "data": [
    "data_ingestion",
    "preprocessing",
    "language_detection",
    "routing",
    "monitoring"
  ]
}
```

---

## Real-time

### WebSocket Stream
```http
WS /api/v1/realtime/stream
```

WebSocket endpoint for real-time updates.

**Streams:**
- New feedback ingestion
- Sentiment updates
- Alert notifications
- Dashboard updates

**Message Format:**
```json
{
  "type": "update",
  "data": {
    "new_feedback": 5,
    "latest": {
      "id": "feedback-uuid",
      "source": "rss",
      "created_at": "2025-11-14T19:00:00Z"
    }
  },
  "timestamp": "2025-11-14T19:00:00Z"
}
```

**Client Messages:**
- `"ping"` - Keep-alive ping
- Server responds with `{"type": "pong"}`

---

## Sample Data

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

Get list of recommended RSS feeds for Kenya.

**Response:**
```json
{
  "success": true,
  "message": "Sample RSS feeds for Kenya",
  "data": [
    {
      "name": "Nation Africa",
      "url": "https://www.nation.co.ke/rss",
      "description": "Kenya's leading news source"
    },
    {
      "name": "The Standard",
      "url": "https://www.standardmedia.co.ke/rss",
      "description": "Daily news and analysis"
    }
  ]
}
```

---

## Response Format

All API responses follow this standard format:

```json
{
  "success": boolean,
  "message": "string",
  "data": object | array,
  "timestamp": "ISO 8601 datetime"
}
```

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... },
  "timestamp": "2025-11-14T19:00:00Z"
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "data": null,
  "timestamp": "2025-11-14T19:00:00Z"
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

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

---

## Rate Limiting

Rate limiting is enabled on selected endpoints using `slowapi`.

Defaults (development): conservative limits to avoid API abuse. In production, configure limits per endpoint and client identity (IP/user/key).

Standard 429 response:

```json
{
  "detail": "Rate limit exceeded"
}
```

---

## Authentication

Most endpoints require authentication via Supabase Auth.

Preferred: HTTP header

```
Authorization: Bearer <access_token>
```

Avoid passing tokens in query strings except for testing.

---

## Interactive API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Examples

### cURL Examples

#### Ingest RSS Feed
```bash
curl -X POST "http://localhost:8000/api/v1/ingest/rss" \
  -H "Content-Type: application/json" \
  -d '["https://www.bbc.com/news/world/africa/rss.xml"]'
```

#### Analyze Sentiment
```bash
curl -X POST "http://localhost:8000/api/v1/ai/analyze-sentiment" \
  -H "Content-Type: application/json" \
  -d '{
    "feedback_id": "test-id",
    "text": "Great service!",
    "language": "en"
  }'
```

#### Get Dashboard Insights
```bash
curl "http://localhost:8000/api/v1/dashboard/insights?days=7"
```

#### Generate Sample Data
```bash
curl -X POST "http://localhost:8000/api/v1/sample/sample" \
  -H "Content-Type: application/json" \
  -d '{"count": 10, "sectors": ["health", "education"]}'
```

---

## Changelog

### Version 1.0.0 (2025-11-14)
- Initial API release
- All core endpoints implemented
- Vertex AI integration
- Jaseci agent support
- Real-time WebSocket streaming

---

## Quick Reference

### Total: 50+ Endpoints

#### Data Ingestion (8 endpoints)
- `POST /api/v1/ingest/twitter` - Ingest Twitter data
- `POST /api/v1/ingest/facebook` - Ingest Facebook data
- `POST /api/v1/ingest/rss` - Ingest RSS feeds
- `POST /api/v1/ingest/open-data` - Ingest open data
- `POST /api/v1/ingest/government-complaints` - Ingest government complaints
- `POST /api/v1/ingest/county` - Ingest county data
- `GET /api/v1/ingest/status` - Get ingestion status
- `GET /api/v1/ingest/sources` - List data sources

#### AI Analysis (6 endpoints)
- `POST /api/v1/ai/analyze-sentiment` - Analyze sentiment
- `POST /api/v1/ai/classify-sector` - Classify sector
- `POST /api/v1/ai/summarize` - Generate summary
- `POST /api/v1/ai/policy-report` - Generate policy report
- `GET /api/v1/ai/summaries` - Get summaries
- `GET /api/v1/ai/recommendations` - Get recommendations

#### Chat (1 endpoint)
- `POST /api/v1/chat/message` - Send chat message

#### Dashboard (4 endpoints)
- `GET /api/v1/dashboard/insights` - Get comprehensive insights
- `GET /api/v1/dashboard/sentiment-trends` - Get sentiment trends
- `GET /api/v1/dashboard/top-issues` - Get top issues
- `GET /api/v1/dashboard/county-heatmap` - Get county heatmap

#### Alerts (5 endpoints)
- `POST /api/v1/alerts/check-trending` - Check trending complaints
- `GET /api/v1/alerts/red-flags` - Get red flag alerts
- `GET /api/v1/alerts/` - List all alerts
- `POST /api/v1/alerts/{alert_id}/ack` - Acknowledge alert
- `POST /api/v1/alerts/test` - Test alert creation

#### Crisis Detection (4 endpoints)
- `POST /api/v1/crisis/detect` - Detect crisis signals
- `POST /api/v1/crisis/monitor-policy` - Monitor specific policy
- `GET /api/v1/crisis/signals` - Get recent signals
- `GET /api/v1/crisis/dashboard` - Get crisis dashboard

#### Reports (3 endpoints)
- `POST /api/v1/reports/pulse` - Generate pulse report
- `GET /api/v1/reports/pulse` - Get pulse reports
- `GET /api/v1/reports/pulse/{report_id}/html` - Get report HTML

#### Transparency (4 endpoints)
- `GET /api/v1/transparency/metrics` - Get transparency metrics
- `POST /api/v1/transparency/response` - Submit government response
- `GET /api/v1/transparency/agencies` - List agencies
- `GET /api/v1/transparency/timeline/{issue_id}` - Get issue timeline

#### Search (1 endpoint)
- `GET /api/v1/search/feedback` - Search feedback

#### Rules (5 endpoints)
- `GET /api/v1/rules` - List alert rules
- `POST /api/v1/rules` - Create alert rule
- `PATCH /api/v1/rules/{rule_id}` - Update alert rule
- `DELETE /api/v1/rules/{rule_id}` - Delete alert rule
- `POST /api/v1/rules:eval` - Evaluate rules

#### Configuration (2 endpoints)
- `GET /api/v1/config/alerts` - Get alert configuration
- `POST /api/v1/config/alerts` - Update alert configuration

#### Jaseci Agents (3 endpoints)
- `POST /api/v1/agents/run` - Run agent
- `GET /api/v1/agents/status` - Get agent status
- `GET /api/v1/agents/types` - Get available agents

#### Authentication (2 endpoints)
- `GET /api/v1/auth/profile` - Get user profile
- `GET /api/v1/auth/verify` - Verify token

#### Sample Data (2 endpoints)
- `POST /api/v1/sample/sample` - Generate sample data
- `GET /api/v1/sample/feeds` - Get sample RSS feeds

#### Real-time (1 endpoint)
- `WS /api/v1/realtime/stream` - WebSocket stream

#### System (2 endpoints)
- `GET /` - Root endpoint
- `GET /health` - Health check

---

**Last Updated**: 2025-11-17  
**API Version**: 1.0.0

## Changelog

### Version 1.0.0 (2025-11-17)
- Added Crisis Detection endpoints (4 endpoints)
- Added Chat interface endpoint
- Added Transparency tracking endpoints (4 endpoints)
- Added Search functionality
- Added Rules management endpoints (5 endpoints)
- Added Configuration endpoints (2 endpoints)
- Enhanced Alerts endpoints (5 endpoints)
- Enhanced Reports endpoints (3 endpoints)
- Enhanced Data Ingestion endpoints (8 endpoints)
- Total: 50+ endpoints

