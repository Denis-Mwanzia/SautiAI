"""
Real-time Endpoints
Endpoints for real-time data streaming and updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from typing import List
import logging
import json

from app.services.realtime_service import RealtimeService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/stream")
async def websocket_stream(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    
    Streams:
    - New feedback ingestion
    - Sentiment updates
    - Alert notifications
    - Dashboard updates
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        service = RealtimeService()
        await service.subscribe(websocket)
        
        # Keep connection alive and stream updates
        while True:
            # Send periodic updates
            try:
                updates = await service.get_updates()
                if updates:
                    await websocket.send_json(updates)
            except Exception as se:
                logger.debug(f"WS send/update error: {se}")
            
            # Check for client messages (ping/pong) without blocking the loop
            try:
                msg = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                if msg == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                pass
            except Exception as re:
                logger.debug(f"WS recv error: {re}")
            
            await asyncio.sleep(2)
                
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

