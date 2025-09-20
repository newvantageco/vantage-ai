"""
AI Content Celery Tasks
Handles AI content generation, optimization, and batch processing
"""

from celery import Task
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio

from app.workers.celery_app import celery_app
from app.models.ai_content import AIRequest, AIBatchJob, AIOptimization
from app.services.ai_service import AIService


class AIContentTask(Task):
    """Base task for AI content operations"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure"""
        print(f"AI Content Task {task_id} failed: {exc}")
        # FIXME: Add proper error logging and notification
    
    def on_success(self, retval, task_id, args, kwargs):
        """Handle task success"""
        print(f"AI Content Task {task_id} completed successfully")


@celery_app.task(bind=True, base=AIContentTask, default_retry_delay=300, max_retries=3)
def generate_ai_content_task(
    self,
    prompt: str,
    content_type: str,
    user_id: int,
    organization_id: int,
    brand_guide_id: Optional[int] = None,
    locale: str = "en-US"
) -> Dict[str, Any]:
    """
    Generate AI content using the model router.
    """
    try:
        print(f"Generating AI content for user {user_id}: {prompt[:50]}...")
        
        # Initialize AI service
        ai_service = AIService()
        
        # Generate content
        result = asyncio.run(ai_service.generate_content(
            prompt=prompt,
            content_type=content_type,
            brand_guide_id=brand_guide_id,
            locale=locale
        ))
        
        if result.get("success"):
            # Save to database
            ai_request = AIRequest(
                organization_id=organization_id,
                user_id=user_id,
                prompt=prompt,
                brand_guide_id=brand_guide_id,
                locale=locale,
                generated_text=result.get("text"),
                provider=result.get("provider"),
                model=result.get("model"),
                prompt_tokens=result.get("token_usage", {}).get("prompt_tokens", 0),
                completion_tokens=result.get("token_usage", {}).get("completion_tokens", 0),
                total_tokens=result.get("token_usage", {}).get("total_tokens", 0),
                cost_usd=result.get("cost_usd", 0.0),
                status="completed"
            )
            
            # FIXME: Save to database using proper session management
            # db.add(ai_request)
            # db.commit()
            
            print(f"AI content generated successfully: {result.get('text', '')[:50]}...")
            return {
                "success": True,
                "text": result.get("text"),
                "provider": result.get("provider"),
                "model": result.get("model"),
                "token_usage": result.get("token_usage"),
                "cost_usd": result.get("cost_usd")
            }
        else:
            print(f"AI content generation failed: {result.get('error')}")
            return {
                "success": False,
                "error": result.get("error")
            }
            
    except Exception as e:
        print(f"Error generating AI content: {e}")
        self.retry(exc=e)


@celery_app.task(bind=True, base=AIContentTask, default_retry_delay=600, max_retries=5)
def process_batch_ai_content_task(
    self,
    job_id: str,
    prompts: List[str],
    brand_guide_id: Optional[int],
    locale: str,
    organization_id: int,
    user_id: int
) -> Dict[str, Any]:
    """
    Process batch AI content generation.
    """
    try:
        print(f"Processing batch AI content job {job_id} with {len(prompts)} prompts")
        
        # Initialize AI service
        ai_service = AIService()
        
        results = []
        completed_count = 0
        failed_count = 0
        
        # Process each prompt
        for i, prompt in enumerate(prompts):
            try:
                print(f"Processing prompt {i+1}/{len(prompts)}: {prompt[:50]}...")
                
                # Generate content
                result = asyncio.run(ai_service.generate_content(
                    prompt=prompt,
                    content_type="text",
                    brand_guide_id=brand_guide_id,
                    locale=locale
                ))
                
                if result.get("success"):
                    results.append({
                        "prompt": prompt,
                        "generated_text": result.get("text"),
                        "provider": result.get("provider"),
                        "model": result.get("model"),
                        "token_usage": result.get("token_usage"),
                        "cost_usd": result.get("cost_usd"),
                        "status": "completed"
                    })
                    completed_count += 1
                else:
                    results.append({
                        "prompt": prompt,
                        "error": result.get("error"),
                        "status": "failed"
                    })
                    failed_count += 1
                
                # Update progress
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i + 1,
                        "total": len(prompts),
                        "completed": completed_count,
                        "failed": failed_count
                    }
                )
                
            except Exception as e:
                print(f"Error processing prompt {i+1}: {e}")
                results.append({
                    "prompt": prompt,
                    "error": str(e),
                    "status": "failed"
                })
                failed_count += 1
        
        # Update batch job status
        # FIXME: Update database with results
        # batch_job = db.query(AIBatchJob).filter(AIBatchJob.job_id == job_id).first()
        # if batch_job:
        #     batch_job.status = "completed"
        #     batch_job.completed_prompts = completed_count
        #     batch_job.failed_prompts = failed_count
        #     batch_job.results = results
        #     batch_job.completed_at = datetime.utcnow()
        #     db.commit()
        
        print(f"Batch AI content job {job_id} completed: {completed_count} successful, {failed_count} failed")
        
        return {
            "success": True,
            "job_id": job_id,
            "total_prompts": len(prompts),
            "completed": completed_count,
            "failed": failed_count,
            "results": results
        }
        
    except Exception as e:
        print(f"Error processing batch AI content: {e}")
        self.retry(exc=e)


