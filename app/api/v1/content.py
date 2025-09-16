from __future__ import annotations

from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, constr
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.content import BrandGuide, Campaign, ContentItem, ContentStatus
from app.ai.safety import validate_caption, ValidationResult


router = APIRouter(tags=["content"])


class BrandGuideIn(BaseModel):
    org_id: constr(min_length=1, max_length=36)
    voice: Optional[str] = None
    audience: Optional[str] = None
    pillars: Optional[str] = None


class BrandGuideOut(BaseModel):
    id: str
    org_id: str
    voice: Optional[str]
    audience: Optional[str]
    pillars: Optional[str]
class ValidateIn(BaseModel):
    caption: str
    brand_guide_id: Optional[str] = None


class ValidateOut(BaseModel):
    ok: bool
    reasons: list[str]
    fixed_text: str


@router.post("/content/validate", response_model=ValidateOut)
def validate_caption_endpoint(payload: ValidateIn, db: Session = Depends(get_db)):
    guide = db.get(BrandGuide, payload.brand_guide_id) if payload.brand_guide_id else None
    res: ValidationResult = validate_caption(payload.caption, guide)
    return ValidateOut(ok=res.ok, reasons=res.reasons, fixed_text=res.fixed_text)


@router.post("/brand-guide", response_model=BrandGuideOut, status_code=status.HTTP_201_CREATED)
def create_brand_guide(payload: BrandGuideIn, db: Session = Depends(get_db)):
    bg = BrandGuide(
        id=payload.org_id,  # 1:1 mapping by org for simplicity; could be uuid
        org_id=payload.org_id,
        voice=payload.voice,
        audience=payload.audience,
        pillars=payload.pillars,
    )
    db.add(bg)
    try:
        db.commit()
    except Exception:
        db.rollback()
        # On conflict, update existing
        existing: Optional[BrandGuide] = db.get(BrandGuide, payload.org_id)
        if not existing:
            raise HTTPException(status_code=400, detail="Failed to create brand guide")
        existing.voice = payload.voice
        existing.audience = payload.audience
        existing.pillars = payload.pillars
        db.add(existing)
        db.commit()
        db.refresh(existing)
        return BrandGuideOut.model_validate(existing.__dict__, from_attributes=True)
    db.refresh(bg)
    return BrandGuideOut.model_validate(bg.__dict__, from_attributes=True)


class CampaignIn(BaseModel):
    org_id: constr(min_length=1, max_length=36)
    name: constr(min_length=1, max_length=255)
    objective: Optional[str] = None
    start_date: Optional[str] = None  # ISO date
    end_date: Optional[str] = None


class CampaignOut(BaseModel):
    id: str
    org_id: str
    name: str
    objective: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]


@router.get("/campaigns", response_model=List[CampaignOut])
def list_campaigns(org_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(Campaign)
        .filter(Campaign.org_id == org_id)
        .order_by(Campaign.created_at.desc())
        .all()
    )
    return [CampaignOut.model_validate(r.__dict__, from_attributes=True) for r in rows]


@router.post("/campaigns", response_model=CampaignOut, status_code=status.HTTP_201_CREATED)
def create_campaign(payload: CampaignIn, db: Session = Depends(get_db)):
    from uuid import uuid4
    camp = Campaign(
        id=str(uuid4()),
        org_id=payload.org_id,
        name=payload.name,
        objective=payload.objective,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
    db.add(camp)
    db.commit()
    db.refresh(camp)
    return CampaignOut.model_validate(camp.__dict__, from_attributes=True)


class ContentItemIn(BaseModel):
    org_id: constr(min_length=1, max_length=36)
    campaign_id: Optional[str] = None
    title: Optional[str] = None
    caption: Optional[str] = None
    alt_text: Optional[str] = None
    first_comment: Optional[str] = None
    hashtags: Optional[str] = None
    status: ContentStatus = ContentStatus.draft


class ContentItemOut(BaseModel):
    id: str
    org_id: str
    campaign_id: Optional[str]
    title: Optional[str]
    caption: Optional[str]
    alt_text: Optional[str]
    first_comment: Optional[str]
    hashtags: Optional[str]
    status: ContentStatus
    created_at: str

    class Config:
        from_attributes = True


@router.post("/content-items", response_model=ContentItemOut, status_code=status.HTTP_201_CREATED)
def create_content_item(payload: ContentItemIn, db: Session = Depends(get_db)):
    """Create a new content item."""
    from uuid import uuid4
    
    content_item = ContentItem(
        id=str(uuid4()),
        org_id=payload.org_id,
        campaign_id=payload.campaign_id,
        title=payload.title,
        caption=payload.caption,
        alt_text=payload.alt_text,
        first_comment=payload.first_comment,
        hashtags=payload.hashtags,
        status=payload.status,
    )
    
    db.add(content_item)
    db.commit()
    db.refresh(content_item)
    return ContentItemOut.model_validate(content_item.__dict__, from_attributes=True)


@router.get("/content-items", response_model=List[ContentItemOut])
def list_content_items(org_id: str, db: Session = Depends(get_db)):
    """List content items for an organization."""
    rows = db.query(ContentItem).filter(ContentItem.org_id == org_id).all()
    return [ContentItemOut.model_validate(r.__dict__, from_attributes=True) for r in rows]


