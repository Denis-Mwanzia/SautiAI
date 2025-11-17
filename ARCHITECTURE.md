# Sauti AI Architecture

## System Overview

Sauti AI is a real-time, agentic, generative-AI civic intelligence platform built with a modern microservices architecture.

## Technology Stack

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **TailwindCSS** - Utility-first CSS framework
- **Recharts** - Data visualization
- **Supabase Auth** - Authentication

### Backend
- **FastAPI** - Python async web framework
- **Supabase** - PostgreSQL database + edge functions
- **Python 3.11+** - Backend runtime

### AI & Agentic Layer
- **Jaseci + Jac** - Object-Spatial Programming for agents
- **Jac byLLM** - Autonomous AI agent reasoning
- **Vertex AI** - Google Cloud LLM services
- **Genkit** - Generation workflows
- **ADK** - Agentic inference and planning

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Dashboard│  │  Crisis  │  │  Alerts  │  │ Feedback │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   Chat   │  │ Reports  │  │Transparency│ │ Settings │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │ HTTP/REST
┌───────────────────────▼─────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Ingest API │  │  Agents API  │  │   AI API     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Crisis API  │  │  Alerts API │  │  Chat API    │     │
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
┌─────────────────────────────▼───────────────────────────────┐
│              External Data Sources                           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Twitter  │  │ Facebook │  │   RSS    │                  │
│  │   API    │  │   API    │  │  Feeds   │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│              Google Cloud AI Services                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │ Vertex   │  │  Genkit  │  │   ADK    │                  │
│  │   AI     │  │          │  │          │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                    Supabase Database                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Feedback   │  │  Sentiment  │  │   Sectors   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Summaries   │  │  Policies    │  │   Alerts     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Crisis       │  │ Government   │  │ Transparency │     │
│  │ Signals      │  │ Alerts       │  │ Tracking     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Data Ingestion Flow

```
External Source → Ingestion Service → Preprocessing → Database
     ↓
Jaseci Agent (data_ingestion_agent)
```

### 2. Processing Flow

```
Database → Jaseci Agent (preprocessing) → Language Detection → Routing
     ↓
Sentiment Analysis (Vertex AI)
Sector Classification (Vertex AI)
Summary Generation (Genkit)
Policy Analysis (ADK)
```

### 3. Dashboard Flow

```
Database → Dashboard Service → Aggregation → Frontend
```

## Agent Architecture

### Jaseci OSP Model

Agents are modeled as graph-based walkers in Jaseci:

- **Nodes**: Represent data states or processing stages
- **Walkers**: Autonomous agents that traverse nodes
- **Edges**: Define relationships and data flow

### Agent Types

1. **Data Ingestion Agent**: Collects from Twitter, Facebook, RSS
2. **Preprocessing Agent**: Cleans and normalizes text
3. **Language Detection Agent**: Detects language using byLLM
4. **Routing Agent**: Routes to appropriate LLM pipelines
5. **Monitoring Agent**: Monitors risks and generates alerts

## Database Schema

See `supabase/migrations/001_initial_schema.sql` for complete schema.

Key tables:
- `citizen_feedback` - Raw feedback data
- `sentiment_scores` - Sentiment analysis results
- `sector_classification` - Sector categorization
- `ai_summary_batches` - AI-generated summaries
- `policy_recommendations` - Policy recommendations
- `alerts` - System alerts
- `audit_logs` - Audit trail

## Security

- **Row Level Security (RLS)**: Enabled on all tables
- **Supabase Auth**: User authentication (email/password and Google OAuth)
- **API Keys**: Stored securely in environment variables
- **Data Anonymization**: Author identifiers are hashed
- **CORS**: Configured for specific origins

### Rate Limiting

- Implemented with `slowapi` on key Dashboard endpoints to protect the API

### Authentication Flow

1. Frontend calls Supabase `signInWithOAuth('google')`
2. Google redirects to Supabase `/auth/v1/callback`
3. Supabase redirects back to frontend with hash params
4. Frontend `AuthContext` initializes Supabase with:
   - `detectSessionInUrl: true`
   - `persistSession: true`
   - `autoRefreshToken: true`
5. `onAuthStateChange` handles `INITIAL_SESSION`/`SIGNED_IN`, updates `user`, cleans URL hash
6. `ProtectedRoute` gates app routes by `user`/`loading`

## Scalability

- **Async Processing**: FastAPI async/await for concurrent requests
- **Background Tasks**: Long-running operations run in background
- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Frontend API caching via `useApiCache` reduces redundant requests
- **Load Balancing**: Ready for horizontal scaling

## Monitoring

- **Logging**: Structured logging throughout
- **Health Checks**: `/health` endpoint
- **Audit Logs**: All actions logged for governance
- **Alerts**: Automated anomaly detection

## Frontend UX & Accessibility

- Minimal map popups with improved mobile touch handling
- Accessible focus styles and skip links
- Connection status and onboarding tour components

## Key Features

### Crisis Detection System
- **Sentiment Velocity Analysis**: Tracks rapid sentiment deterioration
- **Hashtag Intelligence**: Monitors trending hashtags and social media signals
- **Policy Monitoring**: Real-time monitoring of any policy, bill, or public issue
- **Protest Organizing Detection**: Identifies organizing language and mobilization signals
- **Escalation Prediction**: ML-based probability scoring for crisis escalation
- **Government Alerts**: Automated stakeholder notifications for critical issues

### Data Processing Pipeline
1. **Ingestion**: Multi-source data collection (Twitter, Facebook, RSS, portals)
2. **Preprocessing**: PII removal, language detection, text normalization
3. **Analysis**: Sentiment analysis, sector classification, NER, topic extraction
4. **Crisis Detection**: Automatic signal detection and alert generation
5. **Storage**: Structured storage with proper indexing and RLS policies

### Real-time Features
- **WebSocket Streaming**: Real-time updates for dashboard and alerts
- **Auto-refresh**: Automatic data refresh with caching
- **Connection Management**: Optimized reconnection with exponential backoff

## Future Enhancements

- Advanced ML models for classification
- Mobile app
- Public API for third-party integrations
- Enhanced email notifications
- Database-driven stakeholder configuration

