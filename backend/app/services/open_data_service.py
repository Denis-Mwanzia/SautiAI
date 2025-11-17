"""
Open Data Portal Service
Service for ingesting data from Kenya Open Data Portal and other government APIs
"""

import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.data_sources import OPEN_DATA_SOURCES, DataSource
from app.core.constants import VALID_CATEGORIES
from app.db.supabase import get_supabase_service
from app.services.ingestion import IngestionService

logger = logging.getLogger(__name__)


class OpenDataService:
    """Service for ingesting from open data portals"""
    
    def __init__(self):
        self.supabase_service = get_supabase_service()
        self.ingestion_service = IngestionService()
    
    async def ingest_kenya_open_data(
        self,
        dataset: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest data from Kenya Open Data Portal
        
        Args:
            dataset: Specific dataset to ingest (optional)
        """
        logger.info("Starting Kenya Open Data Portal ingestion")
        
        source = None
        for s in OPEN_DATA_SOURCES:
            if "opendata.go.ke" in s.url:
                source = s
                break
        
        if not source:
            logger.error("Kenya Open Data Portal source not found")
            return {"success": False, "error": "Source not configured"}
        
        results = {
            "processed": 0,
            "stored": 0,
            "errors": []
        }
        
        try:
            # Get available datasets
            datasets = source.metadata.get("datasets", [])
            
            if dataset:
                datasets = [d for d in datasets if dataset in d]
            
            for dataset_name in datasets:
                try:
                    # Construct API endpoint
                    api_url = f"{source.metadata.get('api_base', '')}/datasets/{dataset_name}"
                    
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        response = await client.get(api_url)
                        
                        if response.status_code == 200:
                            data = response.json()
                            processed = await self._process_open_data(
                                data,
                                source,
                                dataset_name
                            )
                            results["processed"] += processed.get("processed", 0)
                            results["stored"] += processed.get("stored", 0)
                        else:
                            logger.warning(f"API error for {dataset_name}: {response.status_code}")
                            results["errors"].append(f"{dataset_name}: HTTP {response.status_code}")
                            
                except Exception as e:
                    logger.error(f"Error processing dataset {dataset_name}: {e}")
                    results["errors"].append(f"{dataset_name}: {str(e)}")
            
            logger.info(f"Open Data ingestion completed: {results['stored']} items stored")
            return {"success": True, **results}
            
        except Exception as e:
            logger.error(f"Error ingesting from Open Data Portal: {e}")
            return {"success": False, "error": str(e), **results}
    
    async def _process_open_data(
        self,
        data: Dict[str, Any],
        source: DataSource,
        dataset_name: str
    ) -> Dict[str, Any]:
        """Process open data records"""
        processed = 0
        stored = 0
        
        # Extract records from API response
        records = data.get("data", []) or data.get("records", []) or []
        
        for record in records:
            try:
                # Extract text/description from record
                text = (
                    record.get("description", "") or
                    record.get("summary", "") or
                    record.get("title", "") or
                    str(record)
                )
                
                if not text or len(text) < 10:
                    continue
                
                # Create feedback record
                feedback = {
                    "source": f"open_data_{dataset_name}",
                    "source_id": f"{dataset_name}_{record.get('id', processed)}",
                    "text": text[:5000],  # Limit length
                    "language": "en",  # Most open data is in English
                    "author": None,  # Open data is anonymous
                    "location": record.get("county") or record.get("location"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "raw_data": record
                }
                
                # Store using ingestion service (includes validation)
                stored_item = await self.ingestion_service._store_feedback(feedback)
                if stored_item:
                    stored += 1
                    # Trigger analysis
                    await self.ingestion_service._trigger_analysis(
                        stored_item["id"],
                        text,
                        "en"
                    )
                
                processed += 1
                
            except Exception as e:
                logger.error(f"Error processing open data record: {e}")
                continue
        
        return {"processed": processed, "stored": stored}
    
    async def ingest_knbs_data(
        self,
        dataset: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ingest data from Kenya National Bureau of Statistics
        
        Args:
            dataset: Specific dataset (census, economic-surveys, etc.)
        """
        logger.info("Starting KNBS data ingestion")
        
        # Similar implementation to Kenya Open Data
        # KNBS may have different API structure
        return {"success": False, "message": "KNBS API integration pending"}
    
    async def ingest_majidata(
        self
    ) -> Dict[str, Any]:
        """
        Ingest water and sanitation data from Majidata
        """
        logger.info("Starting Majidata ingestion")
        
        # Focus on infrastructure/public_services category
        return {"success": False, "message": "Majidata API integration pending"}