@celery_app.task(bind=True, base=AIContentTask, default_retry_delay=300, max_retries=3)
def optimize_content_task(
    self,
    platform: str,
    draft_content: str,
    user_id: int,
    organization_id: int,
    brand_guide_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Optimize content for a specific platform.
    """
    try:
        print(f"Optimizing content for {platform}: {draft_content[:50]}...")
        
        # Initialize AI service
        ai_service = AIService()
        
        # Optimize content
        result = asyncio.run(ai_service.optimize_content(
            platform=platform,
            draft_content=draft_content,
            brand_guide_id=brand_guide_id
        ))
        
        if result.get("success"):
            # Save to database
            optimization = AIOptimization(
                organization_id=organization_id,
                user_id=user_id,
                platform=platform,
                draft_content=draft_content,
                brand_guide_id=brand_guide_id,
                optimized_text=result.get("optimized_text"),
                constraints_applied=result.get("constraints_applied"),
                character_count=result.get("character_count"),
                hashtag_count=result.get("hashtag_count"),
                status="completed"
            )
            
            # FIXME: Save to database using proper session management
            # db.add(optimization)
            # db.commit()
            
            print(f"Content optimized successfully for {platform}")
            return {
                "success": True,
                "optimized_text": result.get("optimized_text"),
                "constraints_applied": result.get("constraints_applied"),
                "character_count": result.get("character_count"),
                "hashtag_count": result.get("hashtag_count")
            }
        else:
            print(f"Content optimization failed: {result.get('error')}")
            return {
                "success": False,
                "error": result.get("error")
            }
            
    except Exception as e:
        print(f"Error optimizing content: {e}")
        self.retry(exc=e)


@celery_app.task(bind=True, base=AIContentTask, default_retry_delay=300, max_retries=3)
def generate_content_variations_task(
    self,
    base_content: str,
    variations_count: int,
    user_id: int,
    organization_id: int,
    brand_guide_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate multiple variations of content.
    """
    try:
        print(f"Generating {variations_count} variations of content: {base_content[:50]}...")
        
        # Initialize AI service
        ai_service = AIService()
        
        variations = []
        
        for i in range(variations_count):
            try:
                # Generate variation
                result = asyncio.run(ai_service.generate_content_variation(
                    base_content=base_content,
                    variation_type=f"variation_{i+1}",
                    brand_guide_id=brand_guide_id
                ))
                
                if result.get("success"):
                    variations.append({
                        "variation": i + 1,
                        "content": result.get("text"),
                        "provider": result.get("provider"),
                        "model": result.get("model"),
                        "status": "completed"
                    })
                else:
                    variations.append({
                        "variation": i + 1,
                        "error": result.get("error"),
                        "status": "failed"
                    })
                
                # Update progress
                self.update_state(
                    state="PROGRESS",
                    meta={
                        "current": i + 1,
                        "total": variations_count,
                        "completed": len([v for v in variations if v.get("status") == "completed"])
                    }
                )
                
            except Exception as e:
                print(f"Error generating variation {i+1}: {e}")
                variations.append({
                    "variation": i + 1,
                    "error": str(e),
                    "status": "failed"
                })
        
        print(f"Generated {len(variations)} content variations")
        
        return {
            "success": True,
            "variations": variations,
            "total_variations": len(variations),
            "completed": len([v for v in variations if v.get("status") == "completed"])
        }
        
    except Exception as e:
        print(f"Error generating content variations: {e}")
        self.retry(exc=e)


@celery_app.task(bind=True, base=AIContentTask, default_retry_delay=300, max_retries=3)
def analyze_content_sentiment_task(
    self,
    content: str,
    user_id: int,
    organization_id: int
) -> Dict[str, Any]:
    """
    Analyze content sentiment and tone.
    """
    try:
        print(f"Analyzing content sentiment: {content[:50]}...")
        
        # Initialize AI service
        ai_service = AIService()
        
        # Analyze sentiment
        result = asyncio.run(ai_service.analyze_sentiment(content))
        
        if result.get("success"):
            print(f"Content sentiment analyzed: {result.get('sentiment')}")
            return {
                "success": True,
                "sentiment": result.get("sentiment"),
                "confidence": result.get("confidence"),
                "tone": result.get("tone"),
                "emotions": result.get("emotions"),
                "recommendations": result.get("recommendations")
            }
        else:
            print(f"Content sentiment analysis failed: {result.get('error')}")
            return {
                "success": False,
                "error": result.get("error")
            }
            
    except Exception as e:
        print(f"Error analyzing content sentiment: {e}")
        self.retry(exc=e)


@celery_app.task(bind=True, base=AIContentTask, default_retry_delay=300, max_retries=3)
def generate_hashtags_task(
    self,
    content: str,
    platform: str,
    user_id: int,
    organization_id: int,
    brand_guide_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Generate relevant hashtags for content.
    """
    try:
        print(f"Generating hashtags for {platform}: {content[:50]}...")
        
        # Initialize AI service
        ai_service = AIService()
        
        # Generate hashtags
        result = asyncio.run(ai_service.generate_hashtags(
            content=content,
            platform=platform,
            brand_guide_id=brand_guide_id
        ))
        
        if result.get("success"):
            print(f"Generated {len(result.get('hashtags', []))} hashtags")
            return {
                "success": True,
                "hashtags": result.get("hashtags"),
                "platform": platform,
                "count": len(result.get("hashtags", []))
            }
        else:
            print(f"Hashtag generation failed: {result.get('error')}")
            return {
                "success": False,
                "error": result.get("error")
            }
            
    except Exception as e:
        print(f"Error generating hashtags: {e}")
        self.retry(exc=e)
