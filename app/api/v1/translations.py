from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import secrets
import json

from app.db.session import get_db
from app.models.translations import (
    Translation, TranslationJob, TranslationConfig, 
    SUPPORTED_LOCALES, TRANSLATION_PROVIDERS
)
from app.models.entities import Organization
from app.core.security import get_current_user
from app.workers.translation_worker import process_translation_job
from pydantic import BaseModel

router = APIRouter()


class TranslationRequest(BaseModel):
    content_id: str
    target_locales: List[str]
    translation_provider: Optional[str] = None
    translation_model: Optional[str] = None


class TranslationResponse(BaseModel):
    id: str
    content_id: str
    source_locale: str
    target_locale: str
    translated_content: Dict[str, Any]
    translation_provider: str
    translation_model: Optional[str]
    confidence_score: Optional[float]
    status: str
    is_auto_translated: bool
    is_reviewed: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class TranslationJobResponse(BaseModel):
    id: str
    content_ids: List[str]
    target_locales: List[str]
    translation_provider: str
    translation_model: Optional[str]
    status: str
    progress_percent: int
    total_items: int
    completed_items: int
    failed_items: int
    error_message: Optional[str]
    created_at: str
    started_at: Optional[str]
    completed_at: Optional[str]

    class Config:
        from_attributes = True


class TranslationConfigResponse(BaseModel):
    id: str
    default_provider: str
    default_model: Optional[str]
    supported_locales: List[str]
    default_source_locale: str
    min_confidence_score: float
    auto_review_threshold: float
    auto_translate_enabled: bool
    human_review_required: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.post("/translations/translate", response_model=TranslationJobResponse)
