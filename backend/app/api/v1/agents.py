"""
Jaseci Agents Endpoints
Endpoints for running and managing Jaseci OSP agents
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any
import logging

from app.models.schemas import AgentRunRequest, APIResponse
from app.services.jaseci_service import JaseciService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_jaseci_service() -> JaseciService:
    """Dependency injection for JaseciService"""
    return JaseciService()


@router.post("/run", response_model=APIResponse)
async def run_agent(
    request: AgentRunRequest,
    background_tasks: BackgroundTasks,
    service: JaseciService = Depends(get_jaseci_service)
):
    """
    Run a Jaseci OSP agent
    
    Available agent types:
    - data_ingestion: Autonomous data collection
    - preprocessing: Text cleaning and normalization
    - language_detection: Detect language (en/sw)
    - routing: Route data to appropriate LLM pipeline
    - monitoring: Monitor risks and trends
    """
    try:
        logger.info(f"Running agent: {request.agent_type}")
        
        # Run agent in background
        background_tasks.add_task(
            service.run_agent,
            agent_type=request.agent_type,
            parameters=request.parameters
        )
        
        return APIResponse(
            success=True,
            message=f"Agent {request.agent_type} started",
            data={"agent_type": request.agent_type}
        )
    except Exception as e:
        logger.error(f"Agent execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=APIResponse)
async def agent_status(service: JaseciService = Depends(get_jaseci_service)):
    """Get status of running agents"""
    try:
        status = await service.get_agent_status()
        return APIResponse(
            success=True,
            message="Agent status retrieved",
            data=status
        )
    except Exception as e:
        logger.error(f"Status retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types", response_model=APIResponse)
async def available_agents(service: JaseciService = Depends(get_jaseci_service)):
    """Get list of available agent types"""
    try:
        agents = await service.get_available_agents()
        return APIResponse(
            success=True,
            message="Available agents retrieved",
            data=agents
        )
    except Exception as e:
        logger.error(f"Agent list error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

