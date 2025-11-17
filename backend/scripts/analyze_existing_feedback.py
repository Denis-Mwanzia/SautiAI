#!/usr/bin/env python3
"""
Analyze existing feedback that hasn't been analyzed yet
Run sentiment and sector classification on all feedback without analysis
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.ai_service import AIService
from app.db.supabase import init_supabase, get_supabase_service

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def analyze_existing_feedback():
    """Analyze all feedback that doesn't have sentiment or sector classification"""
    await init_supabase()
    supabase = get_supabase_service()
    ai_service = AIService()
    
    # Get all feedback
    feedback_result = supabase.table("citizen_feedback").select("*").execute()
    feedback_items = feedback_result.data
    
    logger.info(f"Found {len(feedback_items)} feedback items")
    
    # Get existing sentiment scores
    sentiment_result = supabase.table("sentiment_scores").select("feedback_id").execute()
    analyzed_sentiment_ids = {s["feedback_id"] for s in sentiment_result.data}
    
    # Get existing sector classifications
    sector_result = supabase.table("sector_classification").select("feedback_id").execute()
    analyzed_sector_ids = {s["feedback_id"] for s in sector_result.data}
    
    # Find items that need analysis
    needs_sentiment = [f for f in feedback_items if f["id"] not in analyzed_sentiment_ids]
    needs_sector = [f for f in feedback_items if f["id"] not in analyzed_sector_ids]
    
    logger.info(f"Items needing sentiment analysis: {len(needs_sentiment)}")
    logger.info(f"Items needing sector classification: {len(needs_sector)}")
    
    # Analyze sentiment
    sentiment_count = 0
    for feedback in needs_sentiment[:50]:  # Limit to 50 for now
        try:
            await ai_service.analyze_sentiment(
                feedback["id"],
                feedback["text"],
                feedback.get("language", "en")
            )
            sentiment_count += 1
            if sentiment_count % 10 == 0:
                logger.info(f"Analyzed sentiment for {sentiment_count} items...")
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {feedback['id']}: {e}")
    
    logger.info(f"✓ Completed sentiment analysis for {sentiment_count} items")
    
    # Analyze sectors
    sector_count = 0
    for feedback in needs_sector[:50]:  # Limit to 50 for now
        try:
            await ai_service.classify_sector(
                feedback["id"],
                feedback["text"],
                feedback.get("language", "en")
            )
            sector_count += 1
            if sector_count % 10 == 0:
                logger.info(f"Classified sector for {sector_count} items...")
        except Exception as e:
            logger.error(f"Error classifying sector for {feedback['id']}: {e}")
    
    logger.info(f"✓ Completed sector classification for {sector_count} items")
    logger.info("Analysis complete!")


if __name__ == "__main__":
    try:
        asyncio.run(analyze_existing_feedback())
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.fatal(f"Fatal error: {e}", exc_info=True)

