"""
Chat Endpoints
Endpoints for conversational interaction with data
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

from app.models.schemas import APIResponse
from app.services.chat_service import ChatService

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatMessageRequest(BaseModel):
    """Request model for chat messages"""
    message: str = Field(..., description="User's message")
    conversation_history: Optional[List[Dict[str, str]]] = Field(
        None, 
        description="Previous messages in conversation"
    )


def get_chat_service() -> ChatService:
    """Dependency injection for ChatService"""
    return ChatService()


@router.post("/message", response_model=APIResponse)
async def send_message(
    request: ChatMessageRequest,
    service: ChatService = Depends(get_chat_service)
):
    """
    Send a chat message and get AI response
    
    Args:
        request: Chat message request with message and optional conversation history
        
    Returns:
        AI response with relevant data
    """
    try:
        logger.info(f"Processing chat message: {request.message[:100]}")
        
        result = await service.chat(request.message, request.conversation_history)
        
        return APIResponse(
            success=True,
            message="Chat response generated",
            data=result
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

