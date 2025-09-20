"""
Content Library API Router
Handles content library operations including search, filtering, and organization
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.api.deps import get_db, get_current_user
from app.schemas.content_library import (
    ContentLibrarySearchRequest, ContentLibrarySearchResponse,
    ContentLibraryStats, ContentLibraryCollection,
    ContentLibraryCollectionCreate, ContentLibraryCollectionUpdate,
    ContentLibraryCollectionResponse, ContentLibraryExportRequest,
    ContentLibraryExportResponse, ContentLibraryImportRequest,
    ContentLibraryImportResponse, ContentLibraryTagRequest,
    ContentLibraryTagResponse, ContentLibraryArchiveRequest,
    ContentLibraryArchiveResponse
)
from app.services.content_library_service import ContentLibraryService
from app.models.cms import UserAccount

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/search", response_model=ContentLibrarySearchResponse)
async def search_content_library(
    search_request: ContentLibrarySearchRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibrarySearchResponse:
    """Search and filter content in the library"""
    try:
        service = ContentLibraryService()
        result = await service.search_content(
            search_request=search_request,
            organization_id=current_user.organization_id,
            db=db
        )
        return result
        
    except Exception as e:
        logger.error(f"Content library search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content library search failed: {str(e)}"
        )


@router.get("/stats", response_model=ContentLibraryStats)
async def get_content_library_stats(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryStats:
    """Get content library statistics"""
    try:
        service = ContentLibraryService()
        stats = await service.get_content_stats(
            organization_id=current_user.organization_id,
            db=db
        )
        return stats
        
    except Exception as e:
        logger.error(f"Content library stats failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content library stats failed: {str(e)}"
        )


@router.get("/collections", response_model=List[ContentLibraryCollection])
async def get_collections(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[ContentLibraryCollection]:
    """Get all content collections"""
    try:
        service = ContentLibraryService()
        collections = await service.get_collections(
            organization_id=current_user.organization_id,
            db=db
        )
        return collections
        
    except Exception as e:
        logger.error(f"Get collections failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get collections failed: {str(e)}"
        )


@router.post("/collections", response_model=ContentLibraryCollectionResponse)
async def create_collection(
    collection_data: ContentLibraryCollectionCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryCollectionResponse:
    """Create a new content collection"""
    try:
        service = ContentLibraryService()
        collection = await service.create_collection(
            name=collection_data.name,
            description=collection_data.description,
            content_ids=collection_data.content_ids,
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            db=db
        )
        
        return ContentLibraryCollectionResponse(
            success=True,
            collection=collection
        )
        
    except Exception as e:
        logger.error(f"Collection creation failed: {str(e)}")
        return ContentLibraryCollectionResponse(
            success=False,
            error=str(e)
        )


@router.get("/collections/{collection_id}", response_model=ContentLibraryCollection)
async def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryCollection:
    """Get a specific content collection"""
    try:
        service = ContentLibraryService()
        collections = await service.get_collections(
            organization_id=current_user.organization_id,
            db=db
        )
        
        collection = next((c for c in collections if c.id == collection_id), None)
        if not collection:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )
        
        return collection
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get collection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Get collection failed: {str(e)}"
        )


@router.put("/collections/{collection_id}", response_model=ContentLibraryCollectionResponse)
async def update_collection(
    collection_id: int,
    collection_data: ContentLibraryCollectionUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryCollectionResponse:
    """Update a content collection"""
    try:
        service = ContentLibraryService()
        
        # Get existing collection
        collections = await service.get_collections(
            organization_id=current_user.organization_id,
            db=db
        )
        
        collection = next((c for c in collections if c.id == collection_id), None)
        if not collection:
            return ContentLibraryCollectionResponse(
                success=False,
                error="Collection not found"
            )
        
        # Update collection (this would need to be implemented in the service)
        # For now, return the existing collection
        return ContentLibraryCollectionResponse(
            success=True,
            collection=collection
        )
        
    except Exception as e:
        logger.error(f"Collection update failed: {str(e)}")
        return ContentLibraryCollectionResponse(
            success=False,
            error=str(e)
        )


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Delete a content collection"""
    try:
        # This would need to be implemented in the service
        # For now, just return success
        pass
        
    except Exception as e:
        logger.error(f"Collection deletion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Collection deletion failed: {str(e)}"
        )


