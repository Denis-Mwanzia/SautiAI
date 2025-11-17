"""
Config Service
Simple JSON-backed configuration for runtime-tunable settings (e.g., alert webhooks).
"""

from __future__ import annotations

import json
import os
import threading
from typing import Any, Dict, Optional

_LOCK = threading.RLock()
_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "data")
_CFG_PATH = os.path.abspath(os.path.join(_DATA_DIR, "config.json"))


def _ensure_dir():
    os.makedirs(_DATA_DIR, exist_ok=True)


class ConfigService:
    def __init__(self) -> None:
        _ensure_dir()
        self._path = _CFG_PATH
        self._cache: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        with _LOCK:
            if not os.path.exists(self._path):
                self._cache = {}
                return
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    self._cache = json.load(f) or {}
            except Exception:
                self._cache = {}

    def _flush(self) -> None:
        with _LOCK:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)

    def get_alerts_config(self) -> Dict[str, Any]:
        with _LOCK:
            return self._cache.get("alerts", {})

    def set_alerts_config(self, cfg: Dict[str, Any]) -> Dict[str, Any]:
        with _LOCK:
            self._cache["alerts"] = cfg or {}
            self._flush()
            return self._cache["alerts"]


