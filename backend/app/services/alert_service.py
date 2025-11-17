"""
Alert Service
Service for generating red flag alerts and monitoring high-risk signals
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re

from app.db.supabase import get_supabase, get_supabase_service
from app.models.schemas import UrgencyLevel
from app.core.config import settings
from app.services.config_service import ConfigService
# Lazy import to avoid circular dependency
# from app.services.crisis_detection_service import CrisisDetectionService
import httpx

logger = logging.getLogger(__name__)


class AlertService:
    """Service for generating and managing alerts"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.supabase_service = get_supabase_service()
        self.cfg = ConfigService()
        # Lazy load crisis_service to avoid circular import
        self._crisis_service = None
        
        # High-risk keywords that trigger red flags
        self.red_flag_keywords = {
            "critical": [
                "collapse", "collapsing", "emergency", "urgent", "dangerous",
                "life-threatening", "death", "died", "fatal", "accident",
                "disaster", "crisis", "outbreak", "epidemic", "violence",
                "attack", "fire", "flood", "landslide"
            ],
            "high": [
                "broken", "damaged", "unsafe", "hazardous", "contaminated",
                "polluted", "corruption", "fraud", "theft", "robbery",
                "missing", "lost", "stolen", "abandoned", "neglected"
            ],
            "medium": [
                "problem", "issue", "concern", "complaint", "poor",
                "inadequate", "insufficient", "delayed", "late", "slow"
            ]
        }
    
    async def check_for_red_flags(
        self,
        feedback_id: str,
        text: str,
        source: str,
        location: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if feedback contains red flag indicators
        
        Args:
            feedback_id: ID of the feedback
            text: Feedback text
            source: Source of feedback
            location: Optional location
            
        Returns:
            Alert dict if red flag detected, None otherwise
        """
        try:
            text_lower = text.lower()
            detected_severity = None
            matched_keywords = []
            
            # Check for critical keywords
            for keyword in self.red_flag_keywords["critical"]:
                if keyword in text_lower:
                    detected_severity = "critical"
                    matched_keywords.append(keyword)
                    break
            
            # Check for high keywords if no critical found
            if not detected_severity:
                for keyword in self.red_flag_keywords["high"]:
                    if keyword in text_lower:
                        detected_severity = "high"
                        matched_keywords.append(keyword)
                        break
            
            # Check for medium keywords if no high/critical found
            if not detected_severity:
                for keyword in self.red_flag_keywords["medium"]:
                    if keyword in text_lower:
                        detected_severity = "medium"
                        matched_keywords.append(keyword)
                        break
            
            if not detected_severity:
                return None
            
            # Check if similar alert already exists (avoid duplicates)
            existing = await self._check_existing_alert(text, location)
            if existing:
                return None
            
            # Generate alert
            alert = {
                "alert_type": "red_flag",
                "severity": detected_severity,
                "title": self._generate_alert_title(text, detected_severity),
                "description": self._generate_alert_description(text, matched_keywords, location),
                "sector": await self._detect_sector_from_text(text),
                "affected_counties": [location] if location else [],
                "metadata": {
                    "feedback_id": feedback_id,
                    "source": source,
                    "matched_keywords": matched_keywords,
                    "text_snippet": text[:200]
                },
                "created_at": datetime.utcnow().isoformat(),
                "acknowledged": False
            }
            
            # Store alert
            result = self.supabase_service.table("alerts").insert(alert).execute()
            
            if result.data:
                logger.info(f"Red flag alert generated: {alert['title']}")
                try:
                    await self._notify_channels(result.data[0])
                except Exception as ne:
                    logger.warning(f"Alert notification failed: {ne}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking for red flags: {e}", exc_info=True)
            return None
    
    async def check_trending_complaints(
        self,
        hours: int = 24,
        threshold: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Check for trending complaints that might need alerts
        
        Args:
            hours: Time window in hours
            threshold: Minimum number of similar complaints to trigger alert
            
        Returns:
            List of alerts for trending issues
        """
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get recent feedback
            result = self.supabase.table("citizen_feedback").select(
                "id, text, source, location, created_at"
            ).gte("created_at", start_time.isoformat()).execute()
            
            if not result.data or len(result.data) < threshold:
                return []
            
            # Group by keywords/sectors
            from collections import defaultdict
            keyword_groups = defaultdict(list)
            
            for item in result.data:
                text_lower = item["text"].lower()
                # Extract potential keywords
                for keyword in self.red_flag_keywords["critical"] + self.red_flag_keywords["high"]:
                    if keyword in text_lower:
                        keyword_groups[keyword].append(item)
                        break
            
            alerts = []
            for keyword, items in keyword_groups.items():
                if len(items) >= threshold:
                    # Generate trending alert
                    alert = {
                        "alert_type": "trending_issue",
                        "severity": "high" if len(items) >= threshold * 2 else "medium",
                        "title": f"Trending Issue: {keyword.title()} ({len(items)} reports)",
                        "description": f"Multiple reports ({len(items)}) about '{keyword}' in the last {hours} hours.",
                        "sector": await self._detect_sector_from_text(items[0]["text"]),
                        "affected_counties": list(set([i["location"] for i in items if i.get("location")])),
                        "metadata": {
                            "keyword": keyword,
                            "count": len(items),
                            "time_window_hours": hours,
                            "feedback_ids": [i["id"] for i in items]
                        },
                        "created_at": datetime.utcnow().isoformat(),
                        "acknowledged": False
                    }
                    
                    result = self.supabase_service.table("alerts").insert(alert).execute()
                    if result.data:
                        alerts.append(result.data[0])
                        try:
                            await self._notify_channels(result.data[0])
                        except Exception as ne:
                            logger.warning(f"Alert notification failed: {ne}")
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking trending complaints: {e}", exc_info=True)
            return []
    
    async def _check_existing_alert(
        self,
        text: str,
        location: Optional[str]
    ) -> bool:
        """Check if similar alert already exists"""
        try:
            # Check for alerts in last 24 hours with similar text
            start_time = datetime.utcnow() - timedelta(hours=24)
            
            result = self.supabase.table("alerts").select("id").gte(
                "created_at", start_time.isoformat()
            ).eq("alert_type", "red_flag").execute()
            
            # Simple check - in production, use text similarity
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Error checking existing alerts: {e}")
            return False
    
    def _generate_alert_title(self, text: str, severity: str) -> str:
        """Generate alert title from text"""
        # Extract first meaningful sentence
        sentences = re.split(r'[.!?]+', text)
        first_sentence = sentences[0].strip() if sentences else text[:100]
        
        if len(first_sentence) > 80:
            first_sentence = first_sentence[:77] + "..."
        
        severity_prefix = "🚨 CRITICAL: " if severity == "critical" else "⚠️ "
        return f"{severity_prefix}{first_sentence}"
    
    def _generate_alert_description(
        self,
        text: str,
        keywords: List[str],
        location: Optional[str]
    ) -> str:
        """Generate alert description"""
        desc = f"Red flag detected in citizen feedback. "
        desc += f"Keywords: {', '.join(keywords)}. "
        if location:
            desc += f"Location: {location}. "
        desc += f"Details: {text[:300]}"
        return desc
    
    async def _detect_sector_from_text(self, text: str) -> Optional[str]:
        """Detect sector from text"""
        text_lower = text.lower()
        
        sector_keywords = {
            "health": ["hospital", "clinic", "doctor", "medicine", "health"],
            "education": ["school", "teacher", "student", "education"],
            "transport": ["road", "traffic", "bus", "transport", "vehicle"],
            "governance": ["government", "minister", "policy", "corruption"],
            "infrastructure": ["water", "electricity", "internet", "housing"],
            "security": ["police", "crime", "safety", "violence"]
        }
        
        for sector, keywords in sector_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return sector
        
        return "other"

    async def _notify_channels(self, alert: Dict[str, Any]):
        """Send alert notifications to Slack/Webhook if configured"""
        tasks = []
        override = self.cfg.get_alerts_config() or {}
        slack_url = (override.get("SLACK_WEBHOOK_URL") or '').strip() or (settings.SLACK_WEBHOOK_URL or '').strip()
        hook_url = (override.get("ALERT_WEBHOOK_URL") or '').strip() or (settings.ALERT_WEBHOOK_URL or '').strip()
        if slack_url:
            payload = {
                "text": f"[{alert.get('severity','').upper()}] {alert.get('title','Alert')}\n{alert.get('description','')}"
            }
            tasks.append(self._post_json(slack_url, payload))
        if hook_url:
            tasks.append(self._post_json(hook_url, alert))
        if tasks:
            async with httpx.AsyncClient(timeout=5) as client:
                await httpx.AsyncClient.gather(*[t(client) for t in tasks])

    def _post_json(self, url: str, payload: Dict[str, Any]):
        async def sender(client: httpx.AsyncClient):
            try:
                await client.post(url, json=payload)
            except Exception as e:
                logger.debug(f"Webhook post failed: {e}")
        return sender

    async def create_alert(self, alert: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Persist an alert and notify channels (used by rule evaluations)."""
        try:
            payload = {
                **alert,
                "created_at": alert.get("created_at") or datetime.utcnow().isoformat(),
                "acknowledged": bool(alert.get("acknowledged", False)),
            }
            res = self.supabase_service.table("alerts").insert(payload).execute()
            if res.data:
                try:
                    await self._notify_channels(res.data[0])
                except Exception as ne:
                    logger.warning(f"Alert notify failed: {ne}")
                return res.data[0]
        except Exception as e:
            logger.error(f"create_alert failed: {e}")
        return None

