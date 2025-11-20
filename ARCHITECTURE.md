# Sauti AI Architecture

Comprehensive system architecture documentation for the Sauti AI - Voice of the People platform.

## 📋 Table of Contents

- [System Overview](#system-overview)
- [Technology Stack](#technology-stack)
- [Architecture Diagram](#architecture-diagram)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Database Schema](#database-schema)
- [Security Architecture](#security-architecture)
- [API Design](#api-design)
- [Frontend Architecture](#frontend-architecture)
- [Backend Architecture](#backend-architecture)
- [AI & Agentic Layer](#ai--agentic-layer)
- [Real-time Communication](#real-time-communication)
- [Scalability & Performance](#scalability--performance)
- [Deployment Architecture](#deployment-architecture)
- [Monitoring & Logging](#monitoring--logging)
- [Error Handling Strategy](#error-handling-strategy)

## 🎯 System Overview

Sauti AI is a real-time, agentic, generative-AI civic intelligence platform built with a modern microservices architecture. The system is designed to:

1. **Ingest** citizen feedback from multiple sources (Twitter, Facebook, RSS, government portals)
2. **Process** feedback using autonomous AI agents (Jaseci OSP)
3. **Analyze** using advanced LLMs (Vertex AI, Genkit, ADK)
4. **Detect** crisis signals and emerging issues
5. **Alert** stakeholders when critical issues require attention
6. **Report** actionable insights through automated reports
7. **Track** government transparency and response rates

## 🛠️ Technology Stack

### Frontend

- **React 18** - UI framework with hooks and context API
- **Vite 5** - Build tool and dev server (fast HMR)
- **TailwindCSS 3** - Utility-first CSS framework
- **Recharts 2** - Data visualization library
- **React Router 6** - Client-side routing
- **Axios** - HTTP client for API calls
- **Supabase JS** - Authentication and database client
- **Lucide React** - Icon library
- **Leaflet** - Interactive maps

### Backend

- **FastAPI 0.109** - Python async web framework
- **Python 3.11+** - Backend runtime
- **Uvicorn** - ASGI server
- **Pydantic 2** - Data validation and settings
- **Supabase Python Client** - Database and auth integration
- **AsyncPG** - Async PostgreSQL driver
- **SQLAlchemy 2** - ORM (optional, primarily using Supabase)

### AI & Agentic Layer

- **Jaseci 1.4+** - Object-Spatial Programming for agents
- **Jac byLLM** - Autonomous AI agent reasoning
- **Vertex AI** - Google Cloud LLM services (Gemini)
- **Genkit** - Generation workflows
- **ADK** - Agentic inference and planning

### Database & Infrastructure

- **Supabase** - PostgreSQL database + edge functions + auth
- **PostgreSQL** - Primary database (via Supabase)
- **Row Level Security (RLS)** - Database-level access control

### Development & DevOps

- **Docker** - Containerization
- **Git** - Version control
- **ESLint** - JavaScript linting
- **Pytest** - Python testing
- **Sentry** - Error tracking (optional)

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Dashboard│  │  Crisis  │  │  Alerts  │  │ Feedback │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Chat   │  │ Reports  │  │Transparency│ │ Settings │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         React Contexts (Auth, Toast)                │  │
│  │         Custom Hooks (useRealtime, useApiCache)     │  │
│  │         API Services (axios clients)                 │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST + WebSocket
┌───────────────────────▼─────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Ingest API │  │  Agents API  │  │   AI API     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Crisis API  │  │  Alerts API │  │  Chat API    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Dashboard   │  │  Reports API │  │ Transparency│     │
│  │ API         │  │              │  │ API         │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │              │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐     │
│  │ Ingestion    │  │  Jaseci      │  │  AI Service  │     │
│  │ Service      │  │  Service     │  │              │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐     │
│  │ Crisis       │  │  Alert       │  │  Chat        │     │
│  │ Detection    │  │  Service     │  │  Service     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼─────────────┐
│                    Jaseci OSP Agents                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Data         │  │ Preprocessing│  │ Language     │     │
│  │ Ingestion    │  │              │  │ Detection    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐                       │
│  │ Routing      │  │ Monitoring   │                       │
│  └──────────────┘  └──────────────┘                       │
└───────────────────────────┬───────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────┐
│              External Data Sources                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Twitter  │  │ Facebook │  │   RSS    │               │
│  │   API    │  │   API    │  │  Feeds   │               │
│  └──────────┘  └──────────┘  └──────────┘               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │Government│  │  County  │  │   Open   │               │
│  │ Portals  │  │ Portals  │  │   Data   │               │
│  └──────────┘  └──────────┘  └──────────┘               │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────┐
│              Google Cloud AI Services                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Vertex   │  │  Genkit  │  │   ADK    │               │
│  │   AI     │  │          │  │          │               │
│  │ (Gemini) │  │          │  │          │               │
│  └──────────┘  └──────────┘  └──────────┘               │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────┐
│                    Supabase Database                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Feedback   │  │  Sentiment  │  │   Sectors   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  Summaries   │  │  Policies    │  │   Alerts     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Crisis       │  │ Government   │  │ Transparency │   │
│  │ Signals      │  │ Responses    │  │ Tracking     │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Reports    │  │   Rules      │  │ Audit Logs  │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Component Architecture

### Frontend Components

#### Layout Components
- **Layout.jsx** - Main application layout with sidebar, header, footer
- **Footer.jsx** - Application footer with links and information
- **ConnectionStatus.jsx** - Real-time connection status indicator
- **ProtectedRoute.jsx** - Route guard for authenticated routes
- **ErrorBoundary.jsx** - Error boundary for React error handling

#### Page Components
- **Dashboard.jsx** - Main dashboard with statistics and charts
- **CrisisDashboard.jsx** - Crisis detection and monitoring
- **Alerts.jsx** - Alert management and rule builder
- **FeedbackExplorer.jsx** - Search and filter feedback
- **Chat.jsx** - AI chat interface
- **Reports.jsx** - Report generation and viewing
- **Transparency.jsx** - Government transparency tracking
- **Settings.jsx** - Application settings
- **Login.jsx** - Authentication page

#### Custom Hooks
- **useRealtime.js** - WebSocket connection management
- **useApiCache.js** - API response caching
- **useRequestDeduplication.js** - Request deduplication
- **useAutoRefresh.js** - Automatic data refresh
- **useDebounce.js** - Debounce utility hook
- **useAuth.js** - Authentication context hook
- **useToast.js** - Toast notification context hook

### Backend Services

#### API Routes (`app/api/v1/`)
- **ingest.py** - Data ingestion endpoints
- **ai.py** - AI analysis endpoints
- **chat.py** - Chat interface endpoints
- **dashboard.py** - Dashboard data endpoints
- **alerts.py** - Alert management endpoints
- **crisis.py** - Crisis detection endpoints
- **reports.py** - Report generation endpoints
- **transparency.py** - Transparency tracking endpoints
- **search.py** - Search functionality endpoints
- **rules.py** - Alert rule management endpoints
- **config.py** - Configuration endpoints
- **agents.py** - Jaseci agent endpoints
- **auth.py** - Authentication endpoints
- **sample.py** - Sample data generation endpoints
- **realtime.py** - WebSocket endpoints

#### Business Logic (`app/services/`)
- **ingestion_service.py** - Data ingestion logic
- **ai_service.py** - AI analysis logic
- **dashboard_service.py** - Dashboard aggregation logic
- **alert_service.py** - Alert generation logic
- **crisis_service.py** - Crisis detection logic
- **chat_service.py** - Chat response generation
- **report_service.py** - Report generation logic
- **transparency_service.py** - Transparency tracking logic

#### Data Models (`app/models/`)
- Pydantic models for request/response validation
- Type definitions for all API endpoints

## 🔄 Data Flow

### 1. Data Ingestion Flow

```
External Source (Twitter/Facebook/RSS)
    ↓
Ingestion Service
    ↓
Preprocessing (Jaseci Agent)
    ↓
Language Detection (Jaseci Agent)
    ↓
Database (citizen_feedback table)
    ↓
Trigger AI Analysis (if enabled)
```

### 2. AI Processing Flow

```
Database (citizen_feedback)
    ↓
AI Service
    ↓
Vertex AI (Sentiment Analysis)
    ↓
Vertex AI (Sector Classification)
    ↓
Database (sentiment_scores, sector_classification)
    ↓
Crisis Detection Service (if threshold met)
    ↓
Alert Generation (if crisis detected)
```

### 3. Dashboard Flow

```
Frontend Request
    ↓
Dashboard API Endpoint
    ↓
Dashboard Service
    ↓
Database Queries (aggregated)
    ↓
Data Aggregation & Processing
    ↓
Response to Frontend
    ↓
Caching (useApiCache)
```

### 4. Real-time Update Flow

```
Database Change (new feedback)
    ↓
Backend Event Detection
    ↓
WebSocket Broadcast
    ↓
Frontend (useRealtime hook)
    ↓
State Update
    ↓
UI Re-render
```

## 🗄️ Database Schema

### Core Tables

#### `citizen_feedback`
Stores raw feedback data from all sources.

**Key Fields:**
- `id` (UUID, Primary Key)
- `source` (VARCHAR) - Source type (twitter, facebook, rss, etc.)
- `source_id` (VARCHAR) - Unique ID from source
- `text` (TEXT) - Feedback content
- `language` (VARCHAR) - Detected language (en, sw, mixed, sheng)
- `author` (VARCHAR) - Author identifier (hashed for privacy)
- `location` (VARCHAR) - Geographic location
- `timestamp` (TIMESTAMPTZ) - Original timestamp
- `raw_data` (JSONB) - Original data from source
- `created_at`, `updated_at` (TIMESTAMPTZ)

**Indexes:**
- `idx_feedback_source` - Source type
- `idx_feedback_timestamp` - Timestamp (DESC)
- `idx_feedback_language` - Language
- `idx_feedback_location` - Location
- `idx_feedback_text_search` - Full-text search (GIN)

#### `sentiment_scores`
Stores sentiment analysis results.

**Key Fields:**
- `id` (UUID, Primary Key)
- `feedback_id` (UUID, Foreign Key → citizen_feedback)
- `sentiment` (VARCHAR) - positive, negative, neutral
- `confidence` (DECIMAL) - Confidence score (0-1)
- `scores` (JSONB) - Detailed sentiment scores
- `analyzed_at` (TIMESTAMPTZ)
- `model_used` (VARCHAR)

#### `sector_classification`
Stores sector classification results.

**Key Fields:**
- `feedback_id` (UUID, Foreign Key)
- `primary_sector` (VARCHAR) - health, education, transport, etc.
- `secondary_sectors` (VARCHAR[]) - Array of secondary sectors
- `confidence` (DECIMAL)
- `classified_at` (TIMESTAMPTZ)
- `model_used` (VARCHAR)

#### `alerts`
Stores system alerts and notifications.

**Key Fields:**
- `id` (UUID, Primary Key)
- `alert_type` (VARCHAR)
- `severity` (VARCHAR) - low, medium, high, critical
- `title` (VARCHAR)
- `description` (TEXT)
- `sector` (VARCHAR)
- `affected_counties` (VARCHAR[])
- `metadata` (JSONB)
- `created_at` (TIMESTAMPTZ)
- `acknowledged` (BOOLEAN)
- `acknowledged_at` (TIMESTAMPTZ)
- `acknowledged_by` (UUID)

#### Additional Tables
- `ai_summary_batches` - AI-generated summaries
- `policy_recommendations` - Policy recommendations
- `pulse_reports` - Generated reports
- `priority_scores` - Priority scoring
- `users` - User profiles (extends Supabase Auth)
- `audit_logs` - Audit trail

### Row Level Security (RLS)

All tables have RLS enabled with policies:
- **Public Read**: Most tables allow public SELECT
- **Service Role Write**: Only service role can INSERT/UPDATE/DELETE
- **User-specific**: Some tables restrict by user_id

## 🔒 Security Architecture

### Authentication

1. **Supabase Auth**: Primary authentication system
   - Email/password with verification
   - Google OAuth
   - Session management with auto-refresh

2. **Token-based API Access**:
   - JWT tokens from Supabase
   - Bearer token in Authorization header
   - Token verification on protected endpoints

### Authorization

1. **Row Level Security (RLS)**:
   - Database-level access control
   - Policies defined per table
   - Service role for backend operations

2. **API-level Authorization**:
   - Token validation on all protected endpoints
   - Role-based access control (user, admin, analyst)

### Data Protection

1. **PII Handling**:
   - Author identifiers are hashed
   - Sensitive data encrypted at rest
   - No storage of raw personal information

2. **API Security**:
   - CORS configured for specific origins
   - Rate limiting on sensitive endpoints
   - Input validation with Pydantic
   - SQL injection prevention (parameterized queries)

3. **Environment Variables**:
   - Secrets stored in environment variables
   - Never committed to version control
   - Different configs for dev/staging/prod

## 🎨 API Design

### RESTful Principles

- **Resource-based URLs**: `/api/v1/dashboard/insights`
- **HTTP Methods**: GET (read), POST (create), PATCH (update), DELETE (remove)
- **Standard Response Format**: Consistent JSON structure
- **Error Handling**: Standard HTTP status codes

### API Versioning

- **Current Version**: `/api/v1`
- **Versioning Strategy**: URL-based versioning
- **Backward Compatibility**: Maintained for at least one major version

### Request/Response Patterns

**Standard Request:**
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

**Standard Response:**
```json
{
  "success": true,
  "message": "Operation completed",
  "data": { ... },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## 🎯 Frontend Architecture

### Component Structure

```
src/
├── components/        # Reusable components
│   ├── Layout.jsx
│   ├── Footer.jsx
│   └── ...
├── pages/            # Page components
│   ├── Dashboard.jsx
│   └── ...
├── hooks/            # Custom React hooks
│   ├── useRealtime.js
│   └── ...
├── contexts/         # React contexts
│   ├── AuthContext.jsx
│   └── ToastContext.jsx
├── services/         # API clients
│   └── api.js
└── utils/           # Utility functions
```

### State Management

- **React Context API**: Global state (auth, toast)
- **Local State**: Component-level state with useState
- **API Caching**: Custom hook for response caching
- **Real-time Updates**: WebSocket integration

### Performance Optimizations

- **Code Splitting**: Lazy loading of routes
- **API Caching**: Reduces redundant requests
- **Request Deduplication**: Prevents duplicate API calls
- **Memoization**: React.memo for expensive components
- **Virtual Scrolling**: For large lists (future)

## ⚙️ Backend Architecture

### Service Layer Pattern

```
API Endpoint
    ↓
Request Validation (Pydantic)
    ↓
Service Layer (Business Logic)
    ↓
Database Access (Supabase)
    ↓
Response Formatting
    ↓
Return to Client
```

### Async/Await Pattern

All I/O operations use async/await:
- Database queries
- External API calls
- File operations
- WebSocket connections

### Error Handling

- **Try-catch blocks**: Around all async operations
- **Graceful degradation**: Default values on errors
- **Error logging**: Structured logging with context
- **User-friendly messages**: Clear error messages

## 🤖 AI & Agentic Layer

### Jaseci OSP Model

Agents are modeled as graph-based walkers:

- **Nodes**: Represent data states or processing stages
- **Walkers**: Autonomous agents that traverse nodes
- **Edges**: Define relationships and data flow

### Agent Types

1. **Data Ingestion Agent**: Collects from Twitter, Facebook, RSS
2. **Preprocessing Agent**: Cleans and normalizes text
3. **Language Detection Agent**: Detects language using byLLM
4. **Routing Agent**: Routes to appropriate LLM pipelines
5. **Monitoring Agent**: Monitors risks and generates alerts

### Vertex AI Integration

- **Sentiment Analysis**: Gemini model for sentiment classification
- **Sector Classification**: Custom prompts for sector detection
- **Summary Generation**: Genkit workflows for summaries
- **Policy Recommendations**: ADK for policy analysis

## 🔴 Real-time Communication

### WebSocket Architecture

```
Client (Frontend)
    ↓
WebSocket Connection
    ↓
Backend WebSocket Handler
    ↓
Event Detection (Database changes)
    ↓
Broadcast to Connected Clients
    ↓
Client State Update
```

### Connection Management

- **Auto-reconnect**: Exponential backoff on failure
- **Heartbeat**: Ping/pong for connection health
- **Connection Pooling**: Multiple client support
- **Graceful Degradation**: Falls back to polling if WebSocket fails

## 📈 Scalability & Performance

### Backend Scalability

- **Async Processing**: FastAPI async/await for concurrency
- **Background Tasks**: Long-running operations in background
- **Database Indexing**: Optimized queries with proper indexes
- **Connection Pooling**: Efficient database connections
- **Horizontal Scaling**: Ready for load balancing

### Frontend Performance

- **API Caching**: Reduces redundant requests
- **Request Deduplication**: Prevents duplicate calls
- **Lazy Loading**: Code splitting for routes
- **Optimistic Updates**: Immediate UI feedback
- **Debouncing**: Reduces API calls on search/filter

### Database Optimization

- **Indexes**: Strategic indexes on frequently queried fields
- **Query Optimization**: Efficient aggregation queries
- **Connection Pooling**: Reuse database connections
- **Caching Strategy**: Application-level caching

## 🚀 Deployment Architecture

### Current Production Deployment

**Platform**: Google Cloud Platform (Cloud Run)

**Backend:**
- **Service**: Google Cloud Run (serverless containers)
- **URL**: https://sauti-ai-backend-7ufmxmr57q-uc.a.run.app
- **Resources**: 2Gi memory, 2 CPU, 1-10 instances
- **Database**: Supabase (managed PostgreSQL)
- **Secrets**: Google Secret Manager
- **AI Services**: Vertex AI (Gemini models)
- **Region**: us-central1

**Frontend:**
- **Service**: Google Cloud Run (Nginx serving static files)
- **URL**: https://sauti-ai-frontend-896121198699.us-central1.run.app
- **Resources**: 512Mi memory, 1 CPU, 0-10 instances
- **Build**: Docker build with Vite
- **CDN**: Cloud Run edge caching

**Infrastructure:**
- **Artifact Registry**: Docker image storage
- **Cloud Build**: CI/CD for automated builds
- **Secret Manager**: Secure environment variable storage
- **CORS**: Configured for frontend origin

### Alternative Deployment Options

**Backend:**
- **Railway**: Easy deployment with automatic scaling
- **Render**: Simple setup with PostgreSQL
- **AWS Elastic Beanstalk**: Managed deployment

**Frontend:**
- **Vercel**: Optimized for React/Vite
- **Netlify**: Fast CDN with continuous deployment
- **GitHub Pages**: Free static hosting
- **AWS S3 + CloudFront**: Scalable CDN hosting

### Docker Deployment

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration

- **Development**: Local `.env` files
- **Staging**: Environment variables in deployment platform
- **Production**: Secure environment variable management

## 📊 Monitoring & Logging

### Logging Strategy

- **Structured Logging**: JSON format for parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Context**: Request IDs, user IDs, timestamps
- **Error Tracking**: Sentry integration (optional)

### Health Checks

- **Endpoint**: `/health`
- **Database**: Connection check
- **External Services**: Status verification
- **Response Time**: Performance monitoring

### Metrics

- **API Response Times**: Track endpoint performance
- **Error Rates**: Monitor error frequency
- **Database Query Times**: Optimize slow queries
- **WebSocket Connections**: Monitor active connections

## 🛡️ Error Handling Strategy

### Error Types

1. **Validation Errors** (422): Invalid input data
2. **Authentication Errors** (401): Invalid or missing token
3. **Authorization Errors** (403): Insufficient permissions
4. **Not Found Errors** (404): Resource doesn't exist
5. **Server Errors** (500): Internal server errors
6. **Service Unavailable** (503): External service down (e.g., AI disabled)

### Error Response Format

```json
{
  "success": false,
  "message": "Error description",
  "data": null,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Error Recovery

- **Graceful Degradation**: Default values on errors
- **Retry Logic**: Automatic retries for transient errors
- **Circuit Breaker**: Prevent cascading failures
- **User Feedback**: Clear error messages to users

## 🔮 Future Enhancements

### Planned Features

- **Mobile App**: React Native application
- **Public API**: Third-party integrations
- **Advanced ML Models**: Custom classification models
- **Enhanced Notifications**: Email, SMS, push notifications
- **Real-time Collaboration**: Multi-user features
- **Advanced Analytics**: Machine learning insights

### Architecture Improvements

- **Microservices**: Split into smaller services
- **Message Queue**: RabbitMQ/Kafka for async processing
- **Caching Layer**: Redis for distributed caching
- **CDN**: Content delivery network for static assets
- **Load Balancing**: Multiple backend instances

---

**Last Updated**: 2025-11-20  
**Version**: 1.0.0  
**Deployment**: Google Cloud Run (Production)  
**Maintained by**: Sauti AI Team
