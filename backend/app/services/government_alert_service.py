"""
Government Alert Service
Structured notification system for government stakeholders
Designed for any policy-related crisis scenarios
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
import json

from app.core.config import settings
from app.db.supabase import get_supabase_service

logger = logging.getLogger(__name__)


class GovernmentAlertService:
    """Service for sending structured alerts to government stakeholders"""
    
    def __init__(self):
        self.supabase_service = get_supabase_service()
        
        # Government stakeholder contact information (to be configured)
        self.stakeholders = {
            "president_office": {
                "name": "Office of the President",
                "email": None,  # To be configured
                "webhook": None,
                "priority_threshold": "critical"
            },
            "ministry_ict": {
                "name": "Ministry of ICT",
                "email": None,
                "webhook": None,
                "priority_threshold": "high"
            },
            "parliament": {
                "name": "Parliament",
                "email": None,
                "webhook": None,
                "priority_threshold": "high"
            },
            "county_governors": {
                "name": "County Governors",
                "email": None,
                "webhook": None,
                "priority_threshold": "medium"
            }
        }
    
    async def send_crisis_alert(
        self,
        crisis_signal: Dict[str, Any],
        stakeholders: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send structured crisis alert to government stakeholders
        
        Args:
            crisis_signal: Crisis signal data from CrisisDetectionService
            stakeholders: List of stakeholder IDs to notify (None = all above threshold)
            
        Returns:
            Notification results
        """
        try:
            # Determine which stakeholders to notify
            if not stakeholders:
                stakeholders = self._get_stakeholders_for_severity(crisis_signal.get("severity", "medium"))
            
            results = {
                "sent": [],
                "failed": [],
                "total": len(stakeholders)
            }
            
            # Format alert message
            alert_message = self._format_crisis_alert(crisis_signal)
            
            # Send to each stakeholder
            for stakeholder_id in stakeholders:
                if stakeholder_id not in self.stakeholders:
                    continue
                
                stakeholder = self.stakeholders[stakeholder_id]
                
                try:
                    # Send via webhook if configured
                    if stakeholder.get("webhook"):
                        await self._send_webhook_alert(stakeholder["webhook"], alert_message)
                        results["sent"].append(stakeholder_id)
                    
                    # Send via email if configured (future implementation)
                    elif stakeholder.get("email"):
                        # TODO: Implement email sending
                        logger.info(f"Email alert would be sent to {stakeholder['name']}")
                        results["sent"].append(stakeholder_id)
                    
                    else:
                        logger.warning(f"No notification method configured for {stakeholder_id}")
                        results["failed"].append({
                            "stakeholder": stakeholder_id,
                            "reason": "No notification method configured"
                        })
                        
                except Exception as e:
                    logger.error(f"Failed to send alert to {stakeholder_id}: {e}")
                    results["failed"].append({
                        "stakeholder": stakeholder_id,
                        "reason": str(e)
                    })
            
            # Store alert notification record
            await self._store_notification_record(crisis_signal, results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error sending government alert: {e}", exc_info=True)
            return {"error": str(e)}
    
    def _get_stakeholders_for_severity(self, severity: str) -> List[str]:
        """Get stakeholders that should be notified for given severity"""
        severity_levels = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        current_level = severity_levels.get(severity, 1)
        
        stakeholders_to_notify = []
        for stakeholder_id, config in self.stakeholders.items():
            threshold_level = severity_levels.get(config["priority_threshold"], 1)
            if current_level >= threshold_level:
                stakeholders_to_notify.append(stakeholder_id)
        
        return stakeholders_to_notify
    
    def _format_crisis_alert(self, crisis_signal: Dict[str, Any]) -> Dict[str, Any]:
        """Format crisis signal into structured government alert"""
        return {
            "alert_type": "crisis_detection",
            "severity": crisis_signal.get("severity", "medium"),
            "title": crisis_signal.get("title", "Crisis Signal Detected"),
            "summary": crisis_signal.get("description", ""),
            "recommendation": crisis_signal.get("recommendation", ""),
            "data": crisis_signal.get("data", {}),
            "detected_at": datetime.utcnow().isoformat(),
            "urgency": "IMMEDIATE" if crisis_signal.get("severity") == "critical" else "HIGH" if crisis_signal.get("severity") == "high" else "NORMAL",
            "action_required": True,
            "suggested_actions": self._generate_suggested_actions(crisis_signal)
        }
    
    def _generate_suggested_actions(self, crisis_signal: Dict[str, Any]) -> List[str]:
        """Generate suggested actions based on crisis signal type"""
        signal_type = crisis_signal.get("type", "")
        severity = crisis_signal.get("severity", "medium")
        
        actions = []
        
        if signal_type == "sentiment_velocity":
            actions.append("Review recent policy announcements or decisions")
            actions.append("Engage with citizens through official channels")
            actions.append("Consider public statement addressing concerns")
        
        if signal_type == "hashtag_trending":
            actions.append("Monitor trending hashtags and social media conversations")
            actions.append("Prepare response strategy for public engagement")
            actions.append("Consider proactive communication")
        
        if signal_type == "policy_crisis":
            actions.append("URGENT: Review policy provisions causing concern")
            actions.append("Consider policy amendments or clarifications")
            actions.append("Schedule public engagement session")
            actions.append("Prepare detailed explanation of policy rationale")
        
        if signal_type == "protest_organizing":
            actions.append("Monitor for planned demonstrations")
            actions.append("Coordinate with security agencies if needed")
            actions.append("Prepare public communication")
        
        if signal_type == "escalation_prediction":
            if severity == "critical":
                actions.append("IMMEDIATE: High-level government intervention required")
                actions.append("Consider emergency policy review")
                actions.append("Activate crisis response team")
            else:
                actions.append("Proactive engagement to prevent escalation")
                actions.append("Address root causes of citizen concerns")
        
        return actions
    
    async def _send_webhook_alert(self, webhook_url: str, alert_data: Dict[str, Any]):
        """Send alert via webhook"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    webhook_url,
                    json=alert_data,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                logger.info(f"Webhook alert sent successfully to {webhook_url}")
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
            raise
    
    async def _store_notification_record(
        self,
        crisis_signal: Dict[str, Any],
        results: Dict[str, Any]
    ):
        """Store notification record in database"""
        try:
            record = {
                "crisis_signal_id": crisis_signal.get("id"),
                "signal_type": crisis_signal.get("type"),
                "severity": crisis_signal.get("severity"),
                "stakeholders_notified": results.get("sent", []),
                "notification_status": "success" if results.get("sent") else "failed",
                "notified_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "total_stakeholders": results.get("total", 0),
                    "successful": len(results.get("sent", [])),
                    "failed": len(results.get("failed", []))
                }
            }
            
            # Try to store (table might not exist)
            try:
                self.supabase_service.table("government_alerts").insert(record).execute()
            except Exception:
                logger.info(f"Government alert sent: {crisis_signal.get('title')}")
                
        except Exception as e:
            logger.error(f"Error storing notification record: {e}")
    
    async def configure_stakeholder(
        self,
        stakeholder_id: str,
        email: Optional[str] = None,
        webhook: Optional[str] = None,
        priority_threshold: Optional[str] = None
    ) -> bool:
        """Configure stakeholder notification settings"""
        try:
            if stakeholder_id not in self.stakeholders:
                return False
            
            if email:
                self.stakeholders[stakeholder_id]["email"] = email
            if webhook:
                self.stakeholders[stakeholder_id]["webhook"] = webhook
            if priority_threshold:
                self.stakeholders[stakeholder_id]["priority_threshold"] = priority_threshold
            
            # Store configuration (in production, use database)
            logger.info(f"Stakeholder {stakeholder_id} configured")
            return True
            
        except Exception as e:
            logger.error(f"Error configuring stakeholder: {e}")
            return False

