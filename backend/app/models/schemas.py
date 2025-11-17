"""
Pydantic Schemas
Request and response models for API validation
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class SentimentType(str, Enum):
    """Sentiment classification"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SectorType(str, Enum):
    """Sector classification"""
    HEALTH = "health"
    EDUCATION = "education"
    TRANSPORT = "transport"
    GOVERNANCE = "governance"
    CORRUPTION = "corruption"
    INFRASTRUCTURE = "infrastructure"
    ECONOMY = "economy"
    SECURITY = "security"
    OTHER = "other"


class UrgencyLevel(str, Enum):
    """Urgency classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class LanguageType(str, Enum):
    """Language detection"""
    ENGLISH = "en"
    KISWAHILI = "sw"
    MIXED = "mixed"
    SHENG = "sheng"  # Nairobi street slang


# Request Models
class TwitterIngestRequest(BaseModel):
    """Twitter data ingestion request"""
    hashtags: List[str] = Field(..., description="Hashtags to track")
    max_results: int = Field(100, ge=1, le=500, description="Maximum results per hashtag")
    geo_bounds: Optional[Dict[str, float]] = Field(None, description="Geographic bounds for Kenya")


class FacebookIngestRequest(BaseModel):
    """Facebook data ingestion request"""
    page_ids: List[str] = Field(..., description="Facebook page IDs to monitor")
    max_posts: int = Field(50, ge=1, le=100, description="Maximum posts per page")


class AgentRunRequest(BaseModel):
    """Request to run Jaseci agent"""
    agent_type: str = Field(..., description="Type of agent to run")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Agent parameters")


class SentimentAnalysisRequest(BaseModel):
    """Request for sentiment analysis"""
    feedback_id: str = Field(..., description="ID of the feedback to analyze")
    text: str = Field(..., description="Text to analyze")
    language: str = Field("en", description="Language of the text (en/sw)")


class SectorClassificationRequest(BaseModel):
    """Request for sector classification"""
    feedback_id: str = Field(..., description="ID of the feedback to classify")
    text: str = Field(..., description="Text to classify")
    language: str = Field("en", description="Language of the text (en/sw)")


# Response Models
class CitizenFeedback(BaseModel):
    """Citizen feedback data model"""
    id: Optional[str] = None
    source: str = Field(..., description="Data source (twitter, facebook, rss, etc.)")
    source_id: str = Field(..., description="Original ID from source")
    text: str = Field(..., description="Feedback text content")
    language: LanguageType = Field(..., description="Detected language")
    author: Optional[str] = Field(None, description="Author identifier (anonymized)")
    location: Optional[str] = Field(None, description="Location if available")
    timestamp: datetime = Field(..., description="Original timestamp")
    raw_data: Optional[Dict[str, Any]] = Field(None, description="Raw source data")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SentimentScore(BaseModel):
    """Sentiment analysis result"""
    feedback_id: str
    sentiment: SentimentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    scores: Dict[str, float] = Field(default_factory=dict)
    analyzed_at: datetime


class SectorClassification(BaseModel):
    """Sector classification result"""
    feedback_id: str
    primary_sector: SectorType
    secondary_sectors: List[SectorType] = Field(default_factory=list)
    confidence: float = Field(..., ge=0.0, le=1.0)
    classified_at: datetime


class AISummary(BaseModel):
    """AI-generated summary"""
    id: Optional[str] = None
    batch_id: str
    summary_text: str
    key_points: List[str] = Field(default_factory=list)
    language: LanguageType
    generated_at: datetime
    model_used: str


class PolicyRecommendation(BaseModel):
    """Policy recommendation from AI analysis"""
    id: Optional[str] = None
    sector: SectorType
    title: str
    description: str
    rationale: str
    priority: UrgencyLevel
    affected_counties: List[str] = Field(default_factory=list)
    generated_at: datetime
    confidence: float = Field(..., ge=0.0, le=1.0)


class Alert(BaseModel):
    """System alert for anomalies or crises"""
    id: Optional[str] = None
    alert_type: str = Field(..., description="Type of alert")
    severity: UrgencyLevel
    title: str
    description: str
    sector: Optional[SectorType] = None
    affected_counties: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    acknowledged: bool = False


class DashboardInsights(BaseModel):
    """Dashboard insights aggregation"""
    total_feedback: int
    sentiment_distribution: Dict[str, int]
    sector_distribution: Dict[str, int]
    top_issues: List[Dict[str, Any]]
    trending_complaints: List[Dict[str, Any]]
    recent_alerts: List[Alert]
    county_heatmap: Dict[str, Dict[str, Any]]
    generated_at: datetime


class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    message: str
    data: Optional[Any] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# User Models
class UserProfile(BaseModel):
    """User profile model"""
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"
    created_at: datetime
    updated_at: datetime

