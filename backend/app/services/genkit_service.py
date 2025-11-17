"""
Genkit Service
Service for multilingual translation and generative policy narratives using Vertex AI
Genkit patterns for translation workflows
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from vertexai.generative_models import GenerativeModel
from google.cloud import translate_v2 as translate
from app.core.config import settings
from app.db.supabase import get_supabase

logger = logging.getLogger(__name__)


class GenkitService:
    """Service for Genkit-style translation and generative workflows"""
    
    def __init__(self):
        self.supabase = get_supabase()
        # Initialize Vertex AI model for generative narratives
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
            logger.info("Genkit service initialized with Vertex AI")
        except Exception as e:
            logger.warning(f"Genkit initialization failed: {e}")
            self.model = None
        
        # Initialize Translation client
        try:
            self.translate_client = translate.Client()
            logger.info("Translation client initialized")
        except Exception as e:
            logger.warning(f"Translation client initialization failed: {e}")
            self.translate_client = None
    
    async def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate text using Genkit translation workflow
        
        Args:
            text: Text to translate
            target_language: Target language code (en, sw, etc.)
            source_language: Optional source language code
            
        Returns:
            Translation result with translated text and metadata
        """
        try:
            if not self.translate_client:
                # Fallback: use Vertex AI for translation
                if self.model:
                    prompt = f"Translate the following text to {target_language}. Only return the translation, no explanations:\n\n{text}"
                    response = self.model.generate_content(prompt)
                    translated_text = response.text.strip()
                else:
                    translated_text = text  # No translation available
                
                return {
                    "original_text": text,
                    "translated_text": translated_text,
                    "source_language": source_language or "auto",
                    "target_language": target_language,
                    "confidence": 0.7,
                    "model_used": "vertex-ai-fallback"
                }
            
            # Use Google Translate API
            result = self.translate_client.translate(
                text,
                target_language=target_language,
                source_language=source_language
            )
            
            return {
                "original_text": text,
                "translated_text": result['translatedText'],
                "source_language": result.get('detectedSourceLanguage', source_language),
                "target_language": target_language,
                "confidence": 0.95,
                "model_used": "google-translate"
            }
            
        except Exception as e:
            logger.error(f"Translation error: {e}", exc_info=True)
            return {
                "original_text": text,
                "translated_text": text,
                "source_language": source_language or "unknown",
                "target_language": target_language,
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def generate_policy_narrative(
        self,
        data: Dict[str, Any],
        language: str = "en"
    ) -> str:
        """
        Generate generative policy narrative using Genkit patterns
        
        Args:
            data: Policy data (insights, recommendations, trends)
            language: Target language for narrative
            
        Returns:
            Generated narrative text
        """
        try:
            if not self.model:
                # Fallback narrative
                return f"Policy analysis for {data.get('sector', 'all sectors')} based on citizen feedback."
            
            # Build narrative prompt
            prompt = f"""Generate a comprehensive policy narrative in {language} based on the following data:

Sector: {data.get('sector', 'All sectors')}
Total Feedback: {data.get('total_feedback', 0)}
Sentiment Distribution: {data.get('sentiment_distribution', {})}
Top Issues: {data.get('top_issues', [])}
Recommendations: {data.get('recommendations', [])}

Create a narrative that:
1. Summarizes the key citizen concerns
2. Highlights emerging trends
3. Provides context for policy recommendations
4. Uses clear, professional language suitable for policymakers

Narrative:"""
            
            response = self.model.generate_content(prompt)
            narrative = response.text.strip()
            
            logger.info(f"Generated policy narrative in {language}")
            return narrative
            
        except Exception as e:
            logger.error(f"Error generating policy narrative: {e}", exc_info=True)
            return f"Policy analysis narrative for {data.get('sector', 'all sectors')}."
    
    async def generate_multilingual_summary(
        self,
        text: str,
        languages: List[str] = ["en", "sw"]
    ) -> Dict[str, str]:
        """
        Generate summaries in multiple languages
        
        Args:
            text: Source text
            languages: List of target languages
            
        Returns:
            Dictionary mapping language codes to summaries
        """
        summaries = {}
        
        for lang in languages:
            try:
                if not self.model:
                    summaries[lang] = text[:500] + "..."
                    continue
                
                prompt = f"""Summarize the following text in {lang}. Provide a concise summary:

{text[:2000]}

Summary:"""
                
                response = self.model.generate_content(prompt)
                summaries[lang] = response.text.strip()
                
            except Exception as e:
                logger.error(f"Error generating summary in {lang}: {e}")
                summaries[lang] = text[:500] + "..."
        
        return summaries

