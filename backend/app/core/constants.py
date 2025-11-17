"""
Core Constants
Defines mandatory categories, validation rules, and data flow constants
"""

# MANDATORY: Only these 6 categories are allowed
VALID_CATEGORIES = [
    "healthcare",
    "education",
    "governance",
    "public_services",
    "infrastructure",
    "security"
]

# Category aliases for flexible matching
CATEGORY_ALIASES = {
    "healthcare": ["health", "medical", "hospital", "clinic", "healthcare", "medicine"],
    "education": ["education", "school", "university", "learning", "student", "teacher"],
    "governance": ["governance", "corruption", "government", "public administration", "policy"],
    "public_services": ["public services", "public service", "service delivery", "citizen services"],
    "infrastructure": ["infrastructure", "roads", "transport", "utilities", "water", "electricity"],
    "security": ["security", "safety", "police", "crime", "law enforcement"]
}

# Urgency levels
URGENCY_LEVELS = ["low", "medium", "high", "critical"]

# PII patterns to detect and remove
PII_PATTERNS = [
    r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Credit card
    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
    r'\b\d{10,}\b',  # Phone numbers
    r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # Dates that might be IDs
]

# Allowed data sources (legal, public only)
ALLOWED_SOURCES = [
    "twitter_api",
    "facebook_public",
    "rss_feed",
    "open_data_portal",
    "public_complaints",
    "news_comments",
    "government_statements"
]

# Data validation rules
MIN_TEXT_LENGTH = 10  # Minimum characters for valid feedback
MAX_TEXT_LENGTH = 5000  # Maximum characters to prevent abuse

