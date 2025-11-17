"""
Dashboard Endpoints
Endpoints for dashboard data and visualizations
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
from datetime import datetime, timedelta
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.models.schemas import APIResponse, DashboardInsights
from app.services.dashboard_service import DashboardService

router = APIRouter()
logger = logging.getLogger(__name__)

# Rate limiter instance (will use app.state.limiter from main.py)
limiter = None

def get_limiter():
    """Get limiter from app state"""
    global limiter
    if limiter is None:
        from app.main import app
        limiter = app.state.limiter
    return limiter


def get_dashboard_service() -> DashboardService:
    """Dependency injection for DashboardService"""
    return DashboardService()


@router.get("/insights", response_model=APIResponse)
async def get_insights(
    request: Request,
    days: int = 7,
    county: Optional[str] = None,
    sector: Optional[str] = None,
    offset: int = 0,
    limit: int = 50,
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get comprehensive dashboard insights
    
    Returns aggregated data for visualizations:
    - Sentiment distribution
    - Sector breakdown
    - Top issues
    - Trending complaints
    - County heatmap
    """
    try:
        logger.info(f"Fetching insights for days={days}, county={county}, sector={sector}")
        
        insights = await service.get_insights(
            days=days,
            county=county,
            sector=sector
        )
        
        # Attach basic pagination meta (for lists inside insights)
        if isinstance(insights, dict):
            insights.setdefault("_meta", {})
            insights["_meta"].update({"offset": offset, "limit": limit})

        return APIResponse(
            success=True,
            message="Insights retrieved",
            data=insights
        )
    except Exception as e:
        logger.error(f"Insights retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment-trends", response_model=APIResponse)
async def get_sentiment_trends(
    request: Request,
    days: int = 30,
    offset: int = 0,
    limit: int = 365,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Get sentiment trends over time"""
    try:
        trends = await service.get_sentiment_trends(days)
        if isinstance(trends, dict):
            trends.setdefault("_meta", {})
            trends["_meta"].update({"offset": offset, "limit": limit})
        return APIResponse(
            success=True,
            message="Sentiment trends retrieved",
            data=trends
        )
    except Exception as e:
        logger.error(f"Trends retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-issues", response_model=APIResponse)
async def get_top_issues(
    limit: int = 10,
    days: int = 7,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Get top issues by volume and urgency"""
    try:
        issues = await service.get_top_issues(limit, days)
        return APIResponse(
            success=True,
            message="Top issues retrieved",
            data=issues
        )
    except Exception as e:
        logger.error(f"Top issues retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/county-heatmap", response_model=APIResponse)
async def get_county_heatmap(
    request: Request,
    days: int = 7,
    service: DashboardService = Depends(get_dashboard_service)
):
    """Get county-level sentiment and issue heatmap"""
    try:
        heatmap = await service.get_county_heatmap(days)
        return APIResponse(
            success=True,
            message="County heatmap retrieved",
            data=heatmap
        )
    except Exception as e:
        logger.error(f"Heatmap retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

