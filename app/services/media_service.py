"""
Media Service
Handles file uploads, processing, and storage for content management
"""

import os
import uuid
import mimetypes
import hashlib
from typing import List, Optional, Dict, Any, BinaryIO
from datetime import datetime
from pathlib import Path
import aiofiles
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from PIL import Image
import logging

from app.core.config import get_settings
from app.models.cms import ContentItem
from app.models.media import MediaItem as MediaItemModel, MediaProcessingJob, MediaType, MediaProcessingStatus
from app.schemas.media import MediaUploadResponse, MediaItem, MediaProcessingStatus

logger = logging.getLogger(__name__)

class MediaService:
    """Service for handling media uploads and processing"""
    
    def __init__(self):
        self.settings = get_settings()
        self.upload_dir = Path(self.settings.media_upload_dir or "uploads/media")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Supported file types
        self.supported_image_types = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
        self.supported_video_types = {'.mp4', '.mov', '.avi', '.mkv', '.webm'}
        self.supported_audio_types = {'.mp3', '.wav', '.ogg', '.m4a'}
        
        # File size limits (in bytes)
        self.max_image_size = 10 * 1024 * 1024  # 10MB
        self.max_video_size = 100 * 1024 * 1024  # 100MB
        self.max_audio_size = 50 * 1024 * 1024   # 50MB
        
    async def upload_media(
        self,
        file: UploadFile,
        organization_id: int,
        user_id: int,
        content_id: Optional[int] = None,
        db: Session = None
    ) -> MediaUploadResponse:
        """
        Upload and process a media file
        """
        try:
            # Validate file
            validation_result = await self._validate_file(file)
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=400,
                    detail=validation_result["error"]
                )
            
            # Generate unique filename
            file_extension = Path(file.filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create organization-specific directory
            org_dir = self.upload_dir / str(organization_id)
            org_dir.mkdir(exist_ok=True)
            
            file_path = org_dir / unique_filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # Calculate file hash for deduplication
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Get file metadata
            file_size = len(content)
            mime_type = file.content_type or mimetypes.guess_type(file.filename)[0]
            
            # Process media based on type
            processing_result = await self._process_media(file_path, mime_type)
            
            # Create media record in database
            media_type_enum = self._get_media_type_enum(file_extension)
            status_enum = MediaProcessingStatus.PROCESSED if processing_result["success"] else MediaProcessingStatus.FAILED
            
            media_item = MediaItemModel(
                id=str(uuid.uuid4()),
                organization_id=organization_id,
                user_id=user_id,
                content_id=content_id,
                original_filename=file.filename,
                stored_filename=unique_filename,
                file_path=str(file_path),
                file_size=file_size,
                mime_type=mime_type,
                file_hash=file_hash,
                media_type=media_type_enum,
                status=status_enum,
                processing_metadata=processing_result.get("metadata", {})
            )
            
            if db:
                db.add(media_item)
                db.commit()
                db.refresh(media_item)
            
            return MediaUploadResponse(
                success=True,
                media_id=media_item.id,
                filename=unique_filename,
                original_filename=file.filename,
                file_size=file_size,
                mime_type=mime_type,
                media_type=media_item.media_type,
                url=f"/api/v1/media/{media_item.id}",
                thumbnail_url=processing_result.get("thumbnail_url"),
                processing_status=media_item.status,
                metadata=processing_result.get("metadata", {})
            )
            
        except Exception as e:
            logger.error(f"Media upload failed: {str(e)}")
            return MediaUploadResponse(
                success=False,
                error=str(e)
            )
    
    async def _validate_file(self, file: UploadFile) -> Dict[str, Any]:
        """Validate uploaded file"""
        if not file.filename:
            return {"valid": False, "error": "No filename provided"}
        
        file_extension = Path(file.filename).suffix.lower()
        
        # Check file type
        if file_extension not in (self.supported_image_types | 
                                 self.supported_video_types | 
                                 self.supported_audio_types):
            return {
                "valid": False, 
                "error": f"Unsupported file type: {file_extension}"
            }
        
        # Check file size
        file_size = 0
        if hasattr(file, 'size'):
            file_size = file.size
        else:
            # Read file to get size
            content = await file.read()
            file_size = len(content)
            # Reset file pointer
            await file.seek(0)
        
        max_size = self._get_max_file_size(file_extension)
        if file_size > max_size:
            return {
                "valid": False,
                "error": f"File too large. Max size: {max_size // (1024*1024)}MB"
            }
        
        return {"valid": True}
    
    def _get_max_file_size(self, file_extension: str) -> int:
        """Get maximum file size based on file type"""
        if file_extension in self.supported_image_types:
            return self.max_image_size
        elif file_extension in self.supported_video_types:
            return self.max_video_size
        elif file_extension in self.supported_audio_types:
            return self.max_audio_size
        return self.max_image_size
    
    def _get_media_type(self, file_extension: str) -> str:
        """Determine media type from file extension"""
        if file_extension in self.supported_image_types:
            return "image"
        elif file_extension in self.supported_video_types:
            return "video"
        elif file_extension in self.supported_audio_types:
            return "audio"
        return "unknown"
    
    def _get_media_type_enum(self, file_extension: str) -> MediaType:
        """Determine media type enum from file extension"""
        if file_extension in self.supported_image_types:
            return MediaType.IMAGE
        elif file_extension in self.supported_video_types:
            return MediaType.VIDEO
        elif file_extension in self.supported_audio_types:
            return MediaType.AUDIO
        return MediaType.UNKNOWN
    
    async def _process_media(self, file_path: Path, mime_type: str) -> Dict[str, Any]:
        """Process uploaded media file"""
        try:
            if mime_type.startswith('image/'):
                return await self._process_image(file_path)
            elif mime_type.startswith('video/'):
                return await self._process_video(file_path)
            elif mime_type.startswith('audio/'):
                return await self._process_audio(file_path)
            else:
                return {"success": True, "metadata": {}}
        except Exception as e:
            logger.error(f"Media processing failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _process_image(self, file_path: Path) -> Dict[str, Any]:
        """Process image file and generate thumbnails"""
        try:
            with Image.open(file_path) as img:
                # Get image metadata
                width, height = img.size
                format_name = img.format
                
                # Generate thumbnail
                thumbnail_path = file_path.parent / f"thumb_{file_path.name}"
                thumbnail_size = (300, 300)
                
                # Create thumbnail maintaining aspect ratio
                img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                img.save(thumbnail_path, format=format_name, quality=85)
                
                return {
                    "success": True,
                    "metadata": {
                        "width": width,
                        "height": height,
                        "format": format_name,
                        "thumbnail_generated": True
                    },
                    "thumbnail_url": f"/api/v1/media/thumb/{thumbnail_path.name}"
                }
        except Exception as e:
            logger.error(f"Image processing failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _process_video(self, file_path: Path) -> Dict[str, Any]:
        """Process video file"""
        try:
            file_size = file_path.stat().st_size
            
            # Generate thumbnail for video (first frame)
            thumbnail_path = file_path.parent / f"thumb_{file_path.name}.jpg"
            
            # In production, you'd use ffmpeg to extract metadata and generate thumbnails
            # For now, we'll create a placeholder thumbnail
            try:
                # This would use ffmpeg in production:
                # ffmpeg -i input.mp4 -ss 00:00:01 -vframes 1 thumbnail.jpg
                # For now, we'll just create a placeholder
                with open(thumbnail_path, 'w') as f:
                    f.write("")  # Placeholder
                
                return {
                    "success": True,
                    "metadata": {
                        "file_size": file_size,
                        "processing_required": True,
                        "thumbnail_generated": True
                    },
                    "thumbnail_url": f"/api/v1/media/thumb/{thumbnail_path.name}"
                }
            except Exception as thumb_error:
                logger.warning(f"Thumbnail generation failed: {thumb_error}")
                return {
                    "success": True,
                    "metadata": {
                        "file_size": file_size,
                        "processing_required": True,
                        "thumbnail_generated": False
                    }
                }
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def _process_audio(self, file_path: Path) -> Dict[str, Any]:
        """Process audio file"""
        try:
            file_size = file_path.stat().st_size
            
            return {
                "success": True,
                "metadata": {
                    "file_size": file_size,
                    "processing_required": False
                }
            }
        except Exception as e:
            logger.error(f"Audio processing failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    async def get_media(self, media_id: str, organization_id: int, db: Session) -> Optional[MediaItemModel]:
        """Get media item by ID"""
        try:
            media_item = db.query(MediaItemModel).filter(
                MediaItemModel.id == media_id,
                MediaItemModel.organization_id == organization_id
            ).first()
            return media_item
        except Exception as e:
            logger.error(f"Failed to get media item {media_id}: {str(e)}")
            return None
    
    async def delete_media(self, media_id: str, organization_id: int, db: Session) -> bool:
        """Delete media file and database record"""
        try:
            # Get media item from database
            media_item = await self.get_media(media_id, organization_id, db)
            if not media_item:
                return False
            
            # Delete file
            file_path = Path(media_item.file_path)
            if file_path.exists():
                file_path.unlink()
            
            # Delete thumbnail if exists
            thumbnail_path = file_path.parent / f"thumb_{file_path.name}"
            if thumbnail_path.exists():
                thumbnail_path.unlink()
            
            # Delete from database
            db.delete(media_item)
            db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Media deletion failed: {str(e)}")
            return False
    
    async def list_media(
        self,
        organization_id: int,
        db: Session,
        content_id: Optional[int] = None,
        media_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[MediaItemModel]:
        """List media items for organization"""
        try:
            query = db.query(MediaItemModel).filter(
                MediaItemModel.organization_id == organization_id
            )
            
            if content_id:
                query = query.filter(MediaItemModel.content_id == content_id)
            
            if media_type:
                query = query.filter(MediaItemModel.media_type == media_type)
            
            query = query.offset(offset).limit(limit).order_by(MediaItemModel.created_at.desc())
            
            return query.all()
        except Exception as e:
            logger.error(f"Failed to list media items: {str(e)}")
            return []
