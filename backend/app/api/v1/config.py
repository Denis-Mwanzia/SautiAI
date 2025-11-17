"""
Config Endpoints
Manage runtime configuration (alerts/webhooks).
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field

from app.models.schemas import APIResponse
from app.services.config_service import ConfigService

router = APIRouter()
cfg = ConfigService()


class AlertsConfigIn(BaseModel):
    SLACK_WEBHOOK_URL: str = Field(default="")
    ALERT_WEBHOOK_URL: str = Field(default="")


@router.get("/config/alerts", response_model=APIResponse)
async def get_alerts_config() -> APIResponse:
    return APIResponse(success=True, message="Alerts config", data=cfg.get_alerts_config())


@router.post("/config/alerts", response_model=APIResponse)
async def set_alerts_config(body: AlertsConfigIn) -> APIResponse:
    saved = cfg.set_alerts_config(body.model_dump())
    return APIResponse(success=True, message="Alerts config saved", data=saved)


