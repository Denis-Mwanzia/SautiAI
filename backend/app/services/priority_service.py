"""
Priority Service
Service for calculating priority scores for emerging threats and high-risk signals
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import math

from app.db.supabase import get_supabase

logger = logging.getLogger(__name__)


class PriorityService:
    """Service for calculating priority scores"""
    
    def __init__(self):
        self.supabase = get_supabase()
    
    async def calculate_priority_score(
        self,
        feedback_id: str,
        text: str,
        sentiment: Optional[str] = None,
        sector: Optional[str] = None,
        location: Optional[str] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate priority score for feedback item
        
        Args:
            feedback_id: ID of the feedback
            text: Feedback text
            sentiment: Detected sentiment
            sector: Detected sector
            location: Location if available
            source: Source of feedback
            
        Returns:
            Priority score with breakdown
        """
        try:
            score_components = {}
            total_score = 0.0
            
            # 1. Sentiment weight (0-30 points)
            sentiment_score = self._calculate_sentiment_weight(sentiment)
            score_components["sentiment"] = sentiment_score
            total_score += sentiment_score
            
            # 2. Urgency keywords weight (0-25 points)
            urgency_score = self._calculate_urgency_weight(text)
            score_components["urgency_keywords"] = urgency_score
            total_score += urgency_score
            
            # 3. Volume/trending weight (0-20 points)
            volume_score = await self._calculate_volume_weight(text, location, sector)
            score_components["volume_trend"] = volume_score
            total_score += volume_score
            
            # 4. Sector criticality weight (0-15 points)
            sector_score = self._calculate_sector_criticality(sector)
            score_components["sector_criticality"] = sector_score
            total_score += sector_score
            
            # 5. Time decay weight (0-10 points)
            time_score = await self._calculate_time_decay(feedback_id)
            score_components["time_decay"] = time_score
            total_score += time_score
            
            # Normalize to 0-100 scale
            normalized_score = min(100, max(0, total_score))
            
            # Determine priority level
            priority_level = self._determine_priority_level(normalized_score)
            
            result = {
                "feedback_id": feedback_id,
                "priority_score": round(normalized_score, 2),
                "priority_level": priority_level,
                "score_breakdown": score_components,
                "calculated_at": datetime.utcnow().isoformat()
            }
            
            # Store priority score
            try:
                self.supabase.table("priority_scores").insert({
                    "feedback_id": feedback_id,
                    "priority_score": normalized_score,
                    "priority_level": priority_level,
                    "score_breakdown": score_components
                }).execute()
            except Exception as e:
                logger.warning(f"Could not store priority score: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating priority score: {e}", exc_info=True)
            return {
                "feedback_id": feedback_id,
                "priority_score": 50.0,
                "priority_level": "medium",
                "error": str(e)
            }
    
    def _calculate_sentiment_weight(self, sentiment: Optional[str]) -> float:
        """Calculate sentiment-based weight"""
        if not sentiment:
            return 10.0  # Neutral default
        
        weights = {
            "negative": 25.0,
            "positive": 5.0,
            "neutral": 10.0
        }
        
        return weights.get(sentiment, 10.0)
    
    def _calculate_urgency_weight(self, text: str) -> float:
        """Calculate urgency based on keywords"""
        text_lower = text.lower()
        
        critical_keywords = [
            "emergency", "urgent", "immediate", "critical", "life-threatening",
            "dangerous", "collapse", "accident", "death", "fatal"
        ]
        
        high_keywords = [
            "broken", "damaged", "unsafe", "hazardous", "problem",
            "issue", "concern", "complaint"
        ]
        
        # Check for critical keywords
        for keyword in critical_keywords:
            if keyword in text_lower:
                return 25.0
        
        # Check for high keywords
        for keyword in high_keywords:
            if keyword in text_lower:
                return 15.0
        
        return 5.0  # Low urgency
    
    async def _calculate_volume_weight(
        self,
        text: str,
        location: Optional[str],
        sector: Optional[str]
    ) -> float:
        """Calculate weight based on volume of similar feedback"""
        try:
            # Check for similar feedback in last 24 hours
            start_time = datetime.utcnow() - timedelta(hours=24)
            
            query = self.supabase.table("citizen_feedback").select(
                "id", count="exact"
            ).gte("created_at", start_time.isoformat())
            
            if location:
                query = query.eq("location", location)
            
            if sector:
                # Join with sector classification
                # Simplified - in production, use proper join
                pass
            
            result = query.execute()
            count = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
            
            # Score based on volume
            if count >= 10:
                return 20.0  # High volume
            elif count >= 5:
                return 15.0  # Medium volume
            elif count >= 2:
                return 10.0  # Low volume
            else:
                return 5.0  # Single report
                
        except Exception as e:
            logger.error(f"Error calculating volume weight: {e}")
            return 5.0
    
    def _calculate_sector_criticality(self, sector: Optional[str]) -> float:
        """Calculate weight based on sector criticality"""
        if not sector:
            return 5.0
        
        critical_sectors = {
            "health": 15.0,
            "security": 15.0,
            "infrastructure": 12.0,
            "governance": 10.0,
            "education": 8.0,
            "transport": 8.0,
            "economy": 7.0,
            "environment": 6.0,
            "other": 5.0
        }
        
        return critical_sectors.get(sector, 5.0)
    
    async def _calculate_time_decay(self, feedback_id: str) -> float:
        """Calculate time-based decay (recent = higher score)"""
        try:
            result = self.supabase.table("citizen_feedback").select(
                "created_at"
            ).eq("id", feedback_id).execute()
            
            if not result.data:
                return 5.0
            
            created_at = datetime.fromisoformat(
                result.data[0]["created_at"].replace("Z", "+00:00")
            )
            now = datetime.utcnow().replace(tzinfo=created_at.tzinfo)
            
            hours_ago = (now - created_at).total_seconds() / 3600
            
            # Decay function: higher score for more recent
            if hours_ago < 1:
                return 10.0  # Very recent
            elif hours_ago < 6:
                return 8.0   # Recent
            elif hours_ago < 24:
                return 6.0   # Today
            elif hours_ago < 72:
                return 4.0   # This week
            else:
                return 2.0   # Older
                
        except Exception as e:
            logger.error(f"Error calculating time decay: {e}")
            return 5.0
    
    def _determine_priority_level(self, score: float) -> str:
        """Determine priority level from score"""
        if score >= 80:
            return "critical"
        elif score >= 60:
            return "high"
        elif score >= 40:
            return "medium"
        else:
            return "low"

