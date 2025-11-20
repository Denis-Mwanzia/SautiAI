# Sauti AI – Voice of the People

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg)](https://reactjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A real-time, agentic, generative-AI civic intelligence platform for Kenya that autonomously collects public feedback, analyzes it using LLMs, and produces actionable policy intelligence.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

Sauti AI is a comprehensive civic intelligence platform designed to:

- **Collect** citizen feedback from multiple sources (Twitter, Facebook, RSS, government portals)
- **Analyze** feedback using advanced AI (sentiment analysis, sector classification, policy recommendations)
- **Detect** crisis signals and emerging issues in real-time
- **Alert** stakeholders when critical issues require attention
- **Report** actionable insights through automated Citizen Pulse Reports
- **Track** government transparency and response rates

The platform uses **Jaseci OSP** for autonomous agent-based processing and **Vertex AI** for advanced language model capabilities.

## ✨ Features

### Core Capabilities

- **Real-time Data Ingestion**: Legal data collection from Twitter, Facebook, news RSS, and government portals
- **Agentic AI System**: Autonomous Jaseci OSP agents for data processing and analysis
- **Multilingual Support**: English, Kiswahili, and Sheng via automatic language detection
- **LLM Analysis**: Vertex AI + Genkit + ADK for sentiment, NER, topic classification, and policy recommendations
- **Interactive Dashboard**: Real-time visualizations of citizen sentiment, trends, and AI-generated reports
- **Crisis Detection**: Early warning system for policy-related crises with sentiment velocity analysis and escalation prediction
- **Government Alerts**: Automated stakeholder notifications for critical issues
- **Policy Monitoring**: Real-time monitoring of any policy, bill, or public issue
- **Transparency Tracking**: Government response tracking and agency performance metrics
- **AI Chat Interface**: Context-aware chat assistant for civic intelligence queries
- **Modern UI/UX**: Clean, professional interface with responsive design and intuitive navigation
- **Production-Ready**: Supabase backend, FastAPI REST API, React frontend

### Dashboard Pages

- **Dashboard**: Real-time statistics, sentiment trends, top issues, county heatmaps
- **Crisis Detection**: Risk assessment, crisis signals, sentiment velocity, hashtag intelligence
- **Alerts**: Custom alert rules, real-time notifications, Slack/Webhook integration
- **Feedback Explorer**: Advanced search, filtering by sector/county, saved views
- **Chat**: AI-powered assistant for querying civic intelligence data
- **Reports**: Automated Citizen Pulse Reports (daily/weekly, bilingual)
- **Transparency**: Government response tracking, agency performance metrics
- **Settings**: API key management, alert configuration, agent schedules

## 🏗️ Architecture

```
SautiAI/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/         # REST endpoints (v1)
│   │   ├── services/    # Business logic
│   │   ├── models/      # Pydantic models
│   │   ├── db/          # Database utilities
│   │   └── core/        # Configuration
│   ├── jaseci/          # Jaseci OSP agents
│   └── requirements.txt
├── frontend/             # React + Vite application
│   ├── src/
│   │   ├── components/  # React components (Layout, Footer, etc.)
│   │   ├── pages/       # Page components (Dashboard, Alerts, etc.)
│   │   ├── hooks/       # Custom hooks (useRealtime, useApiCache, etc.)
│   │   ├── services/    # API clients
│   │   ├── contexts/    # React contexts (Auth, Toast)
│   │   └── utils/       # Utilities
│   └── package.json
├── supabase/             # Database migrations
│   └── migrations/
└── docker-compose.yml    # Local development setup
```

For detailed architecture documentation, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## 📦 Prerequisites

### Required

- **Python 3.11+** - Backend runtime
- **Node.js 18+** - Frontend runtime
- **npm** or **yarn** - Package manager
- **Supabase Account** - Database and authentication
- **Git** - Version control

### Optional (for full functionality)

- **Google Cloud Platform Account** - For Vertex AI (LLM features)
- **Twitter API Bearer Token** - For Twitter data ingestion
- **Facebook Graph API Access Token** - For Facebook data ingestion
- **Jaseci** - For agentic features (install separately)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/sauti-ai.git
cd sauti-ai
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run database migrations
supabase db push

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend
npm install

# Copy and configure environment variables
cp .env.example .env.local
# Edit .env.local with your Supabase credentials

# Start development server
npm run dev
```

Frontend will be available at `http://localhost:5173` (or the port Vite assigns)

### 4. Verify Installation

- Backend health check: `curl http://localhost:8000/health`
- Frontend: Open `http://localhost:5173` in your browser
- API docs: `http://localhost:8000/docs`

## 📖 Installation

### Detailed Backend Setup

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Database Setup**
   ```bash
   # Ensure Supabase CLI is installed
   supabase init
   supabase db push
   ```

5. **Run Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Detailed Frontend Setup

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your credentials
   ```

3. **Start Development Server**
   ```bash
   npm run dev
   ```

### Jaseci Setup (Optional)

```bash
# Install Jaseci
pip install jaseci jaseci-serv

# Start Jaseci server
jsctl serv start
```

## ⚙️ Configuration

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Supabase Configuration
SUPABASE_URL=https://<your-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:password@localhost:5432/postgres

# Google Cloud / Vertex AI (Optional)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Social Media APIs (Optional)
TWITTER_BEARER_TOKEN=your-twitter-token
FACEBOOK_ACCESS_TOKEN=your-facebook-token

# Alert Webhooks (Optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
ALERT_WEBHOOK_URL=https://example.com/webhook

# Application Settings
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
ENABLE_AI=true  # Set to false to disable AI features

# Monitoring (Optional)
SENTRY_DSN=your-sentry-dsn
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
VITE_SUPABASE_URL=https://<your-ref>.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
VITE_API_URL=http://localhost:8000
VITE_ENABLE_GOOGLE_AUTH=true  # Optional
```

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials
3. Add authorized redirect URI: `https://<your-ref>.supabase.co/auth/v1/callback`
4. Configure in Supabase Dashboard → Authentication → Providers → Google

## 🔐 Authentication

The platform supports two authentication methods:

### Email/Password

- Users can sign up with email and password
- Email verification is required
- Password strength validation enforced

### Google OAuth

- One-click sign-in with Google account
- Configured via Supabase Auth
- Requires Google Cloud OAuth credentials

**Frontend Authentication Flow:**

1. User clicks "Sign in with Google" or enters email/password
2. Supabase Auth handles authentication
3. Session is stored and auto-refreshed
4. Protected routes require valid session

## 📡 Data Sources

The platform ingests data from multiple sources:

- **Twitter API**: Track hashtags (#Kenya, #MatatuCommute, #HudumaNamba, etc.)
- **Facebook Graph API**: Public pages (Nairobi City County, Ministry of Health, etc.)
- **RSS Feeds**: Nation Africa, The Standard, BBC Africa
- **Government Open Data**: Kenya Open Data Portal
- **Government Portals**: Official complaint and feedback portals
- **County Portals**: County-specific service request systems

## 🚀 Development

### Running Both Servers

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### Code Structure

- **Backend**: FastAPI with async/await patterns, Pydantic models, and Supabase integration
- **Frontend**: React with hooks, context API, and modern CSS (Tailwind)
- **Real-time**: WebSocket connections for live updates
- **Caching**: API response caching and request deduplication for performance

### Development Guidelines

- Follow existing code patterns and style
- Write tests for new features
- Update documentation for API changes
- Maintain UI/UX consistency with the design system
- Use TypeScript types where applicable (frontend)
- Use Pydantic models for validation (backend)

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
pytest tests/ -v  # Verbose output
pytest tests/test_api.py -v  # Specific test file
```

### Frontend Tests

```bash
cd frontend
npm test
npm run test:coverage  # With coverage report
```

### API Testing

Use the interactive Swagger UI at `http://localhost:8000/docs` or test endpoints directly:

```bash
# Health check
curl http://localhost:8000/health

# Get dashboard insights
curl http://localhost:8000/api/v1/dashboard/insights?days=7

# Generate sample data
curl -X POST http://localhost:8000/api/v1/sample/sample \
  -H "Content-Type: application/json" \
  -d '{"count": 10, "sectors": ["health", "education"]}'
```

## 🚢 Deployment

### Backend Deployment

**Recommended Platforms:**
- **Railway**: Easy deployment with automatic scaling
- **Render**: Simple setup with PostgreSQL
- **Google Cloud Run**: Serverless with auto-scaling (works with Firebase)
- **AWS Elastic Beanstalk**: Managed deployment

**Environment Variables:**
Ensure all required environment variables are set in your deployment platform.

**Database:**
Use Supabase production database or managed PostgreSQL instance.

**Deployment Guides:**
- See `DEPLOY_FIREBASE_FULL_STACK.md` for complete Firebase/Google Cloud deployment (recommended)
- See `backend/DEPLOY_BACKEND.md` for other platform-specific instructions

### Frontend Deployment

**Recommended Platforms:**
- **Firebase Hosting**: Fast CDN, works with Cloud Run backend (recommended)
- **Vercel**: Optimized for React/Vite
- **GitHub Pages**: Free static hosting
- **AWS S3 + CloudFront**: Scalable CDN hosting

**Firebase + Cloud Run (Recommended):**
- Deploy backend to Cloud Run (serverless, auto-scaling)
- Deploy frontend to Firebase Hosting (fast CDN)
- Both in Google Cloud ecosystem, easy integration
- See `DEPLOY_FIREBASE_FULL_STACK.md` for complete guide

**Build Command:**
```bash
npm run build
```

**Output Directory:**
`frontend/dist`

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up -d

# Or build individually
docker build -t sauti-ai-backend ./backend
docker build -t sauti-ai-frontend ./frontend
```

## 📚 API Documentation

Complete API documentation is available in **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)**.

**Interactive Documentation:**
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

**Quick API Examples:**

```bash
# Get Dashboard Insights
curl http://localhost:8000/api/v1/dashboard/insights?days=7

# Ingest RSS Feed
curl -X POST http://localhost:8000/api/v1/ingest/rss \
  -H "Content-Type: application/json" \
  -d '["https://www.bbc.com/news/world/africa/rss.xml"]'

# Analyze Sentiment
curl -X POST http://localhost:8000/api/v1/ai/analyze-sentiment \
  -H "Content-Type: application/json" \
  -d '{"feedback_id": "test", "text": "Great service!", "language": "en"}'

# Detect Crisis Signals
curl -X POST http://localhost:8000/api/v1/crisis/detect \
  -H "Content-Type: application/json" \
  -d '{"time_window_hours": 24, "min_volume": 10}'
```

## 🎨 UI/UX Features

- **Modern Design System**: Clean, minimal interface with consistent styling
- **Responsive Layout**: Fixed sidebar navigation with adaptive content area
- **Real-time Updates**: WebSocket integration for live data updates
- **Interactive Dashboards**: Dynamic charts and visualizations using Recharts
- **Accessibility**: ARIA labels, keyboard navigation, and semantic HTML
- **Performance Optimized**: API caching, request deduplication, and lazy loading

## 🐛 Troubleshooting

### Backend Issues

**Problem**: Supabase connection errors
- **Solution**: Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in `.env`

**Problem**: Database migration errors
- **Solution**: Ensure Supabase CLI is installed and run `supabase db push`

**Problem**: Vertex AI errors
- **Solution**: Verify `GOOGLE_APPLICATION_CREDENTIALS` path and service account permissions

**Problem**: Import errors
- **Solution**: Ensure virtual environment is activated and dependencies are installed

### Frontend Issues

**Problem**: Cannot connect to backend
- **Solution**: Verify `VITE_API_URL` matches backend URL and CORS is configured

**Problem**: Authentication not working
- **Solution**: Check Supabase credentials and ensure OAuth redirect URI is configured

**Problem**: WebSocket connection errors
- **Solution**: WebSocket errors in development (React StrictMode) are expected and handled gracefully. Connection will automatically reconnect.

**Problem**: Build errors
- **Solution**: Clear `node_modules` and reinstall: `rm -rf node_modules package-lock.json && npm install`

### Common Issues

**Problem**: Port already in use
- **Solution**: Change port in command or kill existing process

**Problem**: Environment variables not loading
- **Solution**: Restart server after changing `.env` files

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Follow code style**: Match existing patterns and conventions
4. **Write tests**: Add tests for new features
5. **Update documentation**: Update relevant docs for changes
6. **Commit changes**: Use clear, descriptive commit messages
7. **Push to branch**: `git push origin feature/amazing-feature`
8. **Open Pull Request**: Provide clear description of changes

### Code Standards

- **Backend**: Follow PEP 8, use type hints, write docstrings
- **Frontend**: Use ESLint, follow React best practices, maintain component structure
- **UI/UX**: Maintain consistency with the design system
- **Tests**: Aim for >80% code coverage

## 🔗 Related Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System architecture and design patterns
- **[API_DOCUMENTATION.md](./API_DOCUMENTATION.md)** - Complete API reference with examples

## 🗺️ Roadmap

### Planned Features

- [ ] Mobile app (React Native)
- [ ] Public API for third-party integrations
- [ ] Enhanced email notifications
- [ ] Database-driven stakeholder configuration
- [ ] Advanced ML models for classification
- [ ] Multi-language support expansion
- [ ] Real-time collaboration features
- [ ] Advanced analytics and reporting

### Known Limitations

- AI features require Vertex AI credentials (can be disabled)
- Twitter/Facebook ingestion requires API tokens (optional)
- Jaseci agents require separate installation (optional)
- Some features may have rate limits from external APIs

---

**Built with ❤️ for Kenya's civic intelligence**
