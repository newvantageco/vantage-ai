"""
Safety Service

Provides content moderation, brand guide compliance checks, and safety filters
for AI-generated content before publishing.
"""

from __future__ import annotations

import re
import json
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass
from enum import Enum

import httpx
from openai import AsyncOpenAI

from app.core.config import get_settings


class SafetyLevel(Enum):
    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"


class ViolationType(Enum):
    MODERATION = "moderation"
    BRAND_GUIDE = "brand_guide"
    LENGTH = "length"
    TONE = "tone"
    FORBIDDEN_TERMS = "forbidden_terms"


@dataclass
class SafetyViolation:
    """Details about a safety violation"""
    type: ViolationType
    level: SafetyLevel
    message: str
    suggestion: str
    confidence: float = 0.0


@dataclass
class SafetyResult:
    """Result of safety check"""
    is_safe: bool
    violations: List[SafetyViolation]
    warnings: List[str]
    suggestions: List[str]
    confidence: float


@dataclass
class BrandGuide:
    """Brand guide configuration"""
    blocked_terms: List[str]
    tone_requirements: Dict[str, Any]
    length_limits: Dict[str, int]
    style_guidelines: List[str]
    forbidden_topics: List[str]


class ModerationProvider:
    """Base class for moderation providers"""
    
    async def check_content(self, content: str) -> List[SafetyViolation]:
        """Check content for violations"""
        raise NotImplementedError


