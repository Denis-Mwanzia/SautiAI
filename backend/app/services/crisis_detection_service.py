"""
Crisis Detection Service
Advanced AI-powered service for detecting policy-related crises and early warning signals
Generic system that can detect crises for any policy, bill, or public issue
OPTIMIZED FOR PERFORMANCE
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import re
import math
import asyncio
import hashlib

from app.db.supabase import get_supabase, get_supabase_service
from app.services.ai_service import AIService
# Lazy import to avoid circular dependency
# from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)

# Performance: In-memory cache for crisis detection results
_CRISIS_CACHE: Dict[str, Dict[str, Any]] = {}
_CRISIS_CACHE_TTL_SECONDS = 300  # 5 minutes cache
_MAX_FEEDBACK_ITEMS = 1000  # Limit feedback items for performance
_MAX_HASHTAGS = 50  # Limit hashtags analyzed


class CrisisDetectionService:
    """Service for detecting policy-related crises and early warning signals"""
    
    def __init__(self):
        self.supabase = get_supabase()
        self.supabase_service = get_supabase_service()
        self.ai_service = AIService()
        # Lazy load alert_service to avoid circular import
        self._alert_service = None
        
        # Generic policy-related keywords that indicate potential crises
        self.policy_crisis_keywords = {
            "policy_generic": [
                "policy", "bill", "legislation", "law", "act", "regulation",
                "proposal", "amendment", "reform", "change"
            ],
            "protest_organizing": [
                "protest", "demonstration", "march", "rally", "occupy",
                "reject", "oppose", "boycott", "strike", "shutdown",
                "tuesday", "thursday", "monday", "weekend", "next week"
            ],
            "escalation_signals": [
                "violence", "police", "arrest", "tear gas", "water cannon",
                "injured", "hospital", "death", "killed", "shot",
                "parliament", "state house", "riot", "looting"
            ],
            "sentiment_extreme": [
                "angry", "furious", "outraged", "disgusted", "betrayed",
                "enough is enough", "we are tired", "this is too much"
            ]
        }
        
        # Hashtag patterns for tracking
        self.hashtag_pattern = re.compile(r'#\w+')
        
    async def detect_crisis_signals(
        self,
        time_window_hours: int = 24,
        min_volume: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Detect crisis signals from recent feedback
        
        Args:
            time_window_hours: Time window to analyze
            min_volume: Minimum volume to consider
            
        Returns:
            List of crisis signals detected
        """
        # Performance: Check cache first
        cache_key = f"crisis_signals_{time_window_hours}_{min_volume}"
        now = datetime.utcnow()
        cached = _CRISIS_CACHE.get(cache_key)
        if cached:
            cached_time = cached.get("_cached_at")
            if cached_time:
                if isinstance(cached_time, datetime):
                    if (now - cached_time).total_seconds() < _CRISIS_CACHE_TTL_SECONDS:
                        logger.debug(f"Returning cached crisis signals for {cache_key}")
                        return cached.get("signals", [])
                elif isinstance(cached_time, str):
                    cached_dt = datetime.fromisoformat(cached_time.replace("Z", "+00:00"))
                    if (now - cached_dt).total_seconds() < _CRISIS_CACHE_TTL_SECONDS:
                        logger.debug(f"Returning cached crisis signals for {cache_key}")
                        return cached.get("signals", [])
        
        try:
            start_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Performance: Get feedback and sentiment in parallel queries
            # Get recent feedback
            feedback_result = self.supabase.table("citizen_feedback").select(
                "id, text, source, location, created_at"
            ).gte("created_at", start_time.isoformat()).limit(_MAX_FEEDBACK_ITEMS).order("created_at", desc=True).execute()
            
            if not feedback_result.data or len(feedback_result.data) < min_volume:
                return []
            
            # Get sentiment scores for these feedback items
            feedback_ids = [item.get("id") for item in feedback_result.data]
            sentiment_result = self.supabase.table("sentiment_scores").select(
                "feedback_id, sentiment"
            ).in_("feedback_id", feedback_ids).order("analyzed_at", desc=True).execute()
            
            # Create sentiment map (use most recent sentiment per feedback)
            sentiment_map = {}
            for sent_item in (sentiment_result.data or []):
                fb_id = sent_item.get("feedback_id")
                if fb_id and fb_id not in sentiment_map:
                    sentiment_map[fb_id] = sent_item.get("sentiment", "neutral")
            
            # Combine feedback with sentiment
            feedback_items = []
            for item in feedback_result.data:
                feedback_id = item.get("id")
                sentiment = sentiment_map.get(feedback_id, "neutral")
                
                feedback_items.append({
                    "id": feedback_id,
                    "text": item.get("text", ""),
                    "source": item.get("source"),
                    "location": item.get("location"),
                    "created_at": item.get("created_at"),
                    "sentiment": sentiment
                })
            
            # Performance: Run analyses in parallel
            sentiment_velocity_task = self._analyze_sentiment_velocity(feedback_items, time_window_hours)
            hashtag_intel_task = self._analyze_hashtag_intelligence(feedback_items)
            policy_signals_task = self._detect_policy_crises(feedback_items)
            organizing_signals_task = self._detect_protest_organizing(feedback_items)
            
            # Wait for all analyses to complete
            sentiment_velocity, hashtag_intel, policy_signals, organizing_signals = await asyncio.gather(
                sentiment_velocity_task,
                hashtag_intel_task,
                policy_signals_task,
                organizing_signals_task
            )
            
            # Build crisis signals list
            crisis_signals = []
            
            # 1. Sentiment Velocity Analysis
            if sentiment_velocity.get("velocity_score", 0) > 0.7:
                crisis_signals.append({
                    "type": "sentiment_velocity",
                    "severity": "high",
                    "title": "Rapid Sentiment Deterioration Detected",
                    "description": f"Negative sentiment increased by {sentiment_velocity.get('velocity_percent', 0):.1f}% in {time_window_hours} hours",
                    "data": sentiment_velocity,
                    "recommendation": "Immediate government engagement recommended"
                })
            
            # 2. Hashtag Intelligence
            if hashtag_intel.get("trending_hashtags"):
                crisis_signals.append({
                    "type": "hashtag_trending",
                    "severity": "medium" if len(hashtag_intel["trending_hashtags"]) < 3 else "high",
                    "title": f"Trending Hashtags Detected: {', '.join([h['hashtag'] for h in hashtag_intel['trending_hashtags'][:3]])}",
                    "description": f"{len(hashtag_intel['trending_hashtags'])} hashtags showing rapid growth",
                    "data": hashtag_intel,
                    "recommendation": "Monitor hashtag growth and prepare response"
                })
            
            # 3. Policy-Specific Detection
            crisis_signals.extend(policy_signals)
            
            # 4. Protest Organizing Detection
            crisis_signals.extend(organizing_signals)
            
            # 5. Escalation Prediction (needs results from above)
            escalation_prediction = await self._predict_escalation(feedback_items, sentiment_velocity, hashtag_intel)
            if escalation_prediction.get("escalation_probability", 0) > 0.6:
                crisis_signals.append({
                    "type": "escalation_prediction",
                    "severity": "critical" if escalation_prediction["escalation_probability"] > 0.8 else "high",
                    "title": f"High Escalation Risk: {escalation_prediction['escalation_probability']*100:.0f}% probability",
                    "description": escalation_prediction.get("reason", "Multiple risk factors detected"),
                    "data": escalation_prediction,
                    "recommendation": "URGENT: Immediate intervention required to prevent escalation"
                })
            
            # Performance: Batch store crisis signals
            if crisis_signals:
                await self._batch_store_crisis_signals(crisis_signals)
            
            # Cache the results
            _CRISIS_CACHE[cache_key] = {
                "signals": crisis_signals,
                "_cached_at": now
            }
            
            return crisis_signals
            
        except Exception as e:
            logger.error(f"Error detecting crisis signals: {e}", exc_info=True)
            return []
    
    async def _analyze_sentiment_velocity(
        self,
        feedback_items: List[Dict[str, Any]],
        time_window_hours: int
    ) -> Dict[str, Any]:
        """Analyze how fast sentiment is deteriorating"""
        try:
            if not feedback_items:
                return {"velocity_score": 0, "velocity_percent": 0}
            
            # Performance: Use efficient grouping
            bucket_size = max(1, time_window_hours // 4)
            buckets = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0, "total": 0})
            now = datetime.utcnow()
            
            for item in feedback_items:
                try:
                    created_at = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
                    hours_ago = (now.replace(tzinfo=created_at.tzinfo) - created_at).total_seconds() / 3600
                    bucket = int(hours_ago // bucket_size)
                    
                    sentiment = item.get("sentiment", "neutral")
                    buckets[bucket][sentiment] = buckets[bucket].get(sentiment, 0) + 1
                    buckets[bucket]["total"] += 1
                except (ValueError, KeyError):
                    continue
            
            # Calculate negative sentiment percentage per bucket
            bucket_percentages = []
            for bucket in sorted(buckets.keys()):
                bucket_data = buckets[bucket]
                if bucket_data["total"] > 0:
                    neg_pct = bucket_data["negative"] / bucket_data["total"]
                    bucket_percentages.append(neg_pct)
            
            if len(bucket_percentages) < 2:
                return {"velocity_score": 0, "velocity_percent": 0}
            
            # Calculate velocity (rate of change)
            recent_avg = sum(bucket_percentages[-2:]) / 2 if len(bucket_percentages) >= 2 else bucket_percentages[-1]
            earlier_avg = sum(bucket_percentages[:-2]) / len(bucket_percentages[:-2]) if len(bucket_percentages) > 2 else bucket_percentages[0]
            
            velocity_percent = ((recent_avg - earlier_avg) / max(earlier_avg, 0.1)) * 100
            velocity_score = min(1.0, abs(velocity_percent) / 50)  # Normalize to 0-1
            
            return {
                "velocity_score": velocity_score,
                "velocity_percent": velocity_percent,
                "recent_negative_pct": recent_avg * 100,
                "earlier_negative_pct": earlier_avg * 100,
                "buckets": len(bucket_percentages)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment velocity: {e}")
            return {"velocity_score": 0, "velocity_percent": 0}
    
    async def _analyze_hashtag_intelligence(
        self,
        feedback_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze hashtag trends and growth patterns"""
        try:
            if not feedback_items:
                return {"total_hashtags": 0, "trending_hashtags": []}
            
            hashtag_counts = defaultdict(lambda: {"count": 0, "first_seen": None, "sources": set()})
            
            # Performance: Limit processing to first N items if too many
            items_to_process = feedback_items[:_MAX_FEEDBACK_ITEMS]
            
            for item in items_to_process:
                text = item.get("text", "").lower()
                hashtags = self.hashtag_pattern.findall(text)
                created_at = item["created_at"]
                
                for hashtag in hashtags:
                    hashtag_lower = hashtag.lower()
                    hashtag_counts[hashtag_lower]["count"] += 1
                    if not hashtag_counts[hashtag_lower]["first_seen"]:
                        hashtag_counts[hashtag_lower]["first_seen"] = created_at
                    hashtag_counts[hashtag_lower]["sources"].add(item.get("source", "unknown"))
            
            # Performance: Limit hashtags analyzed
            trending_hashtags = []
            for hashtag, data in hashtag_counts.items():
                if data["count"] >= 3:  # Minimum threshold
                    growth_score = data["count"] * len(data["sources"])
                    trending_hashtags.append({
                        "hashtag": hashtag,
                        "count": data["count"],
                        "sources": list(data["sources"]),
                        "growth_score": growth_score,
                        "first_seen": data["first_seen"]
                    })
            
            # Sort by growth score and limit
            trending_hashtags.sort(key=lambda x: x["growth_score"], reverse=True)
            trending_hashtags = trending_hashtags[:_MAX_HASHTAGS]
            
            return {
                "total_hashtags": len(hashtag_counts),
                "trending_hashtags": trending_hashtags,
                "top_hashtag": trending_hashtags[0] if trending_hashtags else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing hashtag intelligence: {e}")
            return {"total_hashtags": 0, "trending_hashtags": []}
    
    async def _detect_policy_crises(
        self,
        feedback_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect policy-specific crisis signals"""
        signals = []
        
        try:
            if not feedback_items:
                return signals
            
            # Performance: Build text corpus more efficiently
            text_corpus = " ".join([item.get("text", "").lower() for item in feedback_items[:500]])  # Limit corpus size
            
            # Check for policy-related mentions (generic detection)
            policy_keywords = self.policy_crisis_keywords["policy_generic"]
            policy_mentions = sum(1 for keyword in policy_keywords 
                                 if keyword in text_corpus)
            
            if policy_mentions >= 5:
                # Get sentiment for policy-related items
                policy_items = [item for item in feedback_items[:500]  # Limit search
                               if any(kw in item.get("text", "").lower() 
                                     for kw in policy_keywords)]
                
                if policy_items:
                    negative_count = sum(1 for item in policy_items 
                                       if item.get("sentiment") == "negative")
                    negative_pct = (negative_count / len(policy_items)) * 100
                    
                    if negative_pct > 70:
                        signals.append({
                            "type": "policy_crisis",
                            "severity": "critical" if negative_pct > 85 else "high",
                            "title": "Policy-Related Crisis Detected",
                            "description": f"Policy-related content mentioned {policy_mentions} times with {negative_pct:.0f}% negative sentiment",
                            "data": {
                                "policy": "Policy/Issue",
                                "mentions": policy_mentions,
                                "negative_percent": negative_pct,
                                "total_feedback": len(policy_items)
                            },
                            "recommendation": "URGENT: Review policy provisions and engage citizens immediately"
                        })
            
            return signals
            
        except Exception as e:
            logger.error(f"Error detecting policy crises: {e}")
            return []
    
    async def _detect_protest_organizing(
        self,
        feedback_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect language indicating protest organization"""
        signals = []
        
        try:
            if not feedback_items:
                return signals
            
            organizing_items = []
            # Performance: Limit search to first N items
            items_to_check = feedback_items[:500]
            
            for item in items_to_check:
                text_lower = item.get("text", "").lower()
                
                # Check for organizing keywords
                organizing_keywords_found = [
                    kw for kw in self.policy_crisis_keywords["protest_organizing"]
                    if kw in text_lower
                ]
                
                if len(organizing_keywords_found) >= 2:  # Multiple organizing signals
                    organizing_items.append({
                        **item,
                        "organizing_keywords": organizing_keywords_found
                    })
            
            if len(organizing_items) >= 5:
                signals.append({
                    "type": "protest_organizing",
                    "severity": "high" if len(organizing_items) >= 10 else "medium",
                    "title": f"Protest Organizing Detected: {len(organizing_items)} organizing messages",
                    "description": f"Multiple messages contain protest organizing language. Potential demonstration being planned.",
                    "data": {
                        "organizing_messages": len(organizing_items),
                        "sample_keywords": list(set([kw for item in organizing_items 
                                                    for kw in item.get("organizing_keywords", [])]))[:5]
                    },
                    "recommendation": "Monitor closely and prepare for potential demonstrations"
                })
            
            return signals
            
        except Exception as e:
            logger.error(f"Error detecting protest organizing: {e}")
            return []
    
    async def _predict_escalation(
        self,
        feedback_items: List[Dict[str, Any]],
        sentiment_velocity: Dict[str, Any],
        hashtag_intel: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict likelihood of escalation using multiple factors"""
        try:
            if not feedback_items:
                return {"escalation_probability": 0, "risk_factors": []}
            
            risk_factors = []
            risk_score = 0.0
            
            # Factor 1: Sentiment velocity
            if sentiment_velocity.get("velocity_score", 0) > 0.5:
                risk_score += 0.3
                risk_factors.append("Rapid sentiment deterioration")
            
            # Factor 2: Hashtag trending
            if hashtag_intel.get("trending_hashtags") and len(hashtag_intel["trending_hashtags"]) >= 3:
                risk_score += 0.2
                risk_factors.append("Multiple trending hashtags")
            
            # Factor 3: Volume spike
            if len(feedback_items) > 50:
                risk_score += 0.2
                risk_factors.append("High feedback volume")
            
            # Factor 4: Escalation keywords (limit search for performance)
            escalation_keywords_found = 0
            for item in feedback_items[:500]:  # Limit search
                text_lower = item.get("text", "").lower()
                if any(kw in text_lower for kw in self.policy_crisis_keywords["escalation_signals"]):
                    escalation_keywords_found += 1
            
            if escalation_keywords_found > 5:
                risk_score += 0.3
                risk_factors.append("Escalation language detected")
            
            # Factor 5: Negative sentiment percentage
            negative_count = sum(1 for item in feedback_items if item.get("sentiment") == "negative")
            negative_pct = (negative_count / len(feedback_items)) * 100 if feedback_items else 0
            
            if negative_pct > 80:
                risk_score += 0.2
                risk_factors.append(f"Extremely high negative sentiment ({negative_pct:.0f}%)")
            
            # Normalize to 0-1 probability
            escalation_probability = min(1.0, risk_score)
            
            return {
                "escalation_probability": escalation_probability,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                "negative_sentiment_pct": negative_pct,
                "total_feedback": len(feedback_items),
                "recommendation": self._generate_escalation_recommendation(escalation_probability, risk_factors)
            }
            
        except Exception as e:
            logger.error(f"Error predicting escalation: {e}")
            return {"escalation_probability": 0, "risk_factors": []}
    
    def _generate_escalation_recommendation(
        self,
        probability: float,
        risk_factors: List[str]
    ) -> str:
        """Generate recommendation based on escalation probability"""
        if probability > 0.8:
            return "CRITICAL: Immediate government intervention required. Consider policy amendments or public engagement."
        elif probability > 0.6:
            return "HIGH RISK: Proactive engagement recommended. Address concerns before escalation."
        elif probability > 0.4:
            return "MODERATE RISK: Monitor closely and prepare response strategy."
        else:
            return "LOW RISK: Continue monitoring."
    
    async def _batch_store_crisis_signal(self, signal: Dict[str, Any]):
        """Store crisis signal in database (single)"""
        try:
            payload = {
                "signal_type": signal["type"],
                "severity": signal["severity"],
                "title": signal["title"],
                "description": signal["description"],
                "data": signal.get("data", {}),
                "recommendation": signal.get("recommendation", ""),
                "created_at": datetime.utcnow().isoformat()
            }
            
            try:
                self.supabase_service.table("crisis_signals").insert(payload).execute()
            except Exception:
                logger.info(f"Crisis signal detected: {signal['title']}")
                
        except Exception as e:
            logger.error(f"Error storing crisis signal: {e}")
    
    async def _batch_store_crisis_signals(self, signals: List[Dict[str, Any]]):
        """Performance: Batch store crisis signals"""
        try:
            if not signals:
                return
            
            # Batch insert all signals at once
            payloads = []
            for signal in signals:
                payloads.append({
                    "signal_type": signal["type"],
                    "severity": signal["severity"],
                    "title": signal["title"],
                    "description": signal["description"],
                    "data": signal.get("data", {}),
                    "recommendation": signal.get("recommendation", ""),
                    "created_at": datetime.utcnow().isoformat()
                })
            
            try:
                self.supabase_service.table("crisis_signals").insert(payloads).execute()
                logger.info(f"Batch stored {len(signals)} crisis signals")
            except Exception as e:
                logger.warning(f"Could not batch store crisis signals: {e}")
                # Fallback to individual storage
                for signal in signals:
                    await self._batch_store_crisis_signal(signal)
            
            # Performance: Batch create alerts (lazy import)
            if not self._alert_service:
                from app.services.alert_service import AlertService
                self._alert_service = AlertService()
            
            alert_tasks = []
            for signal in signals:
                alert_tasks.append(self._alert_service.create_alert({
                    "alert_type": "crisis_signal",
                    "severity": signal["severity"],
                    "title": signal["title"],
                    "description": signal["description"],
                    "metadata": signal.get("data", {}),
                    "created_at": datetime.utcnow().isoformat(),
                    "acknowledged": False
                }))
            
            # Run alert creation in parallel
            await asyncio.gather(*alert_tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Error batch storing crisis signals: {e}")
    
    async def monitor_policy(
        self,
        policy_name: str,
        keywords: List[str],
        time_window_hours: int = 168  # 7 days
    ) -> Dict[str, Any]:
        """
        Monitor a specific policy for crisis signals
        
        Args:
            policy_name: Name of policy to monitor (e.g., "Finance Bill 2024", "Healthcare Act", "Education Policy")
            keywords: Keywords related to the policy
            time_window_hours: Time window to analyze
            
        Returns:
            Policy monitoring results
        """
        try:
            start_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Performance: Get feedback and sentiment separately for reliability
            # Get feedback matching policy keywords
            result = self.supabase.table("citizen_feedback").select(
                "id, text, source, location, created_at"
            ).gte("created_at", start_time.isoformat()).limit(_MAX_FEEDBACK_ITEMS).order("created_at", desc=True).execute()
            
            if not result.data:
                return {
                    "policy": policy_name,
                    "status": "no_data",
                    "total_mentions": 0
                }
            
            # Filter for policy-related items (in memory for performance)
            policy_feedback = []
            for item in result.data:
                text_lower = item.get("text", "").lower()
                if any(keyword.lower() in text_lower for keyword in keywords):
                    policy_feedback.append(item)
            
            if not policy_feedback:
                return {
                    "policy": policy_name,
                    "status": "no_mentions",
                    "total_mentions": 0
                }
            
            # Get sentiment scores for policy-related feedback
            policy_feedback_ids = [item.get("id") for item in policy_feedback]
            sentiment_result = self.supabase.table("sentiment_scores").select(
                "feedback_id, sentiment"
            ).in_("feedback_id", policy_feedback_ids).order("analyzed_at", desc=True).execute()
            
            # Create sentiment map
            sentiment_map = {}
            for sent_item in (sentiment_result.data or []):
                fb_id = sent_item.get("feedback_id")
                if fb_id and fb_id not in sentiment_map:
                    sentiment_map[fb_id] = sent_item.get("sentiment", "neutral")
            
            # Combine feedback with sentiment
            policy_items = []
            for item in policy_feedback:
                feedback_id = item.get("id")
                sentiment = sentiment_map.get(feedback_id, "neutral")
                policy_items.append({
                    "id": feedback_id,
                    "text": item.get("text", ""),
                    "source": item.get("source"),
                    "location": item.get("location"),
                    "created_at": item.get("created_at"),
                    "sentiment": sentiment
                })
            
            if not policy_items:
                return {
                    "policy": policy_name,
                    "status": "no_mentions",
                    "total_mentions": 0
                }
            
            # Analyze policy sentiment
            negative_count = sum(1 for item in policy_items if item.get("sentiment") == "negative")
            negative_pct = (negative_count / len(policy_items)) * 100
            
            # Analyze trends (parallel)
            sentiment_velocity, hashtag_intel = await asyncio.gather(
                self._analyze_sentiment_velocity(policy_items, time_window_hours),
                self._analyze_hashtag_intelligence(policy_items)
            )
            
            # Determine status
            if negative_pct > 80 and sentiment_velocity.get("velocity_score", 0) > 0.5:
                status = "critical"
            elif negative_pct > 60:
                status = "high_risk"
            elif negative_pct > 40:
                status = "moderate_risk"
            else:
                status = "low_risk"
            
            return {
                "policy": policy_name,
                "status": status,
                "total_mentions": len(policy_items),
                "negative_sentiment_pct": negative_pct,
                "sentiment_velocity": sentiment_velocity,
                "hashtag_intelligence": hashtag_intel,
                "recommendation": self._generate_policy_recommendation(status, negative_pct, sentiment_velocity)
            }
            
        except Exception as e:
            logger.error(f"Error monitoring policy: {e}", exc_info=True)
            return {
                "policy": policy_name,
                "status": "error",
                "error": str(e)
            }
    
    def _generate_policy_recommendation(
        self,
        status: str,
        negative_pct: float,
        sentiment_velocity: Dict[str, Any]
    ) -> str:
        """Generate recommendation for policy monitoring"""
        if status == "critical":
            return f"CRITICAL: {negative_pct:.0f}% negative sentiment with rapid deterioration. Immediate policy review and citizen engagement required."
        elif status == "high_risk":
            return f"HIGH RISK: {negative_pct:.0f}% negative sentiment. Proactive engagement recommended."
        elif status == "moderate_risk":
            return f"MODERATE RISK: {negative_pct:.0f}% negative sentiment. Monitor closely."
        else:
            return f"LOW RISK: Policy sentiment is manageable. Continue monitoring."
