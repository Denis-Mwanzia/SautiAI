"""
Alert Rules API
CRUD and evaluation test for lightweight alert rules (demo-friendly).
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Body, Query
from pydantic import BaseModel, Field

from app.services.rules_service import RulesService
from app.models.schemas import APIResponse

router = APIRouter()
_rules = RulesService()


class RuleIn(BaseModel):
    name: str = Field(..., max_length=128)
    enabled: bool = True
    sector: Optional[str] = None
    county: Optional[str] = None
    min_count: Optional[int] = Field(default=None, ge=1)
    notify_slack: bool = False
    notify_webhook: bool = False


@router.get("/rules", response_model=APIResponse)
async def list_rules() -> APIResponse:
    items = _rules.list_rules()
    return APIResponse(success=True, message="Rules listed", data=items)


@router.post("/rules", response_model=APIResponse)
async def create_rule(rule: RuleIn) -> APIResponse:
    created = _rules.create_rule(rule.model_dump())
    return APIResponse(success=True, message="Rule created", data=created)


@router.patch("/rules/{rule_id}", response_model=APIResponse)
async def update_rule(rule_id: str, patch: RuleIn) -> APIResponse:
    updated = _rules.update_rule(rule_id, patch.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Rule not found")
    return APIResponse(success=True, message="Rule updated", data=updated)


@router.delete("/rules/{rule_id}", response_model=APIResponse)
async def delete_rule(rule_id: str) -> APIResponse:
    ok = _rules.delete_rule(rule_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Rule not found")
    return APIResponse(success=True, message="Rule deleted")


class EvalRequest(BaseModel):
    counts_by_sector: Dict[str, int] = Field(default_factory=dict)
    counts_by_county: Dict[str, int] = Field(default_factory=dict)


@router.post("/rules:eval", response_model=APIResponse)
async def eval_rules(body: EvalRequest) -> APIResponse:
    out = _rules.evaluate(body.counts_by_sector, body.counts_by_county)
    return APIResponse(success=True, message="Evaluation complete", data=out)


