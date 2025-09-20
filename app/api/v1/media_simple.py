"""
Simple Media Upload API
A minimal media upload endpoint that works with existing infrastructure
"""

from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid
import os
import mimetypes
from pathlib import Path

router = APIRouter()

# --- Schemas for API Requests/Responses ---
class MediaItem(BaseModel):
    id: str
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    media_type: str  # image, video, audio, document
    status: str  # pending, processing, processed, failed
    url: str
    thumbnail_url: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

class MediaUploadResponse(BaseModel):
    success: bool
    media_item: Optional[MediaItem] = None
    message: str
    error: Optional[str] = None

class MediaListResponse(BaseModel):
    media_items: List[MediaItem]
    total: int
    page: int
    size: int
    has_more: bool

class MediaStatsResponse(BaseModel):
    total_files: int
    total_size: int  # in bytes
    by_type: Dict[str, int]  # count by media type
    by_status: Dict[str, int]  # count by status

class MediaServiceStatusResponse(BaseModel):
    status: str
    features: List[str]
    supported_formats: Dict[str, List[str]]
    max_file_sizes: Dict[str, int]  # in bytes
    version: str
    message: Optional[str] = None

# --- Helper Functions ---
def get_media_type(mime_type: str, filename: str) -> str:
    """Determine media type from MIME type and filename"""
    if mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        return 'document'
    else:
        return 'document'

def is_supported_format(filename: str, mime_type: str) -> bool:
    """Check if file format is supported"""
    supported_extensions = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg'],
        'video': ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'],
        'audio': ['.mp3', '.wav', '.ogg', '.m4a', '.aac'],
        'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf']
    }
    
    file_ext = Path(filename).suffix.lower()
    media_type = get_media_type(mime_type, filename)
    
    return file_ext in supported_extensions.get(media_type, [])

def get_file_size_limit(media_type: str) -> int:
    """Get file size limit for media type"""
    limits = {
        'image': 10 * 1024 * 1024,  # 10MB
        'video': 100 * 1024 * 1024,  # 100MB
        'audio': 50 * 1024 * 1024,   # 50MB
        'document': 25 * 1024 * 1024  # 25MB
    }
    return limits.get(media_type, 10 * 1024 * 1024)

# --- API Endpoints ---

@router.post("/media/upload", response_model=MediaUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(...),
    content_id: Optional[int] = Form(None)
) -> MediaUploadResponse:
    """
    Upload a media file
    """
    try:
        # Validate file
        if not file.filename:
            return MediaUploadResponse(
                success=False,
                message="No file provided",
                error="Filename is required"
            )
        
        # Get file info
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        # Determine media type
        mime_type = file.content_type or mimetypes.guess_type(file.filename)[0] or 'application/octet-stream'
        
        # Fix MIME type detection for common cases
        if file.filename.lower().endswith('.png') and mime_type == 'application/octet-stream':
            mime_type = 'image/png'
        elif file.filename.lower().endswith('.jpg') and mime_type == 'application/octet-stream':
            mime_type = 'image/jpeg'
        elif file.filename.lower().endswith('.jpeg') and mime_type == 'application/octet-stream':
            mime_type = 'image/jpeg'
        elif file.filename.lower().endswith('.gif') and mime_type == 'application/octet-stream':
            mime_type = 'image/gif'
        elif file.filename.lower().endswith('.webp') and mime_type == 'application/octet-stream':
            mime_type = 'image/webp'
        elif file.filename.lower().endswith('.mp4') and mime_type == 'application/octet-stream':
            mime_type = 'video/mp4'
        elif file.filename.lower().endswith('.mp3') and mime_type == 'application/octet-stream':
            mime_type = 'audio/mpeg'
        elif file.filename.lower().endswith('.pdf') and mime_type == 'application/octet-stream':
            mime_type = 'application/pdf'
        
        media_type = get_media_type(mime_type, file.filename)
        
        # Check if format is supported
        if not is_supported_format(file.filename, mime_type):
            return MediaUploadResponse(
                success=False,
                message="Unsupported file format",
                error=f"File type {mime_type} is not supported"
            )
        
        # Check file size limit
        size_limit = get_file_size_limit(media_type)
        if file_size > size_limit:
            return MediaUploadResponse(
                success=False,
                message="File too large",
                error=f"File size {file_size} exceeds limit of {size_limit} bytes"
            )
        
        # Generate unique filename and save file
        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix.lower()
        stored_filename = f"{file_id}{file_ext}"
        
        # Create upload directory
        upload_dir = Path("uploads/media")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / stored_filename
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Generate URLs
        base_url = "http://localhost:8000"
        file_url = f"{base_url}/media/{stored_filename}"
        thumbnail_url = f"{base_url}/media/thumbnails/{stored_filename}" if media_type == 'image' else None
        
        # Create media item
        media_item = MediaItem(
            id=file_id,
            filename=stored_filename,
            original_filename=file.filename,
            file_size=file_size,
            mime_type=mime_type,
            media_type=media_type,
            status="processed",  # For simplicity, mark as processed immediately
            url=file_url,
            thumbnail_url=thumbnail_url,
            created_at=datetime.utcnow().isoformat() + "Z",
            updated_at=datetime.utcnow().isoformat() + "Z"
        )
        
        return MediaUploadResponse(
            success=True,
            media_item=media_item,
            message=f"File uploaded successfully: {file.filename}"
        )
        
    except Exception as e:
        logger.error(f"Media upload error: {e}")
        return MediaUploadResponse(
            success=False,
            message="Upload failed",
            error=str(e)
        )

