"""
Translation worker for processing translation jobs.
"""

import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import aiohttp

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.translations import Translation, TranslationJob, TranslationConfig
from app.models.content import ContentItem

logger = logging.getLogger(__name__)


async def process_translation_job(job_id: str):
    """Process a translation job."""
    db = next(get_db())
    
    try:
        # Get the translation job
        job = db.query(TranslationJob).filter(TranslationJob.id == job_id).first()
        if not job:
            logger.error(f"Translation job {job_id} not found")
            return
        
        # Update job status
        job.status = "running"
        job.started_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Starting translation job {job_id}")
        
        # Get content IDs and target locales
        content_ids = job.get_content_ids()
        target_locales = job.get_target_locales()
        
        # Process each content item
        for content_id in content_ids:
            try:
                # Get content item
                content = db.query(ContentItem).filter(
                    ContentItem.id == content_id,
                    ContentItem.org_id == job.org_id
                ).first()
                
                if not content:
                    logger.warning(f"Content item {content_id} not found")
                    job.add_failed_content_id(content_id)
                    job.failed_items += 1
                    continue
                
                # Extract content to translate
                content_to_translate = {
                    "title": content.title or "",
                    "caption": content.caption or "",
                    "alt_text": content.alt_text or "",
                    "first_comment": content.first_comment or "",
                    "hashtags": content.hashtags or ""
                }
                
                # Translate to each target locale
                for target_locale in target_locales:
                    try:
                        # Check if translation already exists
                        existing_translation = db.query(Translation).filter(
                            Translation.content_id == content_id,
                            Translation.target_locale == target_locale
                        ).first()
                        
                        if existing_translation:
                            logger.info(f"Translation already exists for {content_id} -> {target_locale}")
                            job.completed_items += 1
                            continue
                        
                        # Translate content
                        translated_content = await translate_content(
                            content_to_translate,
                            "en",  # Assume source is English
                            target_locale,
                            job.translation_provider,
                            job.translation_model
                        )
                        
                        if translated_content:
                            # Create translation record
                            translation = Translation(
                                id=f"trans_{hash(f'{content_id}_{target_locale}_{datetime.utcnow().timestamp()}')}",
                                content_id=content_id,
                                org_id=job.org_id,
                                user_id=job.user_id,
                                source_locale="en",
                                target_locale=target_locale,
                                translated_content=json.dumps(translated_content),
                                translation_provider=job.translation_provider,
                                translation_model=job.translation_model,
                                confidence_score=translated_content.get("confidence_score"),
                                status="completed",
                                is_auto_translated=True
                            )
                            
                            db.add(translation)
                            job.completed_items += 1
                            
                            logger.info(f"Translated {content_id} to {target_locale}")
                        else:
                            logger.error(f"Failed to translate {content_id} to {target_locale}")
                            job.add_failed_content_id(content_id)
                            job.failed_items += 1
                    
                    except Exception as e:
                        logger.error(f"Error translating {content_id} to {target_locale}: {e}")
                        job.add_failed_content_id(content_id)
                        job.failed_items += 1
                
                # Update progress
                total_items = len(content_ids) * len(target_locales)
                job.progress_percent = int((job.completed_items + job.failed_items) / total_items * 100)
                db.commit()
                
            except Exception as e:
                logger.error(f"Error processing content {content_id}: {e}")
                job.add_failed_content_id(content_id)
                job.failed_items += 1
        
        # Mark job as completed
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.progress_percent = 100
        
        if job.failed_items > 0:
            job.error_message = f"Failed to translate {job.failed_items} items"
        
        db.commit()
        
        logger.info(f"Translation job {job_id} completed. Success: {job.completed_items}, Failed: {job.failed_items}")
        
    except Exception as e:
        logger.error(f"Error processing translation job {job_id}: {e}")
        
        # Mark job as failed
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()
        
    finally:
        db.close()


