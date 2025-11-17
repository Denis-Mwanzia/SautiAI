"""
PII Removal Service
Service for detecting and removing Personally Identifiable Information
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PIIRemovalService:
    """Service for PII detection and removal"""
    
    # PII patterns
    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b(?:\+?254|0)?[17]\d{8}\b',  # Kenyan phone numbers
        "id_number": r'\b\d{8}\b',  # Kenyan ID numbers (8 digits)
        "credit_card": r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    }
    
    def remove_pii(self, text: str) -> Dict[str, Any]:
        """
        Remove PII from text
        
        Returns:
            Dict with cleaned_text and pii_detected flag
        """
        cleaned_text = text
        pii_detected = []
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                pii_detected.append(pii_type)
                cleaned_text = re.sub(pattern, '[REDACTED]', cleaned_text, flags=re.IGNORECASE)
        
        return {
            "cleaned_text": cleaned_text,
            "pii_detected": pii_detected,
            "pii_removed": len(pii_detected) > 0
        }
    
    def validate_no_pii(self, text: str) -> bool:
        """Check if text contains PII"""
        result = self.remove_pii(text)
        return len(result["pii_detected"]) == 0