class OpenAIModerationProvider(ModerationProvider):
    """OpenAI moderation API provider"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def check_content(self, content: str) -> List[SafetyViolation]:
        """Check content using OpenAI moderation API"""
        try:
            response = await self.client.moderations.create(input=content)
            
            violations = []
            categories = response.results[0].categories
            category_scores = response.results[0].category_scores
            
            # Map OpenAI categories to our violation types
            category_mapping = {
                "hate": (ViolationType.MODERATION, "Hate speech detected"),
                "hate/threatening": (ViolationType.MODERATION, "Threatening hate speech detected"),
                "self-harm": (ViolationType.MODERATION, "Self-harm content detected"),
                "sexual": (ViolationType.MODERATION, "Sexual content detected"),
                "sexual/minors": (ViolationType.MODERATION, "Sexual content involving minors detected"),
                "violence": (ViolationType.MODERATION, "Violent content detected"),
                "violence/graphic": (ViolationType.MODERATION, "Graphic violent content detected")
            }
            
            for category, is_flagged in categories.__dict__.items():
                if is_flagged and category in category_mapping:
                    violation_type, message = category_mapping[category]
                    confidence = getattr(category_scores, category, 0.0)
                    
                    violations.append(SafetyViolation(
                        type=violation_type,
                        level=SafetyLevel.BLOCKED,
                        message=message,
                        suggestion="Please revise the content to remove inappropriate language or topics.",
                        confidence=confidence
                    ))
            
            return violations
            
        except Exception as e:
            # If moderation fails, log error but don't block content
            print(f"OpenAI moderation error: {str(e)}")
            return []


class LocalModerationProvider(ModerationProvider):
    """Local moderation using keyword matching and regex patterns"""
    
    def __init__(self):
        # Basic patterns for common violations
        self.patterns = {
            ViolationType.MODERATION: [
                r'\b(fuck|shit|damn|bitch|asshole)\b',
                r'\b(kill|murder|suicide|die)\b',
                r'\b(hate|hateful|racist|sexist)\b',
                r'\b(violence|violent|attack|fight)\b'
            ],
            ViolationType.FORBIDDEN_TERMS: [
                r'\b(competitor|rival|enemy)\b',
                r'\b(cheap|expensive|overpriced)\b',
                r'\b(best|worst|amazing|terrible)\b'
            ]
        }
    
    async def check_content(self, content: str) -> List[SafetyViolation]:
        """Check content using local pattern matching"""
        violations = []
        content_lower = content.lower()
        
        for violation_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content_lower, re.IGNORECASE)
                if matches:
                    violations.append(SafetyViolation(
                        type=violation_type,
                        level=SafetyLevel.WARNING if violation_type == ViolationType.FORBIDDEN_TERMS else SafetyLevel.BLOCKED,
                        message=f"Content contains potentially inappropriate language: {', '.join(set(matches))}",
                        suggestion="Please revise the content to use more professional language.",
                        confidence=0.8
                    ))
        
        return violations


class SafetyService:
    """Main safety service for content moderation and brand compliance"""
    
    def __init__(self):
        self.settings = get_settings()
        self.moderation_provider = self._initialize_moderation_provider()
        self.brand_guides: Dict[str, BrandGuide] = {}
    
    def _initialize_moderation_provider(self) -> ModerationProvider:
        """Initialize the appropriate moderation provider"""
        if self.settings.openai_api_key:
            return OpenAIModerationProvider(self.settings.openai_api_key)
        else:
            return LocalModerationProvider()
    
    def _load_brand_guide(self, brand_guide_id: str) -> Optional[BrandGuide]:
        """Load brand guide from database or cache"""
        # This would typically load from database
        # For now, return a default brand guide
        if brand_guide_id not in self.brand_guides:
            self.brand_guides[brand_guide_id] = BrandGuide(
                blocked_terms=[
                    "competitor", "rival", "enemy", "cheap", "expensive",
                    "overpriced", "best", "worst", "amazing", "terrible"
                ],
                tone_requirements={
                    "professional": True,
                    "positive": True,
                    "inclusive": True,
                    "avoid_slang": True
                },
                length_limits={
                    "twitter": 280,
                    "facebook": 2200,
                    "instagram": 2200,
                    "linkedin": 3000
                },
                style_guidelines=[
                    "Use active voice",
                    "Avoid jargon",
                    "Be concise and clear",
                    "Include call-to-action"
                ],
                forbidden_topics=[
                    "politics", "religion", "controversial issues"
                ]
            )
        
        return self.brand_guides[brand_guide_id]
    
    def _check_length_limits(self, content: str, platform: str, brand_guide: Optional[BrandGuide]) -> List[SafetyViolation]:
        """Check content length against platform limits"""
        violations = []
        
        if not brand_guide:
            return violations
        
        platform_limits = brand_guide.length_limits
        if platform in platform_limits:
            limit = platform_limits[platform]
            if len(content) > limit:
                violations.append(SafetyViolation(
                    type=ViolationType.LENGTH,
                    level=SafetyLevel.WARNING,
                    message=f"Content exceeds {platform} character limit ({len(content)}/{limit})",
                    suggestion=f"Please shorten the content to {limit} characters or less.",
                    confidence=1.0
                ))
        
        return violations
    
    def _check_brand_guide_compliance(self, content: str, brand_guide: Optional[BrandGuide]) -> List[SafetyViolation]:
        """Check content against brand guide requirements"""
        violations = []
        
        if not brand_guide:
            return violations
        
        content_lower = content.lower()
        
        # Check blocked terms
        for term in brand_guide.blocked_terms:
            if term.lower() in content_lower:
                violations.append(SafetyViolation(
                    type=ViolationType.BRAND_GUIDE,
                    level=SafetyLevel.WARNING,
                    message=f"Content contains blocked term: '{term}'",
                    suggestion="Please replace with approved alternatives from your brand guide.",
                    confidence=0.9
                ))
        
        # Check forbidden topics
        for topic in brand_guide.forbidden_topics:
            if topic.lower() in content_lower:
                violations.append(SafetyViolation(
                    type=ViolationType.BRAND_GUIDE,
                    level=SafetyLevel.BLOCKED,
                    message=f"Content contains forbidden topic: '{topic}'",
                    suggestion="Please remove references to this topic or choose a different angle.",
                    confidence=0.9
                ))
        
        return violations
    
    def _check_tone_compliance(self, content: str, brand_guide: Optional[BrandGuide]) -> List[SafetyViolation]:
        """Check content tone against brand requirements"""
        violations = []
        
        if not brand_guide:
            return violations
        
        tone_requirements = brand_guide.tone_requirements
        content_lower = content.lower()
        
        # Check for professional tone
        if tone_requirements.get("professional", False):
            unprofessional_patterns = [
                r'\b(omg|wtf|lol|rofl|btw|fyi)\b',
                r'\b(awesome|cool|amazing|incredible)\b',
                r'[!]{2,}',  # Multiple exclamation marks
                r'[?]{2,}'   # Multiple question marks
            ]
            
            for pattern in unprofessional_patterns:
                if re.search(pattern, content_lower):
                    violations.append(SafetyViolation(
                        type=ViolationType.TONE,
                        level=SafetyLevel.WARNING,
                        message="Content may not meet professional tone requirements",
                        suggestion="Use more formal language and avoid slang or excessive punctuation.",
                        confidence=0.7
                    ))
        
        # Check for positive tone
        if tone_requirements.get("positive", False):
            negative_patterns = [
                r'\b(problem|issue|difficult|challenge|struggle|fail|failure)\b',
                r'\b(not|never|cannot|won\'t|can\'t)\b'
            ]
            
            negative_count = sum(len(re.findall(pattern, content_lower)) for pattern in negative_patterns)
            if negative_count > 2:  # Allow some negative words but not too many
                violations.append(SafetyViolation(
                    type=ViolationType.TONE,
                    level=SafetyLevel.WARNING,
                    message="Content may be too negative for brand tone",
                    suggestion="Focus on positive aspects and solutions rather than problems.",
                    confidence=0.6
                ))
        
        return violations
    
    async def check_content(
        self, 
        content: str, 
        platform: str = "general",
        brand_guide_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> SafetyResult:
        """
        Comprehensive safety check for content
        
        Args:
            content: The content to check
            platform: Target platform (twitter, facebook, instagram, linkedin)
            brand_guide_id: ID of brand guide to check against
            user_id: User ID for personalized checks
        
        Returns:
            SafetyResult with violations, warnings, and suggestions
        """
        violations = []
        warnings = []
        suggestions = []
        
        # Load brand guide if provided
        brand_guide = None
        if brand_guide_id:
            brand_guide = self._load_brand_guide(brand_guide_id)
        
        # 1. Moderation check
        moderation_violations = await self.moderation_provider.check_content(content)
        violations.extend(moderation_violations)
        
        # 2. Brand guide compliance
        brand_violations = self._check_brand_guide_compliance(content, brand_guide)
        violations.extend(brand_violations)
        
        # 3. Length limits
        length_violations = self._check_length_limits(content, platform, brand_guide)
        violations.extend(length_violations)
        
        # 4. Tone compliance
        tone_violations = self._check_tone_compliance(content, brand_guide)
        violations.extend(tone_violations)
        
        # Categorize violations
        blocked_violations = [v for v in violations if v.level == SafetyLevel.BLOCKED]
        warning_violations = [v for v in violations if v.level == SafetyLevel.WARNING]
        
        # Generate warnings and suggestions
        for violation in warning_violations:
            warnings.append(violation.message)
            suggestions.append(violation.suggestion)
        
        # Determine overall safety
        is_safe = len(blocked_violations) == 0
        
        # Calculate confidence based on violation types and counts
        confidence = 1.0
        if violations:
            avg_confidence = sum(v.confidence for v in violations) / len(violations)
            confidence = max(0.0, 1.0 - (len(violations) * 0.1) - (1.0 - avg_confidence))
        
        return SafetyResult(
            is_safe=is_safe,
            violations=violations,
            warnings=warnings,
            suggestions=suggestions,
            confidence=confidence
        )
    
    async def check_batch_content(
        self, 
        contents: List[str], 
        platform: str = "general",
        brand_guide_id: Optional[str] = None
    ) -> List[SafetyResult]:
        """Check multiple content pieces in batch"""
        results = []
        for content in contents:
            result = await self.check_content(content, platform, brand_guide_id)
            results.append(result)
        return results
    
    def get_safety_guidelines(self, brand_guide_id: Optional[str] = None) -> Dict[str, Any]:
        """Get safety guidelines and recommendations"""
        brand_guide = None
        if brand_guide_id:
            brand_guide = self._load_brand_guide(brand_guide_id)
        
        guidelines = {
            "general": {
                "moderation": "Content is checked for inappropriate language, hate speech, and harmful content",
                "length": "Content length is validated against platform limits",
                "tone": "Content tone is checked against brand requirements"
            },
            "platforms": {
                "twitter": {"max_length": 280, "recommended_length": 240},
                "facebook": {"max_length": 2200, "recommended_length": 2000},
                "instagram": {"max_length": 2200, "recommended_length": 2000},
                "linkedin": {"max_length": 3000, "recommended_length": 2800}
            }
        }
        
        if brand_guide:
            guidelines["brand_guide"] = {
                "blocked_terms": brand_guide.blocked_terms,
                "tone_requirements": brand_guide.tone_requirements,
                "style_guidelines": brand_guide.style_guidelines,
                "forbidden_topics": brand_guide.forbidden_topics
            }
        
        return guidelines


# Global instance
safety_service = SafetyService()