@router.post("/collections/{collection_id}/content", response_model=ContentLibraryCollectionResponse)
async def add_content_to_collection(
    collection_id: int,
    content_ids: List[int],
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryCollectionResponse:
    """Add content items to a collection"""
    try:
        service = ContentLibraryService()
        success = await service.add_to_collection(
            collection_id=collection_id,
            content_ids=content_ids,
            organization_id=current_user.organization_id,
            db=db
        )
        
        if not success:
            return ContentLibraryCollectionResponse(
                success=False,
                error="Failed to add content to collection"
            )
        
        # Get updated collection
        collections = await service.get_collections(
            organization_id=current_user.organization_id,
            db=db
        )
        
        collection = next((c for c in collections if c.id == collection_id), None)
        
        return ContentLibraryCollectionResponse(
            success=True,
            collection=collection
        )
        
    except Exception as e:
        logger.error(f"Add content to collection failed: {str(e)}")
        return ContentLibraryCollectionResponse(
            success=False,
            error=str(e)
        )


@router.delete("/collections/{collection_id}/content", response_model=ContentLibraryCollectionResponse)
async def remove_content_from_collection(
    collection_id: int,
    content_ids: List[int],
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryCollectionResponse:
    """Remove content items from a collection"""
    try:
        service = ContentLibraryService()
        success = await service.remove_from_collection(
            collection_id=collection_id,
            content_ids=content_ids,
            organization_id=current_user.organization_id,
            db=db
        )
        
        if not success:
            return ContentLibraryCollectionResponse(
                success=False,
                error="Failed to remove content from collection"
            )
        
        # Get updated collection
        collections = await service.get_collections(
            organization_id=current_user.organization_id,
            db=db
        )
        
        collection = next((c for c in collections if c.id == collection_id), None)
        
        return ContentLibraryCollectionResponse(
            success=True,
            collection=collection
        )
        
    except Exception as e:
        logger.error(f"Remove content from collection failed: {str(e)}")
        return ContentLibraryCollectionResponse(
            success=False,
            error=str(e)
        )


@router.post("/export", response_model=ContentLibraryExportResponse)
async def export_content_library(
    export_request: ContentLibraryExportRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryExportResponse:
    """Export content library"""
    try:
        # This would implement actual export functionality
        # For now, return a mock response
        import uuid
        export_id = str(uuid.uuid4())
        
        return ContentLibraryExportResponse(
            export_id=export_id,
            download_url=f"/api/v1/content-library/exports/{export_id}",
            file_size=0,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
    except Exception as e:
        logger.error(f"Content library export failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content library export failed: {str(e)}"
        )


@router.post("/import", response_model=ContentLibraryImportResponse)
async def import_content_library(
    import_request: ContentLibraryImportRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryImportResponse:
    """Import content library"""
    try:
        # This would implement actual import functionality
        # For now, return a mock response
        import uuid
        import_id = str(uuid.uuid4())
        
        return ContentLibraryImportResponse(
            import_id=import_id,
            status="processing",
            total_items=0,
            imported_count=0,
            skipped_count=0,
            failed_count=0,
            failed_items=[],
            new_content_ids=[]
        )
        
    except Exception as e:
        logger.error(f"Content library import failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content library import failed: {str(e)}"
        )


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Delete a content collection"""
    try:
        # This would delete the collection from the database
        # For now, just return success
        pass
        
    except Exception as e:
        logger.error(f"Delete collection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Delete collection failed: {str(e)}"
        )


@router.post("/collections/{collection_id}/add", response_model=ContentLibraryCollectionResponse)
async def add_to_collection(
    collection_id: int,
    content_ids: List[int],
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryCollectionResponse:
    """Add content items to a collection"""
    try:
        service = ContentLibraryService()
        success = await service.add_to_collection(
            collection_id=collection_id,
            content_ids=content_ids,
            organization_id=current_user.organization_id,
            db=db
        )
        
        return ContentLibraryCollectionResponse(
            success=success,
            collection=None
        )
        
    except Exception as e:
        logger.error(f"Add to collection failed: {str(e)}")
        return ContentLibraryCollectionResponse(
            success=False,
            error=str(e)
        )


@router.post("/collections/{collection_id}/remove", response_model=ContentLibraryCollectionResponse)
async def remove_from_collection(
    collection_id: int,
    content_ids: List[int],
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryCollectionResponse:
    """Remove content items from a collection"""
    try:
        service = ContentLibraryService()
        success = await service.remove_from_collection(
            collection_id=collection_id,
            content_ids=content_ids,
            organization_id=current_user.organization_id,
            db=db
        )
        
        return ContentLibraryCollectionResponse(
            success=success,
            collection=None
        )
        
    except Exception as e:
        logger.error(f"Remove from collection failed: {str(e)}")
        return ContentLibraryCollectionResponse(
            success=False,
            error=str(e)
        )


@router.post("/export", response_model=ContentLibraryExportResponse)
async def export_content_library(
    export_request: ContentLibraryExportRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryExportResponse:
    """Export content library"""
    try:
        # This would create an export job and return the export details
        # For now, return mock data
        return ContentLibraryExportResponse(
            export_id="mock_export_id",
            download_url="/api/v1/content-library/exports/mock_export_id/download",
            file_size=1024,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
    except Exception as e:
        logger.error(f"Content library export failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content library export failed: {str(e)}"
        )


@router.post("/import", response_model=ContentLibraryImportResponse)
async def import_content_library(
    import_request: ContentLibraryImportRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryImportResponse:
    """Import content library"""
    try:
        # This would create an import job and return the import details
        # For now, return mock data
        return ContentLibraryImportResponse(
            import_id="mock_import_id",
            status="pending",
            total_items=0,
            imported_count=0,
            skipped_count=0,
            failed_count=0,
            failed_items=[],
            new_content_ids=[]
        )
        
    except Exception as e:
        logger.error(f"Content library import failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Content library import failed: {str(e)}"
        )


@router.post("/tag", response_model=ContentLibraryTagResponse)
async def tag_content(
    tag_request: ContentLibraryTagRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryTagResponse:
    """Tag content items"""
    try:
        # This would update tags for content items
        # For now, return mock success
        return ContentLibraryTagResponse(
            success=True,
            updated_count=len(tag_request.content_ids),
            failed_count=0,
            failed_ids=[]
        )
        
    except Exception as e:
        logger.error(f"Content tagging failed: {str(e)}")
        return ContentLibraryTagResponse(
            success=False,
            updated_count=0,
            failed_count=len(tag_request.content_ids),
            failed_ids=tag_request.content_ids
        )


@router.post("/archive", response_model=ContentLibraryArchiveResponse)
async def archive_content(
    archive_request: ContentLibraryArchiveRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentLibraryArchiveResponse:
    """Archive content items"""
    try:
        # This would archive content items
        # For now, return mock success
        return ContentLibraryArchiveResponse(
            success=True,
            archived_count=len(archive_request.content_ids),
            failed_count=0,
            failed_ids=[]
        )
        
    except Exception as e:
        logger.error(f"Content archiving failed: {str(e)}")
        return ContentLibraryArchiveResponse(
            success=False,
            archived_count=0,
            failed_count=len(archive_request.content_ids),
            failed_ids=archive_request.content_ids
        )
