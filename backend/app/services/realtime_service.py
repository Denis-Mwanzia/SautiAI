"""
Real-time Service
Service for WebSocket streaming and real-time updates
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import WebSocket
from datetime import datetime, timedelta

from app.db.supabase import get_supabase
from app.services.rules_service import RulesService
from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)

# Cache for realtime updates to reduce query frequency
_REALTIME_CACHE: Optional[Dict[str, Any]] = None
_REALTIME_CACHE_TTL_SECONDS = 5  # 5 seconds cache for realtime updates


class RealtimeService:
    """Service for real-time data streaming"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.connections: List[WebSocket] = []
        self.rules = RulesService()
        self.alerts = AlertService()
    
    async def subscribe(self, websocket: WebSocket):
        """Subscribe WebSocket connection"""
        self.connections.append(websocket)
        logger.info(f"WebSocket subscribed. Total connections: {len(self.connections)}")
    
    async def get_updates(self) -> Optional[Dict[str, Any]]:
        """Get recent updates for streaming and evaluate simple alert rules."""
        # Check cache first (short TTL for realtime)
        global _REALTIME_CACHE
        now = datetime.utcnow()
        if _REALTIME_CACHE:
            cached_time = _REALTIME_CACHE.get("_cached_at")
            if cached_time:
                if isinstance(cached_time, datetime):
                    if (now - cached_time).total_seconds() < _REALTIME_CACHE_TTL_SECONDS:
                        # Return cached but update timestamp
                        result = {k: v for k, v in _REALTIME_CACHE.items() if k != "_cached_at"}
                        result["timestamp"] = now.isoformat()
                        return result
                elif isinstance(cached_time, str):
                    cached_dt = datetime.fromisoformat(cached_time.replace('Z', '+00:00'))
                    if (now - cached_dt).total_seconds() < _REALTIME_CACHE_TTL_SECONDS:
                        result = {k: v for k, v in _REALTIME_CACHE.items() if k != "_cached_at"}
                        result["timestamp"] = now.isoformat()
                        return result
        
        # Recent feedback (reduced limit for performance)
        fb_res = self.supabase.table("citizen_feedback").select(
            "id, source, created_at, location"
        ).order("created_at", desc=True).limit(30).execute()  # Reduced from 50 to 30
        feedback = fb_res.data or []

        since = (datetime.utcnow() - timedelta(hours=24)).isoformat()
        recent_fb = [r for r in feedback if r.get("created_at", "") >= since]

        # Count by county
        counts_by_county: Dict[str, int] = {}
        for row in recent_fb:
            loc = (row.get("location") or "").strip().lower()
            if not loc:
                continue
            counts_by_county[loc] = counts_by_county.get(loc, 0) + 1

        # Count by sector (from recent classifications, reduced limit)
        sc_res = self.supabase.table("sector_classification").select(
            "primary_sector, classified_at"
        ).order("classified_at", desc=True).limit(100).execute()  # Reduced from 200 to 100
        classifications = sc_res.data or []
        counts_by_sector: Dict[str, int] = {}
        for row in classifications:
            if row.get("classified") or row.get("classified_at"):
                ts = row.get("classified_at") or ""
                if ts >= since:
                    sec = (row.get("primary_sector") or "").lower()
                    if sec:
                        counts_by_s = counts_by_sector.get(sec, 0)
                        counts_by_sector[sec] = counts_by_s + 1

        # Evaluate rules
        triggered = self.rules.evaluate(counts_by_sector, counts_by_county)
        persisted = []
        for a in triggered:
            try:
                saved = await self.alerts.create_alert(a)
                if saved:
                    persisted.append(saved)
            except Exception:
                pass

        result = None
        if feedback or triggered:
            result = {
                "type": "update",
                "data": {
                    "new_feedback": len(feedback),
                    "latest": feedback[0] if feedback else None,
                    "rule_alerts": persisted or triggered,
                    "counters": {
                        "by_sector": counts_by_sector,
                        "by_county": counts_by_county,
                    }
                },
                "timestamp": now.isoformat(),
            }
            # Cache the result
            _REALTIME_CACHE = {**result, "_cached_at": now}
        
        return result
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.connections.remove(conn)

