"""
Report Service
Service for generating Citizen Pulse Reports

MANDATORY: All reports must be bilingual (English + Kiswahili)
Generated via Genkit/LLM as PDF/HTML
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.core.constants import VALID_CATEGORIES
from app.db.supabase import get_supabase, get_supabase_service
from app.services.ai_service import AIService
from app.services.genkit_service import GenkitService

logger = logging.getLogger(__name__)


class ReportService:
    """Service for generating Citizen Pulse Reports"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.supabase_service = get_supabase_service()  # Service role for inserts
        # Only initialize AI services if available (lazy import)
        try:
            from app.core.config import settings
            if settings.ENABLE_AI:
                self.ai_service = AIService()
                self.genkit_service = GenkitService()
            else:
                self.ai_service = None
                self.genkit_service = None
        except Exception:
            self.ai_service = None
            self.genkit_service = None
    
    async def generate_pulse_report(
        self,
        period: str = "weekly",
        language: str = "bilingual"  # MANDATORY: Always bilingual
    ) -> Dict[str, Any]:
        """
        Generate Citizen Pulse Report
        
        MANDATORY: Reports must be bilingual (English + Kiswahili)
        
        Args:
            period: "daily", "weekly", or "monthly"
            language: Always "bilingual" (enforced)
        """
        logger.info(f"Generating {period} Citizen Pulse Report (bilingual)")
        
        # Calculate date range
        if period == "daily":
            days = 1
        elif period == "weekly":
            days = 7
        else:  # monthly
            days = 30
        
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Get feedback data (only validated, categorized data)
        feedback_result = self.supabase.table("citizen_feedback").select(
            "*"
        ).eq("category_validated", True).eq("pii_removed", True).gte(
            "created_at", start_date
        ).execute()
        
        feedback_data = feedback_result.data or []
        
        # Get sentiment distribution
        sentiment_result = self.supabase.table("sentiment_scores").select(
            "sentiment"
        ).gte("analyzed_at", start_date).execute()
        
        sentiment_dist = {"positive": 0, "negative": 0, "neutral": 0}
        for item in sentiment_result.data:
            sent = item.get("sentiment", "neutral")
            if sent in sentiment_dist:
                sentiment_dist[sent] += 1
        
        # Get sector distribution (6 categories only)
        sector_result = self.supabase.table("sector_classification").select(
            "primary_sector"
        ).gte("classified_at", start_date).execute()
        
        sector_dist = {}
        for item in sector_result.data:
            sector = item.get("primary_sector")
            if sector in VALID_CATEGORIES:  # Only count valid categories
                sector_dist[sector] = sector_dist.get(sector, 0) + 1
        
        # Get top issues
        top_issues = sorted(sector_dist.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get urgency breakdown
        urgency_result = self.supabase.table("citizen_feedback").select(
            "urgency"
        ).gte("created_at", start_date).execute()
        
        urgency_dist = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        for item in urgency_result.data:
            urgency = item.get("urgency", "low")
            if urgency in urgency_dist:
                urgency_dist[urgency] += 1
        
        # Generate bilingual summary using Genkit (if available)
        summary_text = "\n\n".join([f.get("text", "")[:200] for f in feedback_data[:10]])
        
        if self.genkit_service:
            summaries = await self.genkit_service.generate_multilingual_summary(
                summary_text,
                ["en", "sw"]
            )
        else:
            # Fallback when AI is disabled - create simple summaries
            summaries = {
                "en": f"Citizen feedback analysis for {period} period. Total feedback: {len(feedback_data)}. Top sectors: {', '.join([s for s, _ in top_issues[:3]])}.",
                "sw": f"Uchambuzi wa maoni ya wananchi kwa kipindi cha {period}. Jumla ya maoni: {len(feedback_data)}. Sekta kuu: {', '.join([s for s, _ in top_issues[:3]])}."
            }
        
        # Generate policy recommendations
        recommendations = await self._generate_recommendations(top_issues, sector_dist)
        
        # Build report data to match schema (data is JSONB column)
        report_data = {
            "total_feedback": len(feedback_data),
            "sentiment_breakdown": sentiment_dist,
            "sector_distribution": sector_dist,
            "top_issues": [{"sector": s, "count": c} for s, c in top_issues],
            "urgency_distribution": urgency_dist,
            "policy_recommendations": recommendations,
            "start_date": start_date,
            "end_date": datetime.utcnow().isoformat()
        }
        
        # Build narrative from summaries
        narrative = f"{summaries.get('en', '')}\n\n{summaries.get('sw', '')}"
        
        # Build summaries JSONB
        summaries_json = {
            "en": summaries.get("en", ""),
            "sw": summaries.get("sw", "")
        }
        
        # Build key findings from top issues
        key_findings = [f"{sector}: {count} complaints" for sector, count in top_issues[:5]]
        
        # Build recommendations summary
        recommendations_summary = "\n".join([
            f"- {rec.get('recommendation', '')}" for rec in recommendations[:3]
        ])
        
        # Store report matching the schema
        # Note: language field must be 'en' or 'sw' per schema constraint, but we store bilingual content in summaries
        report = {
            "report_type": "citizen_pulse",
            "period": period,
            "language": "en",  # Schema constraint requires 'en' or 'sw', but summaries contain both
            "data": report_data,
            "narrative": narrative,
            "summaries": summaries_json,
            "key_findings": key_findings,
            "recommendations_summary": recommendations_summary
        }
        
        # Use service role client to bypass RLS for inserts
        self.supabase_service.table("pulse_reports").insert(report).execute()
        
        logger.info(f"Generated {period} Citizen Pulse Report (bilingual)")
        # Return formatted response data for API (not the database record)
        return {
            "period": period,
            "start_date": start_date,
            "end_date": datetime.utcnow().isoformat(),
            "total_feedback": len(feedback_data),
            "sentiment_breakdown": sentiment_dist,
            "sector_distribution": sector_dist,
            "top_issues": [{"sector": s, "count": c} for s, c in top_issues],
            "urgency_distribution": urgency_dist,
            "summary_en": summaries.get("en", ""),
            "summary_sw": summaries.get("sw", ""),
            "policy_recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat(),
            "language": "bilingual"
        }
    
    async def _generate_recommendations(
        self,
        top_issues: List[tuple],
        sector_dist: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """Generate policy recommendations based on top issues"""
        recommendations = []
        
        for sector, count in top_issues[:3]:
            recommendations.append({
                "sector": sector,
                "priority": "high" if count > 10 else "medium",
                "recommendation": f"Address {sector} concerns: {count} complaints require attention",
                "action_items": [
                    f"Review {sector} service delivery",
                    f"Engage with affected communities",
                    f"Implement targeted interventions"
                ]
            })
        
        return recommendations
    
    async def get_recent_reports(
        self,
        limit: int = 10,
        period: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recent Citizen Pulse Reports"""
        query = self.supabase_service.table("pulse_reports").select("*").order(
            "generated_at", desc=True
        ).limit(limit)
        
        if period:
            query = query.eq("period", period)
        
        result = query.execute()
        return result.data or []

    async def render_report_html(self, report_id: str) -> str:
        """Render a stored pulse report as a simple, shareable HTML page."""
        res = self.supabase.table("pulse_reports").select("*").eq("id", report_id).limit(1).execute()
        items = res.data or []
        if not items:
            raise ValueError("Report not found")

        r = items[0]
        period = r.get("period", "weekly")
        data = r.get("data", {})
        summary_en = r.get("summary_en") or data.get("summary_en", "")
        summary_sw = r.get("summary_sw") or data.get("summary_sw", "")
        sentiment = r.get("sentiment_breakdown") or data.get("sentiment_breakdown", {})
        top_issues = r.get("top_issues") or data.get("top_issues", [])
        total_feedback = r.get("total_feedback") or data.get("total_feedback", 0)
        gen_at = r.get("generated_at") or r.get("created_at") or datetime.utcnow().isoformat()

        def esc(s: Any) -> str:
            return (str(s) or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        issues_html = "".join(
            f"<li><strong>{esc(i.get('sector',''))}</strong>: {esc(i.get('count',0))}</li>" for i in (top_issues or [])
        )

        html = f"""
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>SautiAI – {esc(period.title())} Citizen Pulse Report</title>
    <style>
      body {{ font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 0; background: #f6f7f9; color: #222; }}
      .container {{ max-width: 900px; margin: 0 auto; padding: 24px; }}
      .card {{ background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); margin-bottom: 16px; }}
      .title {{ font-size: 28px; font-weight: 800; margin: 0 0 8px; background: linear-gradient(90deg,#2563eb,#7c3aed); -webkit-background-clip: text; color: transparent; }}
      .meta {{ color: #6b7280; font-size: 14px; margin-bottom: 16px; }}
      .grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 12px; }}
      .metric {{ background:#f1f5f9; border-radius:10px; padding:16px; }}
      .metric .label {{ font-size: 12px; color:#64748b; }}
      .metric .value {{ font-size: 22px; font-weight:700; color:#111827; }}
      h2 {{ font-size:18px; margin: 12px 0; }}
      ul {{ padding-left: 18px; }}
      .section {{ margin-top: 16px; }}
      .dual {{ display:grid; grid-template-columns: 1fr 1fr; gap:16px; }}
      @media (max-width: 640px) {{ .dual {{ grid-template-columns: 1fr; }} }}
      .footer {{ color:#6b728b; font-size:12px; text-align:center; margin-top:24px; }}
    </style>
  </head>
  <body>
    <div class=\"container\">
      <div class=\"card\">
        <h1 class=\"title\">SautiAI – {esc(period.title())} Citizen Pulse Report</h1>
        <div class=\"meta\">Generated: {esc(gen_at)}</div>
        <div class=\"grid\">
          <div class=\"metric\"><div class=\"label\">Total Feedback</div><div class=\"value\">{esc(total_feedback)}</div></div>
          <div class=\"metric\"><div class=\"label\">Positive</div><div class=\"value\">{esc(sentiment.get('positive',0))}</div></div>
          <div class=\"metric\"><div class=\"label\">Negative</div><div class=\"value\">{esc(sentiment.get('negative',0))}</div></div>
          <div class=\"metric\"><div class=\"label\">Neutral</div><div class=\"value\">{esc(sentiment.get('neutral',0))}</div></div>
        </div>
        <div class=\"section\">
          <h2>Top Issues</h2>
          <ul>{issues_html or '<li>No issues available</li>'}</ul>
        </div>
      </div>
      <div class=\"card dual\">
        <div>
          <h2>Summary (English)</h2>
          <p>{esc(summary_en) or 'No English summary available.'}</p>
        </div>
        <div>
          <h2>Muhtasari (Kiswahili)</h2>
          <p>{esc(summary_sw) or 'Hakuna muhtasari.'}</p>
        </div>
      </div>
      <div class=\"footer\">SautiAI – Voice of the People</div>
    </div>
  </body>
</html>
        """
        return html
