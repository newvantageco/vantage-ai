"""
Trend Analysis Service
Analyzes social media trends, hashtags, and content patterns using AI
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from collections import Counter, defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.ai.enhanced_router import EnhancedAIRouter, GenerationRequest
from app.models.analytics import PostMetrics, AnalyticsSummary
from app.models.cms import ContentItem
from app.models.publishing import ExternalReference
from app.observability.tracer import tracer


@dataclass
class TrendData:
    """Trend analysis data for a specific topic or hashtag"""
    trend_name: str
    trend_type: str  # hashtag, topic, keyword, event
    platform: str
    popularity_score: float  # 0.0 to 1.0
    growth_rate: float  # Percentage change
    volume: int  # Number of mentions/posts
    sentiment: float  # -1.0 to 1.0
    peak_time: Optional[datetime]
    related_trends: List[str]
    content_examples: List[str]
    engagement_rate: float
    demographics: Dict[str, Any]  # Age groups, locations, etc.


@dataclass
class TrendInsight:
    """Insight derived from trend analysis"""
    insight_type: str  # opportunity, warning, prediction, recommendation
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    impact_score: float  # 0.0 to 1.0
    actionable: bool
    recommendations: List[str]
    data_points: Dict[str, Any]


@dataclass
class TrendReport:
    """Comprehensive trend analysis report"""
    report_id: str
    generated_at: datetime
    platform: str
    time_period: str
    trends: List[TrendData]
    insights: List[TrendInsight]
    top_hashtags: List[Tuple[str, int]]
    top_topics: List[Tuple[str, int]]
    emerging_trends: List[TrendData]
    declining_trends: List[TrendData]
    recommendations: List[str]


class TrendAnalyzer:
    """AI-powered trend analysis service"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.ai_router = EnhancedAIRouter(db_session)
        self.tracer = tracer
    
    def _extract_hashtags_from_content(self, content: str) -> List[str]:
        """Extract hashtags from content text"""
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, content)
        return [tag.lower() for tag in hashtags]
    
    def _extract_keywords_from_content(self, content: str) -> List[str]:
        """Extract keywords from content text"""
        # Remove hashtags, mentions, and URLs
        clean_content = re.sub(r'#\w+|@\w+|https?://\S+', '', content)
        
        # Split into words and filter
        words = re.findall(r'\b\w+\b', clean_content.lower())
        
        # Filter out common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does',
            'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        }
        
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        return keywords
    
    def _get_historical_trend_data(self, org_id: int, platform: str, 
                                 days_back: int = 30) -> Dict[str, Any]:
        """Get historical trend data from organization's content"""
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Get content with metrics
        query = self.db.query(ContentItem, PostMetrics, ExternalReference).join(
            ExternalReference, ContentItem.id == ExternalReference.content_item_id
        ).join(
            PostMetrics, ExternalReference.id == PostMetrics.external_reference_id
        ).filter(
            and_(
                ContentItem.organization_id == org_id,
                PostMetrics.platform == platform,
                PostMetrics.metric_date >= cutoff_date
            )
        )
        
        hashtag_counts = Counter()
        keyword_counts = Counter()
        engagement_by_hashtag = defaultdict(list)
        engagement_by_keyword = defaultdict(list)
        content_examples = defaultdict(list)
        
        for content_item, metrics, ext_ref in query:
            content = content_item.content or ""
            
            # Extract hashtags and keywords
            hashtags = self._extract_hashtags_from_content(content)
            keywords = self._extract_keywords_from_content(content)
            
            # Count occurrences
            for hashtag in hashtags:
                hashtag_counts[hashtag] += 1
                engagement_by_hashtag[hashtag].append(metrics.engagement_rate or 0)
                if len(content_examples[hashtag]) < 3:
                    content_examples[hashtag].append(content[:100] + "...")
            
            for keyword in keywords:
                keyword_counts[keyword] += 1
                engagement_by_keyword[keyword].append(metrics.engagement_rate or 0)
        
        return {
            'hashtag_counts': dict(hashtag_counts.most_common(50)),
            'keyword_counts': dict(keyword_counts.most_common(50)),
            'engagement_by_hashtag': dict(engagement_by_hashtag),
            'engagement_by_keyword': dict(engagement_by_keyword),
            'content_examples': dict(content_examples)
        }
    
    async def _analyze_trend_with_ai(self, trend_name: str, platform: str,
                                   trend_data: Dict[str, Any]) -> TrendData:
        """Use AI to analyze a specific trend"""
        
        prompt = f"""
        Analyze this social media trend and provide insights:

        TREND: {trend_name}
        PLATFORM: {platform}
        
        TREND DATA:
        - Volume: {trend_data.get('volume', 0)} mentions
        - Growth Rate: {trend_data.get('growth_rate', 0):.1f}%
        - Engagement Rate: {trend_data.get('engagement_rate', 0):.3f}
        - Content Examples: {trend_data.get('content_examples', [])}
        
        Provide analysis in this exact JSON format:
        {{
            "popularity_score": <0.0-1.0>,
            "sentiment": <-1.0 to 1.0>,
            "trend_type": "<hashtag|topic|keyword|event>",
            "related_trends": ["trend1", "trend2", "trend3"],
            "demographics": {{
                "age_groups": ["18-24", "25-34"],
                "locations": ["US", "UK"],
                "interests": ["technology", "lifestyle"]
            }},
            "insights": [
                "insight1",
                "insight2"
            ],
            "recommendations": [
                "recommendation1",
                "recommendation2"
            ]
        }}
        
        Consider:
        1. Current popularity and momentum
        2. Sentiment and brand safety
        3. Target audience alignment
        4. Content opportunities
        5. Competitive landscape
        """
        
        request = GenerationRequest(
            task="trend_analysis",
            prompt=prompt,
            system=f"You are a social media trend analyst expert in {platform} trends and audience behavior. Provide data-driven insights and actionable recommendations.",
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
            
            analysis = json.loads(response_text)
            
            return TrendData(
                trend_name=trend_name,
                trend_type=analysis['trend_type'],
                platform=platform,
                popularity_score=analysis['popularity_score'],
                growth_rate=trend_data.get('growth_rate', 0),
                volume=trend_data.get('volume', 0),
                sentiment=analysis['sentiment'],
                peak_time=None,  # Would need time-series analysis
                related_trends=analysis['related_trends'],
                content_examples=trend_data.get('content_examples', []),
                engagement_rate=trend_data.get('engagement_rate', 0),
                demographics=analysis['demographics']
            )
            
        except (json.JSONDecodeError, KeyError):
            # Fallback trend data
            return TrendData(
                trend_name=trend_name,
                trend_type='hashtag',
                platform=platform,
                popularity_score=0.5,
                growth_rate=0,
                volume=trend_data.get('volume', 0),
                sentiment=0.0,
                peak_time=None,
                related_trends=[],
                content_examples=trend_data.get('content_examples', []),
                engagement_rate=trend_data.get('engagement_rate', 0),
                demographics={}
            )
    
    async def analyze_trends(self, org_id: int, platform: str, 
                           days_back: int = 30,
                           min_volume: int = 5) -> TrendReport:
        """
        Analyze trends for an organization's content
        
        Args:
            org_id: Organization ID
            platform: Platform to analyze (facebook, instagram, twitter, linkedin)
            days_back: Number of days to look back
            min_volume: Minimum volume threshold for trends
            
        Returns:
            TrendReport with comprehensive trend analysis
        """
        with self.tracer.start_as_current_span("ai.trend_analysis") as span:
            span.set_attributes({
                "ai.platform": platform,
                "ai.org_id": org_id,
                "ai.days_back": days_back
            })
            
            # Get historical data
            historical_data = self._get_historical_trend_data(org_id, platform, days_back)
            
            # Analyze top hashtags
            top_hashtags = list(historical_data['hashtag_counts'].items())[:20]
            top_topics = list(historical_data['keyword_counts'].items())[:20]
            
            # Generate trend data for top hashtags
            trends = []
            for hashtag, volume in top_hashtags:
                if volume >= min_volume:
                    engagement_rates = historical_data['engagement_by_hashtag'].get(hashtag, [])
                    avg_engagement = sum(engagement_rates) / len(engagement_rates) if engagement_rates else 0
                    
                    trend_data = {
                        'volume': volume,
                        'growth_rate': 0,  # Would need historical comparison
                        'engagement_rate': avg_engagement,
                        'content_examples': historical_data['content_examples'].get(hashtag, [])
                    }
                    
                    trend = await self._analyze_trend_with_ai(hashtag, platform, trend_data)
                    trends.append(trend)
            
            # Identify emerging and declining trends
            emerging_trends = [t for t in trends if t.growth_rate > 10 and t.popularity_score > 0.7]
            declining_trends = [t for t in trends if t.growth_rate < -10 and t.popularity_score < 0.3]
            
            # Generate insights
            insights = await self._generate_trend_insights(trends, historical_data, platform)
            
            # Generate recommendations
            recommendations = await self._generate_trend_recommendations(trends, insights, platform)
            
            report = TrendReport(
                report_id=f"trend_report_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                generated_at=datetime.now(),
                platform=platform,
                time_period=f"{days_back} days",
                trends=trends,
                insights=insights,
                top_hashtags=top_hashtags,
                top_topics=top_topics,
                emerging_trends=emerging_trends,
                declining_trends=declining_trends,
                recommendations=recommendations
            )
            
            span.set_attributes({
                "ai.trends_analyzed": len(trends),
                "ai.insights_generated": len(insights),
                "ai.emerging_trends": len(emerging_trends)
            })
            
            return report
    
    async def _generate_trend_insights(self, trends: List[TrendData], 
                                     historical_data: Dict[str, Any],
                                     platform: str) -> List[TrendInsight]:
        """Generate insights from trend analysis"""
        
        insights = []
        
        # Analyze top performing trends
        high_engagement_trends = [t for t in trends if t.engagement_rate > 0.05]
        if high_engagement_trends:
            insights.append(TrendInsight(
                insight_type="opportunity",
                title="High Engagement Trends Identified",
                description=f"Found {len(high_engagement_trends)} trends with engagement rates above 5%",
                confidence=0.8,
                impact_score=0.7,
                actionable=True,
                recommendations=[
                    "Create content around high-engagement trends",
                    "Monitor these trends for future content opportunities"
                ],
                data_points={"high_engagement_trends": [t.trend_name for t in high_engagement_trends]}
            ))
        
        # Analyze sentiment patterns
        positive_trends = [t for t in trends if t.sentiment > 0.3]
        negative_trends = [t for t in trends if t.sentiment < -0.3]
        
        if len(positive_trends) > len(negative_trends):
            insights.append(TrendInsight(
                insight_type="opportunity",
                title="Positive Sentiment Dominance",
                description="Most trends show positive sentiment, indicating good brand alignment",
                confidence=0.7,
                impact_score=0.6,
                actionable=True,
                recommendations=[
                    "Leverage positive sentiment trends",
                    "Maintain current content strategy"
                ],
                data_points={"positive_trends": len(positive_trends), "negative_trends": len(negative_trends)}
            ))
        
        # Analyze content diversity
        unique_hashtags = len(historical_data['hashtag_counts'])
        if unique_hashtags < 10:
            insights.append(TrendInsight(
                insight_type="warning",
                title="Limited Hashtag Diversity",
                description=f"Only {unique_hashtags} unique hashtags used, limiting reach potential",
                confidence=0.9,
                impact_score=0.5,
                actionable=True,
                recommendations=[
                    "Research and test new hashtags",
                    "Expand hashtag strategy for better discoverability"
                ],
                data_points={"unique_hashtags": unique_hashtags}
            ))
        
        return insights
    
    async def _generate_trend_recommendations(self, trends: List[TrendData],
                                            insights: List[TrendInsight],
                                            platform: str) -> List[str]:
        """Generate actionable recommendations based on trend analysis"""
        
        recommendations = []
        
        # Get top performing trends
        top_trends = sorted(trends, key=lambda t: t.engagement_rate, reverse=True)[:5]
        
        if top_trends:
            recommendations.append(f"Focus on top-performing trends: {', '.join([t.trend_name for t in top_trends])}")
        
        # Platform-specific recommendations
        platform_recommendations = {
            'instagram': [
                "Use 15-20 hashtags for maximum reach",
                "Post during peak hours (6-9 PM)",
                "Focus on visual content with trending hashtags"
            ],
            'twitter': [
                "Keep hashtags to 1-2 per tweet",
                "Engage with trending topics in real-time",
                "Use trending hashtags in replies and retweets"
            ],
            'facebook': [
                "Use 2-3 relevant hashtags",
                "Focus on community-building content",
                "Share trending topics in groups"
            ],
            'linkedin': [
                "Use professional hashtags",
                "Focus on industry trends and thought leadership",
                "Engage with trending business topics"
            ]
        }
        
        recommendations.extend(platform_recommendations.get(platform, []))
        
        # AI-generated recommendations
        if trends:
            prompt = f"""
            Based on this trend analysis for {platform}, provide 3 actionable recommendations:

            TOP TRENDS: {[t.trend_name for t in trends[:5]]}
            EMERGING TRENDS: {[t.trend_name for t in trends if t.growth_rate > 10]}
            HIGH ENGAGEMENT: {[t.trend_name for t in trends if t.engagement_rate > 0.05]}

            Provide specific, actionable recommendations for content strategy.
            """
            
            request = GenerationRequest(
                task="trend_recommendations",
                prompt=prompt,
                system=f"You are a social media strategist expert in {platform} marketing. Provide specific, actionable recommendations based on trend data.",
                org_id=None,
                is_critical=False
            )
            
            result = await self.ai_router.generate(request)
            
            # Extract recommendations from AI response
            ai_recommendations = result.text.strip().split('\n')
            recommendations.extend([rec.strip('- ').strip() for rec in ai_recommendations if rec.strip()])
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    async def predict_trend_evolution(self, trend_name: str, platform: str,
                                    historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict how a trend might evolve
        
        Args:
            trend_name: Name of the trend to predict
            platform: Platform the trend is on
            historical_data: Historical performance data
            
        Returns:
            Dictionary with predictions and confidence scores
        """
        
        prompt = f"""
        Predict the evolution of this trend over the next 30 days:

        TREND: {trend_name}
        PLATFORM: {platform}
        
        HISTORICAL DATA:
        - Current Volume: {historical_data.get('volume', 0)}
        - Growth Rate: {historical_data.get('growth_rate', 0):.1f}%
        - Engagement Rate: {historical_data.get('engagement_rate', 0):.3f}
        - Sentiment: {historical_data.get('sentiment', 0):.2f}
        
        Predict in this JSON format:
        {{
            "predicted_volume_30d": <number>,
            "predicted_peak_time": "<date or 'unknown'>",
            "predicted_duration": "<short|medium|long>",
            "confidence_score": <0.0-1.0>,
            "risk_factors": ["factor1", "factor2"],
            "opportunity_factors": ["factor1", "factor2"],
            "recommendations": ["rec1", "rec2"]
        }}
        
        Consider:
        1. Historical growth patterns
        2. Platform-specific trend lifecycles
        3. Seasonal factors
        4. Competitive landscape
        5. External events and news
        """
        
        request = GenerationRequest(
            task="trend_prediction",
            prompt=prompt,
            system=f"You are a trend forecasting expert specializing in {platform} social media trends. Provide data-driven predictions with confidence levels.",
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
            
            prediction = json.loads(response_text)
            return prediction
            
        except (json.JSONDecodeError, KeyError):
            return {
                "predicted_volume_30d": historical_data.get('volume', 0),
                "predicted_peak_time": "unknown",
                "predicted_duration": "medium",
                "confidence_score": 0.3,
                "risk_factors": ["Limited historical data"],
                "opportunity_factors": ["Growing trend"],
                "recommendations": ["Monitor trend closely", "Prepare content variations"]
            }
    
    def get_trend_alerts(self, org_id: int, platform: str,
                        threshold_engagement: float = 0.05,
                        threshold_growth: float = 20.0) -> List[Dict[str, Any]]:
        """
        Get alerts for significant trend changes
        
        Args:
            org_id: Organization ID
            platform: Platform to monitor
            threshold_engagement: Minimum engagement rate for alerts
            threshold_growth: Minimum growth rate for alerts
            
        Returns:
            List of trend alerts
        """
        # This would typically integrate with real-time monitoring
        # For now, return alerts based on recent analysis
        
        alerts = []
        
        # Get recent trend data
        historical_data = self._get_historical_trend_data(org_id, platform, 7)  # Last 7 days
        
        # Check for high-engagement trends
        for hashtag, volume in historical_data['hashtag_counts'].items():
            if volume >= 3:  # Minimum volume threshold
                engagement_rates = historical_data['engagement_by_hashtag'].get(hashtag, [])
                if engagement_rates:
                    avg_engagement = sum(engagement_rates) / len(engagement_rates)
                    if avg_engagement >= threshold_engagement:
                        alerts.append({
                            'type': 'high_engagement',
                            'trend': hashtag,
                            'platform': platform,
                            'value': avg_engagement,
                            'message': f"High engagement trend detected: {hashtag} ({avg_engagement:.3f})",
                            'priority': 'medium',
                            'timestamp': datetime.now()
                        })
        
        return alerts
