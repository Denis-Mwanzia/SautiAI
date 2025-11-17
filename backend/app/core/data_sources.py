"""
Data Sources Configuration
Comprehensive list of legal, public Kenyan data sources for civic intelligence
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class DataSourceType(str, Enum):
    """Types of data sources"""
    RSS_FEED = "rss_feed"
    API = "api"
    OPEN_DATA_PORTAL = "open_data_portal"
    SOCIAL_MEDIA = "social_media"
    GOVERNMENT_PORTAL = "government_portal"
    NEWS_COMMENTS = "news_comments"
    PUBLIC_COMPLAINTS = "public_complaints"


class DataSource:
    """Data source configuration"""
    
    def __init__(
        self,
        name: str,
        source_type: DataSourceType,
        url: str,
        description: str,
        category_focus: List[str],
        requires_auth: bool = False,
        api_key_name: Optional[str] = None,
        enabled: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.source_type = source_type
        self.url = url
        self.description = description
        self.category_focus = category_focus  # Which of 6 categories this source covers
        self.requires_auth = requires_auth
        self.api_key_name = api_key_name
        self.enabled = enabled
        self.metadata = metadata or {}


# ============================================================================
# RSS FEEDS - News and Media
# ============================================================================

RSS_FEEDS = [
    DataSource(
        name="BBC Africa",
        source_type=DataSourceType.RSS_FEED,
        url="https://www.bbc.com/news/world/africa/rss.xml",
        description="International news covering Kenya and East Africa",
        category_focus=["governance", "public_services", "infrastructure", "security"],
        enabled=True
    ),
    DataSource(
        name="Guardian Africa",
        source_type=DataSourceType.RSS_FEED,
        url="https://www.theguardian.com/world/africa/rss",
        description="African news and analysis including Kenya",
        category_focus=["governance", "public_services", "infrastructure"],
        enabled=True
    ),
    DataSource(
        name="Nation Africa",
        source_type=DataSourceType.RSS_FEED,
        url="https://www.nation.co.ke/rss",
        description="Kenya's leading news source - politics, business, society",
        category_focus=["governance", "public_services", "education", "healthcare"],
        enabled=True
    ),
    DataSource(
        name="The Standard",
        source_type=DataSourceType.RSS_FEED,
        url="https://www.standardmedia.co.ke/rss",
        description="Daily news and analysis from Kenya",
        category_focus=["governance", "public_services", "infrastructure"],
        enabled=True
    ),
    DataSource(
        name="Business Daily Africa",
        source_type=DataSourceType.RSS_FEED,
        url="https://www.businessdailyafrica.com/rss",
        description="Business and economic news from Kenya",
        category_focus=["governance", "public_services", "infrastructure"],
        enabled=True
    ),
    DataSource(
        name="Citizen TV",
        source_type=DataSourceType.RSS_FEED,
        url="https://citizentv.co.ke/rss",
        description="News and current affairs from Kenya",
        category_focus=["governance", "public_services", "security"],
        enabled=True
    ),
    DataSource(
        name="Daily Nation",
        source_type=DataSourceType.RSS_FEED,
        url="https://www.nation.co.ke/kenya/rss",
        description="Kenyan daily news coverage",
        category_focus=["governance", "public_services", "healthcare", "education"],
        enabled=True
    ),
]

# ============================================================================
# OPEN DATA PORTALS
# ============================================================================

OPEN_DATA_SOURCES = [
    DataSource(
        name="Kenya Open Data Portal",
        source_type=DataSourceType.OPEN_DATA_PORTAL,
        url="https://www.opendata.go.ke/",
        description="Government datasets: spending, census, development indicators",
        category_focus=["governance", "public_services", "infrastructure", "healthcare", "education"],
        requires_auth=False,
        enabled=True,
        metadata={
            "api_base": "https://www.opendata.go.ke/api",
            "datasets": [
                "government-spending",
                "census-data",
                "development-indicators",
                "health-statistics",
                "education-statistics"
            ]
        }
    ),
    DataSource(
        name="Kenya National Bureau of Statistics (KNBS)",
        source_type=DataSourceType.OPEN_DATA_PORTAL,
        url="https://www.knbs.or.ke/",
        description="Official statistics: census, economic surveys, sector data",
        category_focus=["governance", "public_services", "healthcare", "education", "infrastructure"],
        requires_auth=False,
        enabled=True,
        metadata={
            "api_base": "https://www.knbs.or.ke/api",
            "datasets": [
                "census",
                "economic-surveys",
                "health-statistics",
                "education-statistics"
            ]
        }
    ),
    DataSource(
        name="Majidata - Water & Sanitation",
        source_type=DataSourceType.OPEN_DATA_PORTAL,
        url="https://majidata.go.ke/",
        description="Georeferenced water and sanitation services data",
        category_focus=["infrastructure", "public_services"],
        requires_auth=False,
        enabled=True,
        metadata={
            "api_base": "https://majidata.go.ke/api",
            "focus": "water-sanitation"
        }
    ),
]

# ============================================================================
# GOVERNMENT PORTALS & COMPLAINTS
# ============================================================================

GOVERNMENT_SOURCES = [
    DataSource(
        name="Kenya ICT Public Complaints Portal",
        source_type=DataSourceType.PUBLIC_COMPLAINTS,
        url="https://www.ict.go.ke/",
        description="Public complaints and service delivery issues",
        category_focus=["governance", "public_services", "infrastructure"],
        requires_auth=False,
        enabled=True,
        metadata={
            "api_endpoint": "https://www.ict.go.ke/api/complaints",
            "format": "json"
        }
    ),
    DataSource(
        name="Mzalendo - Parliamentary Monitoring",
        source_type=DataSourceType.GOVERNMENT_PORTAL,
        url="https://www.mzalendo.com/",
        description="Parliamentary transcripts, politician data, governance",
        category_focus=["governance"],
        requires_auth=False,
        enabled=True,
        metadata={
            "api_base": "https://www.mzalendo.com/api",
            "focus": "parliamentary-monitoring"
        }
    ),
    DataSource(
        name="IPOA - Police Oversight",
        source_type=DataSourceType.PUBLIC_COMPLAINTS,
        url="https://www.ipoa.go.ke/",
        description="Police oversight and accountability data",
        category_focus=["security", "governance"],
        requires_auth=False,
        enabled=True,
        metadata={
            "api_base": "https://www.ipoa.go.ke/api",
            "focus": "police-oversight"
        }
    ),
]

# ============================================================================
# SOCIAL MEDIA (Requires API Keys)
# ============================================================================

SOCIAL_MEDIA_SOURCES = [
    DataSource(
        name="Twitter/X API",
        source_type=DataSourceType.SOCIAL_MEDIA,
        url="https://api.twitter.com/2",
        description="Public tweets about Kenya (requires Bearer Token)",
        category_focus=["governance", "public_services", "healthcare", "education", "infrastructure", "security"],
        requires_auth=True,
        api_key_name="TWITTER_BEARER_TOKEN",
        enabled=False,  # Disabled by default - requires token
        metadata={
            "hashtags": [
                "Kenya", "Nairobi", "KenyaNews", "KenyaPolitics",
                "KenyaHealth", "KenyaEducation", "KenyaEconomy"
            ],
            "geo_bounds": {
                "country": "KE",
                "place_country": "KE"
            }
        }
    ),
    DataSource(
        name="Facebook Graph API",
        source_type=DataSourceType.SOCIAL_MEDIA,
        url="https://graph.facebook.com/v18.0",
        description="Public Facebook pages and posts (requires Access Token)",
        category_focus=["governance", "public_services"],
        requires_auth=True,
        api_key_name="FACEBOOK_ACCESS_TOKEN",
        enabled=False,  # Disabled by default - requires token
        metadata={
            "page_ids": [],  # Add public page IDs here
            "fields": "message,created_time,comments"
        }
    ),
]

# ============================================================================
# CIVIL SOCIETY & COMMUNITY DATA
# ============================================================================

CIVIL_SOCIETY_SOURCES = [
    DataSource(
        name="CSO Data Kenya",
        source_type=DataSourceType.OPEN_DATA_PORTAL,
        url="https://csodata.ke/",
        description="Civil society organization data sharing platform",
        category_focus=["governance", "public_services", "healthcare", "education"],
        requires_auth=False,
        enabled=True,
        metadata={
            "api_base": "https://csodata.ke/api",
            "focus": "civil-society-data"
        }
    ),
    DataSource(
        name="Open Schools Kenya",
        source_type=DataSourceType.OPEN_DATA_PORTAL,
        url="https://openschoolskenya.org/",
        description="Educational institutions data and maps",
        category_focus=["education", "public_services"],
        requires_auth=False,
        enabled=True,
        metadata={
            "api_base": "https://openschoolskenya.org/data",
            "focus": "education-data"
        }
    ),
    DataSource(
        name="Ushahidi Platform",
        source_type=DataSourceType.PUBLIC_COMPLAINTS,
        url="https://ushahidi.com/",
        description="Crowdsourced crisis response and citizen reports",
        category_focus=["governance", "public_services", "security", "infrastructure"],
        requires_auth=False,
        enabled=True,
        metadata={
            "api_base": "https://ushahidi.com/api",
            "focus": "citizen-reports"
        }
    ),
]

# ============================================================================
# NEWS COMMENTS & PUBLIC FORUMS
# ============================================================================

NEWS_COMMENT_SOURCES = [
    DataSource(
        name="Nation Comments",
        source_type=DataSourceType.NEWS_COMMENTS,
        url="https://www.nation.co.ke/",
        description="Public comments on Nation articles",
        category_focus=["governance", "public_services", "healthcare", "education"],
        requires_auth=False,
        enabled=True,
        metadata={
            "scraping_method": "rss_with_comments",
            "comment_api": "https://www.nation.co.ke/api/comments"
        }
    ),
    DataSource(
        name="Standard Comments",
        source_type=DataSourceType.NEWS_COMMENTS,
        url="https://www.standardmedia.co.ke/",
        description="Public comments on Standard articles",
        category_focus=["governance", "public_services"],
        requires_auth=False,
        enabled=True,
        metadata={
            "scraping_method": "rss_with_comments"
        }
    ),
]

# ============================================================================
# AGGREGATED SOURCES LIST
# ============================================================================

ALL_DATA_SOURCES: List[DataSource] = (
    RSS_FEEDS +
    OPEN_DATA_SOURCES +
    GOVERNMENT_SOURCES +
    SOCIAL_MEDIA_SOURCES +
    CIVIL_SOCIETY_SOURCES +
    NEWS_COMMENT_SOURCES
)

# Get enabled sources only
ENABLED_SOURCES = [source for source in ALL_DATA_SOURCES if source.enabled]

# Get sources by type
def get_sources_by_type(source_type: DataSourceType) -> List[DataSource]:
    """Get all sources of a specific type"""
    return [source for source in ALL_DATA_SOURCES if source.source_type == source_type]

# Get sources by category
def get_sources_by_category(category: str) -> List[DataSource]:
    """Get sources that focus on a specific category"""
    return [source for source in ALL_DATA_SOURCES if category in source.category_focus]

# Get RSS feed URLs
def get_rss_feed_urls() -> List[str]:
    """Get all enabled RSS feed URLs"""
    rss_sources = get_sources_by_type(DataSourceType.RSS_FEED)
    return [source.url for source in rss_sources if source.enabled]

# Get sources requiring authentication
def get_auth_required_sources() -> List[DataSource]:
    """Get sources that require authentication"""
    return [source for source in ALL_DATA_SOURCES if source.requires_auth]

# Get sources by name
def get_source_by_name(name: str) -> Optional[DataSource]:
    """Get a specific source by name"""
    for source in ALL_DATA_SOURCES:
        if source.name.lower() == name.lower():
            return source
    return None

