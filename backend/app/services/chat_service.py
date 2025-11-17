"""
Chat Service
Service for conversational interaction with the data using Vertex AI
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from app.db.supabase import get_supabase
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class ChatService:
    """Service for chat interactions with data"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.ai_service = AIService()
    
    async def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and generate a response
        
        Args:
            user_message: User's message
            conversation_history: Previous messages in the conversation
            
        Returns:
            Response with answer and relevant data
        """
        logger.info(f"Processing chat message: {user_message[:100]}")
        
        try:
            # Extract intent and entities from user message
            intent = self._extract_intent(user_message)
            entities = self._extract_entities(user_message)
            
            # Get relevant data based on intent and entities
            context_data = await self._get_context_data(intent, user_message, entities)
            
            # Generate response using Vertex AI
            response = await self._generate_response(
                user_message,
                context_data,
                conversation_history or [],
                intent
            )
            
            # Generate follow-up suggestions
            follow_ups = self._generate_follow_ups(intent, entities, context_data)
            
            return {
                "response": response,
                "intent": intent,
                "entities": entities,
                "data_points": context_data.get("summary", {}),
                "follow_ups": follow_ups,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing chat message: {e}", exc_info=True)
            return {
                "response": "I apologize, but I encountered an error processing your request. Please try again.",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _extract_intent(self, message: str) -> str:
        """Extract intent from user message - Enhanced for governance intelligence"""
        message_lower = message.lower()
        
        # Comparative queries (compare, vs, difference, better, worse)
        if any(word in message_lower for word in ['compare', 'vs', 'versus', 'difference', 'better', 'worse', 'more than', 'less than', 'higher', 'lower']):
            return "comparison"
        
        # Temporal queries (when, time period, specific dates)
        if any(word in message_lower for word in ['when', 'date', 'period', 'last week', 'last month', 'yesterday', 'today', 'this week', 'this month']):
            return "temporal"
        
        # Citizen Pulse / Policy Brief queries
        if any(word in message_lower for word in ['pulse', 'brief', 'policy brief', 'summary', 'overview', 'citizen pulse', 'report']):
            return "pulse"
        
        # Predictive Alert / Early Warning queries
        if any(word in message_lower for word in ['alert', 'warning', 'critical', 'urgent', 'emerging', 'risk', 'predictive', 'early warning']):
            return "alerts"
        
        # Sentiment queries
        if any(word in message_lower for word in ['sentiment', 'feeling', 'positive', 'negative', 'neutral', 'satisfaction', 'dissatisfaction', 'happy', 'unhappy', 'angry', 'frustrated']):
            return "sentiment"
        
        # Sector queries (governance-focused sectors)
        if any(word in message_lower for word in ['sector', 'category', 'health', 'healthcare', 'education', 'transport', 'governance', 'public service', 'infrastructure', 'security']):
            return "sector"
        
        # Hotspot / County queries
        if any(word in message_lower for word in ['county', 'location', 'where', 'region', 'hotspot', 'geographic', 'counties', 'nairobi', 'mombasa', 'kisumu']):
            return "location"
        
        # Trend queries
        if any(word in message_lower for word in ['trend', 'change', 'over time', 'recent', 'latest', 'emerging', 'developing', 'increasing', 'decreasing', 'improving', 'worsening']):
            return "trend"
        
        # Issue queries
        if any(word in message_lower for word in ['issue', 'problem', 'complaint', 'top', 'most', 'concern', 'grievance', 'challenge', 'difficulty']):
            return "issues"
        
        # Transparency / Responsiveness queries
        if any(word in message_lower for word in ['transparency', 'responsiveness', 'accountability', 'response time', 'government response', 'agency response', 'acknowledged', 'resolved']):
            return "transparency"
        
        # Count queries
        if any(word in message_lower for word in ['how many', 'count', 'total', 'number of', 'volume', 'quantity']):
            return "count"
        
        # Recommendation queries
        if any(word in message_lower for word in ['recommendation', 'recommend', 'suggestion', 'action', 'policy', 'what should', 'how to', 'what can be done']):
            return "recommendations"
        
        # Why/Explanation queries
        if any(word in message_lower for word in ['why', 'explain', 'reason', 'cause', 'because', 'what caused']):
            return "explanation"
        
        # What/Definition queries
        if message_lower.startswith('what') or message_lower.startswith('what is') or message_lower.startswith('what are'):
            return "definition"
        
        # General query
        return "general"
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities from user message (counties, sectors, dates, numbers)"""
        message_lower = message.lower()
        entities = {
            "counties": [],
            "sectors": [],
            "time_period": None,
            "numbers": [],
            "keywords": []
        }
        
        # Kenyan counties list
        kenyan_counties = [
            "nairobi", "mombasa", "kisumu", "nakuru", "eldoret", "thika", "malindi", "kitale",
            "garissa", "kakamega", "kisii", "meru", "nyeri", "machakos", "embu", "lamu",
            "kilifi", "kwale", "taita taveta", "tana river", "lamu", "turkana", "west pokot",
            "samburu", "trans nzoia", "uasin gishu", "elgeyo marakwet", "nandi", "baringo",
            "laikipia", "nakuru", "narok", "kajiado", "kericho", "bomet", "kakamega",
            "vihiga", "bungoma", "busia", "siaya", "kisumu", "homa bay", "migori",
            "kisii", "nyamira", "nyandarua", "murang'a", "kiambu", "kirinyaga", "nyeri",
            "kakamega", "baringo", "laikipia", "nakuru", "narok", "kajiado", "kericho"
        ]
        
        # Extract counties
        for county in kenyan_counties:
            if county in message_lower:
                entities["counties"].append(county.title())
        
        # Extract sectors
        sectors = ["health", "education", "transport", "governance", "infrastructure", 
                   "security", "water", "agriculture", "energy", "housing"]
        for sector in sectors:
            if sector in message_lower:
                entities["sectors"].append(sector)
        
        # Extract time periods
        time_patterns = {
            "today": 0,
            "yesterday": 1,
            "last week": 7,
            "last month": 30,
            "this week": 7,
            "this month": 30,
            "past week": 7,
            "past month": 30,
            "7 days": 7,
            "30 days": 30,
            "week": 7,
            "month": 30
        }
        
        for pattern, days in time_patterns.items():
            if pattern in message_lower:
                entities["time_period"] = days
                break
        
        # Extract numbers (for counts, limits, etc.)
        import re
        numbers = re.findall(r'\d+', message)
        if numbers:
            entities["numbers"] = [int(n) for n in numbers]
        
        # Extract important keywords
        important_keywords = ["urgent", "critical", "high", "low", "top", "worst", "best", 
                            "increasing", "decreasing", "improving", "worsening"]
        for keyword in important_keywords:
            if keyword in message_lower:
                entities["keywords"].append(keyword)
        
        return entities
    
    async def _get_context_data(self, intent: str, message: str, entities: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get relevant data based on intent - ENHANCED for deeper insights"""
        try:
            context = {}
            entities = entities or {}
            
            # Determine time period from entities or default to 7 days
            days = entities.get("time_period") or 7
            start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Extract counties and sectors from entities for filtering
            counties_filter = entities.get("counties", [])
            sectors_filter = entities.get("sectors", [])
            
            if intent == "sentiment" or intent == "comparison":
                # Get comprehensive sentiment data with detailed feedback
                sentiment_query = self.supabase.table("sentiment_scores").select(
                    "sentiment, feedback_id, analyzed_at, confidence, scores"
                ).gte("analyzed_at", start_date)
                
                # Apply county filter if specified
                if counties_filter:
                    # Get feedback IDs for specified counties first
                    # Use ilike for case-insensitive matching
                    county_fb_ids = []
                    for county in counties_filter:
                        fb_query = self.supabase.table("citizen_feedback").select("id").gte("created_at", start_date)
                        # Use ilike for case-insensitive county matching
                        try:
                            county_result = fb_query.ilike("location", f"%{county}%").execute()
                            county_fb_ids.extend([fb.get("id") for fb in (county_result.data or [])])
                        except:
                            # Fallback: try exact match
                            try:
                                county_result = fb_query.eq("location", county).execute()
                                county_fb_ids.extend([fb.get("id") for fb in (county_result.data or [])])
                            except:
                                pass
                    
                    if county_fb_ids:
                        # Remove duplicates
                        county_fb_ids = list(set(county_fb_ids))
                        if len(county_fb_ids) > 0:
                            # Split into chunks if too many (Supabase limit)
                            if len(county_fb_ids) > 1000:
                                county_fb_ids = county_fb_ids[:1000]
                            sentiment_query = sentiment_query.in_("feedback_id", county_fb_ids)
                
                sentiment_result = sentiment_query.execute()
                
                sentiment_dist = {"positive": 0, "negative": 0, "neutral": 0}
                sentiment_by_county = {}
                sentiment_by_sector = {}
                high_confidence_negative = []
                
                for item in sentiment_result.data:
                    sent = item.get("sentiment", "neutral")
                    if sent in sentiment_dist:
                        sentiment_dist[sent] += 1
                    
                    # Track high-confidence negative sentiment (early warning)
                    if sent == "negative" and item.get("confidence", 0) > 0.8:
                        high_confidence_negative.append(item.get("feedback_id"))
                
                # Get detailed feedback with cross-references
                feedback_ids = [item.get("feedback_id") for item in sentiment_result.data[:30] if item.get("feedback_id")]
                detailed_feedback = []
                if feedback_ids:
                    # Get feedback with full context
                    feedback_result = self.supabase.table("citizen_feedback").select(
                        "id, text, source, location, created_at, category, urgency"
                    ).in_("id", feedback_ids).execute()
                    
                    # Get sector classification for these feedback items
                    sector_result = self.supabase.table("sector_classification").select(
                        "feedback_id, primary_sector, confidence"
                    ).in_("feedback_id", feedback_ids).execute()
                    
                    sector_map = {s.get("feedback_id"): s.get("primary_sector") for s in sector_result.data}
                    
                    for fb in feedback_result.data or []:
                        fb_id = fb.get("id")
                        sentiment_item = next((s for s in sentiment_result.data if s.get("feedback_id") == fb_id), None)
                        
                        detailed_feedback.append({
                            "text": fb.get("text", "")[:200],  # First 200 chars
                            "sentiment": sentiment_item.get("sentiment") if sentiment_item else "unknown",
                            "confidence": sentiment_item.get("confidence", 0) if sentiment_item else 0,
                            "location": fb.get("location", "Unknown"),
                            "sector": sector_map.get(fb_id, "unknown"),
                            "urgency": fb.get("urgency", "low"),
                            "source": fb.get("source", "unknown"),
                            "date": fb.get("created_at", "")[:10]
                        })
                        
                        # Build county and sector breakdowns
                        county = fb.get("location", "Unknown")
                        sector = sector_map.get(fb_id, "unknown")
                        sent = sentiment_item.get("sentiment") if sentiment_item else "neutral"
                        
                        if county not in sentiment_by_county:
                            sentiment_by_county[county] = {"positive": 0, "negative": 0, "neutral": 0}
                        sentiment_by_county[county][sent] = sentiment_by_county[county].get(sent, 0) + 1
                        
                        if sector not in sentiment_by_sector:
                            sentiment_by_sector[sector] = {"positive": 0, "negative": 0, "neutral": 0}
                        sentiment_by_sector[sector][sent] = sentiment_by_sector[sector].get(sent, 0) + 1
                
                # Calculate percentages and insights
                total = sum(sentiment_dist.values())
                positive_pct = (sentiment_dist['positive'] / total * 100) if total > 0 else 0
                negative_pct = (sentiment_dist['negative'] / total * 100) if total > 0 else 0
                
                context["sentiment_distribution"] = sentiment_dist
                context["sentiment_percentages"] = {
                    "positive": round(positive_pct, 1),
                    "negative": round(negative_pct, 1),
                    "neutral": round(100 - positive_pct - negative_pct, 1)
                }
                context["detailed_feedback"] = detailed_feedback[:15]  # Top 15 examples
                context["sentiment_by_county"] = sentiment_by_county
                context["sentiment_by_sector"] = sentiment_by_sector
                context["high_confidence_negative_count"] = len(high_confidence_negative)
                context["total_analyzed"] = total
                context["summary"] = f"""Comprehensive sentiment analysis for last 7 days:
- Total analyzed: {total} feedback items
- Positive: {sentiment_dist['positive']} ({positive_pct:.1f}%) - indicates satisfied citizens
- Negative: {sentiment_dist['negative']} ({negative_pct:.1f}%) - indicates service delivery concerns
- Neutral: {sentiment_dist['neutral']} ({100-positive_pct-negative_pct:.1f}%) - factual reporting
- High-confidence negative concerns: {len(high_confidence_negative)} items requiring immediate attention
- Geographic coverage: {len(sentiment_by_county)} counties
- Sector breakdown available for {len(sentiment_by_sector)} sectors"""
            
            elif intent == "sector" or intent == "comparison":
                # Get sector distribution with county breakdown
                sector_query = self.supabase.table("sector_classification").select(
                    "primary_sector, feedback_id, classified_at"
                ).gte("classified_at", start_date)
                
                # Filter by specific sectors if mentioned
                if sectors_filter:
                    sector_query = sector_query.in_("primary_sector", sectors_filter)
                
                result = sector_query.execute()
                
                sector_dist = {}
                for item in result.data:
                    sector = item.get("primary_sector", "other")
                    sector_dist[sector] = sector_dist.get(sector, 0) + 1
                
                # Get county breakdown for sectors
                feedback_ids = [item.get("feedback_id") for item in result.data if item.get("feedback_id")]
                county_sector = {}
                if feedback_ids:
                    feedback_result = self.supabase.table("citizen_feedback").select(
                        "location, id"
                    ).in_("id", feedback_ids[:20]).execute()
                    for fb in feedback_result.data or []:
                        county = fb.get("location", "Unknown")
                        if county not in county_sector:
                            county_sector[county] = {}
                
                context["sector_distribution"] = sector_dist
                context["county_breakdown"] = county_sector
                context["summary"] = f"Sector classification for last 7 days: {', '.join([f'{k}: {v} complaints' for k, v in sorted(sector_dist.items(), key=lambda x: x[1], reverse=True)[:5]])}. Total classified: {sum(sector_dist.values())}."
            
            elif intent == "count" or intent == "comparison":
                # Get total feedback count with filters
                count_query = self.supabase.table("citizen_feedback").select(
                    "id", count="exact"
                ).gte("created_at", start_date)
                
                # Apply county filter
                if counties_filter:
                    # For count queries, we'll filter after if needed, or use a simpler approach
                    # Count queries with multiple counties are complex, so we'll handle in summary
                    pass  # Will be handled in summary generation
                
                result = count_query.execute()
                
                total = result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
                context["total_feedback"] = total
                context["summary"] = f"Total feedback in the last 7 days: {total}"
            
            elif intent == "issues" or intent == "comparison":
                # Get top issues with urgency and county data
                issues_query = self.supabase.table("sector_classification").select(
                    "primary_sector, feedback_id, classified_at"
                ).gte("classified_at", start_date)
                
                # Filter by sectors if specified
                if sectors_filter:
                    issues_query = issues_query.in_("primary_sector", sectors_filter)
                
                result = issues_query.execute()
                
                sector_counts = {}
                feedback_ids = []
                for item in result.data:
                    sector = item.get("primary_sector", "other")
                    sector_counts[sector] = sector_counts.get(sector, 0) + 1
                    if item.get("feedback_id"):
                        feedback_ids.append(item.get("feedback_id"))
                
                # Get urgency and county data for top issues
                top_issues = sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                issue_details = []
                if feedback_ids:
                    feedback_result = self.supabase.table("citizen_feedback").select(
                        "text, location, source, created_at, id"
                    ).in_("id", feedback_ids[:30]).execute()
                    
                    for sector, count in top_issues:
                        sector_feedback = [f for f in (feedback_result.data or []) if f.get("id") in feedback_ids[:10]]
                        issue_details.append({
                            "sector": sector,
                            "count": count,
                            "sample_complaints": [f.get("text", "")[:100] for f in sector_feedback[:3]],
                            "counties_affected": list(set([f.get("location", "Unknown") for f in sector_feedback if f.get("location")]))
                        })
                
                context["top_issues"] = top_issues
                context["issue_details"] = issue_details
                context["summary"] = f"Top issues identified: {', '.join([f'{sector} ({count} complaints)' for sector, count in top_issues])}. These represent the most frequently reported public service concerns."
            
            elif intent == "alerts":
                # Get recent alerts with details
                result = self.supabase.table("alerts").select(
                    "*"
                ).order("created_at", desc=True).limit(10).execute()
                
                alerts = result.data or []
                unacknowledged = [a for a in alerts if not a.get('acknowledged', False)]
                critical_alerts = [a for a in alerts if a.get('severity') == 'critical']
                
                context["alerts"] = alerts
                context["unacknowledged_count"] = len(unacknowledged)
                context["critical_count"] = len(critical_alerts)
                context["summary"] = f"Alert status: {len(alerts)} total alerts, {len(unacknowledged)} require attention, {len(critical_alerts)} critical. These represent early-warning signals for governance and public service issues."
            
            elif intent == "trend" or intent == "temporal" or intent == "comparison":
                # Get sentiment trends with early warning signals
                trend_days = entities.get("time_period") or 30
                trend_query = self.supabase.table("sentiment_scores").select(
                    "sentiment, analyzed_at, feedback_id"
                ).gte("analyzed_at", (datetime.utcnow() - timedelta(days=trend_days)).isoformat()).order("analyzed_at")
                
                result = trend_query.execute()
                
                trends = {}
                negative_clusters = []
                for item in result.data:
                    date = item["analyzed_at"][:10]
                    if date not in trends:
                        trends[date] = {"positive": 0, "negative": 0, "neutral": 0}
                    trends[date][item["sentiment"]] = trends[date].get(item["sentiment"], 0) + 1
                    
                    # Identify negative sentiment clusters (early warning)
                    if item["sentiment"] == "negative":
                        negative_clusters.append(date)
                
                # Calculate trend direction
                recent_days = list(trends.keys())[-7:] if len(trends) >= 7 else list(trends.keys())
                recent_negative = sum([trends[d].get("negative", 0) for d in recent_days])
                earlier_negative = sum([trends[d].get("negative", 0) for d in list(trends.keys())[:-7]]) if len(trends) > 7 else 0
                
                trend_direction = "increasing" if recent_negative > earlier_negative else "decreasing" if recent_negative < earlier_negative else "stable"
                
                context["trends"] = trends
                context["trend_direction"] = trend_direction
                context["negative_clusters"] = len(set(negative_clusters))
                context["summary"] = f"Sentiment trends over 30 days: {len(trends)} data points. Negative sentiment trend is {trend_direction}. Early warning: {len(set(negative_clusters))} days with negative sentiment clusters."
            
            elif intent == "pulse":
                # Get comprehensive Citizen Pulse report data - transforms scattered feedback into centralized intelligence
                feedback_result = self.supabase.table("citizen_feedback").select(
                    "id, text, location, source, created_at, category, urgency, language", count="exact"
                ).gte("created_at", start_date).execute()
                
                sentiment_result = self.supabase.table("sentiment_scores").select(
                    "sentiment, feedback_id, confidence"
                ).gte("analyzed_at", start_date).execute()
                
                sector_result = self.supabase.table("sector_classification").select(
                    "primary_sector, feedback_id"
                ).gte("classified_at", start_date).execute()
                
                total = feedback_result.count if hasattr(feedback_result, 'count') else len(feedback_result.data) if feedback_result.data else 0
                
                sentiment_dist = {"positive": 0, "negative": 0, "neutral": 0}
                high_urgency_negative = 0
                for item in sentiment_result.data:
                    sent = item.get("sentiment", "neutral")
                    if sent in sentiment_dist:
                        sentiment_dist[sent] += 1
                
                # Cross-reference with urgency levels
                feedback_data = feedback_result.data or []
                sector_map = {s.get("feedback_id"): s.get("primary_sector") for s in sector_result.data}
                
                for fb in feedback_data:
                    if fb.get("urgency") in ["high", "critical"]:
                        fb_id = fb.get("id")
                        sent_item = next((s for s in sentiment_result.data if s.get("feedback_id") == fb_id), None)
                        if sent_item and sent_item.get("sentiment") == "negative":
                            high_urgency_negative += 1
                
                sector_dist = {}
                county_dist = {}
                language_dist = {}
                source_dist = {}
                
                for item in sector_result.data:
                    sector = item.get("primary_sector", "other")
                    sector_dist[sector] = sector_dist.get(sector, 0) + 1
                
                # County-level and language aggregation (showing scattered → centralized)
                for fb in feedback_data:
                    county = fb.get("location", "Unknown")
                    if county:
                        county_dist[county] = county_dist.get(county, 0) + 1
                    lang = fb.get("language", "en")
                    language_dist[lang] = language_dist.get(lang, 0) + 1
                    source = fb.get("source", "unknown")
                    source_dist[source] = source_dist.get(source, 0) + 1
                
                top_issues = sorted(sector_dist.items(), key=lambda x: x[1], reverse=True)[:5]
                top_counties = sorted(county_dist.items(), key=lambda x: x[1], reverse=True)[:5]
                
                # Get sample feedback for policy brief
                sample_feedback = []
                for fb in feedback_data[:10]:
                    fb_id = fb.get("id")
                    sent_item = next((s for s in sentiment_result.data if s.get("feedback_id") == fb_id), None)
                    sector_item = sector_map.get(fb_id, "unknown")
                    sample_feedback.append({
                        "text": fb.get("text", "")[:150],
                        "county": fb.get("location", "Unknown"),
                        "sector": sector_item,
                        "sentiment": sent_item.get("sentiment") if sent_item else "neutral",
                        "urgency": fb.get("urgency", "low"),
                        "source": fb.get("source", "unknown"),
                        "language": fb.get("language", "en")
                    })
                
                context["pulse_data"] = {
                    "total_feedback": total,
                    "sentiment_breakdown": sentiment_dist,
                    "top_issues": [{"sector": s, "count": c} for s, c in top_issues],
                    "top_counties": [{"county": c, "count": cnt} for c, cnt in top_counties],
                    "high_urgency_negative": high_urgency_negative,
                    "sample_feedback": sample_feedback,
                    "period": "7 days",
                    "platforms_aggregated": len(source_dist),
                    "languages_processed": language_dist,
                    "counties_covered": len(county_dist)
                }
                context["summary"] = f"""Citizen Pulse Report (7 days) - Centralized Intelligence from Scattered Sources:
- Total feedback aggregated: {total} items from {len(source_dist)} scattered platforms (social media, county forums, feedback portals)
- Negative concerns requiring attention: {sentiment_dist['negative']} ({sentiment_dist['negative']/total*100 if total > 0 else 0:.1f}%)
- High-urgency negative issues: {high_urgency_negative} - immediate policy action needed
- Top sectors: {', '.join([f'{s} ({c})' for s, c in top_issues[:3]])}
- Top counties: {', '.join([f'{c} ({cnt})' for c, cnt in top_counties[:3]])}
- Languages processed: {', '.join([f'{k} ({v})' for k, v in language_dist.items()])} - ensuring no voice lost
- Counties covered: {len(county_dist)} of 47 counties
- This centralized aggregation transforms unstructured, multilingual feedback into real-time insights enabling faster, data-informed governance decisions"""
            
            elif intent == "recommendations":
                # Get data for policy recommendations
                sector_result = self.supabase.table("sector_classification").select(
                    "primary_sector, feedback_id"
                ).gte("classified_at", start_date).execute()
                
                sector_counts = {}
                for item in sector_result.data:
                    sector = item.get("primary_sector", "other")
                    sector_counts[sector] = sector_counts.get(sector, 0) + 1
                
                top_sectors = sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                
                context["recommendation_data"] = {
                    "top_sectors": [{"sector": s, "complaint_count": c} for s, c in top_sectors],
                    "total_complaints": sum(sector_counts.values())
                }
                context["summary"] = f"Policy recommendation context: Top sectors requiring attention are {', '.join([f'{s} ({c} complaints)' for s, c in top_sectors])}. These represent priority areas for governance improvements."
            
            elif intent == "transparency":
                # Get transparency and responsiveness metrics
                # Note: This would ideally track government response times and acknowledgment
                # For now, we track alert acknowledgment as a proxy
                alerts_result = self.supabase.table("alerts").select(
                    "*"
                ).gte("created_at", start_date).execute()
                
                total_alerts = len(alerts_result.data or [])
                acknowledged = len([a for a in alerts_result.data if a.get("acknowledged", False)])
                response_rate = (acknowledged / total_alerts * 100) if total_alerts > 0 else 0
                
                # Get feedback by source to show aggregation from scattered platforms
                feedback_result = self.supabase.table("citizen_feedback").select(
                    "source, location, created_at"
                ).gte("created_at", start_date).execute()
                
                sources = {}
                for item in feedback_result.data or []:
                    source = item.get("source", "unknown")
                    sources[source] = sources.get(source, 0) + 1
                
                context["transparency_metrics"] = {
                    "total_alerts": total_alerts,
                    "acknowledged_alerts": acknowledged,
                    "response_rate": round(response_rate, 1),
                    "platforms_aggregated": len(sources),
                    "total_feedback_aggregated": len(feedback_result.data or [])
                }
                context["source_breakdown"] = sources
                context["summary"] = f"Transparency and Responsiveness Metrics (7 days): {total_alerts} alerts generated, {acknowledged} acknowledged ({response_rate:.1f}% response rate). Feedback aggregated from {len(sources)} scattered platforms into centralized intelligence. This enables tracking of government responsiveness and highlights accountability gaps."
            
            elif intent == "comparison":
                # For comparison queries, get data for both entities being compared
                context["comparison_mode"] = True
                context["entities"] = entities
                # Will be handled by the prompt to generate comparative analysis
                feedback_result = self.supabase.table("citizen_feedback").select(
                    "id, source, location, created_at, text, language", count="exact"
                ).gte("created_at", start_date).execute()
                
                total = feedback_result.count if hasattr(feedback_result, 'count') else len(feedback_result.data) if feedback_result.data else 0
                context["total_feedback"] = total
                context["summary"] = f"Comparison data retrieved for analysis. Total feedback: {total} items over {days} days."
            
            elif intent == "explanation":
                # For "why" questions, get detailed context with cause-effect relationships
                sentiment_result = self.supabase.table("sentiment_scores").select(
                    "sentiment, feedback_id, analyzed_at, confidence"
                ).gte("analyzed_at", start_date).execute()
                
                sector_result = self.supabase.table("sector_classification").select(
                    "primary_sector, feedback_id"
                ).gte("classified_at", start_date).execute()
                
                # Get detailed feedback for explanation
                feedback_ids = [s.get("feedback_id") for s in sentiment_result.data[:50] if s.get("feedback_id")]
                if feedback_ids:
                    feedback_result = self.supabase.table("citizen_feedback").select(
                        "id, text, location, source, created_at, urgency"
                    ).in_("id", feedback_ids).execute()
                    
                    context["detailed_feedback"] = feedback_result.data or []
                    context["sector_map"] = {s.get("feedback_id"): s.get("primary_sector") for s in sector_result.data}
                    context["summary"] = f"Detailed feedback retrieved for explanation analysis. {len(feedback_result.data or [])} items analyzed."
            
            else:
                # General context - get comprehensive overview showing transformation from scattered to centralized
                feedback_query = self.supabase.table("citizen_feedback").select(
                    "id, source, location, created_at, text, language", count="exact"
                ).gte("created_at", start_date)
                
                # Apply filters if specified
                if counties_filter and len(counties_filter) > 0:
                    # Use first county for filtering (Supabase doesn't support multiple OR easily)
                    try:
                        feedback_query = feedback_query.ilike("location", f"%{counties_filter[0]}%")
                    except:
                        pass
                
                feedback_result = feedback_query.execute()
                
                total = feedback_result.count if hasattr(feedback_result, 'count') else len(feedback_result.data) if feedback_result.data else 0
                
                # Get source breakdown (showing aggregation from scattered platforms)
                sources = {}
                counties = {}
                languages = {}
                for item in (feedback_result.data or [])[:100]:
                    source = item.get("source", "unknown")
                    sources[source] = sources.get(source, 0) + 1
                    county = item.get("location")
                    if county:
                        counties[county] = counties.get(county, 0) + 1
                    lang = item.get("language", "en")
                    languages[lang] = languages.get(lang, 0) + 1
                
                context["total_feedback"] = total
                context["source_breakdown"] = sources
                context["county_coverage"] = len(counties)
                context["language_breakdown"] = languages
                context["summary"] = f"""Comprehensive Overview - Transforming Scattered Feedback into Centralized Intelligence:
- Total feedback aggregated: {total} items from {len(sources)} scattered platforms (social media, county forums, feedback portals)
- Counties covered: {len(counties)} of 47 counties - enabling county-specific governance insights
- Languages processed: {', '.join([f'{k} ({v})' for k, v in languages.items()])} - ensuring no voice is lost due to language barriers
- This centralized aggregation enables real-time analysis that prevents genuine public concerns from being lost in noise
- Policymakers now have timely, data-driven insights to make faster, data-informed decisions
- Citizens' voices are being heard and transformed into actionable governance intelligence"""
            
            # Add entity information to context
            if entities:
                context["extracted_entities"] = entities
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting context data: {e}")
            return {"summary": "Unable to retrieve data", "error": str(e)}
    
    async def _generate_response(
        self,
        user_message: str,
        context_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        intent: Optional[str] = None
    ) -> str:
        """Generate response using Vertex AI"""
        try:
            # Check if user wants structured JSON response
            wants_json = any(word in user_message.lower() for word in ['json', 'structured', 'format', 'data structure'])
            wants_swahili = any(word in user_message.lower() for word in ['kiswahili', 'swahili', 'sw', 'translate'])
            
            # Build prompt with context and intent
            prompt = self._build_prompt(user_message, context_data, conversation_history, intent or "general")
            
            # Add JSON format instruction if requested
            if wants_json:
                prompt += "\n\nIMPORTANT: The user requested structured data. Provide your response in JSON format with the following structure:\n{\n  \"summary\": \"...\",\n  \"top_issues\": [...],\n  \"sentiment_breakdown\": {...},\n  \"policy_recommendations\": [...],\n  \"swahili_translation\": \"...\"\n}\n"
            
            # Use Vertex AI to generate response - try direct API first, then SDK, then REST API
            # Check if using direct Generative AI API
            if hasattr(self.ai_service, 'use_direct_api') and self.ai_service.use_direct_api and self.ai_service.model:
                try:
                    response = self.ai_service.model.generate_content(prompt)
                    response_text = response.text.strip()
                    logger.info("Response generated using Direct Generative AI API")
                    
                    # If Swahili requested, add translation
                    if wants_swahili and not wants_json:
                        try:
                            swahili_prompt = f"Translate the following English text to Kiswahili. Keep the same meaning and tone:\n\n{response_text}"
                            swahili_response = self.ai_service.model.generate_content(swahili_prompt)
                            response_text += f"\n\n--- Kiswahili Translation ---\n{swahili_response.text.strip()}"
                        except Exception as e:
                            logger.warning(f"Could not generate Swahili translation: {e}")
                    
                    return response_text
                except Exception as e:
                    logger.warning(f"Direct API call failed: {e}, trying Vertex AI SDK...")
            
            # Try Vertex AI SDK
            if self.ai_service.model:
                try:
                    response = self.ai_service.model.generate_content(prompt)
                    response_text = response.text.strip()
                    logger.info("Response generated using Vertex AI SDK")
                    
                    # If Swahili requested, add translation
                    if wants_swahili and not wants_json:
                        try:
                            swahili_prompt = f"Translate the following English text to Kiswahili. Keep the same meaning and tone:\n\n{response_text}"
                            swahili_response = self.ai_service.model.generate_content(swahili_prompt)
                            response_text += f"\n\n--- Kiswahili Translation ---\n{swahili_response.text.strip()}"
                        except Exception as e:
                            logger.warning(f"Could not generate Swahili translation: {e}")
                    
                    return response_text
                except Exception as e:
                    logger.warning(f"SDK model call failed: {e}, trying REST API...")
                    # Fall through to REST API or fallback
            
            # Try REST API if SDK failed
            if hasattr(self.ai_service, 'use_rest_api') and self.ai_service.use_rest_api:
                try:
                    response_text = await self._generate_response_via_rest_api(prompt)
                    if response_text:
                        return response_text
                except Exception as e:
                    logger.warning(f"REST API call failed: {e}, using fallback...")
            
            # Fallback response if both SDK and REST API fail
            return self._generate_fallback_response(user_message, context_data)
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Fallback response
            return self._generate_fallback_response(user_message, context_data)
    
    def _build_prompt(
        self,
        user_message: str,
        context_data: Dict[str, Any],
        conversation_history: List[Dict[str, str]],
        intent: str = "general"
    ) -> str:
        """Build prompt for Vertex AI"""
        prompt = """You are **Sauti AI – Voice of the People**, an expert civic-intelligence assistant designed to help users and policymakers understand real-time citizen concerns in Kenya.

You analyze:
- Citizen feedback from Supabase datasets
- Text collected by Jaseci OSP agents (web-scraped posts, public comments, county service reviews)
- Public service issues across all 47 counties
- Sentiment, urgency, and sector categories
- Kiswahili + English text

YOUR OBJECTIVES (ALIGNED WITH SAUTI AI MISSION):
1. **Transform scattered citizen feedback into centralized governance intelligence** - Aggregate and analyze feedback from multiple platforms (social media, county forums, feedback portals) into actionable insights.

2. **Provide real-time insights into citizen sentiment and emerging issues** - Enable policymakers to understand public concerns as they develop, not after they escalate.

3. **Generate actionable policy briefs** - Create summaries with specific recommendations for policymakers, addressing the governance gaps caused by delayed decisions.

4. **Detect predictive alerts and early-warning signals** - Identify potential governance risks or emerging citizen dissatisfaction before they escalate, using rapid rise in complaints and negative sentiment clusters.

5. **Support transparency and accountability** - Help track responsiveness of government agencies to issues, highlighting accountability gaps.

6. **Handle multilingual content** - Process English, Kiswahili, and local dialects seamlessly, ensuring no citizen voice is lost due to language barriers.

7. **Provide county and sector-specific insights** - Enable targeted interventions by identifying hotspots in specific counties (all 47 counties) and sectors (health, education, public services, infrastructure, security, governance).

8. **Create Citizen Pulse summaries** - Generate weekly or daily summaries that transform raw feedback into usable governance intelligence.

9. **Bridge the gap between citizens and policymakers** - Ensure citizens feel heard by providing evidence that their concerns are being analyzed and acted upon.

BEHAVIOR REQUIREMENTS:
- Be neutral, factual, and non-political.
- Never guess facts about individuals.
- Respect Kenyan Data Protection Act principles.
- Always anonymize explanations ("citizens reported…", not personal data).
- If asked for data analysis, generate structured JSON summaries:
  {
    "summary": "...",
    "top_issues": [...],
    "sentiment_breakdown": {...},
    "policy_recommendations": [...],
    "swahili_translation": "..."
  }

CHAT BEHAVIOR (GOVERNANCE-FOCUSED):
- **Act as a civic intelligence advisor** - Explain insights clearly, like a smart policymaker advisor who understands both citizen concerns and governance constraints. Be conversational, knowledgeable, and helpful.

- **Answer the actual question** - Read the user's question carefully and answer it directly. Don't give generic overviews when they ask specific questions.

- **Use data strategically** - Don't dump all the data. Select the most relevant data points that answer the question and use them to support your analysis.

- **Be analytical, not descriptive** - Don't just describe what the data shows. Explain what it means, why it matters, and what patterns you see.

- **Provide context** - Help users understand the significance of the data. Is this normal? Is this concerning? What does this trend indicate?

- **Use specific examples** - When making a point, back it up with actual feedback examples from the data. This makes your response credible and concrete.

- **Think critically** - Identify patterns, anomalies, and insights that aren't immediately obvious from just listing the numbers.

- **Be actionable** - Always end with what should be done based on the findings. Give specific, practical recommendations.

If a question is outside Kenyan governance, service delivery, or public issues domain, answer normally but briefly, then redirect to how Sauti AI can help with civic intelligence.

YOU MUST:
- Read and understand the user's specific question
- Answer that question directly using relevant data from context
- Provide analysis, not just data dumps
- Use specific examples to support your points
- Be conversational and helpful, not robotic

"""
        
        # Add comprehensive context data
        prompt += "═══════════════════════════════════════════════════════════\n"
        prompt += "DETAILED CONTEXT DATA FROM DATABASE:\n"
        prompt += "═══════════════════════════════════════════════════════════\n\n"
        prompt += context_data.get("summary", "No specific data available")
        
        # Add detailed sentiment analysis with examples
        if context_data.get("sentiment_distribution"):
            dist = context_data["sentiment_distribution"]
            pct = context_data.get("sentiment_percentages", {})
            prompt += f"\n\n📊 SENTIMENT BREAKDOWN:\n"
            prompt += f"- Positive: {dist.get('positive', 0)} items ({pct.get('positive', 0)}%) - Citizens expressing satisfaction\n"
            prompt += f"- Negative: {dist.get('negative', 0)} items ({pct.get('negative', 0)}%) - Service delivery concerns\n"
            prompt += f"- Neutral: {dist.get('neutral', 0)} items ({pct.get('neutral', 0)}%) - Factual reporting\n"
            
            if context_data.get("detailed_feedback"):
                prompt += f"\n📝 SPECIFIC FEEDBACK EXAMPLES (Use these in your response):\n"
                for i, fb in enumerate(context_data["detailed_feedback"][:10], 1):
                    prompt += f"\n{i}. [{fb.get('sentiment', 'unknown').upper()}] {fb.get('text', '')}\n"
                    prompt += f"   Location: {fb.get('location', 'Unknown')} | Sector: {fb.get('sector', 'unknown')} | Urgency: {fb.get('urgency', 'low')}\n"
            
            if context_data.get("sentiment_by_county"):
                prompt += f"\n🗺️ GEOGRAPHIC BREAKDOWN:\n"
                top_counties = sorted(
                    context_data["sentiment_by_county"].items(),
                    key=lambda x: x[1].get("negative", 0),
                    reverse=True
                )[:5]
                for county, sents in top_counties:
                    prompt += f"- {county}: {sents.get('negative', 0)} negative, {sents.get('positive', 0)} positive, {sents.get('neutral', 0)} neutral\n"
            
            if context_data.get("sentiment_by_sector"):
                prompt += f"\n🏛️ SECTOR BREAKDOWN:\n"
                for sector, sents in context_data["sentiment_by_sector"].items():
                    prompt += f"- {sector}: {sents.get('negative', 0)} negative, {sents.get('positive', 0)} positive, {sents.get('neutral', 0)} neutral\n"
            
            if context_data.get("high_confidence_negative_count", 0) > 0:
                prompt += f"\n⚠️ EARLY WARNING: {context_data['high_confidence_negative_count']} high-confidence negative concerns identified - these require immediate policy attention.\n"
        
        # Add sector distribution with details
        if context_data.get("sector_distribution"):
            sectors = context_data["sector_distribution"]
            prompt += f"\n\n📋 SECTOR DISTRIBUTION:\n"
            sorted_sectors = sorted(sectors.items(), key=lambda x: x[1], reverse=True)
            for sector, count in sorted_sectors[:6]:
                prompt += f"- {sector}: {count} complaints\n"
        
        # Add top issues with details
        if context_data.get("top_issues"):
            prompt += f"\n\n🔥 TOP ISSUES:\n"
            for sector, count in context_data["top_issues"][:5]:
                prompt += f"- {sector}: {count} complaints\n"
        
        if context_data.get("issue_details"):
            prompt += f"\n📋 DETAILED ISSUE ANALYSIS:\n"
            for issue in context_data["issue_details"][:3]:
                prompt += f"\n{issue.get('sector', 'Unknown')} ({issue.get('count', 0)} complaints):\n"
                prompt += f"  Counties affected: {', '.join(issue.get('counties_affected', [])[:5])}\n"
                if issue.get("sample_complaints"):
                    prompt += f"  Sample complaints:\n"
                    for comp in issue.get("sample_complaints", [])[:2]:
                        prompt += f"    - {comp}\n"
        
        # Add alerts with details
        if context_data.get("alerts"):
            alerts = context_data["alerts"]
            prompt += f"\n\n🚨 ALERTS STATUS:\n"
            prompt += f"- Total alerts: {len(alerts)}\n"
            prompt += f"- Unacknowledged: {context_data.get('unacknowledged_count', 0)}\n"
            prompt += f"- Critical: {context_data.get('critical_count', 0)}\n"
            if alerts:
                prompt += f"\nRecent critical alerts:\n"
                for alert in alerts[:3]:
                    prompt += f"- [{alert.get('severity', 'unknown')}] {alert.get('title', 'No title')}: {alert.get('description', '')[:100]}\n"
        
        # Add trend analysis
        if context_data.get("trends"):
            prompt += f"\n\n📈 TREND ANALYSIS:\n"
            prompt += f"- Trend direction: {context_data.get('trend_direction', 'stable')}\n"
            prompt += f"- Negative sentiment clusters: {context_data.get('negative_clusters', 0)} days\n"
            if context_data.get("trend_direction") == "increasing":
                prompt += f"⚠️ WARNING: Negative sentiment is increasing - this indicates deteriorating public satisfaction.\n"
        
        # Add total feedback context
        if context_data.get("total_feedback"):
            prompt += f"\n\n📊 OVERALL STATISTICS:\n"
            prompt += f"- Total feedback items: {context_data['total_feedback']}\n"
            if context_data.get("source_breakdown"):
                prompt += f"- Data sources: {', '.join(context_data['source_breakdown'].keys())}\n"
            if context_data.get("county_coverage"):
                prompt += f"- Counties covered: {context_data['county_coverage']}\n"
        
        prompt += "\n═══════════════════════════════════════════════════════════\n\n"
        
        # Add conversation history
        if conversation_history:
            prompt += "CONVERSATION HISTORY:\n"
            for msg in conversation_history[-3:]:  # Last 3 messages
                # Support both formats: {"user": "...", "assistant": "..."} and {"role": "user", "content": "..."}
                if msg.get('user'):
                    prompt += f"User: {msg.get('user', '')}\n"
                elif msg.get('role') == 'user' and msg.get('content'):
                    prompt += f"User: {msg.get('content', '')}\n"
                
                if msg.get('assistant'):
                    prompt += f"Assistant: {msg.get('assistant', '')}\n"
                elif msg.get('role') == 'assistant' and msg.get('content'):
                    prompt += f"Assistant: {msg.get('content', '')}\n"
            prompt += "\n"
        
        # Add entity information to prompt
        if context_data.get("extracted_entities"):
            entities = context_data["extracted_entities"]
            prompt += f"\n\n🎯 EXTRACTED ENTITIES FROM QUESTION:\n"
            if entities.get("counties"):
                prompt += f"- Counties mentioned: {', '.join(entities['counties'])}\n"
            if entities.get("sectors"):
                prompt += f"- Sectors mentioned: {', '.join(entities['sectors'])}\n"
            if entities.get("time_period"):
                prompt += f"- Time period: Last {entities['time_period']} days\n"
            if entities.get("keywords"):
                prompt += f"- Key modifiers: {', '.join(entities['keywords'])}\n"
        
        prompt += f"\nCURRENT USER QUESTION: {user_message}\n\n"
        
        # Add specific instructions based on intent
        intent_instructions = {
            "comparison": """
⚠️ COMPARISON MODE - CRITICAL INSTRUCTIONS:
- You MUST compare the entities mentioned (counties, sectors, time periods, etc.)
- Create a clear side-by-side comparison with specific numbers
- Calculate and show percentage differences
- Identify which entity has better/worse performance and WHY
- Use specific examples from each entity to illustrate differences
- Explain what the comparison reveals about governance/service delivery
- Format: "Nairobi vs Mombasa: [metric 1] (Nairobi: X, Mombasa: Y, difference: Z%), [metric 2]..."
- Don't just list data - analyze what the differences mean
""",
            "temporal": """
📅 TEMPORAL MODE - CRITICAL INSTRUCTIONS:
- Show clear timeline: "In [period 1], [metric] was X. In [period 2], it changed to Y (Z% change)"
- Identify when significant changes occurred
- Explain what caused the changes based on feedback patterns
- Show trends: "The data shows a [increasing/decreasing/stable] trend over [time period]"
- Compare periods: "Compared to [previous period], [current period] shows [change]"
- Use specific dates/periods from the data
""",
            "explanation": """
❓ EXPLANATION MODE - CRITICAL INSTRUCTIONS:
- You MUST explain WHY something is happening, not just describe WHAT is happening
- Use root cause analysis: "The high number of complaints in health sector is likely due to: [reason 1], [reason 2], [reason 3]"
- Support each reason with specific feedback examples: "This is evidenced by complaints such as: '[quote example]'"
- Identify contributing factors: "Contributing factors include: [factor 1] (seen in X% of complaints), [factor 2] (mentioned in Y feedback items)"
- Explain patterns: "The feedback reveals a pattern of [pattern], which suggests [explanation]"
- Be analytical: Don't just say "there are many complaints" - explain WHY there are many complaints
""",
            "definition": """
📖 DEFINITION MODE - CRITICAL INSTRUCTIONS:
- Provide clear, comprehensive definitions
- Use examples from the actual data to illustrate
- Explain context: "In the context of Sauti AI, [term] refers to..."
- Show how it's used: "For example, when we analyze [term], we look at [specific data points]"
- Make it educational but practical
"""
        }
        
        if intent_instructions.get(intent):
            prompt += intent_instructions[intent]
        
        prompt += """═══════════════════════════════════════════════════════════
CRITICAL INSTRUCTIONS FOR RESPONSE QUALITY:
═══════════════════════════════════════════════════════════════════

**MOST IMPORTANT: ANSWER THE USER'S ACTUAL QUESTION DIRECTLY**

The user asked: "{user_message}"

DO NOT give a generic overview. DO NOT repeat the context summary verbatim. 
ANSWER THE SPECIFIC QUESTION using the data provided.

RESPONSE REQUIREMENTS:

1. **DIRECT ANSWER FIRST**: Start by directly answering the question in 1-2 sentences. If they ask "Why is health sector receiving complaints?", immediately explain WHY based on the data.

2. **USE ACTUAL DATA FROM CONTEXT**: 
   - If sentiment data is provided, use the EXACT numbers and percentages
   - If feedback examples are provided, QUOTE them or paraphrase specific complaints
   - If sector breakdown is provided, reference the EXACT counts
   - If county data is provided, name the specific counties and their numbers

3. **BE ANALYTICAL, NOT DESCRIPTIVE**:
   - Don't just say "there are 50 health complaints"
   - Say "Health sector has 50 complaints (32% of total), with the majority (35 complaints) related to [specific issue from feedback examples]. This represents a 15% increase from the previous period, indicating a growing concern."
   - Explain WHAT the data means, WHY it matters, and WHAT it indicates

4. **FOR "WHY" QUESTIONS**: 
   - Provide root cause analysis using the feedback examples
   - Identify patterns: "Common themes in health complaints include: [list 3-4 specific issues from feedback]"
   - Explain contributing factors: "This may be due to [factor 1], [factor 2], as evidenced by [specific feedback example]"

5. **FOR COMPARISON QUESTIONS**:
   - Create a side-by-side comparison table in your response
   - Highlight specific differences with numbers
   - Explain what the differences mean: "Nairobi has 30% more negative sentiment than Mombasa, primarily driven by [specific sector/issue]"

6. **FOR TEMPORAL QUESTIONS**:
   - Show the trend clearly: "Over the last 30 days, sentiment has [improved/worsened] from X% to Y%"
   - Identify when changes occurred: "The shift occurred around [date/period] when [specific event/pattern]"
   - Explain what caused the change based on feedback patterns

7. **USE FEEDBACK EXAMPLES STRATEGICALLY**:
   - Quote 2-3 specific feedback examples that illustrate your point
   - Format: "For example, one citizen reported: '[quote]' (Location: [county], Sector: [sector])"
   - Use examples to support your analysis, not just list them

8. **PROVIDE INSIGHTS, NOT JUST DATA**:
   - What patterns do you see? "The data reveals three key patterns: [pattern 1], [pattern 2], [pattern 3]"
   - What are the implications? "This suggests that [implication] which could lead to [outcome]"
   - What should be prioritized? "Priority should be given to [specific issue] because [reason based on data]"

9. **STRUCTURE FOR CLARITY**:
   - **Direct Answer** (1-2 sentences answering the question)
   - **Key Findings** (3-5 bullet points with specific data)
   - **Analysis** (explain what the data means, patterns, trends)
   - **Examples** (2-3 specific feedback quotes that illustrate the point)
   - **Recommendations** (actionable next steps based on findings)

10. **BE CONVERSATIONAL BUT PRECISE**:
    - Write like a knowledgeable advisor, not a robot
    - Use natural language: "Based on the data, it appears that..." not "The data indicates that..."
    - Show understanding: "This is concerning because..." or "This is positive as it suggests..."

11. **ACKNOWLEDGE LIMITATIONS WHEN RELEVANT**:
    - If data is limited: "While the dataset shows [X], we should note that [limitation]. However, the available data suggests [insight]."
    - If question can't be fully answered: "I can't provide a complete answer to [part of question] because [reason], but based on available data, [what we can say]."

12. **AVOID THESE MISTAKES**:
    - ❌ Don't repeat the context summary verbatim
    - ❌ Don't give generic responses that could apply to any question
    - ❌ Don't ignore the specific question asked
    - ❌ Don't list data without analysis
    - ❌ Don't use vague statements without backing them up with specific examples

RESPONSE FORMAT:
- **Direct Answer**: 1-2 sentences
- **Detailed Analysis**: 150-300 words with specific data, examples, and insights
- **Recommendations**: 3-5 actionable items
- **Total**: Minimum 200 words, but be comprehensive

NOW PROVIDE YOUR INTELLIGENT, DATA-DRIVEN RESPONSE TO THE USER'S QUESTION:""".format(user_message=user_message)
        
        return prompt
    
    def _generate_follow_ups(self, intent: str, entities: Dict[str, Any], context_data: Dict[str, Any]) -> List[str]:
        """Generate intelligent follow-up question suggestions"""
        follow_ups = []
        
        if intent == "sentiment":
            follow_ups.extend([
                "Which counties have the most negative sentiment?",
                "What sectors are causing the most dissatisfaction?",
                "Show me examples of negative feedback"
            ])
        elif intent == "sector":
            follow_ups.extend([
                "Which counties have the most complaints in this sector?",
                "What's the sentiment breakdown for this sector?",
                "What are the top issues in this sector?"
            ])
        elif intent == "issues":
            follow_ups.extend([
                "Which counties are most affected by these issues?",
                "What's the urgency level of these issues?",
                "What actions should be taken to address these?"
            ])
        elif intent == "location":
            if entities.get("counties"):
                county = entities["counties"][0]
                follow_ups.extend([
                    f"What are the top issues in {county}?",
                    f"What's the sentiment in {county}?",
                    f"Compare {county} with other counties"
                ])
        elif intent == "trend":
            follow_ups.extend([
                "What's causing this trend?",
                "Which sectors are driving this change?",
                "What should be done to address this trend?"
            ])
        elif intent == "comparison":
            follow_ups.extend([
                "Why is there a difference?",
                "What factors contribute to this comparison?",
                "What recommendations do you have?"
            ])
        else:
            follow_ups.extend([
                "What are the top issues right now?",
                "Show me sentiment trends",
                "Which counties need the most attention?"
            ])
        
        return follow_ups[:3]  # Return top 3 suggestions
    
    
    def _generate_fallback_response(
        self,
        user_message: str,
        context_data: Dict[str, Any]
    ) -> str:
        """Generate intelligent fallback response when AI is unavailable"""
        intent = self._extract_intent(user_message)
        entities = self._extract_entities(user_message)
        
        # Generate intelligent, specific responses based on intent and data
        if intent == "sentiment" and context_data.get("sentiment_distribution"):
            dist = context_data["sentiment_distribution"]
            pct = context_data.get("sentiment_percentages", {})
            total = sum(dist.values())
            
            response = f"**Sentiment Analysis for {' '.join(entities.get('counties', [])) or 'Kenya'}**\n\n"
            response += f"Based on {total} analyzed feedback items:\n"
            response += f"- **Positive**: {dist.get('positive', 0)} ({pct.get('positive', 0)}%) - Citizens expressing satisfaction\n"
            response += f"- **Negative**: {dist.get('negative', 0)} ({pct.get('negative', 0)}%) - Service delivery concerns\n"
            response += f"- **Neutral**: {dist.get('neutral', 0)} ({pct.get('neutral', 0)}%) - Factual reporting\n\n"
            
            if context_data.get("sentiment_by_county"):
                top_negative = sorted(context_data["sentiment_by_county"].items(), 
                                     key=lambda x: x[1].get("negative", 0), reverse=True)[:3]
                if top_negative:
                    county_list = [f"{c} ({s.get('negative', 0)} negative)" for c, s in top_negative]
                    response += f"**Counties with most negative sentiment**: {', '.join(county_list)}\n\n"
            
            if context_data.get("detailed_feedback"):
                response += "**Sample feedback**:\n"
                for fb in context_data["detailed_feedback"][:2]:
                    response += f"- [{fb.get('sentiment', 'unknown').upper()}] {fb.get('text', '')[:100]}... (Location: {fb.get('location', 'Unknown')})\n"
            
            return response
        
        elif intent == "sector" and context_data.get("sector_distribution"):
            sectors = context_data["sector_distribution"]
            top_sectors = sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:5]
            total = sum(sectors.values())
            
            response = f"**Sector Distribution Analysis**\n\n"
            response += f"Total complaints across all sectors: {total}\n\n"
            response += "**Top Sectors by Complaint Volume**:\n"
            for i, (sector, count) in enumerate(top_sectors, 1):
                pct = (count / total * 100) if total > 0 else 0
                response += f"{i}. **{sector.title()}**: {count} complaints ({pct:.1f}% of total)\n"
            
            if entities.get("sectors"):
                response += f"\n**Focus on {entities['sectors'][0].title()}**: "
                if entities['sectors'][0] in sectors:
                    count = sectors[entities['sectors'][0]]
                    response += f"{count} complaints ({count/total*100 if total > 0 else 0:.1f}% of total)"
            
            return response
        
        elif intent == "issues" and context_data.get("top_issues"):
            issues = context_data["top_issues"]
            response = f"**Top Public Service Issues**\n\n"
            response += "Based on citizen feedback analysis:\n\n"
            for i, (sector, count) in enumerate(issues[:5], 1):
                response += f"{i}. **{sector.title()}**: {count} complaints\n"
            
            if context_data.get("issue_details"):
                response += "\n**Issue Details**:\n"
                for issue in context_data["issue_details"][:2]:
                    response += f"- {issue.get('sector', 'Unknown')}: Affecting {', '.join(issue.get('counties_affected', [])[:3])}\n"
            
            response += "\n**Recommendation**: These issues require immediate attention from public administrators to improve service delivery."
            return response
        
        elif intent == "location" and entities.get("counties"):
            county = entities["counties"][0]
            response = f"**Analysis for {county}**\n\n"
            
            if context_data.get("sentiment_by_county") and county in context_data["sentiment_by_county"]:
                sents = context_data["sentiment_by_county"][county]
                total = sum(sents.values())
                response += f"**Sentiment Breakdown**:\n"
                response += f"- Positive: {sents.get('positive', 0)} ({sents.get('positive', 0)/total*100 if total > 0 else 0:.1f}%)\n"
                response += f"- Negative: {sents.get('negative', 0)} ({sents.get('negative', 0)/total*100 if total > 0 else 0:.1f}%)\n"
                response += f"- Neutral: {sents.get('neutral', 0)} ({sents.get('neutral', 0)/total*100 if total > 0 else 0:.1f}%)\n\n"
            
            response += f"**Key Insights**: {county} shows {context_data.get('total_feedback', 0)} feedback items in the analyzed period."
            return response
        
        elif intent == "explanation" and context_data.get("detailed_feedback"):
            response = f"**Root Cause Analysis**\n\n"
            response += "Based on the feedback patterns, the main contributing factors are:\n\n"
            
            # Analyze patterns from feedback
            if context_data.get("sector_map"):
                sectors = {}
                for fb in context_data["detailed_feedback"][:10]:
                    sector = context_data["sector_map"].get(fb.get("id"), "unknown")
                    sectors[sector] = sectors.get(sector, 0) + 1
                
                top_sectors = sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:3]
                response += "**Common Themes**:\n"
                for sector, count in top_sectors:
                    response += f"- {sector.title()}: {count} related complaints\n"
            
            response += "\n**Sample Evidence**:\n"
            for fb in context_data["detailed_feedback"][:2]:
                response += f"- \"{fb.get('text', '')[:150]}...\" (Location: {fb.get('location', 'Unknown')})\n"
            
            return response
        
        elif intent == "count" and context_data.get("total_feedback"):
            total = context_data["total_feedback"]
            response = f"**Feedback Volume Analysis**\n\n"
            response += f"Total citizen feedback collected: **{total} items** in the analyzed period.\n\n"
            
            if context_data.get("source_breakdown"):
                response += "**By Source**:\n"
                for source, count in context_data["source_breakdown"].items():
                    response += f"- {source}: {count} items\n"
            
            return response
        
        else:
            summary = context_data.get("summary", "")
            if summary and len(summary) > 50:
                # Extract key points from summary
                lines = summary.split('\n')[:5]
                response = "**Key Insights**\n\n"
                for line in lines:
                    if line.strip() and not line.startswith('-'):
                        response += f"{line.strip()}\n"
                return response
            else:
                return "I'm currently analyzing the available data. Please check the dashboard for real-time insights into citizen feedback, sentiment trends, and public service issues across Kenya's counties."
    
    async def _generate_response_via_rest_api(self, prompt: str) -> str:
        """Generate response using Vertex AI REST API as fallback"""
        try:
            from google.auth.transport.requests import Request
            import requests
            import json
            
            # Get access token
            credentials = self.ai_service.rest_credentials
            credentials.refresh(Request())
            access_token = credentials.token
            
            # Build REST API endpoint
            project = self.ai_service.rest_project
            location = self.ai_service.location
            model = "gemini-1.5-flash-002"  # Try this first
            
            # Try newer available model names
            models_to_try = [
                "gemini-2.5-flash",
                "gemini-2.0-flash-exp",
                "gemini-2.0-flash",
                "gemini-2.5-pro",
                "gemini-1.5-flash-002",
                "gemini-pro"
            ]
            
            for model_name in models_to_try:
                try:
                    url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/{model_name}:predict"
                    
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                    
                    # Vertex AI REST API format
                    payload = {
                        "instances": [{
                            "prompt": prompt
                        }],
                        "parameters": {
                            "temperature": 0.7,
                            "maxOutputTokens": 2048,
                            "topP": 0.95,
                            "topK": 40
                        }
                    }
                    
                    response = requests.post(url, headers=headers, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "predictions" in result and len(result["predictions"]) > 0:
                            response_text = result["predictions"][0].get("content", "")
                            if response_text:
                                logger.info(f"REST API call successful with {model_name}")
                                return response_text.strip()
                    elif response.status_code == 404:
                        # Model not found, try next one
                        continue
                    else:
                        logger.warning(f"REST API call failed with {model_name}: {response.status_code} - {response.text[:200]}")
                        continue
                        
                except Exception as e:
                    logger.debug(f"REST API call failed for {model_name}: {e}")
                    continue
            
            # If all models failed, try alternative endpoint format
            try:
                # Alternative: Use generateContent endpoint (newer API)
                for model_name in models_to_try:
                    url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/publishers/google/models/{model_name}:generateContent"
                    
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": prompt
                            }]
                        }],
                        "generationConfig": {
                            "temperature": 0.7,
                            "maxOutputTokens": 2048,
                            "topP": 0.95,
                            "topK": 40
                        }
                    }
                    
                    response = requests.post(url, headers=headers, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "candidates" in result and len(result["candidates"]) > 0:
                            content = result["candidates"][0].get("content", {})
                            parts = content.get("parts", [])
                            if parts and len(parts) > 0:
                                response_text = parts[0].get("text", "")
                                if response_text:
                                    logger.info(f"REST API generateContent successful with {model_name}")
                                    return response_text.strip()
                    elif response.status_code != 404:
                        logger.warning(f"REST API generateContent failed: {response.status_code} - {response.text[:200]}")
            except Exception as e:
                logger.debug(f"Alternative REST API endpoint failed: {e}")
            
            return None  # All REST API attempts failed
            
        except Exception as e:
            logger.error(f"REST API generation failed: {e}")
            return None

