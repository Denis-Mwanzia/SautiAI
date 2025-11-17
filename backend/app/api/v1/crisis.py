"""
Crisis Detection API
Endpoints for detecting and monitoring policy-related crises
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
import logging

from app.models.schemas import APIResponse
from app.services.crisis_detection_service import CrisisDetectionService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_crisis_service() -> CrisisDetectionService:
    """Dependency injection for CrisisDetectionService"""
    return CrisisDetectionService()


@router.post("/detect", response_model=APIResponse)
async def detect_crisis_signals(
    time_window_hours: int = Query(24, description="Time window in hours to analyze"),
    min_volume: int = Query(10, description="Minimum feedback volume to analyze"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: CrisisDetectionService = Depends(get_crisis_service)
):
    """
    Detect crisis signals from recent feedback
    
    This endpoint analyzes recent citizen feedback to detect:
    - Rapid sentiment deterioration
    - Trending hashtags
    - Policy-specific crises
    - Protest organizing signals
    - Escalation predictions
    
    Returns early warning signals that could indicate a crisis for any policy, bill, or public issue.
    """
    try:
        signals = await service.detect_crisis_signals(time_window_hours, min_volume)
        
        return APIResponse(
            success=True,
            message=f"Detected {len(signals)} crisis signals",
            data={
                "signals": signals,
                "time_window_hours": time_window_hours,
                "total_signals": len(signals),
                "critical_count": sum(1 for s in signals if s.get("severity") == "critical"),
                "high_count": sum(1 for s in signals if s.get("severity") == "high")
            }
        )
    except Exception as e:
        logger.error(f"Crisis detection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitor-policy", response_model=APIResponse)
async def monitor_policy(
    policy_name: str = Query(..., description="Name of policy to monitor (e.g., 'Finance Bill 2024', 'Healthcare Act', 'Education Policy')"),
    keywords: str = Query(..., description="Comma-separated keywords related to the policy"),
    time_window_hours: int = Query(168, description="Time window in hours (default: 7 days)"),
    service: CrisisDetectionService = Depends(get_crisis_service)
):
    """
    Monitor a specific policy for crisis signals
    
    Example:
    - policy_name: "Healthcare Act 2024"
    - keywords: "healthcare,health,act,medical" (comma-separated)
    
    Returns comprehensive analysis of policy sentiment and risk factors.
    """
    try:
        # Parse comma-separated keywords
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        result = await service.monitor_policy(policy_name, keyword_list, time_window_hours)
        
        return APIResponse(
            success=True,
            message=f"Policy monitoring completed for {policy_name}",
            data=result
        )
    except Exception as e:
        logger.error(f"Policy monitoring error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/signals", response_model=APIResponse)
async def get_crisis_signals(
    limit: int = Query(20, description="Maximum number of signals to return"),
    severity: Optional[str] = Query(None, description="Filter by severity (critical/high/medium)"),
    signal_type: Optional[str] = Query(None, description="Filter by signal type"),
    service: CrisisDetectionService = Depends(get_crisis_service)
):
    """
    Get recent crisis signals
    
    Returns list of detected crisis signals with filtering options.
    """
    try:
        # For now, return from alerts table filtered by crisis_signal type
        # In production, this would query a dedicated crisis_signals table
        from app.services.alert_service import AlertService
        alert_service = AlertService()
        
        # Get alerts of type crisis_signal
        result = alert_service.supabase.table("alerts").select(
            "*"
        ).eq("alert_type", "crisis_signal")
        
        if severity:
            result = result.eq("severity", severity)
        
        result = result.order("created_at", desc=True).limit(limit).execute()
        
        signals = result.data if result.data else []
        
        # Filter by signal type if provided
        if signal_type:
            signals = [s for s in signals if s.get("metadata", {}).get("signal_type") == signal_type]
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(signals)} crisis signals",
            data=signals
        )
    except Exception as e:
        logger.error(f"Error getting crisis signals: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard", response_model=APIResponse)
async def get_crisis_dashboard(
    days: int = Query(7, description="Number of days to analyze"),
    service: CrisisDetectionService = Depends(get_crisis_service)
):
    """
    Get crisis dashboard data
    
    Returns comprehensive crisis monitoring dashboard with:
    - Current crisis signals
    - Sentiment trends
    - Hashtag intelligence
    - Escalation predictions
    - Policy monitoring status
    
    Performance: Uses caching and optimized queries
    """
    try:
        from datetime import datetime, timedelta
        from app.db.supabase import get_supabase
        import asyncio
        
        # Performance: Check cache first
        cache_key = f"crisis_dashboard_{days}"
        now = datetime.utcnow()
        
        # Simple in-memory cache check (in production, use Redis)
        if hasattr(get_crisis_dashboard, '_cache'):
            cached = get_crisis_dashboard._cache.get(cache_key)
            if cached:
                cached_time = cached.get("_cached_at")
                if cached_time and (now - cached_time).total_seconds() < 300:  # 5 min cache
                    logger.debug(f"Returning cached crisis dashboard for {days} days")
                    return APIResponse(
                        success=True,
                        message="Crisis dashboard data retrieved (cached)",
                        data=cached.get("data")
                    )
        else:
            get_crisis_dashboard._cache = {}
        
        supabase = get_supabase()
        start_time = datetime.utcnow() - timedelta(days=days)
        
        # Performance: Get feedback and sentiment separately for reliability
        # Get recent feedback (limited to 1000 items)
        feedback_result = supabase.table("citizen_feedback").select(
            "id, text, source, location, created_at"
        ).gte("created_at", start_time.isoformat()).limit(1000).order("created_at", desc=True).execute()
        
        feedback_items = []
        if feedback_result.data:
            # Get sentiment scores for these feedback items
            feedback_ids = [item.get("id") for item in feedback_result.data]
            sentiment_result = supabase.table("sentiment_scores").select(
                "feedback_id, sentiment"
            ).in_("feedback_id", feedback_ids).order("analyzed_at", desc=True).execute()
            
            # Create sentiment map (use most recent sentiment per feedback)
            sentiment_map = {}
            for sent_item in (sentiment_result.data or []):
                fb_id = sent_item.get("feedback_id")
                if fb_id and fb_id not in sentiment_map:
                    sentiment_map[fb_id] = sent_item.get("sentiment", "neutral")
            
            # Combine feedback with sentiment
            for item in feedback_result.data:
                feedback_id = item.get("id")
                sentiment = sentiment_map.get(feedback_id, "neutral")
                feedback_items.append({
                    "id": feedback_id,
                    "text": item.get("text", ""),
                    "source": item.get("source"),
                    "location": item.get("location"),
                    "created_at": item.get("created_at"),
                    "sentiment": sentiment
                })
        
        # Performance: detect_crisis_signals already does all the analysis, so reuse it
        signals = await service.detect_crisis_signals(time_window_hours=days*24, min_volume=5)
        
        # Extract data from signals (already computed)
        sentiment_velocity = {}
        hashtag_intel = {}
        escalation_prediction = {}
        
        for signal in signals:
            if signal.get("type") == "sentiment_velocity":
                sentiment_velocity = signal.get("data", {})
            elif signal.get("type") == "hashtag_trending":
                hashtag_intel = signal.get("data", {})
            elif signal.get("type") == "escalation_prediction":
                escalation_prediction = signal.get("data", {})
        
        # If not in signals, compute separately (fallback)
        if not sentiment_velocity:
            sentiment_velocity = await service._analyze_sentiment_velocity(feedback_items, days*24)
        if not hashtag_intel:
            hashtag_intel = await service._analyze_hashtag_intelligence(feedback_items)
        if not escalation_prediction:
            escalation_prediction = await service._predict_escalation(
                feedback_items,
                sentiment_velocity,
                hashtag_intel
            )
        
        # Performance: Get alerts (non-blocking)
        alerts_result = supabase.table("alerts").select(
            "*"
        ).eq("alert_type", "crisis_signal").gte(
            "created_at", start_time.isoformat()
        ).order("created_at", desc=True).limit(10).execute()
        
        dashboard_data = {
            "crisis_signals": signals,
            "sentiment_velocity": sentiment_velocity,
            "hashtag_intelligence": hashtag_intel,
            "escalation_prediction": escalation_prediction,
            "recent_alerts": alerts_result.data if alerts_result.data else [],
            "total_feedback_analyzed": len(feedback_items),
            "time_period_days": days
        }
        
        # Cache the result
        get_crisis_dashboard._cache[cache_key] = {
            "data": dashboard_data,
            "_cached_at": now
        }
        
        return APIResponse(
            success=True,
            message="Crisis dashboard data retrieved",
            data=dashboard_data
        )
    except Exception as e:
        logger.error(f"Error getting crisis dashboard: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

