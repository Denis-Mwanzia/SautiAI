"""
Data Ingestion Endpoints
Endpoints for ingesting data from various legal sources
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import List, Optional
import logging

from app.models.schemas import (
    TwitterIngestRequest,
    FacebookIngestRequest,
    APIResponse,
    CitizenFeedback
)
from app.services.ingestion import IngestionService
from app.services.open_data_service import OpenDataService
from app.services.government_portal_service import GovernmentPortalService
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


def get_ingestion_service() -> IngestionService:
    """Dependency injection for IngestionService"""
    return IngestionService()


def get_open_data_service() -> OpenDataService:
    """Dependency injection for OpenDataService"""
    return OpenDataService()


def get_government_portal_service() -> GovernmentPortalService:
    """Dependency injection for GovernmentPortalService"""
    return GovernmentPortalService()


@router.post("/twitter", response_model=APIResponse)
async def ingest_twitter(
    request: TwitterIngestRequest,
    background_tasks: BackgroundTasks,
    service: IngestionService = Depends(get_ingestion_service)
):
    """
    Ingest data from Twitter API
    
    Tracks specified hashtags and geo-tagged posts within Kenyan boundaries.
    Processes data asynchronously in the background.
    """
    try:
        logger.info(f"Ingesting Twitter data for hashtags: {request.hashtags}")
        
        # Run ingestion in background
        background_tasks.add_task(
            service.ingest_twitter,
            hashtags=request.hashtags,
            max_results=request.max_results,
            geo_bounds=request.geo_bounds
        )
        
        return APIResponse(
            success=True,
            message=f"Twitter ingestion started for {len(request.hashtags)} hashtags",
            data={"hashtags": request.hashtags}
        )
    except Exception as e:
        logger.error(f"Twitter ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/facebook", response_model=APIResponse)
async def ingest_facebook(
    request: FacebookIngestRequest,
    background_tasks: BackgroundTasks,
    service: IngestionService = Depends(get_ingestion_service)
):
    """
    Ingest data from Facebook Graph API
    
    Monitors public pages (e.g., Nairobi City County, Ministry of Health).
    Only accesses publicly available data.
    """
    try:
        logger.info(f"Ingesting Facebook data for pages: {request.page_ids}")
        
        background_tasks.add_task(
            service.ingest_facebook,
            page_ids=request.page_ids,
            max_posts=request.max_posts
        )
        
        return APIResponse(
            success=True,
            message=f"Facebook ingestion started for {len(request.page_ids)} pages",
            data={"page_ids": request.page_ids}
        )
    except Exception as e:
        logger.error(f"Facebook ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rss", response_model=APIResponse)
async def ingest_rss(
    feed_urls: List[str],
    background_tasks: BackgroundTasks,
    service: IngestionService = Depends(get_ingestion_service)
):
    """
    Ingest data from RSS feeds
    
    Legal RSS feeds from news sources (Nation Africa, The Standard, etc.)
    """
    try:
        logger.info(f"Ingesting RSS feeds: {feed_urls}")
        
        background_tasks.add_task(
            service.ingest_rss,
            feed_urls=feed_urls
        )
        
        return APIResponse(
            success=True,
            message=f"RSS ingestion started for {len(feed_urls)} feeds",
            data={"feed_urls": feed_urls}
        )
    except Exception as e:
        logger.error(f"RSS ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=APIResponse)
async def ingestion_status(service: IngestionService = Depends(get_ingestion_service)):
    """Get status of recent ingestion jobs"""
    try:
        status = await service.get_ingestion_status()
        return APIResponse(
            success=True,
            message="Ingestion status retrieved",
            data=status
        )
    except Exception as e:
        logger.error(f"Status retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sources", response_model=APIResponse)
async def get_data_sources(
    source_type: Optional[str] = None,
    category: Optional[str] = None,
    enabled_only: bool = True
):
    """
    Get list of available data sources
    
    Returns all configured data sources with their metadata
    """
    try:
        from app.core.data_sources import (
            ALL_DATA_SOURCES,
            ENABLED_SOURCES,
            DataSourceType
        )
        
        sources = ALL_DATA_SOURCES if not enabled_only else ENABLED_SOURCES
        
        # Filter by type if provided
        if source_type:
            try:
                ds_type = DataSourceType(source_type)
                sources = [s for s in sources if s.source_type == ds_type]
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid source type: {source_type}")
        
        # Filter by category if provided
        if category:
            valid_categories = ["healthcare", "education", "governance", "public_services", "infrastructure", "security"]
            if category not in valid_categories:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
            sources = [s for s in sources if category in s.category_focus]
        
        # Convert to dict for JSON serialization
        sources_data = [
            {
                "name": s.name,
                "source_type": s.source_type.value,
                "url": s.url,
                "description": s.description,
                "category_focus": s.category_focus,
                "requires_auth": s.requires_auth,
                "enabled": s.enabled,
                "metadata": s.metadata
            }
            for s in sources
        ]
        
        return APIResponse(
            success=True,
            message=f"Retrieved {len(sources_data)} data sources",
            data={
                "sources": sources_data,
                "total": len(sources_data)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting data sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/open-data", response_model=APIResponse)
async def ingest_open_data(
    dataset: Optional[str] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: OpenDataService = Depends(get_open_data_service)
):
    """
    Ingest data from Kenya Open Data Portal
    
    Fetches public datasets from opendata.go.ke
    """
    try:
        if background_tasks:
            background_tasks.add_task(service.ingest_kenya_open_data, dataset)
            return APIResponse(
                success=True,
                message="Open data ingestion started in background"
            )
        else:
            result = await service.ingest_kenya_open_data(dataset)
            return APIResponse(
                success=result.get("success", False),
                message="Open data ingestion completed",
                data=result
            )
    except Exception as e:
        logger.error(f"Open data ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/government-complaints", response_model=APIResponse)
async def ingest_government_complaints(
    limit: int = 100,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: GovernmentPortalService = Depends(get_government_portal_service)
):
    """
    Ingest public complaints from government portals
    
    Fetches complaints from ICT Portal and other government complaint systems
    """
    try:
        if background_tasks:
            background_tasks.add_task(service.ingest_ict_complaints, limit)
            return APIResponse(
                success=True,
                message="Government complaints ingestion started in background"
            )
        else:
            result = await service.ingest_ict_complaints(limit)
            return APIResponse(
                success=result.get("success", False),
                message="Government complaints ingestion completed",
                data=result
            )
    except Exception as e:
        logger.error(f"Government complaints ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/county", response_model=APIResponse)
async def ingest_county_portal(
    county: str,
    max_items: int = 50,
    background_tasks: BackgroundTasks = None,
    service: IngestionService = Depends(get_ingestion_service)
):
    """Ingest data from county complaint portal"""
    try:
        from app.services.county_portal_service import CountyPortalService
        county_service = CountyPortalService()
        
        if background_tasks:
            background_tasks.add_task(
                county_service.ingest_county_complaints,
                county=county,
                max_items=max_items
            )
            return APIResponse(
                success=True,
                message=f"County portal ingestion started for {county}"
            )
        else:
            result = await county_service.ingest_county_complaints(county, max_items)
            return APIResponse(
                success=True,
                message=f"County portal ingestion completed",
                data=result
            )
    except Exception as e:
        logger.error(f"County portal ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/open-data-kenya", response_model=APIResponse)
async def ingest_open_data_kenya(
    dataset: str = "citizen_feedback",
    max_items: int = 100,
    background_tasks: BackgroundTasks = None
):
    """Ingest data from Kenya Open Data Portal"""
    try:
        from app.services.county_portal_service import CountyPortalService
        county_service = CountyPortalService()
        
        if background_tasks:
            background_tasks.add_task(
                county_service.ingest_open_data_kenya,
                dataset=dataset,
                max_items=max_items
            )
            return APIResponse(
                success=True,
                message=f"Open Data Kenya ingestion started for {dataset}"
            )
        else:
            result = await county_service.ingest_open_data_kenya(dataset, max_items)
            return APIResponse(
                success=True,
                message=f"Open Data Kenya ingestion completed",
                data=result
            )
    except Exception as e:
        logger.error(f"Open Data Kenya ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

