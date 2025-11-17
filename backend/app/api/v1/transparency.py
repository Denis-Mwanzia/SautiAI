"""
Transparency Endpoints
Endpoints for tracking government responsiveness and accountability
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from app.models.schemas import APIResponse
from app.services.transparency_service import TransparencyService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_transparency_service() -> TransparencyService:
    """Dependency injection for TransparencyService"""
    return TransparencyService()


class GovernmentResponseRequest(BaseModel):
    """Request model for recording government responses"""
    issue_id: str = Field(..., description="ID of the alert or feedback")
    issue_type: str = Field(..., description="Type: 'alert' or 'feedback'")
    responding_agency: str = Field(..., description="Name of the responding agency")
    response_text: str = Field(..., description="Response content")
    status: str = Field("acknowledged", description="Response status")


@router.get("/metrics", response_model=APIResponse)
async def get_transparency_metrics(
    days: int = Query(30, description="Number of days to analyze"),
    agency: Optional[str] = Query(None, description="Filter by agency"),
    sector: Optional[str] = Query(None, description="Filter by sector"),
    service: TransparencyService = Depends(get_transparency_service)
):
    """
    Get transparency and responsiveness metrics
    
    Returns:
    - Response rates
    - Resolution rates
    - Average response times
    - Agency performance
    - Status breakdown
    """
    try:
        metrics = await service.get_transparency_metrics(days, agency, sector)
        return APIResponse(
            success=True,
            message="Transparency metrics retrieved",
            data=metrics
        )
    except Exception as e:
        logger.error(f"Error getting transparency metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/response", response_model=APIResponse)
async def record_government_response(
    request: GovernmentResponseRequest,
    service: TransparencyService = Depends(get_transparency_service)
):
    """
    Record a government response to an issue
    
    Tracks:
    - Response time
    - Agency performance
    - Resolution status
    """
    try:
        response = await service.record_government_response(
            request.issue_id,
            request.issue_type,
            request.responding_agency,
            request.response_text,
            request.status
        )
        return APIResponse(
            success=True,
            message="Government response recorded",
            data=response
        )
    except Exception as e:
        logger.error(f"Error recording government response: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agencies", response_model=APIResponse)
async def get_agency_performance(
    agency: Optional[str] = Query(None, description="Filter by agency name"),
    days: int = Query(30, description="Number of days"),
    service: TransparencyService = Depends(get_transparency_service)
):
    """Get agency performance metrics"""
    try:
        performance = await service.get_agency_performance(agency, days)
        return APIResponse(
            success=True,
            message="Agency performance retrieved",
            data=performance
        )
    except Exception as e:
        logger.error(f"Error getting agency performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline/{issue_id}", response_model=APIResponse)
async def get_response_timeline(
    issue_id: str,
    issue_type: str = Query(..., description="Type: 'alert' or 'feedback'"),
    service: TransparencyService = Depends(get_transparency_service)
):
    """Get timeline of responses for an issue"""
    try:
        timeline = await service.get_response_timeline(issue_id, issue_type)
        return APIResponse(
            success=True,
            message="Response timeline retrieved",
            data=timeline
        )
    except Exception as e:
        logger.error(f"Error getting response timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

