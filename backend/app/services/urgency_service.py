"""
Urgency Service
Service for determining urgency levels of feedback
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.constants import URGENCY_LEVELS
from app.db.supabase import get_supabase_service

logger = logging.getLogger(__name__)


class UrgencyService:
    """Service for urgency classification"""
    
    def __init__(self):
        self.supabase_service = get_supabase_service()
    
    async def classify_urgency(
        self,
        feedback_id: str,
        text: str,
        sentiment: Optional[str] = None,
        sector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Classify urgency level (low/medium/high/critical)
        
        Args:
            feedback_id: ID of the feedback
            text: Text content
            sentiment: Sentiment (positive/negative/neutral)
            sector: Sector category
        """
        logger.info(f"Classifying urgency for feedback {feedback_id}")
        
        # Urgency keywords
        critical_keywords = [
            "emergency", "urgent", "critical", "immediate", "life-threatening",
            "death", "died", "kill", "violence", "attack", "crisis", "disaster"
        ]
        
        high_keywords = [
            "serious", "severe", "important", "urgent", "need", "must", "should",
            "problem", "issue", "complaint", "concern", "worry", "danger"
        ]
        
        medium_keywords = [
            "issue", "problem", "concern", "request", "help", "assistance"
        ]
        
        text_lower = text.lower()
        
        # Calculate urgency score
        critical_count = sum(1 for keyword in critical_keywords if keyword in text_lower)
        high_count = sum(1 for keyword in high_keywords if keyword in text_lower)
        medium_count = sum(1 for keyword in medium_keywords if keyword in text_lower)
        
        # Determine urgency level
        if critical_count > 0 or (sentiment == "negative" and high_count >= 3):
            urgency = "critical"
        elif high_count >= 2 or (sentiment == "negative" and high_count >= 1):
            urgency = "high"
        elif medium_count >= 1 or sentiment == "negative":
            urgency = "medium"
        else:
            urgency = "low"
        
        # Store urgency classification
        urgency_record = {
            "feedback_id": feedback_id,
            "urgency_level": urgency,
            "sentiment": sentiment,
            "sector": sector,
            "classified_at": datetime.utcnow().isoformat(),
            "model_used": "rule-based"
        }
        
        try:
            # Update feedback record with urgency
            self.supabase_service.table("citizen_feedback").update({
                "urgency": urgency
            }).eq("id", feedback_id).execute()
            
            logger.info(f"Urgency classified: {urgency} for feedback {feedback_id}")
            return urgency_record
        except Exception as e:
            logger.error(f"Error storing urgency classification: {e}")
            return urgency_record

