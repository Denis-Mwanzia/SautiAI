"""
ADK Service (Agentic Development Kit)
Service for agentic inference, tools, and planning using Vertex AI
ADK patterns for real-time sentiment detection and classification
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from vertexai.generative_models import GenerativeModel
from app.core.config import settings
from app.db.supabase import get_supabase

logger = logging.getLogger(__name__)


class ADKService:
    """Service for ADK-style agentic inference and planning"""
    
    def __init__(self):
        self.supabase = get_supabase()
        # Initialize Vertex AI for agentic inference
        try:
            import os
            from google.cloud import aiplatform
            # Set credentials if provided - expand $(pwd) if present
            creds_path = settings.GOOGLE_APPLICATION_CREDENTIALS
            if creds_path:
                if "$(pwd)" in creds_path:
                    creds_path = creds_path.replace("$(pwd)", os.getcwd())
                elif "${PWD}" in creds_path:
                    creds_path = creds_path.replace("${PWD}", os.getcwd())
                creds_path = os.path.expanduser(creds_path)
                if not os.path.isabs(creds_path):
                    creds_path = os.path.abspath(creds_path)
                if os.path.exists(creds_path):
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path
            if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
                possible_paths = ["gcp-service-account.json", "../gcp-service-account.json"]
                for path in possible_paths:
                    abs_path = os.path.abspath(path)
                    if os.path.exists(abs_path):
                        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = abs_path
                        break
            
            aiplatform.init(
                project=settings.VERTEX_AI_PROJECT,
                location=settings.VERTEX_AI_LOCATION
            )
            # Try newer available model names
            model_names = ["gemini-2.5-flash", "gemini-2.0-flash-exp", "gemini-2.0-flash", "gemini-2.5-pro", "gemini-1.5-flash-002", "gemini-pro"]
            self.model = None
            for model_name in model_names:
                try:
                    self.model = GenerativeModel(model_name)
                    break
                except Exception:
                    continue
            if self.model is None:
                raise Exception(f"Could not initialize Vertex AI model. Tried: {', '.join(model_names)}")
            logger.info("ADK service initialized with Vertex AI")
        except Exception as e:
            logger.warning(f"ADK initialization failed: {e}")
            self.model = None
    
    async def realtime_sentiment_detection(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Real-time sentiment detection using ADK agentic patterns
        
        Args:
            text: Text to analyze
            context: Optional context (source, location, etc.)
            
        Returns:
            Sentiment analysis with agentic reasoning
        """
        try:
            if not self.model:
                # Fallback sentiment
                return {
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "scores": {"positive": 0.33, "negative": 0.33, "neutral": 0.34},
                    "reasoning": "Fallback analysis",
                    "model_used": "fallback"
                }
            
            # Build agentic prompt with context
            context_str = ""
            if context:
                context_str = f"\nContext: Source={context.get('source')}, Location={context.get('location')}"
            
            prompt = f"""As an agentic AI system, analyze the sentiment of this text and provide reasoning:

Text: {text[:1000]}{context_str}

Provide analysis in JSON format:
{{
    "sentiment": "positive" or "negative" or "neutral",
    "confidence": 0.0 to 1.0,
    "scores": {{
        "positive": 0.0 to 1.0,
        "negative": 0.0 to 1.0,
        "neutral": 0.0 to 1.0
    }},
    "reasoning": "Brief explanation of sentiment",
    "key_indicators": ["indicator1", "indicator2"]
}}

JSON only:"""
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse JSON
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            result["model_used"] = "adk-vertex-ai"
            result["analyzed_at"] = datetime.utcnow().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"ADK sentiment detection error: {e}", exc_info=True)
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "scores": {"positive": 0.33, "negative": 0.33, "neutral": 0.34},
                "reasoning": f"Error: {str(e)}",
                "model_used": "fallback"
            }
    
    async def agentic_classification(
        self,
        text: str,
        categories: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Agentic classification with planning and reasoning
        
        Args:
            text: Text to classify
            categories: List of possible categories
            context: Optional context
            
        Returns:
            Classification with agentic reasoning
        """
        try:
            if not self.model:
                return {
                    "category": categories[0] if categories else "other",
                    "confidence": 0.5,
                    "reasoning": "Fallback classification"
                }
            
            prompt = f"""As an agentic AI system, classify this text into one of these categories: {', '.join(categories)}

Text: {text[:1000]}

Provide classification in JSON format:
{{
    "category": "one of the categories",
    "confidence": 0.0 to 1.0,
    "reasoning": "Why this category was chosen",
    "alternative_categories": [{{"category": "name", "confidence": 0.0}}]
}}

JSON only:"""
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse JSON
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            logger.error(f"ADK classification error: {e}", exc_info=True)
            return {
                "category": categories[0] if categories else "other",
                "confidence": 0.5,
                "reasoning": f"Error: {str(e)}"
            }
    
    async def agentic_policy_planning(
        self,
        feedback_data: List[Dict[str, Any]],
        objectives: List[str]
    ) -> Dict[str, Any]:
        """
        Agentic policy planning with multi-step reasoning
        
        Args:
            feedback_data: List of feedback items
            objectives: Policy objectives
            
        Returns:
            Policy plan with agentic reasoning steps
        """
        try:
            if not self.model:
                return {
                    "plan": [],
                    "reasoning": "Fallback planning"
                }
            
            feedback_summary = "\n".join([f["text"][:200] for f in feedback_data[:10]])
            
            prompt = f"""As an agentic AI system, create a policy plan based on citizen feedback.

Feedback Summary:
{feedback_summary}

Policy Objectives:
{chr(10).join(objectives)}

Create a multi-step policy plan in JSON format:
{{
    "analysis": "Overall analysis",
    "steps": [
        {{
            "step": 1,
            "action": "Action description",
            "priority": "high/medium/low",
            "reasoning": "Why this step is needed"
        }}
    ],
    "expected_outcomes": ["outcome1", "outcome2"]
}}

JSON only:"""
            
            response = self.model.generate_content(prompt)
            result_text = response.text.strip()
            
            # Parse JSON
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            result = json.loads(result_text)
            return result
            
        except Exception as e:
            logger.error(f"ADK policy planning error: {e}", exc_info=True)
            return {
                "plan": [],
                "reasoning": f"Error: {str(e)}"
            }

