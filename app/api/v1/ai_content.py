"""
AI Content API Router
Handles AI content generation, optimization, and batch processing
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import uuid
import asyncio

from app.api.deps import get_db, get_current_user
from app.schemas.ai_content import (
    AICompleteRequest, AICompleteResponse,
    AIBatchRequest, AIBatchResponse,
    AIOptimizeRequest, AIOptimizeResponse,
    AIRequestResponse, AIBatchJobResponse, AIOptimizationResponse
)
from app.models.ai_content import AIRequest, AIBatchJob, AIOptimization
from app.models.cms import UserAccount, Organization
from app.workers.tasks.ai_content_tasks import (
    generate_ai_content_task,
    process_batch_ai_content_task,
    optimize_content_task
)
from app.services.ai_router import ai_router
from app.services.budget_guard import BudgetGuard
from app.services.safety import safety_service

router = APIRouter()


@router.post("/ai/complete", response_model=AICompleteResponse, status_code=status.HTTP_200_OK)
async def complete_ai_content(
    request: AICompleteRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> AICompleteResponse:
    """
    Generate AI content from a prompt using the model router with budget and safety checks.
    """
    try:
        # Initialize budget guard
        budget_guard = BudgetGuard(db)
        
        # Estimate tokens and cost for budget check
        estimated_tokens = len(request.prompt) // 4  # Rough estimation
        estimated_cost_usd = estimated_tokens * 0.0001  # Rough cost estimation
        
        # Check budget constraints
        can_make_request, budget_violation = budget_guard.can_make_request(
            org_id=current_user.organization_id,
            user_id=current_user.id,
            estimated_tokens=estimated_tokens,
            estimated_cost_usd=estimated_cost_usd
        )
        
        if not can_make_request:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "message": budget_violation.friendly_message,
                    "upgrade_suggestion": budget_violation.upgrade_suggestion,
                    "limit_type": budget_violation.limit_type.value if budget_violation.limit_type else None,
                    "current_usage": budget_violation.current_usage,
                    "limit": budget_violation.limit,
                    "percentage": budget_violation.percentage
                }
            )
        
        # Generate AI content using the router
        ai_response = await ai_router.complete(
            prompt=request.prompt,
            system=None,  # Could be enhanced to use brand guide as system prompt
            temperature=0.7,
            max_tokens=1000,
            json_mode=False
        )
        
        # Safety check on generated content
        safety_result = await safety_service.check_content(
            content=ai_response.text,
            platform="general",
            brand_guide_id=str(request.brand_guide_id) if request.brand_guide_id else None,
            user_id=current_user.id
        )
        
        if not safety_result.is_safe:
            # Block unsafe content
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Generated content failed safety checks",
                    "violations": [
                        {
                            "type": v.type.value,
                            "level": v.level.value,
                            "message": v.message,
                            "suggestion": v.suggestion
                        } for v in safety_result.violations
                    ],
                    "warnings": safety_result.warnings,
                    "suggestions": safety_result.suggestions
                }
            )
        
        # Record usage in budget guard
        budget_guard.record_usage(
            org_id=current_user.organization_id,
            user_id=current_user.id,
            tokens_used=ai_response.tokens_in + ai_response.tokens_out,
            cost_gbp=ai_response.cost_usd_estimate / 1.25,  # Convert USD to GBP
            model_name=ai_response.provider,
            operation_type="content_generation"
        )
        
        # Save request to database
        ai_request = AIRequest(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            prompt=request.prompt,
            brand_guide_id=request.brand_guide_id,
            locale=request.locale,
            generated_text=ai_response.text,
            provider=ai_response.provider,
            model=ai_response.provider.split(":")[1] if ":" in ai_response.provider else ai_response.provider,
            prompt_tokens=ai_response.tokens_in,
            completion_tokens=ai_response.tokens_out,
            total_tokens=ai_response.tokens_in + ai_response.tokens_out,
            cost_usd=ai_response.cost_usd_estimate,
            status="completed"
        )
        
        db.add(ai_request)
        db.commit()
        db.refresh(ai_request)
        
        # Prepare response
        response_data = {
            "text": ai_response.text,
            "token_usage": {
                "prompt_tokens": ai_response.tokens_in,
                "completion_tokens": ai_response.tokens_out,
                "total_tokens": ai_response.tokens_in + ai_response.tokens_out
            },
            "provider": ai_response.provider,
            "model": ai_response.provider.split(":")[1] if ":" in ai_response.provider else ai_response.provider,
            "cost_usd": ai_response.cost_usd_estimate
        }
        
        # Add safety warnings if any
        if safety_result.warnings:
            response_data["safety_warnings"] = safety_result.warnings
        
        return AICompleteResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI content generation failed: {str(e)}"
        )


@router.post("/ai/batch", response_model=AIBatchResponse, status_code=status.HTTP_202_ACCEPTED)
async def batch_ai_content(
    request: AIBatchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> AIBatchResponse:
    """
    Process multiple prompts in batch using Celery tasks.
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Create batch job record
        batch_job = AIBatchJob(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            job_id=job_id,
            prompts=request.prompts,
            brand_guide_id=request.brand_guide_id,
            locale=request.locale,
            total_prompts=len(request.prompts),
            status="pending"
        )
        
        db.add(batch_job)
        db.commit()
        db.refresh(batch_job)
        
        # Queue Celery task
        task = process_batch_ai_content_task.delay(
            job_id=job_id,
            prompts=request.prompts,
            brand_guide_id=request.brand_guide_id,
            locale=request.locale,
            organization_id=current_user.organization_id,
            user_id=current_user.id
        )
        
        return AIBatchResponse(
            job_id=job_id,
            status="pending",
            total_prompts=len(request.prompts),
            status_url=f"/api/v1/ai/batch/{job_id}/status"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch AI content processing failed: {str(e)}"
        )