async def create_translation_job(
    translation_data: TranslationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a translation job for content items."""
    
    # Validate target locales
    invalid_locales = [locale for locale in translation_data.target_locales if locale not in SUPPORTED_LOCALES]
    if invalid_locales:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid locales: {invalid_locales}. Supported locales: {list(SUPPORTED_LOCALES.keys())}"
        )
    
    # Get or create translation config
    config = db.query(TranslationConfig).filter(
        TranslationConfig.org_id == current_user["org_id"]
    ).first()
    
    if not config:
        # Create default config
        config = TranslationConfig(
            id=secrets.token_urlsafe(16),
            org_id=current_user["org_id"],
            supported_locales=json.dumps(translation_data.target_locales)
        )
        db.add(config)
        db.commit()
    
    # Use provided provider or default
    provider = translation_data.translation_provider or config.default_provider
    model = translation_data.translation_model or config.default_model
    
    # Validate provider
    if provider not in TRANSLATION_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider: {provider}. Available providers: {list(TRANSLATION_PROVIDERS.keys())}"
        )
    
    # Create translation job
    job = TranslationJob(
        id=secrets.token_urlsafe(16),
        org_id=current_user["org_id"],
        user_id=current_user["user_id"],
        content_ids=json.dumps([translation_data.content_id]),
        target_locales=json.dumps(translation_data.target_locales),
        translation_provider=provider,
        translation_model=model,
        total_items=len(translation_data.target_locales)
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Start background task
    background_tasks.add_task(process_translation_job, job.id)
    
    return TranslationJobResponse(
        id=job.id,
        content_ids=job.get_content_ids(),
        target_locales=job.get_target_locales(),
        translation_provider=job.translation_provider,
        translation_model=job.translation_model,
        status=job.status,
        progress_percent=job.progress_percent,
        total_items=job.total_items,
        completed_items=job.completed_items,
        failed_items=job.failed_items,
        error_message=job.error_message,
        created_at=job.created_at.isoformat(),
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None
    )


@router.get("/translations/{content_id}", response_model=List[TranslationResponse])
async def get_translations(
    content_id: str,
    target_locale: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get translations for a content item."""
    query = db.query(Translation).filter(
        Translation.content_id == content_id,
        Translation.org_id == current_user["org_id"]
    )
    
    if target_locale:
        query = query.filter(Translation.target_locale == target_locale)
    
    translations = query.all()
    
    return [
        TranslationResponse(
            id=translation.id,
            content_id=translation.content_id,
            source_locale=translation.source_locale,
            target_locale=translation.target_locale,
            translated_content=translation.get_translated_content(),
            translation_provider=translation.translation_provider,
            translation_model=translation.translation_model,
            confidence_score=translation.confidence_score,
            status=translation.status,
            is_auto_translated=translation.is_auto_translated,
            is_reviewed=translation.is_reviewed,
            created_at=translation.created_at.isoformat(),
            updated_at=translation.updated_at.isoformat()
        )
        for translation in translations
    ]


@router.get("/translations/jobs/{job_id}", response_model=TranslationJobResponse)
async def get_translation_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a translation job status."""
    job = db.query(TranslationJob).filter(
        TranslationJob.id == job_id,
        TranslationJob.org_id == current_user["org_id"]
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation job not found"
        )
    
    return TranslationJobResponse(
        id=job.id,
        content_ids=job.get_content_ids(),
        target_locales=job.get_target_locales(),
        translation_provider=job.translation_provider,
        translation_model=job.translation_model,
        status=job.status,
        progress_percent=job.progress_percent,
        total_items=job.total_items,
        completed_items=job.completed_items,
        failed_items=job.failed_items,
        error_message=job.error_message,
        created_at=job.created_at.isoformat(),
        started_at=job.started_at.isoformat() if job.started_at else None,
        completed_at=job.completed_at.isoformat() if job.completed_at else None
    )


@router.put("/translations/{translation_id}/review")
async def review_translation(
    translation_id: str,
    review_notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark a translation as reviewed."""
    translation = db.query(Translation).filter(
        Translation.id == translation_id,
        Translation.org_id == current_user["org_id"]
    ).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    translation.is_reviewed = True
    translation.reviewed_by = current_user["user_id"]
    translation.review_notes = review_notes
    translation.reviewed_at = datetime.utcnow()
    translation.status = "reviewed"
    
    db.commit()
    
    return {"message": "Translation marked as reviewed"}


@router.put("/translations/{translation_id}/content")
async def update_translation_content(
    translation_id: str,
    field: str,
    value: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a specific field in a translation."""
    translation = db.query(Translation).filter(
        Translation.id == translation_id,
        Translation.org_id == current_user["org_id"]
    ).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    translation.update_field(field, value)
    translation.is_auto_translated = False  # Mark as manually edited
    db.commit()
    
    return {"message": "Translation content updated successfully"}


@router.get("/translations/config", response_model=TranslationConfigResponse)
async def get_translation_config(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get translation configuration for the organization."""
    config = db.query(TranslationConfig).filter(
        TranslationConfig.org_id == current_user["org_id"]
    ).first()
    
    if not config:
        # Create default config
        config = TranslationConfig(
            id=secrets.token_urlsafe(16),
            org_id=current_user["org_id"],
            supported_locales=json.dumps(["en", "es", "fr", "de"])
        )
        db.add(config)
        db.commit()
    
    return TranslationConfigResponse(
        id=config.id,
        default_provider=config.default_provider,
        default_model=config.default_model,
        supported_locales=config.get_supported_locales(),
        default_source_locale=config.default_source_locale,
        min_confidence_score=config.min_confidence_score,
        auto_review_threshold=config.auto_review_threshold,
        auto_translate_enabled=config.auto_translate_enabled,
        human_review_required=config.human_review_required,
        created_at=config.created_at.isoformat(),
        updated_at=config.updated_at.isoformat()
    )


@router.put("/translations/config", response_model=TranslationConfigResponse)
async def update_translation_config(
    config_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update translation configuration."""
    config = db.query(TranslationConfig).filter(
        TranslationConfig.org_id == current_user["org_id"]
    ).first()
    
    if not config:
        config = TranslationConfig(
            id=secrets.token_urlsafe(16),
            org_id=current_user["org_id"]
        )
        db.add(config)
    
    # Update fields
    if "default_provider" in config_data:
        config.default_provider = config_data["default_provider"]
    
    if "default_model" in config_data:
        config.default_model = config_data["default_model"]
    
    if "supported_locales" in config_data:
        config.set_supported_locales(config_data["supported_locales"])
    
    if "default_source_locale" in config_data:
        config.default_source_locale = config_data["default_source_locale"]
    
    if "min_confidence_score" in config_data:
        config.min_confidence_score = config_data["min_confidence_score"]
    
    if "auto_review_threshold" in config_data:
        config.auto_review_threshold = config_data["auto_review_threshold"]
    
    if "auto_translate_enabled" in config_data:
        config.auto_translate_enabled = config_data["auto_translate_enabled"]
    
    if "human_review_required" in config_data:
        config.human_review_required = config_data["human_review_required"]
    
    db.commit()
    db.refresh(config)
    
    return TranslationConfigResponse(
        id=config.id,
        default_provider=config.default_provider,
        default_model=config.default_model,
        supported_locales=config.get_supported_locales(),
        default_source_locale=config.default_source_locale,
        min_confidence_score=config.min_confidence_score,
        auto_review_threshold=config.auto_review_threshold,
        auto_translate_enabled=config.auto_translate_enabled,
        human_review_required=config.human_review_required,
        created_at=config.created_at.isoformat(),
        updated_at=config.updated_at.isoformat()
    )


@router.get("/translations/locales")
async def get_supported_locales():
    """Get all supported locales."""
    return {
        "locales": SUPPORTED_LOCALES,
        "locale_codes": list(SUPPORTED_LOCALES.keys())
    }


@router.get("/translations/providers")
async def get_translation_providers():
    """Get all translation providers."""
    return {
        "providers": TRANSLATION_PROVIDERS,
        "provider_names": list(TRANSLATION_PROVIDERS.keys())
    }


@router.delete("/translations/{translation_id}")
async def delete_translation(
    translation_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a translation."""
    translation = db.query(Translation).filter(
        Translation.id == translation_id,
        Translation.org_id == current_user["org_id"]
    ).first()
    
    if not translation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Translation not found"
        )
    
    db.delete(translation)
    db.commit()
    
    return {"message": "Translation deleted successfully"}


@router.get("/translations/stats")
async def get_translation_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get translation statistics for the organization."""
    from sqlalchemy import func
    
    # Get total translations
    total_translations = db.query(func.count(Translation.id)).filter(
        Translation.org_id == current_user["org_id"]
    ).scalar()
    
    # Get translations by status
    status_counts = db.query(
        Translation.status,
        func.count(Translation.id)
    ).filter(
        Translation.org_id == current_user["org_id"]
    ).group_by(Translation.status).all()
    
    # Get translations by provider
    provider_counts = db.query(
        Translation.translation_provider,
        func.count(Translation.id)
    ).filter(
        Translation.org_id == current_user["org_id"]
    ).group_by(Translation.translation_provider).all()
    
    # Get translations by locale
    locale_counts = db.query(
        Translation.target_locale,
        func.count(Translation.id)
    ).filter(
        Translation.org_id == current_user["org_id"]
    ).group_by(Translation.target_locale).all()
    
    return {
        "total_translations": total_translations,
        "by_status": dict(status_counts),
        "by_provider": dict(provider_counts),
        "by_locale": dict(locale_counts)
    }
