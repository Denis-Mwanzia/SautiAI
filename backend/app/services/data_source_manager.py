"""
Data Source Manager
Centralized service for managing and monitoring all data sources
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from app.core.data_sources import (
    ALL_DATA_SOURCES,
    ENABLED_SOURCES,
    get_sources_by_type,
    get_sources_by_category,
    get_rss_feed_urls,
    DataSourceType
)
from app.db.supabase import get_supabase
from app.services.ingestion import IngestionService
from app.services.open_data_service import OpenDataService
from app.services.government_portal_service import GovernmentPortalService

logger = logging.getLogger(__name__)


class DataSourceManager:
    """Centralized manager for all data sources"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.ingestion_service = IngestionService()
        self.open_data_service = OpenDataService()
        self.gov_portal_service = GovernmentPortalService()
    
    async def ingest_all_enabled_sources(self) -> Dict[str, Any]:
        """
        Ingest from all enabled data sources
        
        Returns summary of ingestion results
        """
        logger.info("Starting ingestion from all enabled sources")
        
        results = {
            "rss": {"success": False, "count": 0},
            "open_data": {"success": False, "count": 0},
            "government": {"success": False, "count": 0},
            "social_media": {"success": False, "count": 0},
            "total_processed": 0,
            "total_stored": 0,
            "errors": []
        }
        
        # RSS Feeds
        try:
            rss_urls = get_rss_feed_urls()
            if rss_urls:
                await self.ingestion_service.ingest_rss(rss_urls)
                results["rss"]["success"] = True
                results["rss"]["count"] = len(rss_urls)
        except Exception as e:
            logger.error(f"RSS ingestion error: {e}")
            results["errors"].append(f"RSS: {str(e)}")
        
        # Open Data Portals
        try:
            open_data_result = await self.open_data_service.ingest_kenya_open_data()
            if open_data_result.get("success"):
                results["open_data"]["success"] = True
                results["open_data"]["count"] = open_data_result.get("stored", 0)
                results["total_stored"] += results["open_data"]["count"]
        except Exception as e:
            logger.error(f"Open data ingestion error: {e}")
            results["errors"].append(f"Open Data: {str(e)}")
        
        # Government Portals
        try:
            gov_result = await self.gov_portal_service.ingest_ict_complaints(limit=100)
            if gov_result.get("success"):
                results["government"]["success"] = True
                results["government"]["count"] = gov_result.get("stored", 0)
                results["total_stored"] += results["government"]["count"]
        except Exception as e:
            logger.error(f"Government portal ingestion error: {e}")
            results["errors"].append(f"Government: {str(e)}")
        
        # Social Media (if tokens available)
        # Handled separately as they require authentication
        
        results["total_processed"] = (
            results["rss"]["count"] +
            results["open_data"]["count"] +
            results["government"]["count"]
        )
        
        logger.info(f"Ingestion completed: {results['total_stored']} items stored")
        return results
    
    async def get_source_statistics(self) -> Dict[str, Any]:
        """
        Get statistics for each data source
        
        Returns ingestion stats, last update times, etc.
        """
        try:
            # Get recent feedback counts by source
            result = self.supabase.table("citizen_feedback").select(
                "source, created_at"
            ).gte(
                "created_at",
                (datetime.utcnow() - timedelta(days=7)).isoformat()
            ).execute()
            
            source_stats = {}
            for item in result.data or []:
                source = item.get("source", "unknown")
                if source not in source_stats:
                    source_stats[source] = {
                        "count": 0,
                        "latest": None
                    }
                source_stats[source]["count"] += 1
                if not source_stats[source]["latest"]:
                    source_stats[source]["latest"] = item.get("created_at")
            
            # Map to configured sources
            stats_by_source = {}
            for source_config in ALL_DATA_SOURCES:
                source_name = source_config.name.lower().replace(" ", "_")
                stats = source_stats.get(source_name, {"count": 0, "latest": None})
                stats_by_source[source_config.name] = {
                    "enabled": source_config.enabled,
                    "requires_auth": source_config.requires_auth,
                    "recent_count": stats["count"],
                    "last_ingestion": stats["latest"],
                    "category_focus": source_config.category_focus
                }
            
            return {
                "sources": stats_by_source,
                "total_sources": len(ALL_DATA_SOURCES),
                "enabled_sources": len(ENABLED_SOURCES),
                "period": "7 days"
            }
            
        except Exception as e:
            logger.error(f"Error getting source statistics: {e}")
            return {"error": str(e)}
    
    async def enable_source(self, source_name: str) -> bool:
        """Enable a data source"""
        # This would update source configuration
        # For now, sources are configured in code
        logger.info(f"Source enablement: {source_name} (requires code update)")
        return False
    
    async def disable_source(self, source_name: str) -> bool:
        """Disable a data source"""
        # This would update source configuration
        logger.info(f"Source disablement: {source_name} (requires code update)")
        return False