@router.get("/ai/batch/{job_id}/status", response_model=AIBatchJobResponse)
async def get_batch_status(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> AIBatchJobResponse:
    """
    Get the status of a batch AI content job.
    """
    batch_job = db.query(AIBatchJob).filter(
        AIBatchJob.job_id == job_id,
        AIBatchJob.organization_id == current_user.organization_id
    ).first()
    
    if not batch_job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Batch job not found"
        )
    
    return AIBatchJobResponse.from_orm(batch_job)


@router.post("/ai/optimize", response_model=AIOptimizeResponse, status_code=status.HTTP_200_OK)
async def optimize_content(
    request: AIOptimizeRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> AIOptimizeResponse:
    """
    Optimize content for a specific platform.
    """
    try:
        # FIXME: Implement actual content optimization logic
        # For now, return mock response
        optimized_text = f"Optimized for {request.platform}: {request.draft_content}"
        constraints_applied = {
            "character_limit": 280 if request.platform == "twitter" else 2200,
            "hashtag_limit": 5,
            "mention_limit": 3
        }
        
        # Save optimization to database
        optimization = AIOptimization(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            platform=request.platform,
            draft_content=request.draft_content,
            brand_guide_id=request.brand_guide_id,
            optimized_text=optimized_text,
            constraints_applied=constraints_applied,
            character_count=len(optimized_text),
            hashtag_count=optimized_text.count("#"),
            status="completed"
        )
        
        db.add(optimization)
        db.commit()
        db.refresh(optimization)
        
        return AIOptimizeResponse(
            optimized_text=optimized_text,
            constraints_applied=constraints_applied,
            character_count=len(optimized_text),
            hashtag_count=optimized_text.count("#"),
            platform=request.platform
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content optimization failed: {str(e)}"
        )


@router.get("/ai/requests", response_model=List[AIRequestResponse])
async def list_ai_requests(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[AIRequestResponse]:
    """
    List AI content generation requests for the current user.
    """
    requests = db.query(AIRequest).filter(
        AIRequest.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    
    return [AIRequestResponse.from_orm(req) for req in requests]


@router.get("/ai/optimizations", response_model=List[AIOptimizationResponse])
async def list_ai_optimizations(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[AIOptimizationResponse]:
    """
    List content optimizations for the current user.
    """
    optimizations = db.query(AIOptimization).filter(
        AIOptimization.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    
    return [AIOptimizationResponse.from_orm(opt) for opt in optimizations]
