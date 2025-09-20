"""
Content Library Service
Handles content storage, search, filtering, and organization
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc
from sqlalchemy.orm import joinedload
import logging

from app.models.cms import ContentItem, Campaign, BrandGuide, UserAccount, Organization
from app.models.content_collection import ContentCollection, ContentCollectionShare
from app.schemas.content_library import (
    ContentLibrarySearchRequest, ContentLibrarySearchResponse,
    ContentLibraryFilter, ContentLibrarySort, ContentLibraryItem,
    ContentLibraryStats, ContentLibraryCollection
)

logger = logging.getLogger(__name__)

class ContentLibraryService:
    """Service for managing content library operations"""
    
    def __init__(self):
        pass
    
    async def search_content(
        self,
        search_request: ContentLibrarySearchRequest,
        organization_id: int,
        db: Session
    ) -> ContentLibrarySearchResponse:
        """Search and filter content in the library"""
        try:
            # Build base query
            query = db.query(ContentItem).filter(
                ContentItem.organization_id == organization_id
            )
            
            # Apply filters
            query = self._apply_filters(query, search_request.filters)
            
            # Apply search
            if search_request.query:
                query = self._apply_search(query, search_request.query)
            
            # Apply sorting
            query = self._apply_sorting(query, search_request.sort)
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply pagination
            offset = (search_request.page - 1) * search_request.size
            query = query.offset(offset).limit(search_request.size)
            
            # Load relationships
            query = query.options(
                joinedload(ContentItem.campaign),
                joinedload(ContentItem.brand_guide),
                joinedload(ContentItem.created_by),
                joinedload(ContentItem.media_items)
            )
            
            # Execute query
            content_items = query.all()
            
            # Convert to response format
            items = []
            for item in content_items:
                items.append(ContentLibraryItem(
                    id=item.id,
                    title=item.title,
                    content=item.content,
                    content_type=item.content_type,
                    status=item.status,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                    published_at=item.published_at,
                    created_by=item.created_by.first_name + " " + item.created_by.last_name if item.created_by else "Unknown",
                    campaign_name=item.campaign.name if item.campaign else None,
                    brand_guide_name=item.brand_guide.name if item.brand_guide else None,
                    tags=item.tags or [],
                    media_count=len(item.media_items) if item.media_items else 0,
                    hashtags=item.hashtags or [],
                    mentions=item.mentions or []
                ))
            
            # Calculate pagination info
            total_pages = (total_count + search_request.size - 1) // search_request.size
            
            return ContentLibrarySearchResponse(
                items=items,
                total=total_count,
                page=search_request.page,
                size=search_request.size,
                total_pages=total_pages,
                filters_applied=len([f for f in search_request.filters if f.value is not None]),
                search_query=search_request.query
            )
            
        except Exception as e:
            logger.error(f"Content library search failed: {str(e)}")
            raise
    
    def _apply_filters(self, query, filters: List[ContentLibraryFilter]):
        """Apply filters to the query"""
        for filter_item in filters:
            if filter_item.value is None:
                continue
                
            if filter_item.field == "status":
                query = query.filter(ContentItem.status == filter_item.value)
            elif filter_item.field == "content_type":
                query = query.filter(ContentItem.content_type == filter_item.value)
            elif filter_item.field == "campaign_id":
                query = query.filter(ContentItem.campaign_id == filter_item.value)
            elif filter_item.field == "brand_guide_id":
                query = query.filter(ContentItem.brand_guide_id == filter_item.value)
            elif filter_item.field == "created_by_id":
                query = query.filter(ContentItem.created_by_id == filter_item.value)
            elif filter_item.field == "created_after":
                query = query.filter(ContentItem.created_at >= filter_item.value)
            elif filter_item.field == "created_before":
                query = query.filter(ContentItem.created_at <= filter_item.value)
            elif filter_item.field == "published_after":
                query = query.filter(ContentItem.published_at >= filter_item.value)
            elif filter_item.field == "published_before":
                query = query.filter(ContentItem.published_at <= filter_item.value)
            elif filter_item.field == "has_tags":
                query = query.filter(ContentItem.tags.contains(filter_item.value))
            elif filter_item.field == "has_hashtags":
                query = query.filter(ContentItem.hashtags.contains(filter_item.value))
            elif filter_item.field == "has_mentions":
                query = query.filter(ContentItem.mentions.contains(filter_item.value))
        
        return query
    
    def _apply_search(self, query, search_query: str):
        """Apply search query to the query"""
        search_terms = search_query.split()
        
        for term in search_terms:
            term = f"%{term}%"
            query = query.filter(
                or_(
                    ContentItem.title.ilike(term),
                    ContentItem.content.ilike(term),
                    ContentItem.tags.cast(str).ilike(term),
                    ContentItem.hashtags.cast(str).ilike(term),
                    ContentItem.mentions.cast(str).ilike(term)
                )
            )
        
        return query
    
    def _apply_sorting(self, query, sort: Optional[ContentLibrarySort]):
        """Apply sorting to the query"""
        if not sort:
            return query.order_by(desc(ContentItem.created_at))
        
        field = getattr(ContentItem, sort.field, None)
        if not field:
            return query.order_by(desc(ContentItem.created_at))
        
        if sort.direction == "asc":
            return query.order_by(asc(field))
        else:
            return query.order_by(desc(field))
    
    async def get_content_stats(
        self,
        organization_id: int,
        db: Session
    ) -> ContentLibraryStats:
        """Get content library statistics"""
        try:
            # Total content count
            total_content = db.query(ContentItem).filter(
                ContentItem.organization_id == organization_id
            ).count()
            
            # Content by status
            status_counts = db.query(
                ContentItem.status,
                func.count(ContentItem.id)
            ).filter(
                ContentItem.organization_id == organization_id
            ).group_by(ContentItem.status).all()
            
            status_breakdown = {status: count for status, count in status_counts}
            
            # Content by type
            type_counts = db.query(
                ContentItem.content_type,
                func.count(ContentItem.id)
            ).filter(
                ContentItem.organization_id == organization_id
            ).group_by(ContentItem.content_type).all()
            
            type_breakdown = {content_type: count for content_type, count in type_counts}
            
            # Recent activity (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_content = db.query(ContentItem).filter(
                ContentItem.organization_id == organization_id,
                ContentItem.created_at >= thirty_days_ago
            ).count()
            
            # Published content (last 30 days)
            recent_published = db.query(ContentItem).filter(
                ContentItem.organization_id == organization_id,
                ContentItem.published_at >= thirty_days_ago
            ).count()
            
            # Most active creators
            creator_counts = db.query(
                UserAccount.first_name,
                UserAccount.last_name,
                func.count(ContentItem.id)
            ).join(ContentItem).filter(
                ContentItem.organization_id == organization_id
            ).group_by(
                UserAccount.id, UserAccount.first_name, UserAccount.last_name
            ).order_by(desc(func.count(ContentItem.id))).limit(5).all()
            
            top_creators = [
                {"name": f"{first} {last}", "count": count}
                for first, last, count in creator_counts
            ]
            
            return ContentLibraryStats(
                total_content=total_content,
                status_breakdown=status_breakdown,
                type_breakdown=type_breakdown,
                recent_content=recent_content,
                recent_published=recent_published,
                top_creators=top_creators
            )
            
        except Exception as e:
            logger.error(f"Content library stats failed: {str(e)}")
            raise
    
    async def create_collection(
        self,
        name: str,
        description: Optional[str],
        content_ids: List[int],
        organization_id: int,
        user_id: int,
        db: Session
    ) -> ContentLibraryCollection:
        """Create a content collection"""
        try:
            # Create the collection
            collection = ContentCollection(
                name=name,
                description=description,
                organization_id=organization_id,
                created_by_id=user_id
            )
            
            db.add(collection)
            db.commit()
            db.refresh(collection)
            
            # Add content items to collection
            if content_ids:
                content_items = db.query(ContentItem).filter(
                    ContentItem.id.in_(content_ids),
                    ContentItem.organization_id == organization_id
                ).all()
                
                for content_item in content_items:
                    collection.content_items.append(content_item)
                
                db.commit()
            
            # Return the collection with content count
            content_count = len(collection.content_items)
            content_ids_list = [item.id for item in collection.content_items]
            
            return ContentLibraryCollection(
                id=collection.id,
                name=collection.name,
                description=collection.description,
                content_count=content_count,
                created_by_id=collection.created_by_id,
                created_at=collection.created_at,
                content_ids=content_ids_list
            )
            
        except Exception as e:
            logger.error(f"Collection creation failed: {str(e)}")
            db.rollback()
            raise
    
    async def get_collections(
        self,
        organization_id: int,
        db: Session
    ) -> List[ContentLibraryCollection]:
        """Get all collections for an organization"""
        try:
            collections = db.query(ContentCollection).filter(
                ContentCollection.organization_id == organization_id
            ).options(
                joinedload(ContentCollection.content_items)
            ).all()
            
            result = []
            for collection in collections:
                content_ids = [item.id for item in collection.content_items]
                result.append(ContentLibraryCollection(
                    id=collection.id,
                    name=collection.name,
                    description=collection.description,
                    content_count=len(collection.content_items),
                    created_by_id=collection.created_by_id,
                    created_at=collection.created_at,
                    content_ids=content_ids
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Collection retrieval failed: {str(e)}")
            raise
    
    async def add_to_collection(
        self,
        collection_id: int,
        content_ids: List[int],
        organization_id: int,
        db: Session
    ) -> bool:
        """Add content items to a collection"""
        try:
            # Get the collection
            collection = db.query(ContentCollection).filter(
                ContentCollection.id == collection_id,
                ContentCollection.organization_id == organization_id
            ).first()
            
            if not collection:
                return False
            
            # Get content items
            content_items = db.query(ContentItem).filter(
                ContentItem.id.in_(content_ids),
                ContentItem.organization_id == organization_id
            ).all()
            
            # Add to collection
            for content_item in content_items:
                if content_item not in collection.content_items:
                    collection.content_items.append(content_item)
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Add to collection failed: {str(e)}")
            db.rollback()
            raise
    
    async def remove_from_collection(
        self,
        collection_id: int,
        content_ids: List[int],
        organization_id: int,
        db: Session
    ) -> bool:
        """Remove content items from a collection"""
        try:
            # Get the collection
            collection = db.query(ContentCollection).filter(
                ContentCollection.id == collection_id,
                ContentCollection.organization_id == organization_id
            ).first()
            
            if not collection:
                return False
            
            # Get content items to remove
            content_items = db.query(ContentItem).filter(
                ContentItem.id.in_(content_ids),
                ContentItem.organization_id == organization_id
            ).all()
            
            # Remove from collection
            for content_item in content_items:
                if content_item in collection.content_items:
                    collection.content_items.remove(content_item)
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Remove from collection failed: {str(e)}")
            db.rollback()
            raise
