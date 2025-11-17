"""
Sample Data Generation Endpoint
Creates sample feedback data for testing and demos (no API tokens needed)
"""

from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional
from pydantic import BaseModel, Field
import random
from datetime import datetime, timedelta
import logging

from app.models.schemas import APIResponse, SectorType, LanguageType, SentimentType
from app.db.supabase import get_supabase, get_supabase_service

router = APIRouter()
logger = logging.getLogger(__name__)


class SampleDataRequest(BaseModel):
    """Request model for sample data generation"""
    count: int = Field(20, ge=1, le=100, description="Number of sample items to generate")
    sectors: Optional[List[str]] = Field(None, description="List of sectors to generate data for")

# Sample feedback templates
SAMPLE_FEEDBACK = {
    "health": [
        "The hospital in my area has long queues. We need more doctors.",
        "NHIF services are slow. Please improve the system.",
        "Medicine prices are too high. Government should regulate.",
        "Rural clinics lack basic equipment. This is unacceptable.",
        "Maternal health services need improvement in our county.",
    ],
    "education": [
        "School fees are too expensive for many families.",
        "Teachers are underpaid. This affects education quality.",
        "Schools lack textbooks and learning materials.",
        "Digital learning infrastructure is poor in rural areas.",
        "University fees should be reduced for needy students.",
    ],
    "transport": [
        "Matatu fares are too high. Government should regulate.",
        "Roads in my area are in terrible condition.",
        "Public transport is unreliable and unsafe.",
        "Traffic jams in Nairobi are getting worse.",
        "We need better public transport infrastructure.",
    ],
    "governance": [
        "Government services are slow and bureaucratic.",
        "Huduma Namba registration process is confusing.",
        "Citizens need better access to government information.",
        "Corruption is still a major problem.",
        "Government should be more transparent.",
    ],
    "infrastructure": [
        "Water supply is unreliable in our area.",
        "Electricity outages are frequent.",
        "Internet connectivity is poor in rural areas.",
        "We need better waste management systems.",
        "Housing is unaffordable for many Kenyans.",
    ],
    "economy": [
        "Unemployment is high, especially among youth.",
        "Cost of living is rising too fast.",
        "Small businesses need more support.",
        "Taxes are too high for middle-class families.",
        "We need more job opportunities.",
    ],
}

KENYAN_COUNTIES = [
    "Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret",
    "Thika", "Malindi", "Kitale", "Garissa", "Kakamega",
    "Kisii", "Meru", "Nyeri", "Machakos", "Uasin Gishu"
]


@router.post("/sample", response_model=APIResponse)
async def generate_sample_data(
    request: SampleDataRequest = Body(...)
):
    """
    Generate sample feedback data for testing
    
    Creates realistic Kenyan citizen feedback without requiring API tokens.
    Perfect for demos and testing.
    """
    try:
        count = request.count
        sectors = request.sectors
        
        if count > 100:
            count = 100  # Limit for safety
        
        if not sectors:
            sectors = list(SAMPLE_FEEDBACK.keys())
        
        supabase_service = get_supabase_service()  # Use service role to bypass RLS
        generated = []
        
        for i in range(count):
            # Random sector
            sector = random.choice(sectors)
            
            # Random feedback text
            feedback_text = random.choice(SAMPLE_FEEDBACK.get(sector, ["General feedback about services."]))
            
            # Random language (mostly English, some Kiswahili)
            language = random.choice([LanguageType.ENGLISH, LanguageType.KISWAHILI])
            
            # Random location
            location = random.choice(KENYAN_COUNTIES)
            
            # Random timestamp (within last 30 days)
            days_ago = random.randint(0, 30)
            timestamp = datetime.utcnow() - timedelta(days=days_ago)
            
            # Create feedback
            feedback = {
                "source": "sample_data",
                "source_id": f"sample_{i}_{timestamp.timestamp()}",
                "text": feedback_text,
                "language": language.value,
                "author": f"user_{random.randint(1000, 9999)}",
                "location": location,
                "timestamp": timestamp.isoformat(),
                "raw_data": {
                    "sector": sector,
                    "generated": True
                }
            }
            
            # Insert into database using service role
            result = supabase_service.table("citizen_feedback").insert(feedback).execute()
            
            if result.data:
                generated.append(result.data[0])
                
                # Also create sentiment score (random for demo)
                sentiment = random.choice(["positive", "negative", "neutral"])
                sentiment_data = {
                    "feedback_id": result.data[0]["id"],
                    "sentiment": sentiment,
                    "confidence": round(random.uniform(0.7, 0.95), 2),
                    "scores": {
                        "positive": round(random.uniform(0, 1), 2),
                        "negative": round(random.uniform(0, 1), 2),
                        "neutral": round(random.uniform(0, 1), 2),
                    }
                }
                supabase_service.table("sentiment_scores").insert(sentiment_data).execute()
                
                # Create sector classification
                sector_data = {
                    "feedback_id": result.data[0]["id"],
                    "primary_sector": sector,
                    "confidence": round(random.uniform(0.8, 0.95), 2)
                }
                supabase_service.table("sector_classification").insert(sector_data).execute()
        
        logger.info(f"Generated {len(generated)} sample feedback items")
        
        return APIResponse(
            success=True,
            message=f"Generated {len(generated)} sample feedback items",
            data={
                "count": len(generated),
                "sectors": sectors,
                "feedback_ids": [f["id"] for f in generated]
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating sample data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sample/feeds", response_model=APIResponse)
async def get_sample_rss_feeds():
    """Get list of recommended RSS feeds for Kenya"""
    feeds = [
        {
            "name": "Nation Africa",
            "url": "https://www.nation.co.ke/rss",
            "description": "Kenya's leading news source"
        },
        {
            "name": "The Standard",
            "url": "https://www.standardmedia.co.ke/rss",
            "description": "Daily news and analysis"
        },
        {
            "name": "Business Daily",
            "url": "https://www.businessdailyafrica.com/rss",
            "description": "Business and economic news"
        },
        {
            "name": "Citizen TV",
            "url": "https://citizentv.co.ke/rss",
            "description": "Breaking news and updates"
        },
    ]
    
    return APIResponse(
        success=True,
        message="Sample RSS feeds for Kenya",
        data=feeds
    )

