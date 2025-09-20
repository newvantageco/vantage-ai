"""
Simple Content Scheduling API
A minimal scheduling endpoint that works with existing infrastructure
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging

router = APIRouter()


class ScheduleRequest(BaseModel):
    content: str
    platforms: List[str]  # ["facebook", "instagram", "linkedin", "google_gbp"]
    scheduled_at: str  # ISO datetime string
    media: List[Dict[str, Any]] = []
    timezone: str = "UTC"


class ScheduleResponse(BaseModel):
    success: bool
    schedule_id: Optional[str] = None
    scheduled_at: str
    platforms: List[str]
    message: str
    errors: List[str] = []


class ScheduleStatus(BaseModel):
    schedule_id: str
    status: str  # "scheduled", "published", "failed", "cancelled"
    scheduled_at: str
    platforms: List[str]
    content_preview: str
    published_at: Optional[str] = None
    error_message: Optional[str] = None


class ScheduleListResponse(BaseModel):
    schedules: List[ScheduleStatus]
    total: int
    page: int
    size: int


@router.post("/schedule/create", response_model=ScheduleResponse)
async def create_schedule(request: ScheduleRequest) -> ScheduleResponse:
    """
    Create a new content schedule
    """
    try:
        # Validate platforms
        valid_platforms = ["facebook", "instagram", "linkedin", "google_gbp"]
        invalid_platforms = [p for p in request.platforms if p not in valid_platforms]
        if invalid_platforms:
            return ScheduleResponse(
                success=False,
                scheduled_at=request.scheduled_at,
                platforms=request.platforms,
                message=f"Invalid platforms: {invalid_platforms}",
                errors=[f"Platform {p} is not supported" for p in invalid_platforms]
            )
        
        # Validate scheduled time
        try:
            scheduled_datetime = datetime.fromisoformat(request.scheduled_at.replace('Z', '+00:00'))
            if scheduled_datetime <= datetime.now(timezone.utc):
                return ScheduleResponse(
                    success=False,
                    scheduled_at=request.scheduled_at,
                    platforms=request.platforms,
                    message="Scheduled time must be in the future",
                    errors=["Scheduled time must be in the future"]
                )
        except ValueError:
            return ScheduleResponse(
                success=False,
                scheduled_at=request.scheduled_at,
                platforms=request.platforms,
                message="Invalid datetime format",
                errors=["Invalid datetime format. Use ISO format: 2024-01-01T12:00:00Z"]
            )
        
        # Validate content length
        if len(request.content) > 3000:
            return ScheduleResponse(
                success=False,
                scheduled_at=request.scheduled_at,
                platforms=request.platforms,
                message="Content too long",
                errors=["Content exceeds 3000 character limit"]
            )
        
        # Create mock schedule (in real implementation, this would save to database)
        schedule_id = f"schedule_{int(datetime.now().timestamp())}"
        
        # Mock successful scheduling
        return ScheduleResponse(
            success=True,
            schedule_id=schedule_id,
            scheduled_at=request.scheduled_at,
            platforms=request.platforms,
            message=f"Content scheduled successfully for {len(request.platforms)} platform(s)",
            errors=[]
        )
        
    except Exception as e:
        logger.error(f"Schedule creation error: {e}")
        return ScheduleResponse(
            success=False,
            scheduled_at=request.scheduled_at,
            platforms=request.platforms,
            message=f"Schedule creation failed: {str(e)}",
            errors=[str(e)]
        )


@router.get("/schedule/list", response_model=ScheduleListResponse)
async def list_schedules(
    page: int = 1,
    size: int = 10,
    status_filter: Optional[str] = None
) -> ScheduleListResponse:
    """
    List all schedules with pagination
    """
    try:
        # Mock schedule data (in real implementation, this would query database)
        mock_schedules = [
            ScheduleStatus(
                schedule_id="schedule_1703123456",
                status="scheduled",
                scheduled_at="2024-01-01T12:00:00Z",
                platforms=["facebook", "linkedin"],
                content_preview="🚀 Exciting news! We're launching our new AI-powered marketing platform...",
                published_at=None,
                error_message=None
            ),
            ScheduleStatus(
                schedule_id="schedule_1703123457",
                status="published",
                scheduled_at="2024-01-01T10:00:00Z",
                platforms=["instagram"],
                content_preview="📱 Transform your social media strategy with AI...",
                published_at="2024-01-01T10:00:05Z",
                error_message=None
            ),
            ScheduleStatus(
                schedule_id="schedule_1703123458",
                status="failed",
                scheduled_at="2024-01-01T08:00:00Z",
                platforms=["twitter"],
                content_preview="🎯 Boost your engagement with our new features...",
                published_at=None,
                error_message="Invalid access token"
            )
        ]
        
        # Apply status filter if provided
        if status_filter:
            mock_schedules = [s for s in mock_schedules if s.status == status_filter]
        
        # Apply pagination
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_schedules = mock_schedules[start_idx:end_idx]
        
        return ScheduleListResponse(
            schedules=paginated_schedules,
            total=len(mock_schedules),
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"List schedules error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list schedules: {str(e)}"
        )


@router.get("/schedule/{schedule_id}", response_model=ScheduleStatus)
async def get_schedule_status(schedule_id: str) -> ScheduleStatus:
    """
    Get status of a specific schedule
    """
    try:
        # Mock schedule data (in real implementation, this would query database)
        mock_schedules = {
            "schedule_1703123456": ScheduleStatus(
                schedule_id="schedule_1703123456",
                status="scheduled",
                scheduled_at="2024-01-01T12:00:00Z",
                platforms=["facebook", "linkedin"],
                content_preview="🚀 Exciting news! We're launching our new AI-powered marketing platform...",
                published_at=None,
                error_message=None
            ),
            "schedule_1703123457": ScheduleStatus(
                schedule_id="schedule_1703123457",
                status="published",
                scheduled_at="2024-01-01T10:00:00Z",
                platforms=["instagram"],
                content_preview="📱 Transform your social media strategy with AI...",
                published_at="2024-01-01T10:00:05Z",
                error_message=None
            )
        }
        
        if schedule_id in mock_schedules:
            return mock_schedules[schedule_id]
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Schedule {schedule_id} not found"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get schedule error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schedule: {str(e)}"
        )


@router.get("/schedule/list", response_model=ScheduleListResponse)
async def list_schedules(
    page: int = 1,
    size: int = 10,
    status_filter: Optional[str] = None
) -> ScheduleListResponse:
    """
    List all schedules with pagination
    """
    try:
        # Mock schedule data (in real implementation, this would query database)
        mock_schedules = [
            ScheduleStatus(
                schedule_id="schedule_1703123456",
                status="scheduled",
                scheduled_at="2024-01-01T12:00:00Z",
                platforms=["facebook", "linkedin"],
                content_preview="🚀 Exciting news! We're launching our new AI-powered marketing platform...",
                published_at=None,
                error_message=None
            ),
            ScheduleStatus(
                schedule_id="schedule_1703123457",
                status="published",
                scheduled_at="2024-01-01T10:00:00Z",
                platforms=["instagram"],
                content_preview="📱 Transform your social media strategy with AI...",
                published_at="2024-01-01T10:00:05Z",
                error_message=None
            ),
            ScheduleStatus(
                schedule_id="schedule_1703123458",
                status="failed",
                scheduled_at="2024-01-01T08:00:00Z",
                platforms=["twitter"],
                content_preview="🎯 Boost your engagement with our new features...",
                published_at=None,
                error_message="Invalid access token"
            )
        ]
        
        # Apply status filter if provided
        if status_filter:
            mock_schedules = [s for s in mock_schedules if s.status == status_filter]
        
        # Apply pagination
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_schedules = mock_schedules[start_idx:end_idx]
        
        return ScheduleListResponse(
            schedules=paginated_schedules,
            total=len(mock_schedules),
            page=page,
            size=size
        )
        
    except Exception as e:
        logger.error(f"List schedules error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list schedules: {str(e)}"
        )


@router.delete("/schedule/{schedule_id}")
async def cancel_schedule(schedule_id: str):
    """
    Cancel a scheduled post
    """
    try:
        # Mock cancellation (in real implementation, this would update database)
        return {
            "success": True,
            "message": f"Schedule {schedule_id} cancelled successfully",
            "schedule_id": schedule_id
        }
        
    except Exception as e:
        logger.error(f"Cancel schedule error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel schedule: {str(e)}"
        )


@router.get("/scheduling/status")
async def get_scheduling_status():
    """Get scheduling service status"""
    return {
        "status": "operational",
        "features": [
            "content_scheduling",
            "multi_platform_support",
            "timezone_support",
            "schedule_management"
        ],
        "supported_platforms": ["facebook", "instagram", "linkedin", "google_gbp"],
        "version": "1.0.0",
        "message": "Scheduling service is ready!"
    }


@router.get("/scheduling/optimal-times")
async def get_optimal_times():
    """Get optimal posting times for different platforms"""
    return {
        "facebook": {
            "best_times": ["09:00-10:00", "15:00-16:00", "19:00-20:00"],
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "timezone": "UTC"
        },
        "instagram": {
            "best_times": ["11:00-12:00", "17:00-18:00", "20:00-21:00"],
            "best_days": ["Monday", "Tuesday", "Wednesday"],
            "timezone": "UTC"
        },
        "linkedin": {
            "best_times": ["08:00-09:00", "12:00-13:00", "17:00-18:00"],
            "best_days": ["Tuesday", "Wednesday", "Thursday"],
            "timezone": "UTC"
        },
        "google_gbp": {
            "best_times": ["09:00-10:00", "14:00-15:00", "18:00-19:00"],
            "best_days": ["Monday", "Tuesday", "Wednesday"],
            "timezone": "UTC"
        }
    }
