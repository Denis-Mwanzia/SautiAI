"""
Dashboard Service
Service for aggregating dashboard data and insights
"""

import logging
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from app.db.supabase import get_supabase

logger = logging.getLogger(__name__)

# Simple in‑process cache to avoid hammering Supabase on every dashboard load
_INSIGHTS_CACHE: Dict[str, Dict[str, Any]] = {}
_INSIGHTS_TTL_SECONDS = 60  # Increased from 15 to 60 seconds
_TRENDS_CACHE: Dict[str, Dict[str, Any]] = {}
_TRENDS_TTL_SECONDS = 120  # Increased from 30 to 120 seconds


class DashboardService:
    """Service for dashboard data aggregation"""
    
    def __init__(self):
        self.supabase = get_supabase()
    
    async def get_insights(
        self,
        days: int = 7,
        county: Optional[str] = None,
        sector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive dashboard insights
        
        Returns aggregated data for visualizations
        """
        key = f"{days}:{county or '*'}:{sector or '*'}"
        now = datetime.utcnow()

        # Serve from cache if fresh
        cached = _INSIGHTS_CACHE.get(key)
        if cached:
            cached_time = cached.get("_cached_at")
            if cached_time:
                if isinstance(cached_time, datetime):
                    if (now - cached_time).total_seconds() < _INSIGHTS_TTL_SECONDS:
                        return {k: v for k, v in cached.items() if k != "_cached_at"}
                elif isinstance(cached_time, str):
                    cached_dt = datetime.fromisoformat(cached_time.replace('Z', '+00:00'))
                    if (now - cached_dt).total_seconds() < _INSIGHTS_TTL_SECONDS:
                        return {k: v for k, v in cached.items() if k != "_cached_at"}

        logger.info(f"Fetching insights (cache miss) for days={days}, county={county}, sector={sector}")

        start_date = (now - timedelta(days=days)).isoformat()
        prev_start = (now - timedelta(days=days * 2)).isoformat()
        prev_end = (now - timedelta(days=days)).isoformat()
        
        # Get total feedback count (sync query, can be parallelized)
        def get_total_feedback():
            try:
                total_query = self.supabase.table("citizen_feedback").select(
                    "id", count="exact"
                ).gte("created_at", start_date)
                
                if county:
                    total_query = total_query.eq("location", county)
                
                total_result = total_query.execute()
                return total_result.count if hasattr(total_result, 'count') else 0
            except Exception as e:
                logger.error(f"Error getting total feedback: {e}")
                return 0
        
        def get_prev_total_feedback():
            try:
                prev_total = self.supabase.table("citizen_feedback").select("id", count="exact").gte("created_at", prev_start).lt("created_at", prev_end).execute()
                return prev_total.count if hasattr(prev_total, 'count') else 0
            except Exception as e:
                logger.error(f"Error getting previous total feedback: {e}")
                return 0
        
        def get_recent_alerts():
            try:
                alerts_result = self.supabase.table("alerts").select("*").order(
                    "created_at", desc=True
                ).limit(10).execute()
                return alerts_result.data if alerts_result else []
            except Exception as e:
                logger.error(f"Error getting recent alerts: {e}")
                return []
        
        # Parallelize independent async queries
        sentiment_dist, sector_dist, top_issues, trending, prev_sent = await asyncio.gather(
            self._get_sentiment_distribution(start_date, county, sector),
            self._get_sector_distribution(start_date, county),
            self._get_top_issues(days, county, sector),
            self._get_trending_complaints(days),
            self._get_sentiment_distribution(prev_start, county, sector),
            return_exceptions=True
        )
        
        # Handle exceptions from parallel queries
        if isinstance(sentiment_dist, Exception):
            logger.error(f"Sentiment distribution error: {sentiment_dist}")
            sentiment_dist = {"positive": 0, "negative": 0, "neutral": 0}
        if isinstance(sector_dist, Exception):
            logger.error(f"Sector distribution error: {sector_dist}")
            sector_dist = {}
        if isinstance(top_issues, Exception):
            logger.error(f"Top issues error: {top_issues}")
            top_issues = []
        if isinstance(trending, Exception):
            logger.error(f"Trending complaints error: {trending}")
            trending = []
        if isinstance(prev_sent, Exception):
            logger.error(f"Previous sentiment error: {prev_sent}")
            prev_sent = {"positive": 0, "negative": 0, "neutral": 0}
        
        # Execute sync queries in parallel using thread pool
        total_feedback, prev_total_feedback, recent_alerts = await asyncio.gather(
            asyncio.to_thread(get_total_feedback),
            asyncio.to_thread(get_prev_total_feedback),
            asyncio.to_thread(get_recent_alerts)
        )

        def pct_change(curr: int, prev: int) -> float:
            if prev <= 0 and curr > 0:
                return 100.0
            if prev == 0:
                return 0.0
            return round(((curr - prev) / prev) * 100.0, 1)

        deltas = {
            "total_feedback_pct": pct_change(total_feedback, prev_total_feedback),
            "positive_pct": pct_change(sentiment_dist.get("positive",0), prev_sent.get("positive",0)),
            "negative_pct": pct_change(sentiment_dist.get("negative",0), prev_sent.get("negative",0)),
            "neutral_pct": pct_change(sentiment_dist.get("neutral",0), prev_sent.get("neutral",0)),
        }

        data = {
            "total_feedback": total_feedback,
            "sentiment_distribution": sentiment_dist,
            "sector_distribution": sector_dist,
            "top_issues": top_issues,
            "trending_complaints": trending,
            "recent_alerts": recent_alerts,
            "generated_at": now.isoformat(),
            "deltas": deltas,
        }
        # Store in cache with datetime object for quick age checks
        _INSIGHTS_CACHE[key] = {**data, "_cached_at": now}
        return data
    
    async def get_sentiment_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get sentiment trends over time"""
        now = datetime.utcnow()
        key = str(days)
        cached = _TRENDS_CACHE.get(key)
        if cached:
            # Handle both datetime and ISO string formats
            cached_time = cached.get("_cached_at")
            if cached_time:
                if isinstance(cached_time, datetime):
                    if (now - cached_time).total_seconds() < _TRENDS_TTL_SECONDS:
                        return {k: v for k, v in cached.items() if k != "_cached_at"}
                elif isinstance(cached_time, str):
                    cached_dt = datetime.fromisoformat(cached_time.replace('Z', '+00:00'))
                    if (now - cached_dt).total_seconds() < _TRENDS_TTL_SECONDS:
                        return {k: v for k, v in cached.items() if k != "_cached_at"}

        start_date = (now - timedelta(days=days)).isoformat()
        
        # Get sentiment scores grouped by date
        try:
            result = self.supabase.table("sentiment_scores").select(
                "sentiment, analyzed_at"
            ).gte("analyzed_at", start_date).order("analyzed_at").execute()
            
            # Group by date
            trends = {}
            for item in result.data:
                date = item["analyzed_at"][:10]  # Extract date
                if date not in trends:
                    trends[date] = {"positive": 0, "negative": 0, "neutral": 0}
                trends[date][item["sentiment"]] = trends[date].get(item["sentiment"], 0) + 1
        except Exception as e:
            logger.error(f"Error getting sentiment trends: {e}")
            trends = {}
        
        data = {
            "trends": trends,
            "period_days": days,
            "generated_at": now.isoformat(),
        }
        _TRENDS_CACHE[key] = {**data, "_cached_at": now}
        return data
    
    async def get_top_issues(
        self,
        limit: int = 10,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get top issues by volume and urgency"""
        try:
            start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Get sector classification with counts
            result = self.supabase.table("sector_classification").select(
                "primary_sector, feedback_id"
            ).gte("classified_at", start_date).execute()
            
            # Count by sector
            sector_counts = {}
            for item in result.data:
                sector = item["primary_sector"]
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
            
            # Sort and format
            top_issues = [
                {"sector": sector, "count": count}
                for sector, count in sorted(
                    sector_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:limit]
            ]
            
            return top_issues
        except Exception as e:
            logger.error(f"Error getting top issues: {e}")
            return []
    
    async def get_county_heatmap(self, days: int = 7) -> Dict[str, Dict[str, Any]]:
        """Get county-level sentiment and issue heatmap"""
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Get feedback with locations
        result = self.supabase.table("citizen_feedback").select(
            "location, id"
        ).gte("created_at", start_date).not_.is_("location", "null").execute()
        
        # Count by county
        county_data = {}
        for item in result.data:
            county = item.get("location", "Unknown")
            if county not in county_data:
                county_data[county] = {"count": 0, "sentiment": {"positive": 0, "negative": 0, "neutral": 0}}
            county_data[county]["count"] += 1
        
        return county_data
    
    async def _get_sentiment_distribution(
        self,
        start_date: str,
        county: Optional[str],
        sector: Optional[str]
    ) -> Dict[str, int]:
        """Get sentiment distribution"""
        try:
            query = self.supabase.table("sentiment_scores").select(
                "sentiment"
            ).gte("analyzed_at", start_date)
            
            result = query.execute()
            
            dist = {"positive": 0, "negative": 0, "neutral": 0}
            for item in result.data:
                sentiment = item["sentiment"]
                if sentiment in dist:
                    dist[sentiment] += 1
            
            return dist
        except Exception as e:
            logger.error(f"Error getting sentiment distribution: {e}")
            return {"positive": 0, "negative": 0, "neutral": 0}
    
    async def _get_sector_distribution(
        self,
        start_date: str,
        county: Optional[str]
    ) -> Dict[str, int]:
        """Get sector distribution"""
        try:
            query = self.supabase.table("sector_classification").select(
                "primary_sector"
            ).gte("classified_at", start_date)
            
            result = query.execute()
            
            dist = {}
            for item in result.data:
                sector = item["primary_sector"]
                dist[sector] = dist.get(sector, 0) + 1
            
            return dist
        except Exception as e:
            logger.error(f"Error getting sector distribution: {e}")
            return {}
    
    async def _get_top_issues(
        self,
        days: int,
        county: Optional[str],
        sector: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get top issues"""
        return await self.get_top_issues(limit=10, days=days)
    
    async def _get_trending_complaints(self, days: int) -> List[Dict[str, Any]]:
        """Get trending complaints"""
        try:
            start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            result = self.supabase.table("citizen_feedback").select(
                "id, text, created_at, source"
            ).gte("created_at", start_date).order(
                "created_at", desc=True
            ).limit(20).execute()
            
            return result.data if result else []
        except Exception as e:
            logger.error(f"Error getting trending complaints: {e}")
            return []

