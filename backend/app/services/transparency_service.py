"""
Transparency Service
Service for tracking government responsiveness and accountability metrics
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.db.supabase import get_supabase, get_supabase_service

logger = logging.getLogger(__name__)

# Cache for transparency metrics
_TRANSPARENCY_CACHE: Dict[str, Dict[str, Any]] = {}
_TRANSPARENCY_TTL_SECONDS = 120  # 2 minutes cache
_AGENCY_CACHE: Dict[str, List[Dict[str, Any]]] = {}
_AGENCY_TTL_SECONDS = 180  # 3 minutes cache


class TransparencyService:
    """Service for transparency and responsiveness tracking"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.supabase_service = get_supabase_service()
    
    async def get_transparency_metrics(
        self,
        days: int = 30,
        agency: Optional[str] = None,
        sector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive transparency and responsiveness metrics
        
        Args:
            days: Number of days to analyze
            agency: Optional agency filter
            sector: Optional sector filter
            
        Returns:
            Transparency metrics including response rates, resolution rates, etc.
        """
        # Check cache
        cache_key = f"{days}:{agency or '*'}:{sector or '*'}"
        now = datetime.utcnow()
        cached = _TRANSPARENCY_CACHE.get(cache_key)
        if cached:
            cached_time = cached.get("_cached_at")
            if cached_time:
                if isinstance(cached_time, datetime):
                    if (now - cached_time).total_seconds() < _TRANSPARENCY_TTL_SECONDS:
                        return {k: v for k, v in cached.items() if k != "_cached_at"}
                elif isinstance(cached_time, str):
                    cached_dt = datetime.fromisoformat(cached_time.replace('Z', '+00:00'))
                    if (now - cached_dt).total_seconds() < _TRANSPARENCY_TTL_SECONDS:
                        return {k: v for k, v in cached.items() if k != "_cached_at"}
        
        try:
            start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Parallelize independent queries
            def get_alerts():
                alerts_result = self.supabase.table("alerts").select(
                    "id, severity, created_at, acknowledged, resolution_status"
                ).gte("created_at", start_date).execute()
                if sector:
                    alerts_result = self.supabase.table("alerts").select(
                        "id, severity, created_at, acknowledged, resolution_status, sector"
                    ).gte("created_at", start_date).eq("sector", sector).execute()
                return alerts_result.data or []
            
            def get_responses():
                responses_query = self.supabase.table("government_responses").select("*").gte("created_at", start_date)
                if agency:
                    responses_query = responses_query.eq("responding_agency", agency)
                if sector:
                    responses_query = responses_query.eq("sector", sector)
                return responses_query.execute().data or []
            
            def get_agency_perf():
                agency_perf_query = self.supabase.table("agency_performance").select("*").gte("period_start", start_date).order("period_start", desc=True)
                if agency:
                    agency_perf_query = agency_perf_query.eq("agency_name", agency)
                return agency_perf_query.execute().data or []
            
            # Execute queries in parallel
            alerts_data, responses, agency_performance = await asyncio.gather(
                asyncio.to_thread(get_alerts),
                asyncio.to_thread(get_responses),
                asyncio.to_thread(get_agency_perf)
            )
            
            total_alerts = len(alerts_data)
            acknowledged_alerts = len([a for a in alerts_data if a.get("acknowledged", False)])
            resolved_alerts = len([a for a in alerts_data if a.get("resolution_status") == "resolved"])
            
            # Calculate response times
            response_times = []
            for response in responses:
                if response.get("response_time_hours"):
                    response_times.append(response.get("response_time_hours"))
            
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            # Calculate overall metrics
            response_rate = (acknowledged_alerts / total_alerts * 100) if total_alerts > 0 else 0
            resolution_rate = (resolved_alerts / total_alerts * 100) if total_alerts > 0 else 0
            
            # Get response status breakdown
            status_breakdown = {
                "pending": len([a for a in alerts_data if not a.get("acknowledged", False)]),
                "acknowledged": len([a for a in alerts_data if a.get("acknowledged", False) and a.get("resolution_status") != "resolved"]),
                "resolved": resolved_alerts,
                "closed": len([a for a in alerts_data if a.get("resolution_status") == "closed"])
            }
            
            data = {
                "period_days": days,
                "total_issues": total_alerts,
                "acknowledged_count": acknowledged_alerts,
                "resolved_count": resolved_alerts,
                "response_rate": round(response_rate, 1),
                "resolution_rate": round(resolution_rate, 1),
                "average_response_time_hours": round(avg_response_time, 1),
                "status_breakdown": status_breakdown,
                "agency_performance": agency_performance[:10],  # Top 10 agencies
                "total_responses": len(responses),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Cache the result
            _TRANSPARENCY_CACHE[cache_key] = {**data, "_cached_at": now}
            return data
            
        except Exception as e:
            logger.error(f"Error getting transparency metrics: {e}")
            raise
    
    async def record_government_response(
        self,
        issue_id: str,
        issue_type: str,
        responding_agency: str,
        response_text: str,
        status: str = "acknowledged"
    ) -> Dict[str, Any]:
        """
        Record a government response to an issue
        
        Args:
            issue_id: ID of the alert or feedback
            issue_type: 'alert' or 'feedback'
            responding_agency: Name of the responding agency
            response_text: Response content
            status: Response status
            
        Returns:
            Created response record
        """
        try:
            # Get the issue to calculate response time
            if issue_type == "alert":
                issue_result = self.supabase.table("alerts").select(
                    "id, created_at, sector, affected_counties"
                ).eq("id", issue_id).execute()
            else:
                issue_result = self.supabase.table("citizen_feedback").select(
                    "id, created_at, category, location"
                ).eq("id", issue_id).execute()
            
            if not issue_result.data:
                raise ValueError(f"Issue {issue_id} not found")
            
            issue = issue_result.data[0]
            issue_created = datetime.fromisoformat(issue["created_at"].replace("Z", "+00:00"))
            response_time = (datetime.utcnow() - issue_created.replace(tzinfo=None)).total_seconds() / 3600
            
            # Create response record
            response_data = {
                "alert_id": issue_id if issue_type == "alert" else None,
                "feedback_id": issue_id if issue_type == "feedback" else None,
                "issue_id": issue_id,
                "issue_type": issue_type,
                "responding_agency": responding_agency,
                "response_text": response_text,
                "response_date": datetime.utcnow().isoformat(),
                "response_time_hours": round(response_time, 1),
                "status": status,
                "sector": issue.get("sector") or issue.get("category"),
                "affected_counties": issue.get("affected_counties") or ([issue.get("location")] if issue.get("location") else [])
            }
            
            result = self.supabase_service.table("government_responses").insert(
                response_data
            ).execute()
            
            # Update alert/feedback status
            if issue_type == "alert":
                self.supabase_service.table("alerts").update({
                    "acknowledged": True,
                    "acknowledged_at": datetime.utcnow().isoformat(),
                    "resolution_status": status,
                    "response_id": result.data[0]["id"] if result.data else None
                }).eq("id", issue_id).execute()
            else:
                self.supabase_service.table("citizen_feedback").update({
                    "response_status": status,
                    "response_id": result.data[0]["id"] if result.data else None
                }).eq("id", issue_id).execute()
            
            # Update agency performance
            await self._update_agency_performance(responding_agency, issue.get("sector") or issue.get("category"))
            
            logger.info(f"Government response recorded for {issue_type} {issue_id} by {responding_agency}")
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Error recording government response: {e}")
            raise
    
    async def _update_agency_performance(self, agency_name: str, sector: Optional[str] = None):
        """Update agency performance metrics"""
        try:
            # Get current period (monthly)
            now = datetime.utcnow()
            period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
            period_end = (now.replace(day=28) + timedelta(days=4)).replace(day=1).isoformat()
            
            # Get agency responses for this period
            responses_result = self.supabase.table("government_responses").select(
                "*"
            ).eq("responding_agency", agency_name).gte(
                "created_at", period_start
            ).lte("created_at", period_end).execute()
            
            if sector:
                responses_result = self.supabase.table("government_responses").select(
                    "*"
                ).eq("responding_agency", agency_name).eq("sector", sector).gte(
                    "created_at", period_start
                ).lte("created_at", period_end).execute()
            
            responses = responses_result.data or []
            total_issues = len(responses)
            acknowledged = len([r for r in responses if r.get("status") != "pending"])
            resolved = len([r for r in responses if r.get("status") == "resolved"])
            
            response_times = [r.get("response_time_hours", 0) for r in responses if r.get("response_time_hours")]
            avg_response_time = sum(response_times) / len(response_times) if response_times else 0
            
            response_rate = (acknowledged / total_issues * 100) if total_issues > 0 else 0
            resolution_rate = (resolved / total_issues * 100) if total_issues > 0 else 0
            
            # Upsert agency performance
            perf_data = {
                "agency_name": agency_name,
                "sector": sector or "all",
                "total_issues": total_issues,
                "acknowledged_count": acknowledged,
                "resolved_count": resolved,
                "average_response_time_hours": round(avg_response_time, 1),
                "response_rate": round(response_rate, 1),
                "resolution_rate": round(resolution_rate, 1),
                "period_start": period_start,
                "period_end": period_end,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Check if record exists
            existing = self.supabase.table("agency_performance").select(
                "id"
            ).eq("agency_name", agency_name).eq(
                "sector", sector or "all"
            ).eq("period_start", period_start).execute()
            
            if existing.data:
                self.supabase_service.table("agency_performance").update(
                    perf_data
                ).eq("id", existing.data[0]["id"]).execute()
            else:
                self.supabase_service.table("agency_performance").insert(
                    perf_data
                ).execute()
            
        except Exception as e:
            logger.error(f"Error updating agency performance: {e}")
    
    async def get_agency_performance(
        self,
        agency: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get agency performance metrics"""
        # Check cache
        cache_key = f"agency-{days}:{agency or '*'}"
        now = datetime.utcnow()
        cached = _AGENCY_CACHE.get(cache_key)
        if cached:
            cached_time = cached.get("_cached_at")
            if cached_time:
                if isinstance(cached_time, datetime):
                    if (now - cached_time).total_seconds() < _AGENCY_TTL_SECONDS:
                        # Return the data list (stored as "_data" key)
                        return cached.get("_data", [])
                elif isinstance(cached_time, str):
                    cached_dt = datetime.fromisoformat(cached_time.replace('Z', '+00:00'))
                    if (now - cached_dt).total_seconds() < _AGENCY_TTL_SECONDS:
                        return cached.get("_data", [])
        
        try:
            start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            query = self.supabase.table("agency_performance").select(
                "*"
            ).gte("period_start", start_date).order("response_rate", desc=True)
            
            if agency:
                query = query.eq("agency_name", agency)
            
            result = query.execute()
            data = result.data or []
            
            # Cache the result properly
            _AGENCY_CACHE[cache_key] = {"_data": data, "_cached_at": now}
            return data
            
        except Exception as e:
            logger.error(f"Error getting agency performance: {e}")
            return []
    
    async def get_response_timeline(
        self,
        issue_id: str,
        issue_type: str
    ) -> List[Dict[str, Any]]:
        """Get timeline of responses for an issue"""
        try:
            query = self.supabase.table("government_responses").select(
                "*"
            )
            
            if issue_type == "alert":
                query = query.eq("alert_id", issue_id)
            else:
                query = query.eq("feedback_id", issue_id)
            
            result = query.order("response_date").execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting response timeline: {e}")
            return []

