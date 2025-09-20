"""
Content Variations Service
Generates multiple variations of content optimized for different platforms and audiences
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from sqlalchemy.orm import Session

from app.ai.enhanced_router import EnhancedAIRouter, GenerationRequest
from app.models.cms import ContentItem, BrandGuide
from app.observability.tracer import tracer


@dataclass
class ContentVariation:
    """A variation of content optimized for specific criteria"""
    variation_id: str
    content: str
    platform: str
    target_audience: str
    tone: str
    length_category: str  # short, medium, long
    hashtags: List[str]
    mentions: List[str]
    call_to_action: Optional[str]
    optimization_focus: str  # engagement, reach, conversion, brand_awareness
    confidence_score: float  # 0.0 to 1.0
    reasoning: str


@dataclass
class VariationRequest:
    """Request for generating content variations"""
    original_content: str
    platforms: List[str]
    target_audiences: List[str]
    optimization_goals: List[str]  # engagement, reach, conversion, brand_awareness
    brand_guide_id: Optional[int] = None
    max_variations_per_platform: int = 3
    include_hashtag_variations: bool = True
    include_tone_variations: bool = True


class ContentVariationsService:
    """Service for generating content variations using AI"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.ai_router = EnhancedAIRouter(db_session)
        self.tracer = tracer
    
    def _extract_content_elements(self, content: str) -> Dict[str, Any]:
        """Extract key elements from original content"""
        # Extract hashtags
        hashtags = re.findall(r'#\w+', content)
        
        # Extract mentions
        mentions = re.findall(r'@\w+', content)
        
        # Extract URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content)
        
        # Extract potential call-to-action phrases
        cta_patterns = [
            r'(click here|learn more|find out|discover|get started|sign up|download|buy now|shop now)',
            r'(don\'t miss|limited time|act now|join us|follow us)',
            r'(share your|tell us|comment below|let us know)'
        ]
        
        ctas = []
        for pattern in cta_patterns:
            matches = re.findall(pattern, content.lower())
            ctas.extend(matches)
        
        # Determine content type
        content_type = 'text'
        if urls:
            content_type = 'link'
        if any(word in content.lower() for word in ['video', 'watch', 'streaming']):
            content_type = 'video'
        if any(word in content.lower() for word in ['image', 'photo', 'picture']):
            content_type = 'image'
        
        return {
            'hashtags': hashtags,
            'mentions': mentions,
            'urls': urls,
            'ctas': ctas,
            'content_type': content_type,
            'word_count': len(content.split()),
            'character_count': len(content)
        }
    
    def _get_platform_constraints(self, platform: str) -> Dict[str, Any]:
        """Get platform-specific constraints and best practices"""
        constraints = {
            'twitter': {
                'max_length': 280,
                'max_hashtags': 2,
                'tone': 'concise',
                'best_times': ['morning', 'lunch', 'evening'],
                'content_style': 'newsy, conversational'
            },
            'facebook': {
                'max_length': 63206,
                'max_hashtags': 3,
                'tone': 'engaging',
                'best_times': ['morning', 'afternoon', 'evening'],
                'content_style': 'storytelling, community-focused'
            },
            'instagram': {
                'max_length': 2200,
                'max_hashtags': 30,
                'tone': 'visual',
                'best_times': ['morning', 'lunch', 'evening'],
                'content_style': 'aesthetic, inspirational'
            },
            'linkedin': {
                'max_length': 3000,
                'max_hashtags': 5,
                'tone': 'professional',
                'best_times': ['morning', 'lunch'],
                'content_style': 'professional, thought-leadership'
            },
            'tiktok': {
                'max_length': 2200,
                'max_hashtags': 100,
                'tone': 'trendy',
                'best_times': ['evening', 'night'],
                'content_style': 'trendy, entertaining'
            }
        }
        
        return constraints.get(platform, constraints['facebook'])
    
    def _get_brand_guide(self, brand_guide_id: Optional[int]) -> Optional[BrandGuide]:
        """Get brand guide if provided"""
        if not brand_guide_id:
            return None
        
        return self.db.query(BrandGuide).filter(BrandGuide.id == brand_guide_id).first()
    
    async def _generate_platform_variation(self, original_content: str, platform: str,
                                         target_audience: str, optimization_goal: str,
                                         brand_guide: Optional[BrandGuide],
                                         content_elements: Dict[str, Any]) -> ContentVariation:
        """Generate a single platform-specific variation"""
        
        constraints = self._get_platform_constraints(platform)
        
        # Build brand voice context
        brand_voice_context = ""
        if brand_guide:
            brand_voice_context = f"""
            BRAND VOICE GUIDELINES:
            - Tone: {brand_guide.voice_tone or 'professional'}
            - Personality: {brand_guide.personality or 'friendly'}
            - Key messages: {brand_guide.key_messages or 'N/A'}
            - Avoid: {brand_guide.avoid_words or 'N/A'}
            """
        
        prompt = f"""
        Create a {platform}-optimized variation of this content:

        ORIGINAL CONTENT: "{original_content}"

        PLATFORM: {platform}
        TARGET AUDIENCE: {target_audience}
        OPTIMIZATION GOAL: {optimization_goal}
        
        PLATFORM CONSTRAINTS:
        - Max length: {constraints['max_length']} characters
        - Max hashtags: {constraints['max_hashtags']}
        - Tone: {constraints['tone']}
        - Style: {constraints['content_style']}
        
        {brand_voice_context}
        
        CONTENT ELEMENTS TO PRESERVE:
        - Hashtags: {', '.join(content_elements['hashtags'])}
        - Mentions: {', '.join(content_elements['mentions'])}
        - URLs: {', '.join(content_elements['urls'])}
        - CTAs: {', '.join(content_elements['ctas'])}
        
        Create a variation that:
        1. Optimizes for {optimization_goal}
        2. Fits {platform} best practices
        3. Appeals to {target_audience}
        4. Maintains brand voice
        5. Preserves key information and calls-to-action
        
        Respond in this exact JSON format:
        {{
            "content": "<optimized content>",
            "tone": "<tone used>",
            "length_category": "<short/medium/long>",
            "hashtags": ["hashtag1", "hashtag2"],
            "mentions": ["mention1", "mention2"],
            "call_to_action": "<CTA or null>",
            "optimization_focus": "<primary optimization>",
            "confidence_score": <0.0-1.0>,
            "reasoning": "<explanation of changes>"
        }}
        """
        
        request = GenerationRequest(
            task="content_variation",
            prompt=prompt,
            system=f"You are an expert social media content strategist specializing in {platform} optimization. Create engaging, platform-specific content variations that drive {optimization_goal}.",
            org_id=None,
            is_critical=False
        )
        
        result = await self.ai_router.generate(request)
        
        try:
            # Extract JSON from AI response
            response_text = result.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            variation_data = json.loads(response_text)
            
            # Generate unique variation ID
            variation_id = f"{platform}_{target_audience}_{optimization_goal}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return ContentVariation(
                variation_id=variation_id,
                content=variation_data['content'],
                platform=platform,
                target_audience=target_audience,
                tone=variation_data['tone'],
                length_category=variation_data['length_category'],
                hashtags=variation_data.get('hashtags', []),
                mentions=variation_data.get('mentions', []),
                call_to_action=variation_data.get('call_to_action'),
                optimization_focus=variation_data['optimization_focus'],
                confidence_score=variation_data['confidence_score'],
                reasoning=variation_data['reasoning']
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback variation if AI fails
            return self._create_fallback_variation(
                original_content, platform, target_audience, optimization_goal, content_elements
            )
    
    def _create_fallback_variation(self, original_content: str, platform: str,
                                 target_audience: str, optimization_goal: str,
                                 content_elements: Dict[str, Any]) -> ContentVariation:
        """Create a fallback variation if AI generation fails"""
        
        constraints = self._get_platform_constraints(platform)
        
        # Simple content adaptation
        adapted_content = original_content
        
        # Truncate if too long
        if len(adapted_content) > constraints['max_length']:
            adapted_content = adapted_content[:constraints['max_length']-3] + "..."
        
        # Limit hashtags
        hashtags = content_elements['hashtags'][:constraints['max_hashtags']]
        
        variation_id = f"{platform}_{target_audience}_{optimization_goal}_fallback"
        
        return ContentVariation(
            variation_id=variation_id,
            content=adapted_content,
            platform=platform,
            target_audience=target_audience,
            tone=constraints['tone'],
            length_category='medium',
            hashtags=hashtags,
            mentions=content_elements['mentions'],
            call_to_action=None,
            optimization_focus=optimization_goal,
            confidence_score=0.3,
            reasoning="Fallback variation created due to AI generation failure"
        )
    
    async def generate_variations(self, request: VariationRequest) -> List[ContentVariation]:
        """
        Generate content variations for multiple platforms and audiences
        
        Args:
            request: VariationRequest with parameters for generation
            
        Returns:
            List of ContentVariation objects
        """
        with self.tracer.start_as_current_span("ai.content_variations") as span:
            span.set_attributes({
                "ai.platforms_count": len(request.platforms),
                "ai.audiences_count": len(request.target_audiences),
                "ai.goals_count": len(request.optimization_goals)
            })
            
            variations = []
            content_elements = self._extract_content_elements(request.original_content)
            brand_guide = self._get_brand_guide(request.brand_guide_id)
            
            # Generate variations for each combination
            for platform in request.platforms:
                for audience in request.target_audiences:
                    for goal in request.optimization_goals:
                        if len(variations) >= request.max_variations_per_platform * len(request.platforms):
                            break
                        
                        variation = await self._generate_platform_variation(
                            request.original_content,
                            platform,
                            audience,
                            goal,
                            brand_guide,
                            content_elements
                        )
                        variations.append(variation)
            
            span.set_attributes({
                "ai.variations_generated": len(variations)
            })
            
            return variations
    
    async def generate_hashtag_variations(self, original_content: str, 
                                        platforms: List[str],
                                        brand_guide_id: Optional[int] = None) -> Dict[str, List[str]]:
        """
        Generate hashtag variations for different platforms
        
        Args:
            original_content: Original content text
            platforms: List of platforms to optimize for
            brand_guide_id: Optional brand guide ID
            
        Returns:
            Dictionary mapping platform to list of hashtag variations
        """
        hashtag_variations = {}
        brand_guide = self._get_brand_guide(brand_guide_id)
        
        for platform in platforms:
            constraints = self._get_platform_constraints(platform)
            max_hashtags = constraints['max_hashtags']
            
            prompt = f"""
            Generate {max_hashtags} relevant hashtags for this content on {platform}:

            CONTENT: "{original_content}"
            PLATFORM: {platform}
            MAX HASHTAGS: {max_hashtags}
            
            {f"BRAND CONTEXT: {brand_guide.key_messages}" if brand_guide else ""}
            
            Provide hashtags that are:
            1. Relevant to the content
            2. Popular on {platform}
            3. Mix of broad and niche tags
            4. Brand-appropriate
            
            Return as a JSON array: ["#hashtag1", "#hashtag2", ...]
            """
            
            request = GenerationRequest(
                task="hashtag_generation",
                prompt=prompt,
                system=f"You are a social media hashtag expert specializing in {platform} trends and best practices.",
                org_id=None,
                is_critical=False
            )
            
            result = await self.ai_router.generate(request)
            
            try:
                response_text = result.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                hashtags = json.loads(response_text)
                hashtag_variations[platform] = hashtags[:max_hashtags]
                
            except (json.JSONDecodeError, KeyError):
                # Fallback to basic hashtags
                hashtag_variations[platform] = ["#socialmedia", "#content", "#marketing"][:max_hashtags]
        
        return hashtag_variations
    
    async def generate_tone_variations(self, original_content: str,
                                     tones: List[str],
                                     brand_guide_id: Optional[int] = None) -> Dict[str, str]:
        """
        Generate content variations with different tones
        
        Args:
            original_content: Original content text
            tones: List of tones to generate (professional, casual, humorous, etc.)
            brand_guide_id: Optional brand guide ID
            
        Returns:
            Dictionary mapping tone to content variation
        """
        tone_variations = {}
        brand_guide = self._get_brand_guide(brand_guide_id)
        
        for tone in tones:
            prompt = f"""
            Rewrite this content in a {tone} tone while preserving the core message:

            ORIGINAL CONTENT: "{original_content}"
            TARGET TONE: {tone}
            
            {f"BRAND VOICE: {brand_guide.voice_tone}" if brand_guide else ""}
            
            Maintain:
            - Core message and information
            - Key calls-to-action
            - Important details
            - Brand appropriateness
            
            Change:
            - Tone and voice
            - Word choice and phrasing
            - Sentence structure (if needed)
            - Emotional appeal
            
            Return only the rewritten content, no explanations.
            """
            
            request = GenerationRequest(
                task="tone_variation",
                prompt=prompt,
                system=f"You are a professional copywriter expert at adapting content tone while maintaining brand voice and message integrity.",
                org_id=None,
                is_critical=False
            )
            
            result = await self.ai_router.generate(request)
            tone_variations[tone] = result.text.strip()
        
        return tone_variations
    
    def analyze_variation_performance(self, variations: List[ContentVariation],
                                    performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze performance of content variations
        
        Args:
            variations: List of ContentVariation objects
            performance_data: Performance metrics for each variation
            
        Returns:
            List of analysis results with recommendations
        """
        analysis_results = []
        
        for variation in variations:
            performance = performance_data.get(variation.variation_id, {})
            
            # Calculate performance score
            engagement_rate = performance.get('engagement_rate', 0)
            reach = performance.get('reach', 0)
            impressions = performance.get('impressions', 0)
            
            performance_score = (engagement_rate * 0.5) + (reach / 1000 * 0.3) + (impressions / 10000 * 0.2)
            
            # Generate insights
            insights = []
            if engagement_rate > 0.05:
                insights.append("High engagement rate - content resonates well")
            if reach > 1000:
                insights.append("Good reach - content has broad appeal")
            if variation.confidence_score > 0.8:
                insights.append("High AI confidence in variation quality")
            
            recommendations = []
            if engagement_rate < 0.02:
                recommendations.append("Consider adjusting tone or adding more engaging elements")
            if reach < 500:
                recommendations.append("Try different hashtags or posting time")
            if variation.hashtag_count < 3 and variation.platform == 'instagram':
                recommendations.append("Add more hashtags for better discoverability")
            
            analysis_results.append({
                'variation_id': variation.variation_id,
                'platform': variation.platform,
                'performance_score': performance_score,
                'insights': insights,
                'recommendations': recommendations,
                'metrics': performance
            })
        
        return analysis_results