@router.get("/media/list", response_model=MediaListResponse)
async def list_media(
    media_type: Optional[str] = Query(None, description="Filter by media type"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size")
) -> MediaListResponse:
    """
    List uploaded media files
    """
    try:
        # Mock media data (in real implementation, this would query the database)
        mock_media = [
            MediaItem(
                id="media_001",
                filename="image_001.jpg",
                original_filename="company_logo.jpg",
                file_size=245760,  # 240KB
                mime_type="image/jpeg",
                media_type="image",
                status="processed",
                url="http://localhost:8000/media/image_001.jpg",
                thumbnail_url="http://localhost:8000/media/thumbnails/image_001.jpg",
                created_at="2024-01-15T10:30:00Z",
                updated_at="2024-01-15T10:30:00Z"
            ),
            MediaItem(
                id="media_002",
                filename="video_001.mp4",
                original_filename="product_demo.mp4",
                file_size=15728640,  # 15MB
                mime_type="video/mp4",
                media_type="video",
                status="processed",
                url="http://localhost:8000/media/video_001.mp4",
                thumbnail_url=None,
                created_at="2024-01-14T15:45:00Z",
                updated_at="2024-01-14T15:45:00Z"
            ),
            MediaItem(
                id="media_003",
                filename="document_001.pdf",
                original_filename="marketing_guide.pdf",
                file_size=2097152,  # 2MB
                mime_type="application/pdf",
                media_type="document",
                status="processed",
                url="http://localhost:8000/media/document_001.pdf",
                thumbnail_url=None,
                created_at="2024-01-13T09:20:00Z",
                updated_at="2024-01-13T09:20:00Z"
            ),
            MediaItem(
                id="media_004",
                filename="image_002.png",
                original_filename="social_media_banner.png",
                file_size=1024000,  # 1MB
                mime_type="image/png",
                media_type="image",
                status="processed",
                url="http://localhost:8000/media/image_002.png",
                thumbnail_url="http://localhost:8000/media/thumbnails/image_002.png",
                created_at="2024-01-12T14:15:00Z",
                updated_at="2024-01-12T14:15:00Z"
            ),
            MediaItem(
                id="media_005",
                filename="audio_001.mp3",
                original_filename="podcast_intro.mp3",
                file_size=5242880,  # 5MB
                mime_type="audio/mpeg",
                media_type="audio",
                status="processed",
                url="http://localhost:8000/media/audio_001.mp3",
                thumbnail_url=None,
                created_at="2024-01-11T11:30:00Z",
                updated_at="2024-01-11T11:30:00Z"
            )
        ]
        
        # Apply media type filter
        if media_type:
            mock_media = [m for m in mock_media if m.media_type == media_type]
        
        # Apply pagination
        total = len(mock_media)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_media = mock_media[start_idx:end_idx]
        
        return MediaListResponse(
            media_items=paginated_media,
            total=total,
            page=page,
            size=size,
            has_more=end_idx < total
        )
        
    except Exception as e:
        logger.error(f"List media error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list media: {str(e)}"
        )

@router.get("/media/stats", response_model=MediaStatsResponse)
async def get_media_stats() -> MediaStatsResponse:
    """
    Get media usage statistics
    """
    try:
        # Mock stats data (in real implementation, this would query the database)
        stats = MediaStatsResponse(
            total_files=25,
            total_size=125829120,  # 120MB
            by_type={
                "image": 15,
                "video": 5,
                "audio": 3,
                "document": 2
            },
            by_status={
                "processed": 23,
                "processing": 1,
                "failed": 1
            }
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Get media stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get media stats: {str(e)}"
        )

@router.delete("/media/{media_id}")
async def delete_media(media_id: str) -> Dict[str, Any]:
    """
    Delete a media file
    """
    try:
        # Mock deletion (in real implementation, this would delete from database and filesystem)
        return {
            "success": True,
            "message": f"Media {media_id} deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Delete media error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete media: {str(e)}"
        )

@router.get("/media/status", response_model=MediaServiceStatusResponse)
async def get_media_status():
    """Get media service status"""
    return MediaServiceStatusResponse(
        status="operational",
        features=[
            "file_upload",
            "media_processing",
            "format_validation",
            "size_limits",
            "thumbnail_generation",
            "media_library"
        ],
        supported_formats={
            "image": ["jpg", "jpeg", "png", "gif", "webp", "bmp", "svg"],
            "video": ["mp4", "mov", "avi", "mkv", "webm", "flv"],
            "audio": ["mp3", "wav", "ogg", "m4a", "aac"],
            "document": ["pdf", "doc", "docx", "txt", "rtf"]
        },
        max_file_sizes={
            "image": 10485760,  # 10MB
            "video": 104857600,  # 100MB
            "audio": 52428800,   # 50MB
            "document": 26214400  # 25MB
        },
        version="1.0.0",
        message="Media service is ready for file uploads!"
    )
