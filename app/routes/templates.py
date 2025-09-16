from __future__ import annotations

import logging
from typing import List, Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.templates import AssetTemplate, TemplateType, TemplateUsage
from app.models.entities import UserAccount
from app.creatives.image_builder import ImageBuilder
from app.creatives.video_builder import VideoBuilder

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/public")
async def get_public_templates(
    type: Optional[TemplateType] = Query(None, description="Filter by template type"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get curated public templates available to all organizations."""
    query = db.query(AssetTemplate).filter(AssetTemplate.is_public == True)
    
    if type:
        query = query.filter(AssetTemplate.type == type)
    
    total = query.count()
    templates = query.offset(offset).limit(limit).all()
    
    return {
        "templates": [template.to_dict() for template in templates],
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.get("/my")
async def get_my_templates(
    type: Optional[TemplateType] = Query(None, description="Filter by template type"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get templates for the current user's organization."""
    query = db.query(AssetTemplate).filter(
        (AssetTemplate.org_id == current_user.org_id) | (AssetTemplate.is_public == True)
    )
    
    if type:
        query = query.filter(AssetTemplate.type == type)
    
    total = query.count()
    templates = query.offset(offset).limit(limit).all()
    
    return {
        "templates": [template.to_dict() for template in templates],
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.post("/")
async def create_template(
    name: str,
    description: Optional[str],
    type: TemplateType,
    spec: Dict[str, Any],
    is_public: bool = False,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Create a new template for the organization."""
    template = AssetTemplate(
        id=str(uuid4()),
        org_id=current_user.org_id,
        name=name,
        description=description,
        type=type,
        spec=spec,
        is_public=is_public,
        created_by=current_user.id
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    logger.info(f"Created template {template.id} for org {current_user.org_id}")
    return template.to_dict()


@router.get("/{template_id}")
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get a specific template by ID."""
    template = db.query(AssetTemplate).filter(
        AssetTemplate.id == template_id,
        (AssetTemplate.org_id == current_user.org_id) | (AssetTemplate.is_public == True)
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template.to_dict()


@router.post("/{template_id}/generate")
async def generate_from_template(
    template_id: str,
    inputs: Dict[str, Any],
    content_item_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate an asset from a template with given inputs."""
    template = db.query(AssetTemplate).filter(
        AssetTemplate.id == template_id,
        (AssetTemplate.org_id == current_user.org_id) | (AssetTemplate.is_public == True)
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    try:
        if template.type == TemplateType.image:
            builder = ImageBuilder()
            result = await builder.render_image(template.spec, inputs)
        elif template.type == TemplateType.video:
            builder = VideoBuilder()
            result = await builder.render_video(template.spec, inputs)
        else:
            raise HTTPException(status_code=400, detail="Unsupported template type")
        
        # Track usage
        usage = TemplateUsage(
            id=str(uuid4()),
            template_id=template_id,
            org_id=current_user.org_id,
            content_item_id=content_item_id,
            inputs=inputs
        )
        db.add(usage)
        db.commit()
        
        logger.info(f"Generated {template.type} from template {template_id} for org {current_user.org_id}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to generate from template {template_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete a template (only if owned by the organization)."""
    template = db.query(AssetTemplate).filter(
        AssetTemplate.id == template_id,
        AssetTemplate.org_id == current_user.org_id
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found or not owned by organization")
    
    db.delete(template)
    db.commit()
    
    logger.info(f"Deleted template {template_id} for org {current_user.org_id}")
    return {"message": "Template deleted successfully"}


@router.get("/{template_id}/usage")
async def get_template_usage(
    template_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get usage statistics for a template."""
    template = db.query(AssetTemplate).filter(
        AssetTemplate.id == template_id,
        (AssetTemplate.org_id == current_user.org_id) | (AssetTemplate.is_public == True)
    ).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    query = db.query(TemplateUsage).filter(
        TemplateUsage.template_id == template_id,
        TemplateUsage.org_id == current_user.org_id
    )
    
    total = query.count()
    usage_records = query.offset(offset).limit(limit).all()
    
    return {
        "template_id": template_id,
        "usage_records": [
            {
                "id": usage.id,
                "used_at": usage.used_at.isoformat(),
                "content_item_id": usage.content_item_id,
                "inputs": usage.inputs
            }
            for usage in usage_records
        ],
        "total": total,
        "offset": offset,
        "limit": limit
    }
