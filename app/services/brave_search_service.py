"""
Brave Search Service for VANTAGE AI
High-level service for integrating Brave Search into VANTAGE AI workflows
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from app.integrations.brave_search import (
    BraveSearchClient,
    SearchType,
    SafeSearchLevel,
    search_web,
    search_news,
    search_images,
    search_local,
    get_ai_summary
)

logger = logging.getLogger(__name__)


class BraveSearchService:
    """High-level service for Brave Search integration in VANTAGE AI"""
    
    def __init__(self):
        self.client = None
    
    async def __aenter__(self):
        self.client = BraveSearchClient()
        await self.client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)
    
    async def research_content_topic(
        self, 
        topic: str, 
        include_news: bool = True,
        include_images: bool = False,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Research a content topic using multiple search types
        Perfect for content planning and research workflows
        """
        try:
            results = {
                "topic": topic,
                "web_results": [],
                "news_results": [],
                "image_results": [],
                "ai_summary": None,
                "research_timestamp": datetime.utcnow().isoformat()
            }
            
            # Web search with AI summary
            web_response = await search_web(
                query=topic,
                count=max_results,
                summary=True
            )
            
            results["web_results"] = [
                {
                    "title": result.title,
                    "url": result.url,
                    "description": result.description,
                    "published_date": result.published_date
                }
                for result in web_response.results
            ]
            
            if web_response.summary:
                results["ai_summary"] = web_response.summary
            
            # News search for recent developments
            if include_news:
                news_response = await search_news(
                    query=topic,
                    count=5,
                    freshness="pd"  # past day
                )
                
                results["news_results"] = [
                    {
                        "title": result.title,
                        "url": result.url,
                        "description": result.description,
                        "source": result.source,
                        "published_date": result.published_date
                    }
                    for result in news_response.results
                ]
            
            # Image search for visual content ideas
            if include_images:
                image_response = await search_images(
                    query=topic,
                    count=5
                )
                
                results["image_results"] = [
                    {
                        "title": result.title,
                        "url": result.url,
                        "thumbnail": result.thumbnail,
                        "description": result.description
                    }
                    for result in image_response.results
                ]
            
            return results
            
        except Exception as e:
            logger.error(f"Content research failed for topic '{topic}': {e}")
            raise
    
    async def find_competitors(
        self, 
        business_name: str, 
        industry: str,
        location: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find competitors using local and web search
        Useful for competitive analysis workflows
        """
        try:
            results = {
                "business_name": business_name,
                "industry": industry,
                "competitors": [],
                "local_competitors": [],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            # Web search for competitors
            competitor_query = f"{industry} companies competitors {business_name}"
            web_response = await search_web(
                query=competitor_query,
                count=10
            )
            
            results["competitors"] = [
                {
                    "name": result.title,
                    "url": result.url,
                    "description": result.description
                }
                for result in web_response.results
            ]
            
            # Local search if location provided
            if location:
                local_query = f"{industry} {location}"
                local_response = await search_local(
                    query=local_query,
                    location=location,
                    count=10
                )
                
                results["local_competitors"] = [
                    {
                        "name": result.title,
                        "url": result.url,
                        "description": result.description,
                        "location": result.location,
                        "rating": result.rating,
                        "price": result.price
                    }
                    for result in local_response.results
                ]
            
            return results
            
        except Exception as e:
            logger.error(f"Competitor analysis failed for '{business_name}': {e}")
            raise
    
    async def monitor_industry_news(
        self, 
        industry: str,
        keywords: List[str] = None,
        hours_back: int = 24
    ) -> Dict[str, Any]:
        """
        Monitor industry news and trends
        Perfect for automated content suggestions and trend analysis
        """
        try:
            results = {
                "industry": industry,
                "keywords": keywords or [],
                "news_articles": [],
                "trending_topics": [],
                "monitor_timestamp": datetime.utcnow().isoformat()
            }
            
            # Build search query
            if keywords:
                query = f"{industry} {' '.join(keywords)}"
            else:
                query = f"{industry} news trends"
            
            # Search for recent news
            news_response = await search_news(
                query=query,
                count=20,
                freshness="pd"  # past day
            )
            
            results["news_articles"] = [
                {
                    "title": result.title,
                    "url": result.url,
                    "description": result.description,
                    "source": result.source,
                    "published_date": result.published_date
                }
                for result in news_response.results
            ]
            
            # Extract trending topics from news titles
            trending_topics = set()
            for article in results["news_articles"]:
                # Simple keyword extraction (could be enhanced with NLP)
                words = article["title"].lower().split()
                for word in words:
                    if len(word) > 4 and word not in ["news", "industry", "market", "business"]:
                        trending_topics.add(word)
            
            results["trending_topics"] = list(trending_topics)[:10]
            
            return results
            
        except Exception as e:
            logger.error(f"Industry monitoring failed for '{industry}': {e}")
            raise
    
    async def find_content_inspiration(
        self, 
        content_type: str,
        target_audience: str,
        industry: str
    ) -> Dict[str, Any]:
        """
        Find content inspiration using image and web search
        Great for creative content generation workflows
        """
        try:
            results = {
                "content_type": content_type,
                "target_audience": target_audience,
                "industry": industry,
                "inspiration_sources": [],
                "visual_inspiration": [],
                "content_ideas": [],
                "inspiration_timestamp": datetime.utcnow().isoformat()
            }
            
            # Search for content examples
            content_query = f"{content_type} {target_audience} {industry} examples"
            web_response = await search_web(
                query=content_query,
                count=10
            )
            
            results["inspiration_sources"] = [
                {
                    "title": result.title,
                    "url": result.url,
                    "description": result.description
                }
                for result in web_response.results
            ]
            
            # Search for visual inspiration
            visual_query = f"{content_type} {industry} design inspiration"
            image_response = await search_images(
                query=visual_query,
                count=8
            )
            
            results["visual_inspiration"] = [
                {
                    "title": result.title,
                    "url": result.url,
                    "thumbnail": result.thumbnail,
                    "description": result.description
                }
                for result in image_response.results
            ]
            
            # Generate content ideas based on search results
            content_ideas = []
            for source in results["inspiration_sources"][:5]:
                idea = {
                    "title": f"Content idea inspired by: {source['title']}",
                    "description": f"Create {content_type} targeting {target_audience} based on: {source['description'][:100]}...",
                    "source_url": source["url"]
                }
                content_ideas.append(idea)
            
            results["content_ideas"] = content_ideas
            
            return results
            
        except Exception as e:
            logger.error(f"Content inspiration search failed: {e}")
            raise
    
    async def analyze_market_sentiment(
        self, 
        brand_name: str,
        product_name: str = None
    ) -> Dict[str, Any]:
        """
        Analyze market sentiment using news search
        Useful for brand monitoring and reputation management
        """
        try:
            results = {
                "brand_name": brand_name,
                "product_name": product_name,
                "sentiment_analysis": {
                    "positive_mentions": 0,
                    "negative_mentions": 0,
                    "neutral_mentions": 0
                },
                "recent_mentions": [],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
            # Search for brand mentions
            search_query = f"{brand_name}"
            if product_name:
                search_query += f" {product_name}"
            
            news_response = await search_news(
                query=search_query,
                count=20,
                freshness="pw"  # past week
            )
            
            # Simple sentiment analysis (could be enhanced with NLP)
            positive_keywords = ["great", "excellent", "amazing", "love", "best", "outstanding", "innovative"]
            negative_keywords = ["bad", "terrible", "awful", "hate", "worst", "disappointing", "problem"]
            
            for article in news_response.results:
                mention = {
                    "title": article.title,
                    "url": article.url,
                    "description": article.description,
                    "source": article.source,
                    "published_date": article.published_date,
                    "sentiment": "neutral"
                }
                
                # Simple sentiment detection
                text = (article.title + " " + article.description).lower()
                positive_count = sum(1 for word in positive_keywords if word in text)
                negative_count = sum(1 for word in negative_keywords if word in text)
                
                if positive_count > negative_count:
                    mention["sentiment"] = "positive"
                    results["sentiment_analysis"]["positive_mentions"] += 1
                elif negative_count > positive_count:
                    mention["sentiment"] = "negative"
                    results["sentiment_analysis"]["negative_mentions"] += 1
                else:
                    results["sentiment_analysis"]["neutral_mentions"] += 1
                
                results["recent_mentions"].append(mention)
            
            return results
            
        except Exception as e:
            logger.error(f"Market sentiment analysis failed for '{brand_name}': {e}")
            raise


# Convenience functions for easy integration
async def research_topic(topic: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for content research"""
    async with BraveSearchService() as service:
        return await service.research_content_topic(topic, **kwargs)


async def find_competitors_for_business(business_name: str, industry: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for competitor analysis"""
    async with BraveSearchService() as service:
        return await service.find_competitors(business_name, industry, **kwargs)


async def monitor_industry(industry: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for industry monitoring"""
    async with BraveSearchService() as service:
        return await service.monitor_industry_news(industry, **kwargs)


async def get_content_inspiration(content_type: str, target_audience: str, industry: str) -> Dict[str, Any]:
    """Convenience function for content inspiration"""
    async with BraveSearchService() as service:
        return await service.find_content_inspiration(content_type, target_audience, industry)


async def analyze_brand_sentiment(brand_name: str, **kwargs) -> Dict[str, Any]:
    """Convenience function for sentiment analysis"""
    async with BraveSearchService() as service:
        return await service.analyze_market_sentiment(brand_name, **kwargs)
