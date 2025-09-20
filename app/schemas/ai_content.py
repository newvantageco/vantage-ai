"""
AI Content Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AICompleteRequest(BaseModel):
    prompt: str = Field(..., description="The prompt for AI content generation")
    brand_guide_id: Optional[int] = Field(None, description="ID of the brand guide to use")
    locale: str = Field("en-US", description="Locale for content generation")


class AICompleteResponse(BaseModel):
    text: str = Field(..., description="Generated content text")
    token_usage: Dict[str, int] = Field(..., description="Token usage statistics")
    provider: str = Field(..., description="AI provider used")
    model: str = Field(..., description="AI model used")
    cost_usd: float = Field(0.0, description="Cost in USD")


class AIBatchRequest(BaseModel):
    prompts: List[str] = Field(..., max_items=50, description="Array of prompts (max 50)")
    brand_guide_id: Optional[int] = Field(None, description="ID of the brand guide to use")
    locale: str = Field("en-US", description="Locale for content generation")


class AIBatchResponse(BaseModel):
    job_id: str = Field(..., description="Job ID for tracking")
    status: str = Field(..., description="Job status")
    total_prompts: int = Field(..., description="Total number of prompts")
    status_url: str = Field(..., description="URL to check job status")


class AIOptimizeRequest(BaseModel):
    platform: str = Field(..., description="Target platform (facebook, instagram, etc.)")
    draft_content: str = Field(..., description="Draft content to optimize")
    brand_guide_id: Optional[int] = Field(None, description="ID of the brand guide to use")


class AIOptimizeResponse(BaseModel):
    optimized_text: str = Field(..., description="Optimized content text")
    constraints_applied: Dict[str, Any] = Field(..., description="Platform-specific constraints applied")
    character_count: int = Field(..., description="Character count")
    hashtag_count: int = Field(..., description="Hashtag count")
    platform: str = Field(..., description="Target platform")


class AIRequestResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    prompt: str
    brand_guide_id: Optional[int]
    locale: str
    generated_text: Optional[str]
    provider: Optional[str]
    model: Optional[str]
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class AIBatchJobResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    job_id: str
    prompts: List[str]
    brand_guide_id: Optional[int]
    locale: str
    status: str
    total_prompts: int
    completed_prompts: int
    failed_prompts: int
    results: Optional[List[str]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class AIOptimizationResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    platform: str
    draft_content: str
    brand_guide_id: Optional[int]
    optimized_text: Optional[str]
    constraints_applied: Optional[Dict[str, Any]]
    character_count: Optional[int]
    hashtag_count: Optional[int]
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
