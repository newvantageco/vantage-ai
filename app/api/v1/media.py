"""
Media API Router
Handles media upload, processing, and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from pathlib import Path
import logging

from app.api.deps import get_db, get_current_user
from app.schemas.media import (
    MediaUploadResponse, MediaListResponse, MediaItem,
    MediaSearchRequest, MediaBulkDeleteRequest, MediaBulkDeleteResponse,
    MediaUpdateRequest
)
from app.services.media_service import MediaService
from app.models.cms import UserAccount
from app.models.media import MediaItem as MediaItemModel

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(...),
    content_id: Optional[int] = Form(None),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> MediaUploadResponse:
    """Upload a media file"""
    try:
        media_service = MediaService()
        result = await media_service.upload_media(
            file=file,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            content_id=content_id,
            db=db
        )
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Media upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Media upload failed: {str(e)}"
        )


@router.get("/", response_model=MediaListResponse)
async def list_media(
    content_id: Optional[int] = Query(None, description="Filter by content ID"),
    media_type: Optional[str] = Query(None, description="Filter by media type"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> MediaListResponse:
    """List media items for the organization"""
    try:
        media_service = MediaService()
        offset = (page - 1) * size
        
        media_items = await media_service.list_media(
            organization_id=current_user.organization_id,
            db=db,
            content_id=content_id,
            media_type=media_type,
            limit=size,
            offset=offset
        )
        
        # Convert to response format
        items = []
        for item in media_items:
            items.append(MediaItem(
                id=item.id,
                organization_id=item.organization_id,
                user_id=item.user_id,
                content_id=item.content_id,
                original_filename=item.original_filename,
                stored_filename=item.stored_filename,
                file_path=item.file_path,
                file_size=item.file_size,
                mime_type=item.mime_type,
                file_hash=item.file_hash,
                media_type=item.media_type,
                status=item.status,
                processing_metadata=item.processing_metadata or {},
                created_at=item.created_at,
                updated_at=item.updated_at
            ))
        
        # Get total count
        total_query = db.query(MediaItemModel).filter(
            MediaItemModel.organization_id == current_user.organization_id
        )
        if content_id:
            total_query = total_query.filter(MediaItemModel.content_id == content_id)
        if media_type:
            total_query = total_query.filter(MediaItemModel.media_type == media_type)
        
        total = total_query.count()
        total_pages = (total + size - 1) // size
        
        return MediaListResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Failed to list media: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list media: {str(e)}"
        )


@router.get("/{media_id}", response_model=MediaItem)
async def get_media(
    media_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> MediaItem:
    """Get a specific media item"""
    try:
        media_service = MediaService()
        media_item = await media_service.get_media(media_id, current_user.organization_id, db)
        
        if not media_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found"
            )
        
        return media_item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Media retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve media: {str(e)}"
        )


@router.put("/{media_id}", response_model=MediaItem)
async def update_media(
    media_id: str,
    update_data: MediaUpdateRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> MediaItem:
    """Update media metadata"""
    try:
        media_service = MediaService()
        media_item = await media_service.get_media(media_id, current_user.organization_id, db)
        
        if not media_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found"
            )
        
        # Update media item
        if update_data.content_id is not None:
            media_item.content_id = update_data.content_id
        if update_data.metadata is not None:
            media_item.processing_metadata.update(update_data.metadata)
        
        # Save to database
        # db.commit()
        # db.refresh(media_item)
        
        return media_item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Media update failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update media: {str(e)}"
        )


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Delete a media item"""
    try:
        media_service = MediaService()
        success = await media_service.delete_media(media_id, current_user.organization_id, db)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Media deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete media: {str(e)}"
        )


@router.post("/bulk-delete", response_model=MediaBulkDeleteResponse)
async def bulk_delete_media(
    request: MediaBulkDeleteRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> MediaBulkDeleteResponse:
    """Delete multiple media items"""
    try:
        media_service = MediaService()
        deleted_count = 0
        failed_count = 0
        failed_ids = []
        
        for media_id in request.media_ids:
            success = await media_service.delete_media(media_id, current_user.organization_id, db)
            if success:
                deleted_count += 1
            else:
                failed_count += 1
                failed_ids.append(media_id)
        
        return MediaBulkDeleteResponse(
            deleted_count=deleted_count,
            failed_count=failed_count,
            failed_ids=failed_ids
        )
        
    except Exception as e:
        logger.error(f"Bulk media deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk media deletion failed: {str(e)}"
        )


@router.get("/{media_id}/download")
async def download_media(
    media_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Download a media file"""
    try:
        media_service = MediaService()
        media_item = await media_service.get_media(media_id, current_user.organization_id, db)
        
        if not media_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found"
            )
        
        # Return file for download
        from fastapi.responses import FileResponse
        return FileResponse(
            path=media_item.file_path,
            filename=media_item.original_filename,
            media_type=media_item.mime_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Media download failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download media: {str(e)}"
        )


@router.post("/search", response_model=MediaListResponse)
async def search_media(
    search_request: MediaSearchRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> MediaListResponse:
    """Search media items"""
    try:
        # Build query
        query = db.query(MediaItemModel).filter(
            MediaItemModel.organization_id == current_user.organization_id
        )
        
        if search_request.query:
            query = query.filter(
                or_(
                    MediaItemModel.original_filename.ilike(f"%{search_request.query}%"),
                    MediaItemModel.mime_type.ilike(f"%{search_request.query}%")
                )
            )
        
        if search_request.media_type:
            query = query.filter(MediaItemModel.media_type == search_request.media_type)
        
        if search_request.content_id:
            query = query.filter(MediaItemModel.content_id == search_request.content_id)
        
        if search_request.date_from:
            query = query.filter(MediaItemModel.created_at >= search_request.date_from)
        
        if search_request.date_to:
            query = query.filter(MediaItemModel.created_at <= search_request.date_to)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (search_request.page - 1) * search_request.size
        media_items = query.offset(offset).limit(search_request.size).all()
        
        # Convert to response format
        items = []
        for item in media_items:
            items.append(MediaItem(
                id=item.id,
                organization_id=item.organization_id,
                user_id=item.user_id,
                content_id=item.content_id,
                original_filename=item.original_filename,
                stored_filename=item.stored_filename,
                file_path=item.file_path,
                file_size=item.file_size,
                mime_type=item.mime_type,
                file_hash=item.file_hash,
                media_type=item.media_type,
                status=item.status,
                processing_metadata=item.processing_metadata or {},
                created_at=item.created_at,
                updated_at=item.updated_at
            ))
        
        total_pages = (total + search_request.size - 1) // search_request.size
        
        return MediaListResponse(
            items=items,
            total=total,
            page=search_request.page,
            size=search_request.size,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Media search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Media search failed: {str(e)}"
        )


@router.get("/{media_id}/thumbnail")
async def get_media_thumbnail(
    media_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Get media thumbnail"""
    try:
        media_service = MediaService()
        media_item = await media_service.get_media(media_id, current_user.organization_id, db)
        
        if not media_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Media not found"
            )
        
        # Generate thumbnail path
        file_path = Path(media_item.file_path)
        thumbnail_path = file_path.parent / f"thumb_{file_path.name}"
        
        if not thumbnail_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thumbnail not found"
            )
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=str(thumbnail_path),
            media_type="image/jpeg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Media thumbnail failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Media thumbnail failed: {str(e)}"
        )
