from __future__ import annotations

from datetime import datetime
from typing import Optional, List
import json

from sqlalchemy import String, Text, DateTime, ForeignKey, Integer, Float, Boolean, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class DocumentStore(Base):
    """Knowledge base documents with vector embeddings."""
    __tablename__ = "document_store"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Document content
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Document metadata
    document_type: Mapped[str] = mapped_column(String(50), default="general", nullable=False)  # faq, policy, guide, etc.
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # URL, file name, etc.
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of tags
    
    # Vector embedding (1536 dimensions for OpenAI text-embedding-ada-002)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(1536), nullable=True)
    
    # Processing status
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Usage tracking
    query_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_queried_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_document_store_org_id", "org_id"),
        Index("ix_document_store_document_type", "document_type"),
        Index("ix_document_store_is_processed", "is_processed"),
        Index("ix_document_store_created_at", "created_at"),
        # Vector similarity search index
        Index("ix_document_store_embedding", "embedding", postgresql_using="ivfflat"),
    )

    def get_tags(self) -> List[str]:
        """Get tags as a list."""
        if not self.tags:
            return []
        try:
            return json.loads(self.tags)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_tags(self, tags: List[str]) -> None:
        """Set tags from a list."""
        self.tags = json.dumps(tags)

    def add_tag(self, tag: str) -> None:
        """Add a single tag."""
        tags = self.get_tags()
        if tag not in tags:
            tags.append(tag)
            self.set_tags(tags)

    def remove_tag(self, tag: str) -> None:
        """Remove a single tag."""
        tags = self.get_tags()
        if tag in tags:
            tags.remove(tag)
            self.set_tags(tags)

    def record_query(self) -> None:
        """Record that this document was queried."""
        self.query_count += 1
        self.last_queried_at = datetime.utcnow()


class KnowledgeQuery(Base):
    """Track knowledge base queries for analytics."""
    __tablename__ = "knowledge_queries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    # Query details
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[str] = mapped_column(String(50), default="search", nullable=False)  # search, suggestion, etc.
    
    # Results
    results_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    results_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of result IDs
    
    # Performance
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Context
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Where the query came from
    session_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_knowledge_queries_org_id", "org_id"),
        Index("ix_knowledge_queries_user_id", "user_id"),
        Index("ix_knowledge_queries_query_type", "query_type"),
        Index("ix_knowledge_queries_created_at", "created_at"),
        Index("ix_knowledge_queries_session_id", "session_id"),
    )

    def get_results(self) -> List[str]:
        """Get results as a list of document IDs."""
        if not self.results_json:
            return []
        try:
            return json.loads(self.results_json)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_results(self, result_ids: List[str]) -> None:
        """Set results from a list of document IDs."""
        self.results_json = json.dumps(result_ids)
        self.results_count = len(result_ids)


class KnowledgeSuggestion(Base):
    """AI-generated suggestions based on knowledge base."""
    __tablename__ = "knowledge_suggestions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    
    # Suggestion context
    context_type: Mapped[str] = mapped_column(String(50), nullable=False)  # inbox_reply, content_creation, etc.
    context_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # ID of the context object
    
    # Suggestion content
    suggestion_text: Mapped[str] = mapped_column(Text, nullable=False)
    suggestion_type: Mapped[str] = mapped_column(String(50), nullable=False)  # response, content, action, etc.
    
    # Related documents
    related_doc_ids: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of document IDs
    
    # User feedback
    is_helpful: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    feedback_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    feedback_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_knowledge_suggestions_org_id", "org_id"),
        Index("ix_knowledge_suggestions_user_id", "user_id"),
        Index("ix_knowledge_suggestions_context_type", "context_type"),
        Index("ix_knowledge_suggestions_context_id", "context_id"),
        Index("ix_knowledge_suggestions_created_at", "created_at"),
    )

    def get_related_docs(self) -> List[str]:
        """Get related document IDs as a list."""
        if not self.related_doc_ids:
            return []
        try:
            return json.loads(self.related_doc_ids)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_related_docs(self, doc_ids: List[str]) -> None:
        """Set related document IDs from a list."""
        self.related_doc_ids = json.dumps(doc_ids)


class KnowledgeConfig(Base):
    """Configuration for knowledge base features."""
    __tablename__ = "knowledge_config"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, unique=True)
    
    # Embedding settings
    embedding_model: Mapped[str] = mapped_column(String(100), default="text-embedding-ada-002", nullable=False)
    embedding_dimensions: Mapped[int] = mapped_column(Integer, default=1536, nullable=False)
    
    # Search settings
    similarity_threshold: Mapped[float] = mapped_column(Float, default=0.7, nullable=False)
    max_results: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    
    # AI integration
    ai_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    auto_suggestions: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_knowledge_config_org_id", "org_id"),
    )


# Document types
class DocumentTypes:
    """Available document types for the knowledge base."""
    
    FAQ = "faq"
    POLICY = "policy"
    GUIDE = "guide"
    PROCEDURE = "procedure"
    TEMPLATE = "template"
    REFERENCE = "reference"
    GENERAL = "general"
    
    ALL_TYPES = [FAQ, POLICY, GUIDE, PROCEDURE, TEMPLATE, REFERENCE, GENERAL]
    
    @classmethod
    def validate_type(cls, doc_type: str) -> bool:
        """Validate that a document type is valid."""
        return doc_type in cls.ALL_TYPES


# Query types
class QueryTypes:
    """Available query types."""
    
    SEARCH = "search"
    SUGGESTION = "suggestion"
    AUTOCOMPLETE = "autocomplete"
    SIMILAR = "similar"
    
    ALL_TYPES = [SEARCH, SUGGESTION, AUTOCOMPLETE, SIMILAR]
    
    @classmethod
    def validate_type(cls, query_type: str) -> bool:
        """Validate that a query type is valid."""
        return query_type in cls.ALL_TYPES


# Suggestion types
class SuggestionTypes:
    """Available suggestion types."""
    
    RESPONSE = "response"
    CONTENT = "content"
    ACTION = "action"
    RESOURCE = "resource"
    
    ALL_TYPES = [RESPONSE, CONTENT, ACTION, RESOURCE]
    
    @classmethod
    def validate_type(cls, suggestion_type: str) -> bool:
        """Validate that a suggestion type is valid."""
        return suggestion_type in cls.ALL_TYPES
