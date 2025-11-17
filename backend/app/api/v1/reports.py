"""
Reports Endpoints
Endpoints for Citizen Pulse Reports
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Optional
import logging

from app.models.schemas import APIResponse
from app.services.report_service import ReportService
from app.core.config import settings
from fastapi.responses import HTMLResponse

router = APIRouter()
logger = logging.getLogger(__name__)


def get_report_service() -> ReportService:
    """Dependency injection for ReportService"""
    return ReportService()


@router.post("/pulse", response_model=APIResponse)
async def generate_pulse_report(
    period: str = Query("weekly", description="Report period: daily, weekly, monthly"),
    language: str = Query("bilingual", description="Report language: always bilingual"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: ReportService = Depends(get_report_service)
):
    """
    Generate Citizen Pulse Report
    
    Args:
        period: Report period ("daily", "weekly", "monthly")
        language: Always "bilingual" (enforced)
    """
    # Check if AI features are enabled
    if not settings.ENABLE_AI:
        raise HTTPException(
            status_code=503,
            detail="Report generation requires AI features to be enabled. Please set ENABLE_AI=true in the backend configuration."
        )
    
    try:
        # Force bilingual for all reports
        language = "bilingual"
        
        # Generate report synchronously for testing, or use background tasks in production
        report = await service.generate_pulse_report(period=period, language=language)
        return APIResponse(
            success=True,
            message=f"{period} pulse report generated successfully",
            data=report
        )
    except Exception as e:
        logger.error(f"Pulse report generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pulse")
async def get_pulse_reports(
    limit: int = 10,
    period: Optional[str] = None,
    service: ReportService = Depends(get_report_service)
):
    """Get recent Citizen Pulse Reports"""
    try:
        reports = await service.get_recent_reports(limit, period)
        return {
            "success": True,
            "message": "Pulse reports retrieved",
            "data": reports
        }
    except Exception as e:
        logger.error(f"Reports retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pulse/{report_id}/html")
async def export_pulse_report_html(
    report_id: str,
    service: ReportService = Depends(get_report_service)
):
    """
    Export a single pulse report as static HTML (shareable).
    """
    try:
        html = await service.render_report_html(report_id)
        return HTMLResponse(content=html, status_code=200)
    except Exception as e:
        logger.error(f"Export HTML error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
