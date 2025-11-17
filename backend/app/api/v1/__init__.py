"""
API v1 Router
Main API router that includes all endpoint routers
"""

from fastapi import APIRouter
from app.api.v1 import ingest, agents, dashboard, auth, realtime, sample_data, alerts, transparency, search, crisis
from app.core.config import settings
from app.api.v1 import rules, config

api_router = APIRouter()

# Include all routers
api_router.include_router(ingest.router, prefix="/ingest", tags=["Data Ingestion"])
api_router.include_router(agents.router, prefix="/agents", tags=["Jaseci Agents"])
# Reports router always available (GET doesn't need AI, POST checks ENABLE_AI)
from app.api.v1 import reports
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
if settings.ENABLE_AI:
    from app.api.v1 import ai, chat
    api_router.include_router(ai.router, prefix="/ai", tags=["AI Analysis"])
    api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(realtime.router, prefix="/realtime", tags=["Real-time"])
api_router.include_router(sample_data.router, prefix="/sample", tags=["Sample Data"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(transparency.router, prefix="/transparency", tags=["Transparency"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(crisis.router, prefix="/crisis", tags=["Crisis Detection"])
api_router.include_router(rules.router, tags=["Rules"])
api_router.include_router(config.router, tags=["Config"])

