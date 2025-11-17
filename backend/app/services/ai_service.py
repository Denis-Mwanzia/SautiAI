"""
AI Service
Service for LLM analysis using Vertex AI, Genkit, and ADK
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from app.core.config import settings
from app.core.constants import VALID_CATEGORIES, URGENCY_LEVELS, CATEGORY_ALIASES

# Mapping from new VALID_CATEGORIES to old sector_classification values
# The database constraint uses old values, but we use new categories in code
CATEGORY_TO_SECTOR_MAP = {
    "healthcare": "health",
    "education": "education",
    "governance": "governance",
    "public_services": "governance",  # Map to governance as closest match
    "infrastructure": "infrastructure",
    "security": "security"
}
from app.db.supabase import get_supabase, get_supabase_service
from app.models.schemas import AISummary, PolicyRecommendation, SectorType, UrgencyLevel, SentimentType
from app.services.genkit_service import GenkitService
from app.services.adk_service import ADKService

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI/LLM operations"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.supabase_service = get_supabase_service()
        # Store project/location for REST API calls
        self.project = settings.VERTEX_AI_PROJECT
        self.location = settings.VERTEX_AI_LOCATION
        # Initialize Genkit and ADK services
        self.genkit_service = GenkitService()
        self.adk_service = ADKService()
        # Initialize Vertex AI
        try:
            # Lazy import Google SDKs
            from google.cloud import aiplatform  # type: ignore
            from vertexai.generative_models import GenerativeModel  # type: ignore
            from google.cloud import translate_v2 as translate  # type: ignore
            import os
            # Set credentials if provided - expand $(pwd) if present
            creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
            if creds_path:
                # Expand $(pwd) or ${PWD} if present
                if "$(pwd)" in creds_path:
                    creds_path = creds_path.replace("$(pwd)", os.getcwd())
                elif "${PWD}" in creds_path:
                    creds_path = creds_path.replace("${PWD}", os.getcwd())
                # Expand ~ if present
                creds_path = os.path.expanduser(creds_path)
                # Make absolute if relative
                if not os.path.isabs(creds_path):
                    creds_path = os.path.abspath(creds_path)
                if os.path.exists(creds_path):
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
                    logger.info(f"Using credentials from: {creds_path}")
                else:
                    logger.warning(f"Credentials file not found: {creds_path}")
            # Try common locations if not set
            if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
                possible_paths = [
                    "gcp-service-account.json",
                    "../gcp-service-account.json",
                    os.path.join(os.path.dirname(__file__), "..", "..", "gcp-service-account.json"),
                    os.path.expanduser("~/gcp-service-account.json")
                ]
                for path in possible_paths:
                    abs_path = os.path.abspath(path)
                    if os.path.exists(abs_path):
                        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abs_path
                        logger.info(f"Found credentials at: {abs_path}")
                        break
            
            # Try Google Generative AI API directly first (more reliable, uses newer models)
            try:
                import google.generativeai as genai
                genai.configure(transport='rest')
                # Use newer available models
                direct_model_names = [
                    "gemini-2.5-flash",           # Latest stable
                    "gemini-2.0-flash-exp",        # Working experimental
                    "gemini-2.5-pro",              # Pro version
                    "gemini-2.0-flash",            # Stable 2.0
                    "gemini-flash-latest",         # Latest alias
                ]
                for model_name in direct_model_names:
                    try:
                        direct_model = genai.GenerativeModel(model_name)
                        # Test it works
                        test_response = direct_model.generate_content("test")
                        self.model = direct_model
                        self.use_direct_api = True
                        logger.info(f"Google Generative AI API initialized with {model_name}")
                        break
                    except Exception as direct_error:
                        logger.debug(f"Direct API model {model_name} failed: {direct_error}")
                        continue
                if not hasattr(self, 'use_direct_api'):
                    self.use_direct_api = False
            except ImportError:
                logger.debug("google-generativeai not available, using Vertex AI only")
                self.use_direct_api = False
            except Exception as e:
                logger.debug(f"Direct API initialization failed: {e}")
                self.use_direct_api = False
            
            # If direct API didn't work, try Vertex AI SDK
            if not hasattr(self, 'model') or self.model is None:
                aiplatform.init(
                    project=settings.VERTEX_AI_PROJECT,
                    location=settings.VERTEX_AI_LOCATION
                )
                # Use newer available model names
                model_names = [
                    "gemini-2.0-flash-exp",        # Working experimental
                    "gemini-2.5-flash",            # Latest stable
                    "gemini-2.0-flash",            # Stable 2.0
                    "gemini-2.5-pro",              # Pro version
                    "gemini-1.5-flash-002",        # Older but might work
                    "gemini-1.5-flash-001",        # Older fallback
                    "gemini-pro",                  # Legacy fallback
                ]
                self.model = None
                self.use_rest_api = False
                last_error = None
                
                for model_name in model_names:
                    try:
                        self.model = GenerativeModel(model_name)
                        # Don't test on init - just initialize
                        logger.info(f"Vertex AI model initialized: {model_name}")
                        break
                    except Exception as e:
                        last_error = e
                        error_str = str(e)
                        if "404" in error_str:
                            logger.debug(f"Model {model_name} not found (404)")
                        elif "403" in error_str:
                            logger.warning(f"Model {model_name} access denied (403)")
                        else:
                            logger.debug(f"Failed to initialize {model_name}: {error_str[:200]}")
                        continue
            
            # If SDK approach failed, try REST API approach
            if self.model is None:
                logger.warning("SDK model initialization failed, attempting REST API approach...")
                try:
                    # Initialize REST API client
                    from google.auth import default
                    from google.auth.transport.requests import Request
                    import requests
                    
                    credentials, project = default()
                    if credentials:
                        self.use_rest_api = True
                        self.rest_credentials = credentials
                        self.rest_project = project or settings.VERTEX_AI_PROJECT
                        self.rest_location = settings.VERTEX_AI_LOCATION
                        # Try to determine available model
                        self.rest_model = "gemini-2.5-flash"  # Default, will try others if needed
                        logger.info(f"Vertex AI REST API initialized for project {self.rest_project}")
                    else:
                        raise Exception("Could not get default credentials")
                except Exception as rest_error:
                    logger.error(f"REST API initialization also failed: {rest_error}")
                    logger.error(f"Failed to initialize any Gemini model. Last SDK error: {last_error}")
                    # Don't raise - allow fallback responses
                    self.model = None
        except Exception as e:
            logger.warning(f"Vertex AI initialization failed: {e}. Some features may not work.")
            self.model = None
        # Initialize Translation client
        try:
            # translate may not be available if SDK missing
            from google.cloud import translate_v2 as translate  # type: ignore
            self.translate_client = translate.Client()
        except Exception as e:
            logger.warning(f"Translation client initialization failed: {e}")
            self.translate_client = None
    
    async def generate_summary(
        self,
        feedback_ids: List[str],
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate AI summary for a batch of feedback
        
        Args:
            feedback_ids: List of feedback IDs to summarize
            language: Target language (en or sw)
        """
        logger.info(f"Generating summary for {len(feedback_ids)} feedback items")
        
        # Fetch feedback from database
        feedback_data = []
        for fid in feedback_ids:
            result = self.supabase.table("citizen_feedback").select("*").eq(
                "id", fid
            ).execute()
            if result.data:
                feedback_data.append(result.data[0])
        
        if not feedback_data:
            raise ValueError("No feedback found for provided IDs")
        
        # Combine text
        combined_text = "\n\n".join([f["text"] for f in feedback_data])
        
        # Generate summary using Vertex AI
        summary_text = await self._call_vertex_ai_summarize(combined_text, language)
        
        # Extract key points
        key_points = await self._extract_key_points(combined_text, language)
        
        # Store summary
        summary = {
            "batch_id": f"batch_{datetime.utcnow().isoformat()}",
            "summary_text": summary_text,
            "key_points": key_points,
            "language": language,
            "generated_at": datetime.utcnow().isoformat(),
            "model_used": "vertex-ai"
        }
        
        result = self.supabase.table("ai_summary_batches").insert(summary).execute()
        
        return {
            "id": result.data[0]["id"] if result.data else None,
            **summary
        }
    
    async def generate_policy_report(
        self,
        sector: Optional[str] = None,
        county: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate policy recommendation report
        
        Uses Vertex AI + ADK for agentic policy analysis
        """
        logger.info(f"Generating policy report for sector={sector}, county={county}")
        
        # Fetch relevant feedback
        query = self.supabase.table("citizen_feedback").select("*")
        
        if sector:
            # Join with sector classification
            # This is simplified - actual implementation would use proper joins
            pass
        
        feedback_result = query.limit(100).execute()
        
        # Generate report using Vertex AI (ADK simulation)
        report = await self._call_adk_policy_analysis(
            feedback_result.data,
            sector,
            county
        )
        
        # Store recommendations
        for rec in report.get("recommendations", []):
            self.supabase.table("policy_recommendations").insert(rec).execute()
        
        return report
    
    async def get_summaries(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get recent AI-generated summaries"""
        result = self.supabase.table("ai_summary_batches").select(
            "*"
        ).order("generated_at", desc=True).limit(limit).offset(offset).execute()
        
        return result.data
    
    async def get_recommendations(
        self,
        sector: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get policy recommendations"""
        query = self.supabase.table("policy_recommendations").select("*")
        
        if sector:
            query = query.eq("sector", sector)
        
        result = query.order("generated_at", desc=True).limit(limit).execute()
        
        return result.data
    
    async def analyze_sentiment(
        self,
        feedback_id: str,
        text: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of feedback text using Vertex AI
        
        Args:
            feedback_id: ID of the feedback
            text: Text to analyze
            language: Language of the text
        """
        logger.info(f"Analyzing sentiment for feedback {feedback_id}")
        
        try:
            # Use ADK service for agentic sentiment detection
            context = {"source": "feedback", "language": language}
            adk_result = await self.adk_service.realtime_sentiment_detection(text, context)
            
            # Store sentiment score
            sentiment_record = {
                "feedback_id": feedback_id,
                "sentiment": adk_result["sentiment"],
                "confidence": float(adk_result["confidence"]),
                "scores": adk_result["scores"],
                "analyzed_at": datetime.utcnow().isoformat(),
                "model_used": adk_result.get("model_used", "adk-vertex-ai")
            }
            
            self.supabase_service.table("sentiment_scores").insert(sentiment_record).execute()
            
            logger.info(f"Sentiment analyzed: {adk_result['sentiment']} (confidence: {adk_result['confidence']})")
            return sentiment_record
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}", exc_info=True)
            # Fallback to rule-based
            return await self._fallback_sentiment_analysis(text, feedback_id)
    
    async def classify_sector(
        self,
        feedback_id: str,
        text: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Classify feedback into a sector using ADK agentic classification
        
        MANDATORY: Only uses the 6 valid categories. If no match, returns None.
        
        Args:
            feedback_id: ID of the feedback
            text: Text to classify
            language: Language of the text
        """
        logger.info(f"Classifying sector for feedback {feedback_id}")
        
        # MANDATORY: Only these 6 categories allowed
        valid_sectors = VALID_CATEGORIES
        
        try:
            # Use ADK service for agentic classification
            context = {"language": language, "valid_categories": valid_sectors}
            adk_result = await self.adk_service.agentic_classification(text, valid_sectors, context)
            
            primary_sector = adk_result.get("category", None)
            
            # STRICT VALIDATION: Must match one of 6 categories
            if primary_sector not in valid_sectors:
                logger.warning(f"Classification result '{primary_sector}' not in valid categories. Discarding.")
                return None  # Discard if no valid category match
            
            # Map to database sector value (database uses old constraint values)
            db_sector = CATEGORY_TO_SECTOR_MAP.get(primary_sector, "other")
            
            # Store classification
            sector_record = {
                "feedback_id": feedback_id,
                "primary_sector": db_sector,  # Use mapped value for database
                "confidence": float(adk_result.get("confidence", 0.8)),
                "classified_at": datetime.utcnow().isoformat(),
                "model_used": "adk-vertex-ai"
            }
            
            self.supabase_service.table("sector_classification").insert(sector_record).execute()
            
            # Return with original category for API response
            sector_record["category"] = primary_sector  # Keep original category
            
            logger.info(f"Sector classified: {primary_sector} (confidence: {adk_result.get('confidence', 0.8)})")
            return sector_record
            
        except Exception as e:
            logger.error(f"Error classifying sector: {e}", exc_info=True)
            # Fallback to keyword-based (still enforces 6 categories)
            return await self._fallback_sector_classification(text, feedback_id)
    
    async def _fallback_sentiment_analysis(self, text: str, feedback_id: Optional[str] = None) -> Dict[str, Any]:
        """Fallback rule-based sentiment analysis"""
        text_lower = text.lower()
        
        positive_words = ["good", "great", "excellent", "happy", "satisfied", "thank", "appreciate", "love", "best", "wonderful"]
        negative_words = ["bad", "terrible", "awful", "hate", "angry", "frustrated", "disappointed", "worst", "problem", "issue", "fail"]
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = "positive"
            confidence = min(0.7, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = "negative"
            confidence = min(0.7, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        sentiment_record = {
            "feedback_id": feedback_id,
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": {
                "positive": 0.33 if sentiment == "positive" else 0.33,
                "negative": 0.33 if sentiment == "negative" else 0.33,
                "neutral": 0.34 if sentiment == "neutral" else 0.33
            },
            "analyzed_at": datetime.utcnow().isoformat(),
            "model_used": "rule-based-fallback"
        }
        
        if feedback_id:
            self.supabase_service.table("sentiment_scores").insert(sentiment_record).execute()
        
        return sentiment_record
    
    async def _fallback_sector_classification(self, text: str, feedback_id: str) -> Optional[Dict[str, Any]]:
        """
        Fallback keyword-based sector classification
        
        MANDATORY: Only uses the 6 valid categories. Returns None if no match.
        """
        text_lower = text.lower()
        
        # MANDATORY: Only 6 categories with their keywords
        sector_keywords = {
            "healthcare": ["hospital", "clinic", "doctor", "medicine", "health", "medical", "treatment", "patient", "healthcare"],
            "education": ["school", "teacher", "student", "education", "learn", "university", "college", "curriculum"],
            "governance": ["government", "minister", "policy", "corruption", "officials", "administration", "governance"],
            "public_services": ["public service", "service delivery", "citizen service", "public services"],
            "infrastructure": ["road", "traffic", "bus", "train", "transport", "vehicle", "highway", "infrastructure", "water", "electricity", "utilities"],
            "security": ["security", "police", "crime", "safety", "violence", "theft", "robbery", "law enforcement"]
        }
        
        scores = {}
        for sector in VALID_CATEGORIES:
            keywords = sector_keywords.get(sector, [])
            scores[sector] = sum(1 for keyword in keywords if keyword in text_lower)
        
        # Only proceed if we have a match
        if max(scores.values()) == 0:
            logger.info(f"No category match found for feedback {feedback_id}. Discarding.")
            return None  # Discard if no category match
        
        primary_sector = max(scores.items(), key=lambda x: x[1])[0]
        confidence = min(0.8, 0.5 + scores[primary_sector] * 0.1)
        
        # Map to database sector value (database uses old constraint values)
        db_sector = CATEGORY_TO_SECTOR_MAP.get(primary_sector, "other")
        
        sector_record = {
            "feedback_id": feedback_id,
            "primary_sector": db_sector,  # Use mapped value for database
            "confidence": confidence,
            "classified_at": datetime.utcnow().isoformat(),
            "model_used": "keyword-based-fallback"
        }
        
        self.supabase_service.table("sector_classification").insert(sector_record).execute()
        
        # Return with original category for API response
        sector_record["category"] = primary_sector  # Keep original category
        return sector_record
    
    async def _call_vertex_ai_summarize(self, text: str, language: str) -> str:
        """Call Genkit for multilingual summarization"""
        try:
            # Use Genkit service for translation-aware summarization
            summaries = await self.genkit_service.generate_multilingual_summary(
                text,
                [language] if language else ["en"]
            )
            
            summary = summaries.get(language, summaries.get("en", text[:500] + "..."))
            
            logger.info(f"Generated summary using Genkit")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            # Fallback summary
            return f"Summary: {text[:500]}..."
    
    async def _extract_key_points(self, text: str, language: str) -> List[str]:
        """Extract key points from text"""
        try:
            if not self.model:
                # Fallback: return first few sentences
                sentences = text.split('.')[:3]
                return [s.strip() + '.' for s in sentences if s.strip()]
            
            prompt = f"""Extract the 3-5 most important key points from the following text. List them as bullet points:

{text[:4000]}

Key points:"""
            
            response = self.model.generate_content(prompt)
            key_points_text = response.text.strip()
            
            # Parse key points (assume they're separated by newlines or bullets)
            key_points = []
            for line in key_points_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                    key_points.append(line[1:].strip())
                elif line and len(line) > 10:
                    key_points.append(line)
            
            return key_points[:5] if key_points else ["Key point extracted from text"]
            
        except Exception as e:
            logger.error(f"Error extracting key points: {e}", exc_info=True)
            # Fallback
            sentences = text.split('.')[:3]
            return [s.strip() + '.' for s in sentences if s.strip() and len(s.strip()) > 20]
    
    async def _call_adk_policy_analysis(
        self,
        feedback: List[Dict[str, Any]],
        sector: Optional[str],
        county: Optional[str]
    ) -> Dict[str, Any]:
        """Call ADK for agentic policy analysis"""
        try:
            # Use ADK service for agentic planning
            objectives = [
                "Improve citizen satisfaction",
                "Address critical issues",
                "Enhance service delivery"
            ]
            
            plan = await self.adk_service.agentic_policy_planning(feedback, objectives)
            
            # Convert plan to recommendations format
            recommendations = []
            for step in plan.get("steps", []):
                recommendations.append({
                    "sector": sector or "other",
                    "title": step.get("action", "Policy Action"),
                    "description": step.get("reasoning", ""),
                    "urgency": step.get("priority", "medium"),
                    "priority": 8 if step.get("priority") == "high" else 5,
                    "county": county,
                    "generated_at": datetime.utcnow().isoformat(),
                    "model_used": "adk-vertex-ai"
                })
            
            return {
                "recommendations": recommendations,
                "analysis": plan.get("analysis", "Policy analysis completed")
            }
            
        except Exception as e:
            logger.error(f"Error in ADK policy analysis: {e}", exc_info=True)
            # Fallback to basic analysis
            return {
                "recommendations": [],
                "analysis": f"Policy analysis error: {str(e)}"
            }

