"""
Performance Prediction Service
Uses AI to predict content performance based on historical data and content characteristics
"""

from __future__ import annotations

import json
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.ai.enhanced_router import EnhancedAIRouter, GenerationRequest
from app.models.analytics import PostMetrics, AnalyticsSummary
from app.models.cms import ContentItem
from app.models.publishing import ExternalReference
from app.observability.tracer import tracer


@dataclass
class PerformancePrediction:
    """Predicted performance metrics for content"""
    predicted_impressions: int
    predicted_reach: int
    predicted_engagements: int
    predicted_ctr: float
    predicted_engagement_rate: float
    confidence_score: float  # 0.0 to 1.0
    factors: Dict[str, Any]  # Key factors influencing prediction
    recommendations: List[str]  # AI-generated recommendations


@dataclass
class ContentFeatures:
    """Extracted features from content for prediction"""
    content_length: int
    hashtag_count: int
    mention_count: int
    has_media: bool
    content_type: str
    platform: str
    time_of_day: int  # Hour of day
    day_of_week: int  # 0-6 (Monday-Sunday)
    sentiment_score: float  # -1.0 to 1.0
    topic_categories: List[str]
    brand_voice_match: float  # 0.0 to 1.0


class PerformancePredictor:
    """AI-powered performance prediction service"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.ai_router = EnhancedAIRouter(db_session)
        self.tracer = tracer
    
    def _extract_content_features(self, content: str, platform: str, 
                                scheduled_at: Optional[datetime] = None,
                                brand_guide_id: Optional[int] = None) -> ContentFeatures:
        """Extract features from content for prediction"""
        
        # Basic content analysis
        content_length = len(content)
        hashtag_count = content.count('#')
        mention_count = content.count('@')
        has_media = bool(content.count('http') or content.count('www.'))
        
        # Time analysis
        if scheduled_at:
            time_of_day = scheduled_at.hour
            day_of_week = scheduled_at.weekday()
        else:
            time_of_day = datetime.now().hour
            day_of_week = datetime.now().weekday()
        
        # Simple sentiment analysis (can be enhanced with proper NLP)
        positive_words = ['great', 'amazing', 'wonderful', 'excellent', 'fantastic', 'love', 'best']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'worst', 'disappointed']
        
        content_lower = content.lower()
        positive_count = sum(1 for word in positive_words if word in content_lower)
        negative_count = sum(1 for word in negative_words if word in content_lower)
        
        sentiment_score = (positive_count - negative_count) / max(1, len(content.split()))
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        # Topic categorization (simplified)
        topic_categories = []
        if any(word in content_lower for word in ['sale', 'discount', 'offer', 'deal']):
            topic_categories.append('promotional')
        if any(word in content_lower for word in ['new', 'launch', 'announcement']):
            topic_categories.append('announcement')
        if any(word in content_lower for word in ['tip', 'how', 'guide', 'tutorial']):
            topic_categories.append('educational')
        if any(word in content_lower for word in ['thank', 'appreciate', 'grateful']):
            topic_categories.append('gratitude')
        
        return ContentFeatures(
            content_length=content_length,
            hashtag_count=hashtag_count,
            mention_count=mention_count,
            has_media=has_media,
            content_type='text',  # Could be enhanced to detect image/video
            platform=platform,
            time_of_day=time_of_day,
            day_of_week=day_of_week,
            sentiment_score=sentiment_score,
            topic_categories=topic_categories,
            brand_voice_match=0.8  # Placeholder - would need brand guide analysis
        )
    
    def _get_historical_performance(self, org_id: int, platform: str, 
                                  days_back: int = 90) -> List[Dict[str, Any]]:
        """Get historical performance data for similar content"""
        
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        # Get post metrics with external references to link to content
        metrics_query = self.db.query(PostMetrics, ExternalReference).join(
            ExternalReference, PostMetrics.external_reference_id == ExternalReference.id
        ).filter(
            and_(
                PostMetrics.organization_id == org_id,
                PostMetrics.platform == platform,
                PostMetrics.metric_date >= cutoff_date,
                PostMetrics.impressions > 0  # Only posts with some performance data
            )
        ).order_by(desc(PostMetrics.metric_date)).limit(100)
        
        historical_data = []
        for metrics, ext_ref in metrics_query:
            # Get content details if available
            content_item = None
            if ext_ref and ext_ref.schedule_id:
                # Try to get content from schedule
                from app.models.schedules import Schedule
                schedule = self.db.query(Schedule).filter(
                    Schedule.id == ext_ref.schedule_id
                ).first()
                if schedule and schedule.content_item_id:
                    content_item = self.db.query(ContentItem).filter(
                        ContentItem.id == schedule.content_item_id
                    ).first()
            
            historical_data.append({
                'impressions': metrics.impressions,
                'reach': metrics.reach,
                'engagements': metrics.engagements,
                'ctr': metrics.ctr,
                'engagement_rate': metrics.engagement_rate,
                'content_length': len(content_item.content) if content_item else 0,
                'hashtag_count': len(content_item.hashtags) if content_item and content_item.hashtags else 0,
                'metric_date': metrics.metric_date,
                'platform': metrics.platform
            })
        
        return historical_data
    
    def _calculate_baseline_metrics(self, historical_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate baseline metrics from historical data"""
        if not historical_data:
            return {
                'avg_impressions': 1000,
                'avg_reach': 800,
                'avg_engagements': 50,
                'avg_ctr': 0.02,
                'avg_engagement_rate': 0.05
            }
        
        impressions = [d['impressions'] for d in historical_data if d['impressions'] > 0]
        reach = [d['reach'] for d in historical_data if d['reach'] > 0]
        engagements = [d['engagements'] for d in historical_data if d['engagements'] > 0]
        ctrs = [d['ctr'] for d in historical_data if d['ctr'] > 0]
        engagement_rates = [d['engagement_rate'] for d in historical_data if d['engagement_rate'] > 0]
        
        return {
            'avg_impressions': statistics.mean(impressions) if impressions else 1000,
            'avg_reach': statistics.mean(reach) if reach else 800,
            'avg_engagements': statistics.mean(engagements) if engagements else 50,
            'avg_ctr': statistics.mean(ctrs) if ctrs else 0.02,
            'avg_engagement_rate': statistics.mean(engagement_rates) if engagement_rates else 0.05
        }
    
    async def _generate_ai_prediction(self, content: str, features: ContentFeatures,
                                    historical_data: List[Dict[str, Any]],
                                    baseline_metrics: Dict[str, float]) -> Dict[str, Any]:
        """Use AI to generate performance predictions"""
        
        # Prepare context for AI
        historical_summary = {
            'total_posts': len(historical_data),
            'avg_impressions': baseline_metrics['avg_impressions'],
            'avg_engagement_rate': baseline_metrics['avg_engagement_rate'],
            'best_performing_length': statistics.mode([d['content_length'] for d in historical_data[-20:]]) if historical_data else 100,
            'best_hashtag_count': statistics.mode([d['hashtag_count'] for d in historical_data[-20:]]) if historical_data else 3
        }
        
        prompt = f"""
        As a social media performance analyst, predict the performance of this content:

        CONTENT: "{content}"
        PLATFORM: {features.platform}
        CONTENT LENGTH: {features.content_length} characters
        HASHTAGS: {features.hashtag_count}
        MENTIONS: {features.mention_count}
        HAS MEDIA: {features.has_media}
        TIME OF DAY: {features.time_of_day}:00
        DAY OF WEEK: {features.day_of_week}
        SENTIMENT: {features.sentiment_score:.2f}
        TOPICS: {', '.join(features.topic_categories)}

        HISTORICAL PERFORMANCE:
        - Average impressions: {historical_summary['avg_impressions']:.0f}
        - Average engagement rate: {historical_summary['avg_engagement_rate']:.3f}
        - Total historical posts: {historical_summary['total_posts']}
        - Best performing content length: {historical_summary['best_performing_length']} characters
        - Best hashtag count: {historical_summary['best_hashtag_count']}

        Provide predictions in this exact JSON format:
        {{
            "predicted_impressions": <number>,
            "predicted_reach": <number>,
            "predicted_engagements": <number>,
            "predicted_ctr": <decimal>,
            "predicted_engagement_rate": <decimal>,
            "confidence_score": <decimal 0.0-1.0>,
            "key_factors": ["factor1", "factor2", "factor3"],
            "recommendations": ["recommendation1", "recommendation2"]
        }}

        Base predictions on:
        1. Content length vs historical performance
        2. Timing (day/time) patterns
        3. Hashtag usage patterns
        4. Sentiment and topic analysis
        5. Platform-specific characteristics
        """
        
        request = GenerationRequest(
            task="performance_prediction",
            prompt=prompt,
            system="You are an expert social media performance analyst. Provide accurate, data-driven predictions based on historical performance patterns and content characteristics.",
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
            
            prediction_data = json.loads(response_text)
            return prediction_data
        except (json.JSONDecodeError, KeyError) as e:
            # Fallback to baseline predictions if AI fails
            return {
                "predicted_impressions": int(baseline_metrics['avg_impressions']),
                "predicted_reach": int(baseline_metrics['avg_reach']),
                "predicted_engagements": int(baseline_metrics['avg_engagements']),
                "predicted_ctr": baseline_metrics['avg_ctr'],
                "predicted_engagement_rate": baseline_metrics['avg_engagement_rate'],
                "confidence_score": 0.3,
                "key_factors": ["Limited historical data", "Baseline prediction"],
                "recommendations": ["Gather more performance data", "Test different content formats"]
            }
    
    async def predict_performance(self, content: str, platform: str, org_id: int,
                                scheduled_at: Optional[datetime] = None,
                                brand_guide_id: Optional[int] = None) -> PerformancePrediction:
        """
        Predict content performance using AI and historical data
        
        Args:
            content: The content text to predict performance for
            platform: Target platform (facebook, instagram, twitter, linkedin)
            org_id: Organization ID for historical data
            scheduled_at: When the content will be posted (for timing analysis)
            brand_guide_id: Brand guide ID for voice matching
            
        Returns:
            PerformancePrediction with predicted metrics and recommendations
        """
        with self.tracer.start_as_current_span("ai.performance_prediction") as span:
            span.set_attributes({
                "ai.platform": platform,
                "ai.org_id": org_id,
                "ai.content_length": len(content)
            })
            
            # Extract content features
            features = self._extract_content_features(content, platform, scheduled_at, brand_guide_id)
            
            # Get historical performance data
            historical_data = self._get_historical_performance(org_id, platform)
            baseline_metrics = self._calculate_baseline_metrics(historical_data)
            
            # Generate AI prediction
            ai_prediction = await self._generate_ai_prediction(
                content, features, historical_data, baseline_metrics
            )
            
            # Create prediction result
            prediction = PerformancePrediction(
                predicted_impressions=int(ai_prediction['predicted_impressions']),
                predicted_reach=int(ai_prediction['predicted_reach']),
                predicted_engagements=int(ai_prediction['predicted_engagements']),
                predicted_ctr=float(ai_prediction['predicted_ctr']),
                predicted_engagement_rate=float(ai_prediction['predicted_engagement_rate']),
                confidence_score=float(ai_prediction['confidence_score']),
                factors={
                    'content_length': features.content_length,
                    'hashtag_count': features.hashtag_count,
                    'time_of_day': features.time_of_day,
                    'day_of_week': features.day_of_week,
                    'sentiment_score': features.sentiment_score,
                    'topic_categories': features.topic_categories,
                    'historical_posts_count': len(historical_data),
                    'baseline_impressions': baseline_metrics['avg_impressions']
                },
                recommendations=ai_prediction['recommendations']
            )
            
            span.set_attributes({
                "ai.predicted_impressions": prediction.predicted_impressions,
                "ai.confidence_score": prediction.confidence_score,
                "ai.historical_posts": len(historical_data)
            })
            
            return prediction
    
    async def batch_predict_performance(self, content_items: List[Tuple[str, str, int]],
                                      scheduled_times: Optional[List[datetime]] = None) -> List[PerformancePrediction]:
        """
        Predict performance for multiple content items
        
        Args:
            content_items: List of (content, platform, org_id) tuples
            scheduled_times: Optional list of scheduled times for each item
            
        Returns:
            List of PerformancePrediction objects
        """
        predictions = []
        
        for i, (content, platform, org_id) in enumerate(content_items):
            scheduled_at = scheduled_times[i] if scheduled_times and i < len(scheduled_times) else None
            prediction = await self.predict_performance(content, platform, org_id, scheduled_at)
            predictions.append(prediction)
        
        return predictions
    
    def get_performance_insights(self, org_id: int, platform: str, 
                               days_back: int = 30) -> Dict[str, Any]:
        """
        Get performance insights and patterns for an organization
        
        Returns:
            Dictionary with performance insights and recommendations
        """
        historical_data = self._get_historical_performance(org_id, platform, days_back)
        
        if not historical_data:
            return {
                'insights': ['No historical data available'],
                'recommendations': ['Start posting content to build performance history'],
                'best_times': [],
                'content_patterns': {}
            }
        
        # Analyze timing patterns
        time_performance = {}
        for data in historical_data:
            hour = data['metric_date'].hour
            if hour not in time_performance:
                time_performance[hour] = []
            time_performance[hour].append(data['engagement_rate'])
        
        best_times = []
        for hour, rates in time_performance.items():
            avg_rate = statistics.mean(rates)
            best_times.append({'hour': hour, 'avg_engagement_rate': avg_rate})
        
        best_times.sort(key=lambda x: x['avg_engagement_rate'], reverse=True)
        
        # Analyze content patterns
        content_patterns = {
            'best_length_range': self._get_optimal_length_range(historical_data),
            'best_hashtag_count': self._get_optimal_hashtag_count(historical_data),
            'top_performing_topics': self._get_top_topics(historical_data)
        }
        
        return {
            'insights': [
                f"Average engagement rate: {statistics.mean([d['engagement_rate'] for d in historical_data]):.3f}",
                f"Best posting time: {best_times[0]['hour']}:00 ({best_times[0]['avg_engagement_rate']:.3f} engagement rate)",
                f"Total posts analyzed: {len(historical_data)}"
            ],
            'recommendations': [
                f"Post around {best_times[0]['hour']}:00 for best engagement",
                f"Optimal content length: {content_patterns['best_length_range']} characters",
                f"Use {content_patterns['best_hashtag_count']} hashtags for best performance"
            ],
            'best_times': best_times[:5],
            'content_patterns': content_patterns
        }
    
    def _get_optimal_length_range(self, historical_data: List[Dict[str, Any]]) -> str:
        """Get optimal content length range based on historical data"""
        lengths = [d['content_length'] for d in historical_data]
        if not lengths:
            return "100-200"
        
        # Find length range with best average engagement
        length_ranges = {
            'short (0-100)': [d for d in historical_data if d['content_length'] <= 100],
            'medium (101-200)': [d for d in historical_data if 101 <= d['content_length'] <= 200],
            'long (201-300)': [d for d in historical_data if 201 <= d['content_length'] <= 300],
            'very long (300+)': [d for d in historical_data if d['content_length'] > 300]
        }
        
        best_range = 'medium (101-200)'
        best_avg = 0
        
        for range_name, data in length_ranges.items():
            if data:
                avg_engagement = statistics.mean([d['engagement_rate'] for d in data])
                if avg_engagement > best_avg:
                    best_avg = avg_engagement
                    best_range = range_name
        
        return best_range
    
    def _get_optimal_hashtag_count(self, historical_data: List[Dict[str, Any]]) -> int:
        """Get optimal hashtag count based on historical data"""
        hashtag_performance = {}
        for data in historical_data:
            count = data['hashtag_count']
            if count not in hashtag_performance:
                hashtag_performance[count] = []
            hashtag_performance[count].append(data['engagement_rate'])
        
        best_count = 3  # Default
        best_avg = 0
        
        for count, rates in hashtag_performance.items():
            avg_rate = statistics.mean(rates)
            if avg_rate > best_avg:
                best_avg = avg_rate
                best_count = count
        
        return best_count
    
    def _get_top_topics(self, historical_data: List[Dict[str, Any]]) -> List[str]:
        """Get top performing topic categories (simplified)"""
        # This would need to be enhanced with proper topic analysis
        return ['promotional', 'educational', 'announcement']
