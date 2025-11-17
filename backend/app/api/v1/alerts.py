"""
Alerts Endpoints
Endpoints for managing alerts and red flags
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Optional
import logging

from app.models.schemas import APIResponse
from app.services.alert_service import AlertService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_alert_service() -> AlertService:
    """Dependency injection for AlertService"""
    return AlertService()


@router.post("/check-trending", response_model=APIResponse)
async def check_trending_complaints(
    hours: int = Query(24, description="Time window in hours"),
    threshold: int = Query(5, description="Minimum number of similar complaints"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: AlertService = Depends(get_alert_service)
):
    """
    Check for trending complaints and generate alerts
    
    Args:
        hours: Time window in hours
        threshold: Minimum number of similar complaints
    """
    try:
        alerts = await service.check_trending_complaints(hours, threshold)
        return APIResponse(
            success=True,
            message=f"Found {len(alerts)} trending issues",
            data=alerts
        )
    except Exception as e:
        logger.error(f"Trending complaints check error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/red-flags", response_model=APIResponse)
async def get_red_flags(
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: int = Query(20, description="Maximum number of alerts to return"),
    service: AlertService = Depends(get_alert_service)
):
    """Get red flag alerts"""
    try:
        query = service.supabase.table("alerts").select("*").eq(
            "alert_type", "red_flag"
        ).order("created_at", desc=True).limit(limit)
        
        if severity:
            query = query.eq("severity", severity)
        
        result = query.execute()
        
        return APIResponse(
            success=True,
            message="Red flag alerts retrieved",
            data=result.data or []
        )
    except Exception as e:
        logger.error(f"Red flags retrieval error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test", response_model=APIResponse)
async def send_test_alert(
    title: str = "Test Alert",
    severity: str = "medium",
    service: AlertService = Depends(get_alert_service)
):
    """
    Send a test alert to verify Slack/Webhook configuration.
    """
    try:
        alert = {
            "alert_type": "test",
            "severity": severity,
            "title": title,
            "description": "This is a test alert from SautiAI.",
            "affected_counties": [],
            "metadata": {"source": "test"},
            "created_at": None,
            "acknowledged": False,
        }
        saved = await service.create_alert(alert)
        return APIResponse(success=True, message="Test alert sent", data=saved)
    except Exception as e:
        logger.error(f"Test alert error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=APIResponse)
async def list_alerts(
    limit: int = Query(50, description="Maximum number of alerts"),
    service: AlertService = Depends(get_alert_service)
):
    """List recent alerts (any type)"""
    try:
        result = service.supabase.table("alerts").select("*").order("created_at", desc=True).limit(limit).execute()
        return APIResponse(success=True, message="Alerts retrieved", data=result.data or [])
    except Exception as e:
        logger.error(f"Alerts list error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{alert_id}/ack", response_model=APIResponse)
async def acknowledge_alert(
    alert_id: str,
    service: AlertService = Depends(get_alert_service)
):
    """Acknowledge an alert"""
    try:
        result = service.supabase.table("alerts").update({"acknowledged": True}).eq("id", alert_id).execute()
        return APIResponse(success=True, message="Alert acknowledged", data=result.data or [])
    except Exception as e:
        logger.error(f"Alert ack error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

