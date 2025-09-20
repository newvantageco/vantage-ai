"""
AI Content Models
Handles AI content generation, optimization, and batch processing
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class AIRequest(Base):
    __tablename__ = "ai_requests"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Request details
    prompt = Column(Text, nullable=False)
    brand_guide_id = Column(Integer, ForeignKey("brand_guides.id"), nullable=True)
    locale = Column(String(10), default="en-US")
    
    # AI response
    generated_text = Column(Text, nullable=True)
    provider = Column(String(50), nullable=True)  # openai, ollama, etc.
    model = Column(String(100), nullable=True)  # gpt-4o-mini, llama3.1, etc.
    
    # Token usage
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    
    # Cost tracking
    cost_usd = Column(Float, default=0.0)
    
    # Status
    status = Column(String(20), default="pending")  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("UserAccount")
    brand_guide = relationship("BrandGuide")


class AIBatchJob(Base):
    __tablename__ = "ai_batch_jobs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Job details
    job_id = Column(String(100), unique=True, nullable=False, index=True)
    prompts = Column(JSON, nullable=False)  # Array of prompts
    brand_guide_id = Column(Integer, ForeignKey("brand_guides.id"), nullable=True)
    locale = Column(String(10), default="en-US")
    
    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    total_prompts = Column(Integer, nullable=False)
    completed_prompts = Column(Integer, default=0)
    failed_prompts = Column(Integer, default=0)
    
    # Results
    results = Column(JSON, nullable=True)  # Array of generated texts
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("UserAccount")
    brand_guide = relationship("BrandGuide")


class AIOptimization(Base):
    __tablename__ = "ai_optimizations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Input
    platform = Column(String(50), nullable=False)  # facebook, instagram, linkedin, etc.
    draft_content = Column(Text, nullable=False)
    brand_guide_id = Column(Integer, ForeignKey("brand_guides.id"), nullable=True)
    
    # Output
    optimized_text = Column(Text, nullable=True)
    constraints_applied = Column(JSON, nullable=True)  # Platform-specific constraints
    character_count = Column(Integer, nullable=True)
    hashtag_count = Column(Integer, nullable=True)
    
    # Status
    status = Column(String(20), default="pending")  # pending, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("UserAccount")
    brand_guide = relationship("BrandGuide")
