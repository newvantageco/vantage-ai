from __future__ import annotations

import logging
from typing import Optional

from app.ai.safety import validate_caption
from app.models.content import BrandGuide

logger = logging.getLogger(__name__)


def sanitize_caption(caption: str, brand_guide: Optional[BrandGuide] = None) -> str:
    """
    Sanitize caption using safety validation and platform-specific limits.
    
    Args:
        caption: The original caption text
        brand_guide: Optional brand guide for additional validation
        
    Returns:
        Sanitized caption text
    """
    logger.info(f"Sanitizing caption: {len(caption)} characters")
    
    # Apply safety validation
    validation_result = validate_caption(caption, brand_guide)
    
    if not validation_result.ok:
        logger.warning(f"Caption validation issues: {validation_result.reasons}")
        logger.info(f"Using fixed text: {validation_result.fixed_text}")
    
    return validation_result.fixed_text


def truncate_for_platform(text: str, platform: str, max_length: int) -> str:
    """
    Truncate text for specific platform limits.
    
    Args:
        text: Text to truncate
        platform: Platform name for logging
        max_length: Maximum allowed length
        
    Returns:
        Truncated text if needed
    """
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length-3] + "..."
    logger.warning(f"Truncated {platform} caption from {len(text)} to {len(truncated)} characters")
    return truncated


# Platform-specific limits
PLATFORM_LIMITS = {
    "linkedin": 3000,  # LinkedIn UGC posts
    "facebook": 63206,  # Facebook posts
    "instagram": 2200,  # Instagram captions
    "google_business": 1500,  # Google Business Profile posts
}
