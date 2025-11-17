"""
Search Endpoints
Full-text search over citizen feedback with basic filters
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import logging
import hashlib

from app.models.schemas import APIResponse
from datetime import datetime, timedelta, timezone
from app.db.supabase import get_supabase

router = APIRouter()
logger = logging.getLogger(__name__)

# Simple cache for search results
_SEARCH_CACHE: Dict[str, Dict[str, Any]] = {}
_SEARCH_TTL_SECONDS = 60  # 1 minute cache


@router.get("/feedback", response_model=APIResponse)
async def search_feedback(
    q: str = Query("", description="Search query"),
    sector: Optional[str] = Query(None),
    county: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """Search feedback by text with optional sector/county filters"""
    # Check cache
    cache_key = hashlib.md5(f"{q}:{sector}:{county}:{limit}".encode()).hexdigest()
    now = datetime.utcnow()
    cached = _SEARCH_CACHE.get(cache_key)
    if cached:
        cached_time = cached.get("_cached_at")
        if cached_time:
            if isinstance(cached_time, datetime):
                if (now - cached_time).total_seconds() < _SEARCH_TTL_SECONDS:
                    return APIResponse(
                        success=True,
                        message=f"Found {len(cached.get('data', []))} feedback items (cached)",
                        data=cached.get("data", [])
                    )
            elif isinstance(cached_time, str):
                cached_dt = datetime.fromisoformat(cached_time.replace('Z', '+00:00'))
                if (now - cached_dt).total_seconds() < _SEARCH_TTL_SECONDS:
                    return APIResponse(
                        success=True,
                        message=f"Found {len(cached.get('data', []))} feedback items (cached)",
                        data=cached.get("data", [])
                    )
    
    try:
        supabase = get_supabase()

        # Base filter
        query = supabase.table("citizen_feedback").select(
            "id, text, source, location, created_at"
        ).order("created_at", desc=True).limit(200)

        if sector:
            # If a sector filter is provided, join via separate call
            sc = supabase.table("sector_classification").select("feedback_id, primary_sector").eq("primary_sector", sector).limit(500).execute()
            ids = [r["feedback_id"] for r in (sc.data or [])]
            if ids:
                query = query.in_("id", ids[:1000])
            else:
                result = APIResponse(success=True, message="Found 0 feedback items", data=[])
                _SEARCH_CACHE[cache_key] = {"data": [], "_cached_at": now}
                return result

        if county:
            query = query.eq("location", county)

        base = query.execute().data or []

        # Simple hybrid scoring: term frequency + recency boost
        terms = [t.lower() for t in q.split()] if q else []
        now_tz = datetime.now(timezone.utc)
        scored = []
        for row in base:
            text = (row.get("text") or "")
            tlower = text.lower()
            tf = sum(tlower.count(t) for t in terms) if terms else 0
            # recency: decay by days
            ts = row.get("created_at") or ""
            try:
                if isinstance(ts, str):
                    dt = datetime.fromisoformat(ts.replace("Z","+00:00"))
                    # Ensure timezone-aware
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                else:
                    dt = now_tz
            except Exception:
                dt = now_tz
            # Both should be timezone-aware now
            days = max((now_tz - dt).total_seconds() / 86400.0, 0.0)
            recency = max(0.0, 5.0 - min(5.0, days))  # up to 5 points if within 0-5 days
            score = tf + recency

            # highlights & whyMatched
            highlights = []
            for t in terms:
                if t in tlower:
                    highlights.append(t)
            why = {
                "termFrequency": tf,
                "recentDays": round(days, 2),
                "recencyBoost": round(recency, 2),
                "explanation": f"Matched {tf} term(s); recency boost {round(recency,2)}"
            }
            scored.append({**row, "_score": score, "whyMatched": why, "highlights": list(set(highlights))})

        scored.sort(key=lambda r: r.get("_score", 0), reverse=True)
        data = scored[: max(1, min(limit, len(scored)))]

        # Cache the result
        _SEARCH_CACHE[cache_key] = {"data": data, "_cached_at": now}
        
        return APIResponse(
            success=True,
            message=f"Found {len(data)} feedback items",
            data=data
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
