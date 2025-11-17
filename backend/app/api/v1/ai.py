"""
AI Analysis Endpoints
Endpoints for LLM analysis using Vertex AI, Genkit, and ADK
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
from datetime import datetime
import logging

from app.models.schemas import (
    APIResponse, 
    AISummary, 
    PolicyRecommendation,
    SentimentAnalysisRequest,
    SectorClassificationRequest
)
from app.services.ai_service import AIService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_ai_service() -> AIService:
    """Dependency injection for AIService"""
    return AIService()


@router.post("/summarize", response_model=APIResponse)
async def summarize_feedback(
    feedback_ids: List[str],
    language: Optional[str] = "en",
    background_tasks: BackgroundTasks = None,
    service: AIService = Depends(get_ai_service)
):
    """
    Generate AI summary for a batch of feedback
    
    Uses Vertex AI to generate multilingual summaries
    """
    try:
        logger.info(f"Summarizing {len(feedback_ids)} feedback items")
        
        if background_tasks:
            background_tasks.add_task(
                service.generate_summary,
                feedback_ids=feedback_ids,
                language=language
            )
            return APIResponse(
                success=True,
                message="Summary generation started",
                data={"feedback_count": len(feedback_ids)}
            )
        else:
            summary = await service.generate_summary(feedback_ids, language)
            return APIResponse(
                success=True,
                message="Summary generated",
                data=summary
            )
    except Exception as e:
        logger.error(f"Summary generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/policy-report", response_model=APIResponse)
async def generate_policy_report(
    sector: Optional[str] = None,
    county: Optional[str] = None,
    background_tasks: BackgroundTasks = None,
    service: AIService = Depends(get_ai_service)
):
    """
    Generate policy recommendation report
    
    Uses Vertex AI + ADK for agentic policy analysis
    """
    try:
        logger.info(f"Generating policy report for sector={sector}, county={county}")
        
        if background_tasks:
            background_tasks.add_task(
                service.generate_policy_report,
                sector=sector,
                county=county
            )
            return APIResponse(
                success=True,
                message="Policy report generation started"
            )
        else:
            report = await service.generate_policy_report(sector, county)
            return APIResponse(
                success=True,
                message="Policy report generated",
                data=report
            )
    except Exception as e:
        logger.error(f"Policy report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summaries", response_model=APIResponse)
async def get_summaries(
    limit: int = 10,
    offset: int = 0,
    service: AIService = Depends(get_ai_service)
):
    """Get recent AI-generated summaries"""
    try:
        summaries = await service.get_summaries(limit, offset)
        return APIResponse(
            success=True,
            message="Summaries retrieved",
            data=summaries
        )
    except Exception as e:
        logger.error(f"Summaries retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations", response_model=APIResponse)
async def get_recommendations(
    sector: Optional[str] = None,
    limit: int = 10,
    service: AIService = Depends(get_ai_service)
):
    """Get policy recommendations"""
    try:
        recommendations = await service.get_recommendations(sector, limit)
        return APIResponse(
            success=True,
            message="Recommendations retrieved",
            data=recommendations
        )
    except Exception as e:
        logger.error(f"Recommendations retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-sentiment", response_model=APIResponse)
async def analyze_sentiment(
    request: SentimentAnalysisRequest,
    service: AIService = Depends(get_ai_service)
):
    """
    Analyze sentiment of feedback text
    
    Uses Vertex AI to analyze sentiment (positive/negative/neutral)
    """
    try:
        logger.info(f"Analyzing sentiment for feedback {request.feedback_id}")
        result = await service.analyze_sentiment(
            request.feedback_id, 
            request.text, 
            request.language
        )
        return APIResponse(
            success=True,
            message="Sentiment analyzed",
            data=result
        )
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/classify-sector", response_model=APIResponse)
async def classify_sector(
    request: SectorClassificationRequest,
    service: AIService = Depends(get_ai_service)
):
    """
    Classify feedback into a sector
    
    Uses Vertex AI to classify feedback into sectors (health, education, transport, etc.)
    """
    try:
        logger.info(f"Classifying sector for feedback {request.feedback_id}")
        result = await service.classify_sector(
            request.feedback_id, 
            request.text, 
            request.language
        )
        return APIResponse(
            success=True,
            message="Sector classified",
            data=result
        )
    except Exception as e:
        logger.error(f"Sector classification error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

