"""
Government Portal Service
Service for ingesting from government portals and complaint systems
"""

import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.data_sources import GOVERNMENT_SOURCES, DataSource
from app.db.supabase import get_supabase_service
from app.services.ingestion import IngestionService

logger = logging.getLogger(__name__)


class GovernmentPortalService:
    """Service for ingesting from government portals"""
    
    def __init__(self):
        self.supabase_service = get_supabase_service()
        self.ingestion_service = IngestionService()
    
    async def ingest_ict_complaints(
        self,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Ingest public complaints from Kenya ICT Portal
        
        Args:
            limit: Maximum number of complaints to fetch
        """
        logger.info("Starting ICT Public Complaints ingestion")
        
        source = None
        for s in GOVERNMENT_SOURCES:
            if "ict.go.ke" in s.url:
                source = s
                break
        
        if not source:
            return {"success": False, "error": "ICT Portal source not configured"}
        
        try:
            api_url = source.metadata.get("api_endpoint", "")
            
            if not api_url:
                logger.warning("ICT Portal API endpoint not configured")
                return {"success": False, "error": "API endpoint not configured"}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    api_url,
                    params={"limit": limit, "status": "public"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = await self._process_complaints(
                        data,
                        source,
                        "ict_complaints"
                    )
                    return {"success": True, **results}
                else:
                    logger.warning(f"ICT Portal API error: {response.status_code}")
                    return {"success": False, "error": f"HTTP {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"Error ingesting ICT complaints: {e}")
            return {"success": False, "error": str(e)}
    
    async def ingest_ipoa_data(
        self,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Ingest police oversight data from IPOA
        
        Args:
            limit: Maximum records to fetch
        """
        logger.info("Starting IPOA data ingestion")
        
        # Similar to ICT complaints but focused on security/governance
        return {"success": False, "message": "IPOA API integration pending"}
    
    async def ingest_mzalendo(
        self,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Ingest parliamentary data from Mzalendo
        
        Args:
            limit: Maximum records to fetch
        """
        logger.info("Starting Mzalendo ingestion")
        
        # Focus on governance category
        return {"success": False, "message": "Mzalendo API integration pending"}
    
    async def _process_complaints(
        self,
        data: Dict[str, Any],
        source: DataSource,
        source_name: str
    ) -> Dict[str, Any]:
        """Process complaint records"""
        processed = 0
        stored = 0
        
        complaints = data.get("data", []) or data.get("complaints", []) or []
        
        for complaint in complaints:
            try:
                text = (
                    complaint.get("description", "") or
                    complaint.get("complaint_text", "") or
                    complaint.get("issue", "") or
                    str(complaint)
                )
                
                if not text or len(text) < 10:
                    continue
                
                feedback = {
                    "source": source_name,
                    "source_id": f"{source_name}_{complaint.get('id', processed)}",
                    "text": text[:5000],
                    "language": complaint.get("language", "en"),
                    "author": None,  # Complaints are typically anonymous
                    "location": complaint.get("county") or complaint.get("location"),
                    "timestamp": (
                        complaint.get("created_at") or
                        complaint.get("timestamp") or
                        datetime.utcnow().isoformat()
                    ),
                    "raw_data": complaint
                }
                
                stored_item = await self.ingestion_service._store_feedback(feedback)
                if stored_item:
                    stored += 1
                    await self.ingestion_service._trigger_analysis(
                        stored_item["id"],
                        text,
                        feedback["language"]
                    )
                
                processed += 1
                
            except Exception as e:
                logger.error(f"Error processing complaint: {e}")
                continue
        
        return {"processed": processed, "stored": stored}