async def translate_content(
    content: Dict[str, str],
    source_locale: str,
    target_locale: str,
    provider: str,
    model: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Translate content using the specified provider."""
    try:
        if provider == "google":
            return await translate_with_google(content, source_locale, target_locale)
        elif provider == "azure":
            return await translate_with_azure(content, source_locale, target_locale)
        elif provider == "openai":
            return await translate_with_openai(content, source_locale, target_locale, model)
        elif provider == "manual":
            return await translate_manually(content, source_locale, target_locale)
        else:
            logger.error(f"Unknown translation provider: {provider}")
            return None
    
    except Exception as e:
        logger.error(f"Error translating content: {e}")
        return None


async def translate_with_google(content: Dict[str, str], source_locale: str, target_locale: str) -> Optional[Dict[str, Any]]:
    """Translate content using Google Translate API."""
    try:
        # This would integrate with Google Cloud Translation API
        # For now, return mock translation
        translated = {}
        for field, text in content.items():
            if text:
                # Mock translation - in real implementation, call Google API
                translated[field] = f"[{target_locale}] {text}"
            else:
                translated[field] = ""
        
        translated["confidence_score"] = 0.95
        return translated
    
    except Exception as e:
        logger.error(f"Google translation error: {e}")
        return None


async def translate_with_azure(content: Dict[str, str], source_locale: str, target_locale: str) -> Optional[Dict[str, Any]]:
    """Translate content using Azure Translator API."""
    try:
        # This would integrate with Azure Cognitive Services Translator
        # For now, return mock translation
        translated = {}
        for field, text in content.items():
            if text:
                # Mock translation - in real implementation, call Azure API
                translated[field] = f"[{target_locale}] {text}"
            else:
                translated[field] = ""
        
        translated["confidence_score"] = 0.90
        return translated
    
    except Exception as e:
        logger.error(f"Azure translation error: {e}")
        return None


async def translate_with_openai(content: Dict[str, str], source_locale: str, target_locale: str, model: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Translate content using OpenAI API."""
    try:
        # This would integrate with OpenAI API
        # For now, return mock translation
        translated = {}
        for field, text in content.items():
            if text:
                # Mock translation - in real implementation, call OpenAI API
                translated[field] = f"[{target_locale}] {text}"
            else:
                translated[field] = ""
        
        translated["confidence_score"] = 0.85
        return translated
    
    except Exception as e:
        logger.error(f"OpenAI translation error: {e}")
        return None


async def translate_manually(content: Dict[str, str], source_locale: str, target_locale: str) -> Optional[Dict[str, Any]]:
    """Create manual translation placeholder."""
    try:
        # For manual translation, create a placeholder that can be filled by humans
        translated = {}
        for field, text in content.items():
            if text:
                translated[field] = f"[MANUAL TRANSLATION NEEDED] {text}"
            else:
                translated[field] = ""
        
        translated["confidence_score"] = 0.0  # Manual translation needs review
        return translated
    
    except Exception as e:
        logger.error(f"Manual translation error: {e}")
        return None


async def detect_language(text: str) -> str:
    """Detect the language of text."""
    try:
        # This would integrate with a language detection service
        # For now, return English as default
        return "en"
    
    except Exception as e:
        logger.error(f"Language detection error: {e}")
        return "en"


async def get_translation_quality_score(original: str, translated: str) -> float:
    """Get quality score for translation."""
    try:
        # This would use a translation quality assessment model
        # For now, return a mock score
        if not original or not translated:
            return 0.0
        
        # Simple heuristic based on length similarity
        length_ratio = len(translated) / len(original) if original else 0
        if 0.5 <= length_ratio <= 2.0:  # Reasonable length ratio
            return 0.8
        else:
            return 0.6
    
    except Exception as e:
        logger.error(f"Quality assessment error: {e}")
        return 0.5


if __name__ == "__main__":
    # This can be run as a standalone worker
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python translation_worker.py <job_id>")
        sys.exit(1)
    
    job_id = sys.argv[1]
    asyncio.run(process_translation_job(job_id))
