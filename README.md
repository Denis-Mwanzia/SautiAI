# Sauti AI – Voice of the People

A real-time, agentic, generative-AI civic intelligence platform for Kenya that autonomously collects public feedback, analyzes it using LLMs, and produces actionable policy intelligence.

## 🎯 Core Features

- **Real-time Data Ingestion**: Legal data collection from Twitter, Facebook, news RSS, and government portals
- **Agentic AI System**: Autonomous Jaseci OSP agents for data processing and analysis
- **Multilingual Support**: English, Kiswahili, and Sheng via language detection
- **LLM Analysis**: Vertex AI + Genkit + ADK for sentiment, NER, topic classification, and policy recommendations
- **Interactive Dashboard**: Real-time visualizations of citizen sentiment, trends, and AI-generated reports
- **Crisis Detection**: Early warning system for policy-related crises with sentiment velocity analysis and escalation prediction
- **Government Alerts**: Automated stakeholder notifications for critical issues
- **Policy Monitoring**: Real-time monitoring of any policy, bill, or public issue
- **Transparency Tracking**: Government response tracking and agency performance metrics
- **AI Chat Interface**: Context-aware chat assistant for civic intelligence queries
- **Production-Ready**: Supabase backend, FastAPI REST API, React frontend

## 🏗️ Architecture

```
SautiAI/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # REST endpoints
│   │   ├── services/    # Business logic
│   │   ├── models/      # Pydantic models
│   │   ├── db/          # Database utilities
│   │   └── core/        # Configuration
│   ├── jaseci/          # Jaseci OSP agents
│   └── requirements.txt
├── frontend/             # React + Vite application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   ├── hooks/       # Custom hooks
│   │   ├── services/    # API clients
│   │   └── utils/       # Utilities
│   └── package.json
├── supabase/             # Database migrations
│   └── migrations/
└── docker-compose.yml    # Local development setup
```

## 📖 Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture and design
- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Complete API reference

Quick start below covers local dev. See files referenced for env variables.

### Prerequisites

- Python 3.11+
- Node.js 18+
- Supabase account and project
- Google Cloud Platform account (for Vertex AI)
- Twitter API Bearer Token (optional)
- Facebook Graph API Access Token (optional)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run migrations
supabase db push

# Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your Supabase credentials

# Start development server
npm run dev
```

### Jaseci Setup

```bash
# Install Jaseci
pip install jaseci jaseci-serv

# Start Jaseci server
jsctl serv start
```

## 🔐 Authentication

- Email/password via Supabase Auth
- Google OAuth via Supabase (configured with `detectSessionInUrl`, session persistence, and auto-refresh)

Frontend environment:

```
VITE_SUPABASE_URL=https://<your-ref>.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

Google OAuth: Add the Supabase callback URL to Google Cloud Console Authorized redirect URIs:

```
https://<your-ref>.supabase.co/auth/v1/callback
```

## 📡 Data Sources

- **Twitter API**: Track hashtags (#Kenya, #MatatuCommute, #HudumaNamba, etc.)
- **Facebook Graph API**: Public pages (Nairobi City County, Ministry of Health, etc.)
- **RSS Feeds**: Nation Africa, The Standard, BBC Africa
- **Government Open Data**: Kenya Open Data Portal
- **Government Portals**: Official complaint and feedback portals
- **County Portals**: County-specific service request systems

## ⚙️ Environment Variables

Backend `.env` (examples):

```
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=
DATABASE_URL=
```

Frontend `.env.local` (examples):

```
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
```

## 📚 API Documentation

Complete API documentation is available in **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)**.

Interactive documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Quick API Examples

**Get Dashboard Insights:**
```bash
curl http://localhost:8000/api/v1/dashboard/insights?days=7
```

**Ingest RSS Feed:**
```bash
curl -X POST http://localhost:8000/api/v1/ingest/rss \
  -H "Content-Type: application/json" \
  -d '["https://www.bbc.com/news/world/africa/rss.xml"]'
```

**Analyze Sentiment:**
```bash
curl -X POST http://localhost:8000/api/v1/ai/analyze-sentiment \
  -H "Content-Type: application/json" \
  -d '{"feedback_id": "test", "text": "Great service!", "language": "en"}'
```

**Detect Crisis Signals:**
```bash
curl -X POST http://localhost:8000/api/v1/crisis/detect \
  -H "Content-Type: application/json" \
  -d '{"time_window_hours": 24, "min_volume": 10}'
```

**Monitor Policy:**
```bash
curl -X POST http://localhost:8000/api/v1/crisis/monitor-policy \
  -H "Content-Type: application/json" \
  -d '{"policy_name": "Finance Bill 2024"}'
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 📄 License

MIT License - See LICENSE file for details.

