"""
AI Service
Handles AI content generation, optimization, and analysis
"""

import httpx
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from sqlalchemy.orm import Session

from app.core.config import get_settings

settings = get_settings()


class AIService:
    """Service for handling AI operations"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.default_model = os.getenv("DEFAULT_AI_MODEL", "gpt-4o-mini")
        self.timeout = 30
        self.db_session = db_session
    
    async def generate_content(
        self,
        prompt: str,
        content_type: str = "text",
        brand_guide_id: Optional[int] = None,
        locale: str = "en-US"
    ) -> Dict[str, Any]:
        """
        Generate AI content using the model router.
        """
        try:
            # Use the Enhanced AI Router for real AI generation
            from app.ai.enhanced_router import EnhancedAIRouter, GenerationRequest
            
            router = EnhancedAIRouter()
            request = GenerationRequest(
                task="content_generation",
                prompt=prompt,
                system=f"You are a professional content creator. Generate {content_type} content.",
                org_id=None,  # Will be set by the calling code
                is_critical=False
            )
            
            result = await router.generate(request)
            
            return {
                "success": True,
                "text": result.text,
                "provider": result.provider,
                "model": result.provider.split(":")[1] if ":" in result.provider else result.provider,
                "token_usage": {
                    "prompt_tokens": result.tokens_in,
                    "completion_tokens": result.tokens_out,
                    "total_tokens": result.tokens_in + result.tokens_out
                },
                "cost_usd": result.cost_gbp * 1.25  # Convert GBP to USD
            }
            
        except Exception as e:
            return {"success": False, "error": f"Content generation failed: {str(e)}"}
    
    async def optimize_content(
        self,
        platform: str,
        draft_content: str,
        brand_guide_id: Optional[int] = None,
        org_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Optimize content for a specific platform using AI.
        """
        try:
            from app.ai.enhanced_router import EnhancedAIRouter, GenerationRequest
            
            router = EnhancedAIRouter(self.db_session)
            
            # Platform-specific optimization rules
            optimization_rules = {
                "facebook": {
                    "max_length": 63206,
                    "max_hashtags": 3,
                    "tone": "engaging",
                    "style": "storytelling, community-focused"
                },
                "instagram": {
                    "max_length": 2200,
                    "max_hashtags": 30,
                    "tone": "visual",
                    "style": "aesthetic, inspirational"
                },
                "linkedin": {
                    "max_length": 3000,
                    "max_hashtags": 5,
                    "tone": "professional",
                    "style": "professional, thought-leadership"
                },
                "twitter": {
                    "max_length": 280,
                    "max_hashtags": 2,
                    "tone": "concise",
                    "style": "newsy, conversational"
                }
            }
            
            rules = optimization_rules.get(platform, optimization_rules["facebook"])
            
            # Get brand guide if provided
            brand_voice_context = ""
            if brand_guide_id and self.db_session:
                from app.models.cms import BrandGuide
                brand_guide = self.db_session.query(BrandGuide).filter(BrandGuide.id == brand_guide_id).first()
                if brand_guide:
                    brand_voice_context = f"""
                    BRAND VOICE GUIDELINES:
                    - Tone: {brand_guide.voice_tone or 'professional'}
                    - Personality: {brand_guide.personality or 'friendly'}
                    - Key messages: {brand_guide.key_messages or 'N/A'}
                    - Avoid: {brand_guide.avoid_words or 'N/A'}
                    """
            
            prompt = f"""
            Optimize this content for {platform}:

            ORIGINAL CONTENT: "{draft_content}"

            PLATFORM CONSTRAINTS:
            - Max length: {rules['max_length']} characters
            - Max hashtags: {rules['max_hashtags']}
            - Tone: {rules['tone']}
            - Style: {rules['style']}
            
            {brand_voice_context}
            
            Optimize the content to:
            1. Fit platform best practices
            2. Maximize engagement potential
            3. Maintain brand voice
            4. Include relevant hashtags (up to {rules['max_hashtags']})
            5. Add compelling call-to-action if appropriate
            
            Return only the optimized content, no explanations.
            """
            
            request = GenerationRequest(
                task="content_optimization",
                prompt=prompt,
                system=f"You are a social media optimization expert specializing in {platform} content. Create engaging, platform-optimized content that drives engagement.",
                org_id=org_id,
                is_critical=False
            )
            
            result = await router.generate(request)
            optimized_text = result.text.strip()
            
            # Apply length constraint if needed
            if len(optimized_text) > rules["max_length"]:
                optimized_text = optimized_text[:rules["max_length"]-3] + "..."
            
            # Count hashtags
            hashtag_count = optimized_text.count("#")
            
            # Apply constraints
            constraints_applied = {
                "character_limit": rules["max_length"],
                "hashtag_limit": rules["max_hashtags"],
                "tone": rules["tone"],
                "style": rules["style"]
            }
            
            return {
                "success": True,
                "optimized_text": optimized_text,
                "constraints_applied": constraints_applied,
                "character_count": len(optimized_text),
                "hashtag_count": hashtag_count,
                "provider": result.provider,
                "cost_gbp": result.cost_gbp,
                "optimization_improvements": [
                    "Content optimized for platform best practices",
                    f"Tone adjusted to {rules['tone']}",
                    f"Length optimized for {platform}",
                    f"Hashtags optimized (using {hashtag_count}/{rules['max_hashtags']})"
                ]
            }
            
        except Exception as e:
            return {"success": False, "error": f"Content optimization failed: {str(e)}"}
    
    async def generate_content_variation(
        self,
        base_content: str,
        variation_type: str,
        brand_guide_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate variations of existing content.
        """
        try:
            # FIXME: Implement actual content variation generation
            variations = {
                "variation_1": f"Variation 1: {base_content}",
                "variation_2": f"Variation 2: {base_content}",
                "variation_3": f"Variation 3: {base_content}"
            }
            
            variation_text = variations.get(variation_type, base_content)
            
            return {
                "success": True,
                "text": variation_text,
                "provider": "openai",
                "model": self.default_model,
                "token_usage": {
                    "prompt_tokens": 5,
                    "completion_tokens": 25,
                    "total_tokens": 30
                },
                "cost_usd": 0.00005
            }
            
        except Exception as e:
            return {"success": False, "error": f"Content variation generation failed: {str(e)}"}
    
    async def analyze_sentiment(
        self,
        content: str
    ) -> Dict[str, Any]:
        """
        Analyze content sentiment and tone.
        """
        try:
            # FIXME: Implement actual sentiment analysis
            # For now, return mock analysis
            mock_analysis = {
                "success": True,
                "sentiment": "positive",
                "confidence": 0.85,
                "tone": "professional",
                "emotions": ["confident", "engaging"],
                "recommendations": [
                    "Content has a positive tone",
                    "Consider adding more emotional appeal",
                    "Good balance of professional and engaging"
                ]
            }
            
            return mock_analysis
            
        except Exception as e:
            return {"success": False, "error": f"Sentiment analysis failed: {str(e)}"}
    
    async def generate_hashtags(
        self,
        content: str,
        platform: str,
        brand_guide_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate relevant hashtags for content.
        """
        try:
            # FIXME: Implement actual hashtag generation
            # For now, return mock hashtags
            mock_hashtags = [
                "#content",
                "#marketing",
                "#socialmedia",
                "#engagement",
                "#brand"
            ]
            
            # Platform-specific hashtag limits
            platform_limits = {
                "facebook": 3,
                "instagram": 30,
                "linkedin": 5,
                "twitter": 2
            }
            
            limit = platform_limits.get(platform, 5)
            hashtags = mock_hashtags[:limit]
            
            return {
                "success": True,
                "hashtags": hashtags,
                "platform": platform,
                "count": len(hashtags)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Hashtag generation failed: {str(e)}"}
    
    async def translate_content(
        self,
        content: str,
        target_language: str,
        source_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Translate content to target language.
        """
        try:
            # FIXME: Implement actual translation
            # For now, return mock translation
            mock_translation = f"Translated to {target_language}: {content}"
            
            return {
                "success": True,
                "translated_text": mock_translation,
                "source_language": source_language,
                "target_language": target_language,
                "provider": "openai",
                "model": self.default_model
            }
            
        except Exception as e:
            return {"success": False, "error": f"Translation failed: {str(e)}"}
    
    async def summarize_content(
        self,
        content: str,
        max_length: int = 100
    ) -> Dict[str, Any]:
        """
        Summarize content to specified length.
        """
        try:
            # FIXME: Implement actual content summarization
            # For now, return mock summary
            mock_summary = content[:max_length] + "..." if len(content) > max_length else content
            
            return {
                "success": True,
                "summary": mock_summary,
                "original_length": len(content),
                "summary_length": len(mock_summary),
                "compression_ratio": len(mock_summary) / len(content)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Content summarization failed: {str(e)}"}
    
    async def generate_content_ideas(
        self,
        topic: str,
        platform: str,
        count: int = 5
    ) -> Dict[str, Any]:
        """
        Generate content ideas for a topic and platform.
        """
        try:
            # FIXME: Implement actual content idea generation
            # For now, return mock ideas
            mock_ideas = [
                f"Content idea 1 for {topic} on {platform}",
                f"Content idea 2 for {topic} on {platform}",
                f"Content idea 3 for {topic} on {platform}",
                f"Content idea 4 for {topic} on {platform}",
                f"Content idea 5 for {topic} on {platform}"
            ]
            
            return {
                "success": True,
                "ideas": mock_ideas[:count],
                "topic": topic,
                "platform": platform,
                "count": len(mock_ideas[:count])
            }
            
        except Exception as e:
            return {"success": False, "error": f"Content idea generation failed: {str(e)}"}
    
    async def check_content_quality(
        self,
        content: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Check content quality and provide recommendations.
        """
        try:
            # FIXME: Implement actual content quality checking
            # For now, return mock quality check
            quality_score = 85
            recommendations = [
                "Content is well-structured",
                "Consider adding more emotional appeal",
                "Good use of keywords",
                "Could benefit from more visual elements"
            ]
            
            return {
                "success": True,
                "quality_score": quality_score,
                "recommendations": recommendations,
                "platform": platform,
                "content_length": len(content)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Content quality check failed: {str(e)}"}
    
    async def generate_emoji_suggestions(
        self,
        content: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Generate emoji suggestions for content.
        """
        try:
            # FIXME: Implement actual emoji suggestion
            # For now, return mock emojis
            mock_emojis = ["🚀", "💡", "✨", "🎯", "🔥"]
            
            return {
                "success": True,
                "emojis": mock_emojis,
                "platform": platform,
                "count": len(mock_emojis)
            }
            
        except Exception as e:
            return {"success": False, "error": f"Emoji suggestion failed: {str(e)}"}
    
    async def generate_call_to_action(
        self,
        content: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Generate call-to-action suggestions for content.
        """
        try:
            # FIXME: Implement actual CTA generation
            # For now, return mock CTAs
            mock_ctas = [
                "Learn more about our services",
                "Follow us for daily updates",
                "Share your thoughts in the comments",
                "Visit our website for more info",
                "Join our community today"
            ]
            
            return {
                "success": True,
                "ctas": mock_ctas,
                "platform": platform,
                "count": len(mock_ctas)
            }
            
        except Exception as e:
            return {"success": False, "error": f"CTA generation failed: {str(e)}"}
    
    async def predict_performance(
        self,
        content: str,
        platform: str,
        org_id: int,
        scheduled_at: Optional[datetime] = None,
        brand_guide_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Predict content performance using AI and historical data.
        """
        try:
            if not self.db_session:
                return {"success": False, "error": "Database session required for performance prediction"}
            
            from app.ai.performance_predictor import PerformancePredictor
            
            predictor = PerformancePredictor(self.db_session)
            prediction = await predictor.predict_performance(
                content=content,
                platform=platform,
                org_id=org_id,
                scheduled_at=scheduled_at,
                brand_guide_id=brand_guide_id
            )
            
            return {
                "success": True,
                "prediction": {
                    "predicted_impressions": prediction.predicted_impressions,
                    "predicted_reach": prediction.predicted_reach,
                    "predicted_engagements": prediction.predicted_engagements,
                    "predicted_ctr": prediction.predicted_ctr,
                    "predicted_engagement_rate": prediction.predicted_engagement_rate,
                    "confidence_score": prediction.confidence_score,
                    "factors": prediction.factors,
                    "recommendations": prediction.recommendations
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Performance prediction failed: {str(e)}"}
    
    async def generate_content_variations(
        self,
        original_content: str,
        platforms: List[str],
        target_audiences: List[str],
        optimization_goals: List[str],
        brand_guide_id: Optional[int] = None,
        max_variations_per_platform: int = 3
    ) -> Dict[str, Any]:
        """
        Generate content variations for multiple platforms and audiences.
        """
        try:
            if not self.db_session:
                return {"success": False, "error": "Database session required for content variations"}
            
            from app.ai.content_variations import ContentVariationsService, VariationRequest
            
            variations_service = ContentVariationsService(self.db_session)
            
            request = VariationRequest(
                original_content=original_content,
                platforms=platforms,
                target_audiences=target_audiences,
                optimization_goals=optimization_goals,
                brand_guide_id=brand_guide_id,
                max_variations_per_platform=max_variations_per_platform
            )
            
            variations = await variations_service.generate_variations(request)
            
            # Convert variations to dictionary format
            variations_data = []
            for variation in variations:
                variations_data.append({
                    "variation_id": variation.variation_id,
                    "content": variation.content,
                    "platform": variation.platform,
                    "target_audience": variation.target_audience,
                    "tone": variation.tone,
                    "length_category": variation.length_category,
                    "hashtags": variation.hashtags,
                    "mentions": variation.mentions,
                    "call_to_action": variation.call_to_action,
                    "optimization_focus": variation.optimization_focus,
                    "confidence_score": variation.confidence_score,
                    "reasoning": variation.reasoning
                })
            
            return {
                "success": True,
                "variations": variations_data,
                "total_variations": len(variations_data),
                "platforms": platforms,
                "audiences": target_audiences,
                "goals": optimization_goals
            }
            
        except Exception as e:
            return {"success": False, "error": f"Content variations generation failed: {str(e)}"}
    
    async def analyze_trends(
        self,
        org_id: int,
        platform: str,
        days_back: int = 30,
        min_volume: int = 5
    ) -> Dict[str, Any]:
        """
        Analyze social media trends for an organization.
        """
        try:
            if not self.db_session:
                return {"success": False, "error": "Database session required for trend analysis"}
            
            from app.ai.trend_analyzer import TrendAnalyzer
            
            analyzer = TrendAnalyzer(self.db_session)
            report = await analyzer.analyze_trends(
                org_id=org_id,
                platform=platform,
                days_back=days_back,
                min_volume=min_volume
            )
            
            # Convert trends to dictionary format
            trends_data = []
            for trend in report.trends:
                trends_data.append({
                    "trend_name": trend.trend_name,
                    "trend_type": trend.trend_type,
                    "platform": trend.platform,
                    "popularity_score": trend.popularity_score,
                    "growth_rate": trend.growth_rate,
                    "volume": trend.volume,
                    "sentiment": trend.sentiment,
                    "related_trends": trend.related_trends,
                    "content_examples": trend.content_examples,
                    "engagement_rate": trend.engagement_rate,
                    "demographics": trend.demographics
                })
            
            # Convert insights to dictionary format
            insights_data = []
            for insight in report.insights:
                insights_data.append({
                    "insight_type": insight.insight_type,
                    "title": insight.title,
                    "description": insight.description,
                    "confidence": insight.confidence,
                    "impact_score": insight.impact_score,
                    "actionable": insight.actionable,
                    "recommendations": insight.recommendations,
                    "data_points": insight.data_points
                })
            
            return {
                "success": True,
                "report": {
                    "report_id": report.report_id,
                    "generated_at": report.generated_at.isoformat(),
                    "platform": report.platform,
                    "time_period": report.time_period,
                    "trends": trends_data,
                    "insights": insights_data,
                    "top_hashtags": report.top_hashtags,
                    "top_topics": report.top_topics,
                    "emerging_trends": [t.trend_name for t in report.emerging_trends],
                    "declining_trends": [t.trend_name for t in report.declining_trends],
                    "recommendations": report.recommendations
                }
            }
            
        except Exception as e:
            return {"success": False, "error": f"Trend analysis failed: {str(e)}"}
    
    async def get_performance_insights(
        self,
        org_id: int,
        platform: str,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Get performance insights and patterns for an organization.
        """
        try:
            if not self.db_session:
                return {"success": False, "error": "Database session required for performance insights"}
            
            from app.ai.performance_predictor import PerformancePredictor
            
            predictor = PerformancePredictor(self.db_session)
            insights = predictor.get_performance_insights(org_id, platform, days_back)
            
            return {
                "success": True,
                "insights": insights
            }
            
        except Exception as e:
            return {"success": False, "error": f"Performance insights failed: {str(e)}"}
    
    async def generate_hashtag_variations(
        self,
        content: str,
        platforms: List[str],
        brand_guide_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate hashtag variations for different platforms.
        """
        try:
            if not self.db_session:
                return {"success": False, "error": "Database session required for hashtag variations"}
            
            from app.ai.content_variations import ContentVariationsService
            
            variations_service = ContentVariationsService(self.db_session)
            hashtag_variations = await variations_service.generate_hashtag_variations(
                content, platforms, brand_guide_id
            )
            
            return {
                "success": True,
                "hashtag_variations": hashtag_variations,
                "platforms": platforms
            }
            
        except Exception as e:
            return {"success": False, "error": f"Hashtag variations generation failed: {str(e)}"}
    
    async def generate_tone_variations(
        self,
        content: str,
        tones: List[str],
        brand_guide_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate content variations with different tones.
        """
        try:
            if not self.db_session:
                return {"success": False, "error": "Database session required for tone variations"}
            
            from app.ai.content_variations import ContentVariationsService
            
            variations_service = ContentVariationsService(self.db_session)
            tone_variations = await variations_service.generate_tone_variations(
                content, tones, brand_guide_id
            )
            
            return {
                "success": True,
                "tone_variations": tone_variations,
                "tones": tones
            }
            
        except Exception as e:
            return {"success": False, "error": f"Tone variations generation failed: {str(e)}"}
