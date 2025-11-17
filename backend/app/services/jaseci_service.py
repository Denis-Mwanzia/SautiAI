"""
Jaseci Service
Service for running and managing Jaseci OSP agents
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class JaseciService:
    """Service for interacting with Jaseci agents"""
    
    def __init__(self):
        self.jaseci_url = settings.JASECI_SERVER_URL
        self.master_key = settings.JASECI_MASTER_KEY
        self.timeout = 30.0
    
    async def run_agent(
        self,
        agent_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a Jaseci OSP agent
        
        Args:
            agent_type: Type of agent to run
            parameters: Agent parameters
            
        Returns:
            Result from agent execution
        """
        logger.info(f"Running Jaseci agent: {agent_type} with parameters: {parameters}")
        
        try:
            # Map agent types to Jac walker names
            walker_map = {
                "data_ingestion": "data_ingestion_agent",
                "preprocessing": "preprocessing_agent",
                "language_detection": "language_detection_agent",
                "routing": "routing_agent",
                "monitoring": "monitoring_agent"
            }
            
            walker_name = walker_map.get(agent_type, agent_type)
            
            # Check if Jaseci server is available
            if not self.jaseci_url or self.jaseci_url == "http://localhost:8000":
                logger.warning("Jaseci server URL not configured or using default. Agent execution will be simulated.")
                return await self._simulate_agent_execution(agent_type, parameters)
            
            # Call Jaseci API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Jaseci API endpoint for running walkers
                url = f"{self.jaseci_url}/js/walker_run"
                
                payload = {
                    "name": walker_name,
                    "ctx": parameters,
                    "master": self.master_key
                }
                
                response = await client.post(url, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Agent {agent_type} executed successfully")
                    return result
                else:
                    logger.error(f"Jaseci API error: {response.status_code} - {response.text}")
                    # Fallback to simulation
                    return await self._simulate_agent_execution(agent_type, parameters)
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to Jaseci server at {self.jaseci_url}")
            return await self._simulate_agent_execution(agent_type, parameters)
        except Exception as e:
            logger.error(f"Error running Jaseci agent {agent_type}: {e}", exc_info=True)
            return await self._simulate_agent_execution(agent_type, parameters)
    
    async def _simulate_agent_execution(
        self,
        agent_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate agent execution when Jaseci server is not available"""
        logger.info(f"Simulating agent execution for {agent_type}")
        
        # Return simulated result based on agent type
        if agent_type == "data_ingestion":
            return {
                "status": "completed",
                "collected_count": 0,
                "message": "Data ingestion simulated (Jaseci server not available)"
            }
        elif agent_type == "preprocessing":
            return {
                "status": "completed",
                "processed_count": 0,
                "message": "Preprocessing simulated"
            }
        elif agent_type == "language_detection":
            return {
                "status": "completed",
                "detected_language": "en",
                "message": "Language detection simulated"
            }
        elif agent_type == "routing":
            return {
                "status": "completed",
                "routed_to": ["sentiment", "classification"],
                "message": "Routing simulated"
            }
        elif agent_type == "monitoring":
            return {
                "status": "completed",
                "alerts_generated": 0,
                "message": "Monitoring simulated"
            }
        else:
            return {
                "status": "completed",
                "message": f"Agent {agent_type} execution simulated"
            }
    
    async def get_agent_status(self, agent_type: Optional[str] = None) -> Dict[str, Any]:
        """Get status of running agents"""
        try:
            if not self.jaseci_url or self.jaseci_url == "http://localhost:8000":
                return {
                    "active_agents": [],
                    "status": "simulated",
                    "message": "Jaseci server not configured"
                }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.jaseci_url}/js/active_walkers"
                response = await client.get(url, params={"master": self.master_key})
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {
                        "active_agents": [],
                        "status": "unknown",
                        "error": f"Status check failed: {response.status_code}"
                    }
        except Exception as e:
            logger.error(f"Error getting agent status: {e}")
            return {
                "active_agents": [],
                "status": "error",
                "error": str(e)
            }
    
    async def get_available_agents(self) -> List[str]:
        """Get list of available agent types"""
        return [
            "data_ingestion",
            "preprocessing",
            "language_detection",
            "routing",
            "monitoring"
        ]
    
    async def get_agent_types(self) -> List[str]:
        """Alias for get_available_agents for compatibility"""
        return await self.get_available_agents()

