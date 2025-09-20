"""
Content Collection Models
Handles content collections and organization
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, JSON, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base

# Association table for many-to-many relationship between collections and content
collection_content_association = Table(
    'collection_content_association',
    Base.metadata,
    Column('collection_id', Integer, ForeignKey('content_collections.id', ondelete='CASCADE'), primary_key=True),
    Column('content_id', Integer, ForeignKey('content_items.id', ondelete='CASCADE'), primary_key=True)
)


class ContentCollection(Base):
    """Content collection model for organizing content items"""
    __tablename__ = "content_collections"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    created_by_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False, index=True)
    
    # Collection details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Collection settings
    is_public = Column(Boolean, default=False, nullable=False)
    tags = Column(JSON, nullable=True)  # Array of tags for the collection
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="content_collections")
    created_by = relationship("UserAccount", back_populates="content_collections")
    content_items = relationship("ContentItem", secondary=collection_content_association, back_populates="collections")


class ContentCollectionShare(Base):
    """Content collection sharing model"""
    __tablename__ = "content_collection_shares"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("content_collections.id"), nullable=False, index=True)
    shared_with_user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False, index=True)
    shared_by_user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False, index=True)
    
    # Permission levels
    permission_level = Column(String(20), default="view", nullable=False)  # view, edit, admin
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    collection = relationship("ContentCollection")
    shared_with_user = relationship("UserAccount", foreign_keys=[shared_with_user_id])
    shared_by_user = relationship("UserAccount", foreign_keys=[shared_by_user_id])
