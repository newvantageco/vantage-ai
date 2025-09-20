"""
Simple Content Library API
A minimal content library endpoint that works with existing infrastructure
"""

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid

router = APIRouter()

# --- Schemas for API Requests/Responses ---
class ContentItem(BaseModel):
    id: str
    title: str
    content: str
    content_type: str  # text, image, video, carousel
    status: str  # draft, scheduled, published, archived
    tags: List[str] = []
    hashtags: List[str] = []
    mentions: List[str] = []
    media_urls: List[str] = []
    platform_content: Dict[str, str] = {}  # Platform-specific variations
    created_at: str
    updated_at: str
    published_at: Optional[str] = None
    created_by: str
    campaign_id: Optional[str] = None

class ContentCreateRequest(BaseModel):
    title: str
    content: str
    content_type: str = "text"
    tags: List[str] = []
    hashtags: List[str] = []
    mentions: List[str] = []
    media_urls: List[str] = []
    platform_content: Dict[str, str] = {}
    campaign_id: Optional[str] = None

class ContentUpdateRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    content_type: Optional[str] = None
    tags: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    media_urls: Optional[List[str]] = None
    platform_content: Optional[Dict[str, str]] = None
    status: Optional[str] = None

class ContentListResponse(BaseModel):
    content_items: List[ContentItem]
    total: int
    page: int
    size: int
    has_more: bool

class ContentStatsResponse(BaseModel):
    total_content: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_campaign: Dict[str, int]
    recent_activity: List[Dict[str, Any]]

class ContentTemplate(BaseModel):
    id: str
    name: str
    description: str
    content_template: str
    tags: List[str] = []
    content_type: str = "text"
    created_at: str
    usage_count: int = 0

class ContentLibraryStatusResponse(BaseModel):
    status: str
    features: List[str]
    content_types: List[str]
    statuses: List[str]
    version: str
    message: Optional[str] = None

# --- Helper Functions ---
def generate_mock_content() -> List[ContentItem]:
    """Generate mock content data"""
    return [
        ContentItem(
            id="content_001",
            title="Welcome to VANTAGE AI",
            content="🚀 Exciting news! We're launching our new AI-powered marketing platform that helps businesses automate their content creation and optimize their social media presence. #AI #Marketing #Automation #SocialMedia #VantageAI",
            content_type="text",
            status="published",
            tags=["announcement", "launch", "ai"],
            hashtags=["#AI", "#Marketing", "#Automation", "#SocialMedia", "#VantageAI"],
            mentions=[],
            media_urls=["http://localhost:8000/media/image_001.jpg"],
            platform_content={
                "facebook": "🚀 Exciting news! We're launching our new AI-powered marketing platform...",
                "linkedin": "💼 Professional insights: How AI is changing the marketing landscape...",
                "instagram": "📱 Transform your social media strategy with AI..."
            },
            created_at="2024-01-15T10:30:00Z",
            updated_at="2024-01-15T10:30:00Z",
            published_at="2024-01-15T10:30:00Z",
            created_by="admin@vantage.ai",
            campaign_id="campaign_001"
        ),
        ContentItem(
            id="content_002",
            title="AI Content Generation Tips",
            content="💡 Pro tip: Use specific prompts to get better AI-generated content. Instead of 'write a post about our product', try 'write an engaging social media post about our new AI marketing tool, highlighting time-saving benefits for small businesses' #ContentCreation #AITips",
            content_type="text",
            status="draft",
            tags=["tips", "ai", "content-creation"],
            hashtags=["#ContentCreation", "#AITips"],
            mentions=[],
            media_urls=[],
            platform_content={},
            created_at="2024-01-14T15:45:00Z",
            updated_at="2024-01-14T15:45:00Z",
            published_at=None,
            created_by="admin@vantage.ai",
            campaign_id=None
        ),
        ContentItem(
            id="content_003",
            title="Social Media Analytics Dashboard",
            content="📊 Our new analytics dashboard gives you real-time insights into your social media performance. Track engagement, reach, and conversions across all platforms. #Analytics #SocialMedia #DataDriven",
            content_type="text",
            status="scheduled",
            tags=["analytics", "dashboard", "insights"],
            hashtags=["#Analytics", "#SocialMedia", "#DataDriven"],
            mentions=[],
            media_urls=["http://localhost:8000/media/image_002.png"],
            platform_content={
                "facebook": "📊 Our new analytics dashboard gives you real-time insights...",
                "linkedin": "📈 Data-driven marketing: How analytics can transform your strategy...",
                "twitter": "📊 Real-time social media insights at your fingertips..."
            },
            created_at="2024-01-13T09:20:00Z",
            updated_at="2024-01-13T09:20:00Z",
            published_at=None,
            created_by="admin@vantage.ai",
            campaign_id="campaign_002"
        ),
        ContentItem(
            id="content_004",
            title="Team Collaboration Features",
            content="👥 Working with a team? Our collaboration features let you share content drafts, leave feedback, and approve posts before they go live. Perfect for agencies and marketing teams! #TeamWork #Collaboration #Marketing",
            content_type="text",
            status="published",
            tags=["collaboration", "team", "workflow"],
            hashtags=["#TeamWork", "#Collaboration", "#Marketing"],
            mentions=[],
            media_urls=[],
            platform_content={},
            created_at="2024-01-12T14:15:00Z",
            updated_at="2024-01-12T14:15:00Z",
            published_at="2024-01-12T14:15:00Z",
            created_by="admin@vantage.ai",
            campaign_id="campaign_001"
        ),
        ContentItem(
            id="content_005",
            title="Content Scheduling Made Easy",
            content="⏰ Schedule your posts for optimal engagement times. Our AI analyzes your audience behavior to suggest the best times to post. Set it and forget it! #Scheduling #Automation #SocialMedia",
            content_type="text",
            status="archived",
            tags=["scheduling", "automation", "timing"],
            hashtags=["#Scheduling", "#Automation", "#SocialMedia"],
            mentions=[],
            media_urls=[],
            platform_content={},
            created_at="2024-01-11T11:30:00Z",
            updated_at="2024-01-11T11:30:00Z",
            published_at="2024-01-11T11:30:00Z",
            created_by="admin@vantage.ai",
            campaign_id=None
        )
    ]

