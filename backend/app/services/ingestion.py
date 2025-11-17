"""
Data Ingestion Service
Handles data collection from legal sources (Twitter, Facebook, RSS)
"""

import httpx
import asyncio
import logging
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import feedparser
from langdetect import detect

from app.core.config import settings
from app.core.constants import (
    VALID_CATEGORIES,
    CATEGORY_ALIASES,
    PII_PATTERNS,
    ALLOWED_SOURCES,
    MIN_TEXT_LENGTH,
    MAX_TEXT_LENGTH
)
from app.db.supabase import get_supabase, get_supabase_service
from app.models.schemas import CitizenFeedback, LanguageType

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for ingesting data from various sources with strict validation"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.supabase_service = get_supabase_service()  # For inserts that need to bypass RLS
        self.twitter_base_url = "https://api.twitter.com/2"
        self.facebook_base_url = "https://graph.facebook.com/v18.0"
    
    def _remove_pii(self, text: str) -> str:
        """Remove PII from text"""
        cleaned_text = text
        for pattern in PII_PATTERNS:
            cleaned_text = re.sub(pattern, '[REDACTED]', cleaned_text, flags=re.IGNORECASE)
        return cleaned_text
    
    def _validate_source(self, source: str) -> bool:
        """Validate that source is in allowed list"""
        return source in ALLOWED_SOURCES or any(allowed in source.lower() for allowed in ['rss', 'twitter', 'facebook', 'api'])
    
    def _validate_text(self, text: str) -> bool:
        """Validate text meets requirements"""
        if not text or not isinstance(text, str):
            return False
        cleaned = text.strip()
        if len(cleaned) < MIN_TEXT_LENGTH:
            return False
        if len(cleaned) > MAX_TEXT_LENGTH:
            return False
        return True
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text: remove URLs, extra whitespace, junk"""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that are likely junk
        text = re.sub(r'[^\w\s.,!?;:\'\"-]', '', text)
        return text.strip()
    
    async def _validate_category(self, text: str) -> Optional[str]:
        """Validate that text matches one of the 6 mandatory categories"""
        text_lower = text.lower()
        
        # Check each category and its aliases
        for category, aliases in CATEGORY_ALIASES.items():
            for alias in aliases:
                if alias in text_lower:
                    return category
        
        # If no match found, return None (will be discarded)
        return None
    
    async def ingest_twitter(
        self,
        hashtags: List[str],
        max_results: int = 100,
        geo_bounds: Optional[Dict[str, float]] = None
    ):
        """
        Ingest data from Twitter API
        
        Args:
            hashtags: List of hashtags to track
            max_results: Maximum results per hashtag
            geo_bounds: Optional geographic bounds for Kenya
        """
        if not settings.TWITTER_BEARER_TOKEN:
            logger.warning("Twitter Bearer Token not configured. Skipping Twitter ingestion.")
            return
        
        logger.info(f"Starting Twitter ingestion for {len(hashtags)} hashtags")
        
        headers = {
            "Authorization": f"Bearer {settings.TWITTER_BEARER_TOKEN}"
        }
        
        async with httpx.AsyncClient() as client:
            for hashtag in hashtags:
                try:
                    # Build query
                    query = f"#{hashtag} lang:en OR lang:sw"
                    if geo_bounds:
                        # Add geo filter for Kenya
                        query += f" place_country:KE"
                    
                    params = {
                        "query": query,
                        "max_results": min(max_results, 100),
                        "tweet.fields": "created_at,author_id,geo,public_metrics,lang",
                        "user.fields": "name,username,location",
                        "expansions": "author_id,geo.place_id"
                    }
                    
                    response = await client.get(
                        f"{self.twitter_base_url}/tweets/search/recent",
                        headers=headers,
                        params=params,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        await self._process_twitter_data(data, hashtag)
                    else:
                        logger.warning(f"Twitter API error for {hashtag}: {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Error ingesting Twitter hashtag {hashtag}: {e}")
                
                # Rate limiting
                await asyncio.sleep(1)
        
        logger.info("Twitter ingestion completed")
    
    async def _process_twitter_data(self, data: Dict[str, Any], hashtag: str):
        """Process and store Twitter data"""
        tweets = data.get("data", [])
        users = {u["id"]: u for u in data.get("includes", {}).get("users", [])}
        
        for tweet in tweets:
            try:
                # Detect language
                text = tweet.get("text", "")
                lang = self._detect_language(text)
                
                # Anonymize author
                author_id = tweet.get("author_id")
                author = users.get(author_id, {})
                author_name = self._anonymize_author(author.get("username", "unknown"))
                
                feedback = {
                    "source": "twitter",
                    "source_id": tweet.get("id"),
                    "text": text,
                    "language": lang.value,
                    "author": author_name,
                    "location": author.get("location"),
                    "timestamp": datetime.fromisoformat(
                        tweet.get("created_at", datetime.utcnow().isoformat()).replace("Z", "+00:00")
                    ),
                    "raw_data": tweet
                }
                
                # Store in database
                stored_feedback = await self._store_feedback(feedback)
                if stored_feedback:
                    await self._trigger_analysis(stored_feedback["id"], text, lang.value)
                    await self._check_red_flags(stored_feedback["id"], text, "twitter", author.get("location"))
                    await self._calculate_priority(stored_feedback["id"], text, None, None, author.get("location"), "twitter")
                
            except Exception as e:
                logger.error(f"Error processing tweet {tweet.get('id')}: {e}")
    
    async def ingest_facebook(
        self,
        page_ids: List[str],
        max_posts: int = 50
    ):
        """
        Ingest data from Facebook Graph API (public pages only)
        
        Args:
            page_ids: List of Facebook page IDs
            max_posts: Maximum posts per page
        """
        if not settings.FACEBOOK_ACCESS_TOKEN:
            logger.warning("Facebook Access Token not configured. Skipping Facebook ingestion.")
            return
        
        logger.info(f"Starting Facebook ingestion for {len(page_ids)} pages")
        
        async with httpx.AsyncClient() as client:
            for page_id in page_ids:
                try:
                    params = {
                        "access_token": settings.FACEBOOK_ACCESS_TOKEN,
                        "fields": "id,message,created_time,comments{message,created_time,from}",
                        "limit": min(max_posts, 25)  # Facebook API limit
                    }
                    
                    response = await client.get(
                        f"{self.facebook_base_url}/{page_id}/posts",
                        params=params,
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        await self._process_facebook_data(data, page_id)
                    else:
                        logger.warning(f"Facebook API error for page {page_id}: {response.status_code}")
                        
                except Exception as e:
                    logger.error(f"Error ingesting Facebook page {page_id}: {e}")
                
                await asyncio.sleep(1)
        
        logger.info("Facebook ingestion completed")
    
    async def _process_facebook_data(self, data: Dict[str, Any], page_id: str):
        """Process and store Facebook data"""
        posts = data.get("data", [])
        
        for post in posts:
            try:
                # Process post message
                message = post.get("message", "")
                if message:
                    lang = self._detect_language(message)
                    
                    feedback = {
                        "source": "facebook",
                        "source_id": post.get("id"),
                        "text": message,
                        "language": lang.value,
                        "author": self._anonymize_author(page_id),
                        "timestamp": datetime.fromisoformat(
                            post.get("created_time", datetime.utcnow().isoformat()).replace("Z", "+00:00")
                        ),
                        "raw_data": post
                    }
                    
                    stored_feedback = await self._store_feedback(feedback)
                    if stored_feedback:
                        await self._trigger_analysis(stored_feedback["id"], message, lang.value)
                        await self._check_red_flags(stored_feedback["id"], message, "facebook", None)
                        await self._calculate_priority(stored_feedback["id"], message, None, None, None, "facebook")
                
                # Process comments
                comments = post.get("comments", {}).get("data", [])
                for comment in comments:
                    comment_text = comment.get("message", "")
                    if comment_text:
                        lang = self._detect_language(comment_text)
                        
                        feedback = {
                            "source": "facebook_comment",
                            "source_id": comment.get("id"),
                            "text": comment_text,
                            "language": lang.value,
                            "author": self._anonymize_author(
                                comment.get("from", {}).get("name", "unknown")
                            ),
                            "timestamp": datetime.fromisoformat(
                                comment.get("created_time", datetime.utcnow().isoformat()).replace("Z", "+00:00")
                            ),
                            "raw_data": comment
                        }
                        
                        stored_comment = await self._store_feedback(feedback)
                        if stored_comment:
                            await self._trigger_analysis(stored_comment["id"], comment_text, lang.value)
                            await self._check_red_flags(stored_comment["id"], comment_text, "facebook_comment", None)
                            await self._calculate_priority(stored_comment["id"], comment_text, None, None, None, "facebook_comment")
                        
            except Exception as e:
                logger.error(f"Error processing Facebook post {post.get('id')}: {e}")
    
    async def ingest_rss(self, feed_urls: List[str]):
        """
        Ingest data from RSS feeds
        
        Args:
            feed_urls: List of RSS feed URLs
        """
        logger.info(f"Starting RSS ingestion for {len(feed_urls)} feeds")
        
        for feed_url in feed_urls:
            try:
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    response = await client.get(feed_url, timeout=30.0)
                    
                    if response.status_code == 200:
                        feed = feedparser.parse(response.text)
                        if feed.entries:
                            await self._process_rss_data(feed, feed_url)
                            logger.info(f"Successfully processed {len(feed.entries)} entries from {feed_url}")
                        else:
                            logger.warning(f"No entries found in RSS feed: {feed_url}")
                    else:
                        logger.warning(f"RSS feed error for {feed_url}: {response.status_code}")
                        
            except Exception as e:
                logger.error(f"Error ingesting RSS feed {feed_url}: {e}")
    
    async def _process_rss_data(self, feed: Any, feed_url: str):
        """Process and store RSS feed data"""
        entries = feed.get("entries", [])
        processed_count = 0
        skipped_count = 0
        
        for entry in entries:
            try:
                # Extract text from entry - try multiple fields
                text = (
                    entry.get("summary", "") or 
                    entry.get("description", "") or 
                    (entry.get("content", [{}])[0].get("value", "") if entry.get("content") and len(entry.get("content", [])) > 0 else "")
                )
                
                # Clean HTML tags if present
                if text:
                    import re
                    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
                    text = text.strip()
                
                if not text or len(text) < 10:  # Skip very short entries
                    skipped_count += 1
                    logger.debug(f"Skipping entry (text too short): {entry.get('title', 'No title')[:50]}")
                    continue
                
                # Get title for better context
                title = entry.get("title", "")
                
                # Detect language
                lang = self._detect_language(text)
                
                # Get source ID - prefer link, fallback to id
                source_id = entry.get("link", entry.get("id", ""))
                if not source_id:
                    source_id = f"{feed_url}_{entry.get('title', '')[:50]}"
                
                # Parse timestamp
                if entry.get("published_parsed"):
                    try:
                        timestamp = datetime(*entry.published_parsed[:6])
                    except:
                        timestamp = datetime.utcnow()
                else:
                    timestamp = datetime.utcnow()
                
                feedback = {
                    "source": "rss",
                    "source_id": source_id,
                    "text": text[:5000],  # Limit text length
                    "language": lang.value,
                    "author": self._anonymize_author(entry.get("author", feed_url)),
                    "location": None,  # RSS feeds typically don't have location
                    "timestamp": timestamp.isoformat(),
                    "raw_data": {
                        "title": title,
                        "link": entry.get("link", ""),
                        "feed_url": feed_url
                    }
                }
                
                stored_feedback = await self._store_feedback(feedback)
                if stored_feedback:
                    # Trigger automatic analysis
                    await self._trigger_analysis(stored_feedback["id"], text, lang.value)
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error processing RSS entry: {e}", exc_info=True)
                skipped_count += 1
        
        if processed_count > 0:
            logger.info(f"Processed {processed_count} entries from {feed_url} (skipped {skipped_count})")
    
    def _detect_language(self, text: str) -> LanguageType:
        """Detect language of text including Sheng"""
        try:
            text_lower = text.lower()
            
            # Check for Sheng patterns first
            sheng_keywords = [
                "msee", "sasa", "noma", "poa", "sijui", "wapi", "nini",
                "kama", "buda", "dame", "mrembo", "sheng", "nairobi",
                "mtaa", "gang", "crew", "vibe", "chill", "flex"
            ]
            
            sheng_count = sum(1 for keyword in sheng_keywords if keyword in text_lower)
            if sheng_count >= 2:  # Multiple Sheng words indicate Sheng
                return LanguageType.SHENG
            
            # Use langdetect for standard languages
            lang_code = detect(text)
            if lang_code == "sw":
                return LanguageType.KISWAHILI
            elif lang_code == "en":
                return LanguageType.ENGLISH
            else:
                return LanguageType.MIXED
        except:
            return LanguageType.ENGLISH  # Default
    
    def _anonymize_author(self, author: str) -> str:
        """Anonymize author identifier"""
        # Simple hash-based anonymization
        import hashlib
        return hashlib.sha256(author.encode()).hexdigest()[:8]
    
    async def _store_feedback(self, feedback: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Store feedback in Supabase using service role to bypass RLS"""
        try:
            # Check if already exists (use service role for consistency)
            existing = self.supabase_service.table("citizen_feedback").select("id").eq(
                "source_id", feedback["source_id"]
            ).eq("source", feedback["source"]).execute()
            
            if existing.data:
                return None  # Already exists
            
            # Insert new feedback using service role to bypass RLS
            result = self.supabase_service.table("citizen_feedback").insert(feedback).execute()
            if result.data:
                logger.debug(f"Stored feedback: {feedback['source_id'][:50]}")
                return result.data[0]
            else:
                logger.warning(f"No data returned when storing feedback: {feedback['source_id'][:50]}")
                return None
            
        except Exception as e:
            logger.error(f"Error storing feedback {feedback.get('source_id', 'unknown')[:50]}: {e}", exc_info=True)
            return None
    
    async def _trigger_analysis(self, feedback_id: str, text: str, language: str):
        """Trigger automatic sentiment and sector analysis"""
        try:
            from app.services.ai_service import AIService
            ai_service = AIService()
            
            # Run analysis in background (fire and forget)
            import asyncio
            asyncio.create_task(ai_service.analyze_sentiment(feedback_id, text, language))
            asyncio.create_task(ai_service.classify_sector(feedback_id, text, language))
            
            # Trigger crisis detection check periodically (every 50 items or every 10 minutes)
            # This is done via background task to avoid blocking
            asyncio.create_task(self._periodic_crisis_check())
            
        except Exception as e:
            logger.error(f"Error triggering analysis for {feedback_id}: {e}", exc_info=True)
    
    async def _periodic_crisis_check(self):
        """Periodically check for crisis signals (throttled to avoid excessive checks)"""
        try:
            # Use a simple in-memory lock to prevent concurrent checks
            if not hasattr(self, '_last_crisis_check'):
                self._last_crisis_check = datetime.utcnow() - timedelta(minutes=15)  # Initialize to allow first check
            
            # Only check every 10 minutes
            time_since_last_check = (datetime.utcnow() - self._last_crisis_check).total_seconds() / 60
            if time_since_last_check < 10:
                return
            
            self._last_crisis_check = datetime.utcnow()
            
            from app.services.crisis_detection_service import CrisisDetectionService
            crisis_service = CrisisDetectionService()
            
            # Run crisis detection
            signals = await crisis_service.detect_crisis_signals(time_window_hours=24, min_volume=10)
            
            if signals:
                logger.warning(f"CRISIS DETECTED: {len(signals)} crisis signals found")
                # Performance: Batch send government alerts for critical signals
                from app.services.government_alert_service import GovernmentAlertService
                gov_alert_service = GovernmentAlertService()
                
                # Filter critical/high signals
                critical_signals = [s for s in signals if s.get("severity") in ["critical", "high"]]
                
                # Send alerts in parallel
                if critical_signals:
                    import asyncio
                    alert_tasks = [gov_alert_service.send_crisis_alert(signal) for signal in critical_signals]
                    await asyncio.gather(*alert_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error in periodic crisis check: {e}", exc_info=True)
    
    async def _check_red_flags(self, feedback_id: str, text: str, source: str, location: Optional[str]):
        """Check for red flag alerts"""
        try:
            from app.services.alert_service import AlertService
            alert_service = AlertService()
            await alert_service.check_for_red_flags(feedback_id, text, source, location)
        except Exception as e:
            logger.error(f"Error checking red flags for {feedback_id}: {e}", exc_info=True)
    
    async def _calculate_priority(
        self,
        feedback_id: str,
        text: str,
        sentiment: Optional[str],
        sector: Optional[str],
        location: Optional[str],
        source: Optional[str]
    ):
        """Calculate priority score"""
        try:
            from app.services.priority_service import PriorityService
            priority_service = PriorityService()
            await priority_service.calculate_priority_score(
                feedback_id, text, sentiment, sector, location, source
            )
        except Exception as e:
            logger.error(f"Error calculating priority for {feedback_id}: {e}", exc_info=True)
    
    async def get_ingestion_status(self) -> Dict[str, Any]:
        """Get status of recent ingestion jobs"""
        try:
            # Get recent feedback counts by source
            result = self.supabase.table("citizen_feedback").select(
                "source,created_at"
            ).order("created_at", desc=True).limit(1000).execute()
            
            sources = {}
            for item in result.data:
                source = item["source"]
                if source not in sources:
                    sources[source] = {"count": 0, "latest": None}
                sources[source]["count"] += 1
                if not sources[source]["latest"]:
                    sources[source]["latest"] = item["created_at"]
            
            return {
                "sources": sources,
                "total_recent": len(result.data)
            }
        except Exception as e:
            logger.error(f"Error getting ingestion status: {e}")
            return {"sources": {}, "total_recent": 0}

