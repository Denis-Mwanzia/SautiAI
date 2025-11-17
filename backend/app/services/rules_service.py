"""
Rules Service
Lightweight alert rule management with JSON persistence.
Used to drive no‑code alerting in demos without requiring DB migrations.
"""

from __future__ import annotations

import json
import os
import threading
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings


_LOCK = threading.RLock()
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data")
_RULES_PATH = os.path.abspath(os.path.join(_DATA_DIR, "alert_rules.json"))


def _ensure_dir():
    os.makedirs(_DATA_DIR, exist_ok=True)


def _utcnow_iso() -> str:
    return datetime.utcnow().iso8601() if hasattr(datetime.utcnow(), "iso8601") else datetime.utcnow().isoformat()


@dataclass
class AlertRule:
    id: str
    name: str
    enabled: bool = True
    # simple condition set; all provided conditions must be met
    sector: Optional[str] = None          # e.g., "health", "education"
    county: Optional[str] = None          # e.g., "Nairobi"
    min_count: Optional[int] = None       # threshold on count in last 24h
    # notification channels (demo flags; real integration via AlertService)
    notify_slack: bool = False
    notify_webhook: bool = False
    created_at: str = field(default_factory=_utcnow_iso)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AlertRule":
        return AlertRule(
            id=d.get("id") or str(uuid.uuid4()),
            name=d.get("name") or "Untitled rule",
            enabled=bool(d.get("enabled", True)),
            sector=d.get("sector"),
            county=d.get("county"),
            min_count=d.get("min_count"),
            notify_slack=bool(d.get("notify_slack", False)),
            notify_webhook=bool(d.get("notify_webhook", False)),
            created_at=d.get("created_at") or _utcnow_iso(),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RulesStore:
    """In‑process rules registry with JSON persistence."""

    def __init__(self) -> None:
        _ensure_dir()
        self._path = _RULES_PATH
        self._rules: Dict[str, AlertRule] = {}
        self._load()

    def _load(self) -> None:
        with _LOCK:
            if not os.path.exists(self._path):
                self._rules = {}
                return
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                self._rules = {r["id"]: AlertRule.from_dict(r) for r in raw or []}
            except Exception:
                # corrupted file or first run
                self._rules = {}

    def _flush(self) -> None:
        with _LOCK:
            data = [r.to_dict() for r in self._rules.values()]
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def list(self) -> List[AlertRule]:
        with _LOCK:
            return list(self._rules.values())

    def get(self, rule_id: str) -> Optional[AlertRule]:
        with _LOCK:
            return self._rules.get(rule_id)

    def upsert(self, rule: AlertRule) -> AlertRule:
        with _LOCK:
            self._rules[rule.id] = rule
            self._flush()
            return rule

    def delete(self, rule_id: str) -> bool:
        with _LOCK:
            if rule_id in self._rules:
                del self._rules[rule_id]
                self._flush()
                return True
            return False


class RulesService:
    """Facade around RulesStore + simple evaluation helpers."""

    def __init__(self) -> None:
        self._store = RulesStore()

    def list_rules(self) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self._store.list()]

    def create_rule(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        rule = AlertRule.from_dict({**payload, "id": str(uuid.uuid4())})
        return self._store.upsert(rule).to_dict()

    def update_rule(self, rule_id: str, payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        current = self._store.get(rule_id)
        if not current:
            return None
        updated = AlertRule.from_dict({**current.to_dict(), **payload, "id": rule_id})
        return self._store.upsert(updated).to_dict()

    def delete_rule(self, rule_id: str) -> bool:
        return self._store.delete(rule_id)

    def evaluate(self, counts_by_sector: Dict[str, int], counts_by_county: Dict[str, int]) -> List[Dict[str, Any]]:
        """Return a list of triggered alert payloads based on current rules and counts."""
        triggered: List[Dict[str, Any]] = []
        for r in self._store.list():
            if not r.enabled:
                continue
            ok = True
            if r.sector:
                sector_count = counts_by_sector.get(r.sector.lower(), 0)
                if r.min_count is not None and sector_count < r.min_count:
                    ok = False
            if ok and r.county:
                county_count = counts_by_county.get(r.county.lower(), 0)
                if r.min_count is not None and county_count < r.min_count:
                    ok = False
            if ok and (r.sector is None and r.county is None) and r.min_count:
                # global count not provided; skip this rule
                ok = False
            if not ok:
                continue
            severity = "critical" if (r.min_count or 0) >= 50 else ("high" if (r.min_count or 0) >= 20 else "medium")
            desc_parts: List[str] = []
            if r.sector:
                desc_parts.append(f"Sector '{r.sector}' threshold reached")
            if r.county:
                add = f"County '{r.county}' threshold reached"
                desc_parts.append(add)
            description = ", ".join(desc_parts) or "Threshold reached"
            triggered.append({
                "id": str(uuid.uuid4()),
                "title": r.name,
                "severity": severity,
                "description": description,
                "affected_counties": [r.county] if r.county else [],
                "sector": r.sector,
                "created_at": _utcnow_iso(),
                "acknowledged": False,
            })
        return triggered