def generate_mock_templates() -> List[ContentTemplate]:
    """Generate mock content templates"""
    return [
        ContentTemplate(
            id="template_001",
            name="Product Launch Announcement",
            description="Template for announcing new products or features",
            content_template="🚀 Exciting news! We're launching {product_name} - {product_description}. {key_benefits}. #ProductLaunch #Innovation",
            tags=["product", "launch", "announcement"],
            content_type="text",
            created_at="2024-01-10T10:00:00Z",
            usage_count=15
        ),
        ContentTemplate(
            id="template_002",
            name="Behind the Scenes",
            description="Template for sharing behind-the-scenes content",
            content_template="📸 Behind the scenes: {behind_scenes_description}. {team_insight}. #BehindTheScenes #TeamWork",
            tags=["behind-scenes", "team", "culture"],
            content_type="text",
            created_at="2024-01-09T14:30:00Z",
            usage_count=8
        ),
        ContentTemplate(
            id="template_003",
            name="Educational Tip",
            description="Template for sharing educational content and tips",
            content_template="💡 Pro tip: {tip_description}. {explanation}. {call_to_action}. #Tips #Education #{industry}",
            tags=["education", "tips", "helpful"],
            content_type="text",
            created_at="2024-01-08T09:15:00Z",
            usage_count=23
        )
    ]

# --- API Endpoints ---

@router.post("/content/create", response_model=ContentItem, status_code=status.HTTP_201_CREATED)
async def create_content(request: ContentCreateRequest) -> ContentItem:
    """
    Create a new content item
    """
    try:
        # Generate unique ID
        content_id = f"content_{int(datetime.utcnow().timestamp())}"
        
        # Create content item
        content_item = ContentItem(
            id=content_id,
            title=request.title,
            content=request.content,
            content_type=request.content_type,
            status="draft",
            tags=request.tags,
            hashtags=request.hashtags,
            mentions=request.mentions,
            media_urls=request.media_urls,
            platform_content=request.platform_content,
            created_at=datetime.utcnow().isoformat() + "Z",
            updated_at=datetime.utcnow().isoformat() + "Z",
            published_at=None,
            created_by="admin@vantage.ai",
            campaign_id=request.campaign_id
        )
        
        return content_item
        
    except Exception as e:
        logger.error(f"Create content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create content: {str(e)}"
        )

@router.get("/content/list", response_model=ContentListResponse)
async def list_content(
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign"),
    search: Optional[str] = Query(None, description="Search in title and content"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size")
) -> ContentListResponse:
    """
    List content items with filtering and pagination
    """
    try:
        # Get mock content
        mock_content = generate_mock_content()
        
        # Apply filters
        filtered_content = mock_content
        
        if status_filter:
            filtered_content = [c for c in filtered_content if c.status == status_filter]
        
        if content_type:
            filtered_content = [c for c in filtered_content if c.content_type == content_type]
        
        if campaign_id:
            filtered_content = [c for c in filtered_content if c.campaign_id == campaign_id]
        
        if search:
            search_lower = search.lower()
            filtered_content = [
                c for c in filtered_content 
                if search_lower in c.title.lower() or search_lower in c.content.lower()
            ]
        
        # Apply pagination
        total = len(filtered_content)
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        paginated_content = filtered_content[start_idx:end_idx]
        
        return ContentListResponse(
            content_items=paginated_content,
            total=total,
            page=page,
            size=size,
            has_more=end_idx < total
        )
        
    except Exception as e:
        logger.error(f"List content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list content: {str(e)}"
        )

@router.get("/content/{content_id}", response_model=ContentItem)
async def get_content(content_id: str) -> ContentItem:
    """
    Get a specific content item
    """
    try:
        # Get mock content
        mock_content = generate_mock_content()
        
        # Find content by ID
        content_item = next((c for c in mock_content if c.id == content_id), None)
        
        if not content_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content {content_id} not found"
            )
        
        return content_item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content: {str(e)}"
        )

@router.put("/content/{content_id}", response_model=ContentItem)
async def update_content(content_id: str, request: ContentUpdateRequest) -> ContentItem:
    """
    Update a content item
    """
    try:
        # Get mock content
        mock_content = generate_mock_content()
        
        # Find content by ID
        content_item = next((c for c in mock_content if c.id == content_id), None)
        
        if not content_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Content {content_id} not found"
            )
        
        # Update fields
        if request.title is not None:
            content_item.title = request.title
        if request.content is not None:
            content_item.content = request.content
        if request.content_type is not None:
            content_item.content_type = request.content_type
        if request.tags is not None:
            content_item.tags = request.tags
        if request.hashtags is not None:
            content_item.hashtags = request.hashtags
        if request.mentions is not None:
            content_item.mentions = request.mentions
        if request.media_urls is not None:
            content_item.media_urls = request.media_urls
        if request.platform_content is not None:
            content_item.platform_content = request.platform_content
        if request.status is not None:
            content_item.status = request.status
        
        # Update timestamp
        content_item.updated_at = datetime.utcnow().isoformat() + "Z"
        
        return content_item
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update content: {str(e)}"
        )

@router.delete("/content/{content_id}")
async def delete_content(content_id: str) -> Dict[str, Any]:
    """
    Delete a content item
    """
    try:
        # Mock deletion (in real implementation, this would delete from database)
        return {
            "success": True,
            "message": f"Content {content_id} deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Delete content error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete content: {str(e)}"
        )

@router.get("/content/stats", response_model=ContentStatsResponse)
async def get_content_stats() -> ContentStatsResponse:
    """
    Get content statistics
    """
    try:
        # Get mock content
        mock_content = generate_mock_content()
        
        # Calculate stats
        by_status = {}
        by_type = {}
        by_campaign = {}
        
        for content in mock_content:
            # By status
            by_status[content.status] = by_status.get(content.status, 0) + 1
            
            # By type
            by_type[content.content_type] = by_type.get(content.content_type, 0) + 1
            
            # By campaign
            campaign = content.campaign_id or "No Campaign"
            by_campaign[campaign] = by_campaign.get(campaign, 0) + 1
        
        # Recent activity
        recent_activity = [
            {
                "action": "created",
                "content_id": "content_001",
                "title": "Welcome to VANTAGE AI",
                "timestamp": "2024-01-15T10:30:00Z",
                "user": "admin@vantage.ai"
            },
            {
                "action": "updated",
                "content_id": "content_002",
                "title": "AI Content Generation Tips",
                "timestamp": "2024-01-14T15:45:00Z",
                "user": "admin@vantage.ai"
            },
            {
                "action": "published",
                "content_id": "content_004",
                "title": "Team Collaboration Features",
                "timestamp": "2024-01-12T14:15:00Z",
                "user": "admin@vantage.ai"
            }
        ]
        
        return ContentStatsResponse(
            total_content=len(mock_content),
            by_status=by_status,
            by_type=by_type,
            by_campaign=by_campaign,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        logger.error(f"Get content stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get content stats: {str(e)}"
        )

@router.get("/content/templates", response_model=List[ContentTemplate])
async def get_content_templates() -> List[ContentTemplate]:
    """
    Get available content templates
    """
    try:
        return generate_mock_templates()
        
    except Exception as e:
        logger.error(f"Get templates error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get templates: {str(e)}"
        )

@router.get("/content/status", response_model=ContentLibraryStatusResponse)
async def get_content_library_status():
    """Get content library service status"""
    return ContentLibraryStatusResponse(
        status="operational",
        features=[
            "content_creation",
            "content_editing",
            "content_organization",
            "content_templates",
            "content_search",
            "content_analytics",
            "version_control"
        ],
        content_types=["text", "image", "video", "carousel"],
        statuses=["draft", "scheduled", "published", "archived"],
        version="1.0.0",
        message="Content library service is ready for content management!"
    )
