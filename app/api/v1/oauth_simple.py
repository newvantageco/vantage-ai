"""
Simple OAuth Integration API
A minimal OAuth endpoint that works with existing infrastructure
"""

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import uuid

router = APIRouter()

# --- Schemas for API Requests/Responses ---
class OAuthPlatform(BaseModel):
    platform: str
    name: str
    description: str
    status: str  # connected, disconnected, error
    connected_at: Optional[str] = None
    expires_at: Optional[str] = None
    scopes: List[str] = []
    account_info: Optional[Dict[str, Any]] = None

class OAuthConnectionRequest(BaseModel):
    platform: str
    redirect_uri: str
    state: Optional[str] = None

class OAuthConnectionResponse(BaseModel):
    success: bool
    authorization_url: Optional[str] = None
    state: Optional[str] = None
    message: str
    error: Optional[str] = None

class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
    platform: str

class OAuthCallbackResponse(BaseModel):
    success: bool
    platform: str
    account_info: Optional[Dict[str, Any]] = None
    message: str
    error: Optional[str] = None

class OAuthStatusResponse(BaseModel):
    status: str
    features: List[str]
    supported_platforms: List[str]
    oauth_flows: List[str]
    version: str
    message: Optional[str] = None

# --- Helper Functions ---
def generate_oauth_state() -> str:
    """Generate a secure OAuth state parameter"""
    return str(uuid.uuid4())

def get_platform_info(platform: str) -> Dict[str, Any]:
    """Get platform-specific OAuth information"""
    platforms = {
        "facebook": {
            "name": "Facebook",
            "description": "Connect your Facebook page for publishing and analytics",
            "scopes": ["pages_manage_metadata", "pages_read_engagement", "pages_manage_posts"],
            "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
            "client_id": "your_facebook_app_id",
            "redirect_uri": "http://localhost:8000/api/v1/oauth/facebook/callback"
        },
        "instagram": {
            "name": "Instagram",
            "description": "Connect your Instagram Business account for publishing and analytics",
            "scopes": ["instagram_basic", "instagram_manage_comments", "instagram_manage_insights"],
            "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
            "client_id": "your_facebook_app_id",
            "redirect_uri": "http://localhost:8000/api/v1/oauth/instagram/callback"
        },
        "linkedin": {
            "name": "LinkedIn",
            "description": "Connect your LinkedIn company page for professional content publishing",
            "scopes": ["w_member_social", "r_organization_social", "w_organization_social"],
            "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
            "client_id": "your_linkedin_client_id",
            "redirect_uri": "http://localhost:8000/api/v1/oauth/linkedin/callback"
        },
        "google_gbp": {
            "name": "Google Business Profile",
            "description": "Connect your Google Business Profile for local business content",
            "scopes": ["https://www.googleapis.com/auth/business.manage"],
            "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
            "client_id": "your_google_client_id",
            "redirect_uri": "http://localhost:8000/api/v1/oauth/google/callback"
        }
    }
    return platforms.get(platform, {})

def generate_mock_connections() -> List[OAuthPlatform]:
    """Generate mock OAuth connections"""
    return [
        OAuthPlatform(
            platform="facebook",
            name="Facebook",
            description="Connected to Facebook page",
            status="connected",
            connected_at="2024-01-15T10:30:00Z",
            expires_at="2024-03-15T10:30:00Z",
            scopes=["pages_manage_metadata", "pages_read_engagement", "pages_manage_posts"],
            account_info={
                "page_id": "123456789",
                "page_name": "My Business Page",
                "page_url": "https://facebook.com/mybusinesspage"
            }
        ),
        OAuthPlatform(
            platform="linkedin",
            name="LinkedIn",
            description="Connected to LinkedIn company page",
            status="connected",
            connected_at="2024-01-14T15:45:00Z",
            expires_at="2024-02-14T15:45:00Z",
            scopes=["w_member_social", "r_organization_social", "w_organization_social"],
            account_info={
                "company_id": "987654321",
                "company_name": "My Company",
                "company_url": "https://linkedin.com/company/mycompany"
            }
        ),
        OAuthPlatform(
            platform="instagram",
            name="Instagram",
            description="Instagram Business account",
            status="disconnected",
            connected_at=None,
            expires_at=None,
            scopes=["instagram_basic", "instagram_manage_comments"],
            account_info=None
        ),
        OAuthPlatform(
            platform="google_gbp",
            name="Google Business Profile",
            description="Google Business Profile account",
            status="error",
            connected_at="2024-01-13T09:20:00Z",
            expires_at="2024-01-20T09:20:00Z",
            scopes=["https://www.googleapis.com/auth/business.manage"],
            account_info={
                "business_id": "456789123",
                "business_name": "My Local Business",
                "error": "Token expired"
            }
        )
    ]

# --- API Endpoints ---

@router.get("/oauth/status", response_model=OAuthStatusResponse)
async def get_oauth_status():
    """Get OAuth integration service status"""
    return OAuthStatusResponse(
        status="operational",
        features=[
            "oauth_authentication",
            "token_management",
            "account_linking",
            "token_refresh",
            "multi_platform_support"
        ],
        supported_platforms=["facebook", "instagram", "linkedin", "google_gbp"],
        oauth_flows=["authorization_code", "implicit", "refresh_token"],
        version="1.0.0",
        message="OAuth integration service is ready for social media connections!"
    )

@router.get("/oauth/platforms", response_model=List[OAuthPlatform])
async def get_oauth_platforms():
    """Get available OAuth platforms and their connection status"""
    try:
        return generate_mock_connections()
    except Exception as e:
        logger.error(f"Get OAuth platforms error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OAuth platforms: {str(e)}"
        )

@router.post("/oauth/connect", response_model=OAuthConnectionResponse)
async def initiate_oauth_connection(request: OAuthConnectionRequest) -> OAuthConnectionResponse:
    """
    Initiate OAuth connection for a platform
    """
    try:
        # Validate platform
        platform_info = get_platform_info(request.platform)
        if not platform_info:
            return OAuthConnectionResponse(
                success=False,
                message="Unsupported platform",
                error=f"Platform {request.platform} is not supported"
            )
        
        # Generate state parameter
        state = request.state or generate_oauth_state()
        
        # Build authorization URL
        auth_params = {
            "client_id": platform_info["client_id"],
            "redirect_uri": request.redirect_uri,
            "scope": " ".join(platform_info["scopes"]),
            "response_type": "code",
            "state": state
        }
        
        # Add platform-specific parameters
        if request.platform == "google_gbp":
            auth_params["access_type"] = "offline"
            auth_params["prompt"] = "consent"
        
        # Build URL
        from urllib.parse import urlencode
        auth_url = f"{platform_info['auth_url']}?{urlencode(auth_params)}"
        
        return OAuthConnectionResponse(
            success=True,
            authorization_url=auth_url,
            state=state,
            message=f"OAuth connection initiated for {platform_info['name']}"
        )
        
    except Exception as e:
        logger.error(f"OAuth connection initiation error: {e}")
        return OAuthConnectionResponse(
            success=False,
            message="Failed to initiate OAuth connection",
            error=str(e)
        )

@router.post("/oauth/callback", response_model=OAuthCallbackResponse)
async def handle_oauth_callback(request: OAuthCallbackRequest) -> OAuthCallbackResponse:
    """
    Handle OAuth callback and exchange code for tokens
    """
    try:
        # Validate platform
        platform_info = get_platform_info(request.platform)
        if not platform_info:
            return OAuthCallbackResponse(
                success=False,
                platform=request.platform,
                message="Unsupported platform",
                error=f"Platform {request.platform} is not supported"
            )
        
        # Mock token exchange (in real implementation, this would exchange code for tokens)
        mock_account_info = {
            "facebook": {
                "page_id": "123456789",
                "page_name": "My Business Page",
                "page_url": "https://facebook.com/mybusinesspage",
                "access_token": "mock_access_token_123",
                "expires_in": 5184000  # 60 days
            },
            "instagram": {
                "business_id": "987654321",
                "username": "mybusiness",
                "account_url": "https://instagram.com/mybusiness",
                "access_token": "mock_access_token_456",
                "expires_in": 5184000
            },
            "linkedin": {
                "company_id": "456789123",
                "company_name": "My Company",
                "company_url": "https://linkedin.com/company/mycompany",
                "access_token": "mock_access_token_789",
                "expires_in": 5184000
            },
            "google_gbp": {
                "business_id": "789123456",
                "business_name": "My Local Business",
                "business_url": "https://business.google.com/mybusiness",
                "access_token": "mock_access_token_012",
                "expires_in": 3600
            }
        }
        
        account_info = mock_account_info.get(request.platform, {})
        
        return OAuthCallbackResponse(
            success=True,
            platform=request.platform,
            account_info=account_info,
            message=f"Successfully connected {platform_info['name']} account"
        )
        
    except Exception as e:
        logger.error(f"OAuth callback error: {e}")
        return OAuthCallbackResponse(
            success=False,
            platform=request.platform,
            message="Failed to handle OAuth callback",
            error=str(e)
        )

@router.delete("/oauth/disconnect/{platform}")
async def disconnect_oauth_platform(platform: str) -> Dict[str, Any]:
    """
    Disconnect OAuth platform
    """
    try:
        # Validate platform
        platform_info = get_platform_info(platform)
        if not platform_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}"
            )
        
        # Mock disconnection (in real implementation, this would revoke tokens and update database)
        return {
            "success": True,
            "platform": platform,
            "message": f"Successfully disconnected {platform_info['name']} account"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth disconnection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disconnect platform: {str(e)}"
        )

@router.get("/oauth/refresh/{platform}")
async def refresh_oauth_token(platform: str) -> Dict[str, Any]:
    """
    Refresh OAuth token for a platform
    """
    try:
        # Validate platform
        platform_info = get_platform_info(platform)
        if not platform_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}"
            )
        
        # Mock token refresh (in real implementation, this would refresh the actual token)
        return {
            "success": True,
            "platform": platform,
            "new_expires_at": (datetime.utcnow().timestamp() + 5184000),  # 60 days from now
            "message": f"Successfully refreshed {platform_info['name']} token"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"OAuth token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh token: {str(e)}"
        )

@router.get("/oauth/account/{platform}")
async def get_oauth_account_info(platform: str) -> Dict[str, Any]:
    """
    Get OAuth account information for a platform
    """
    try:
        # Validate platform
        platform_info = get_platform_info(platform)
        if not platform_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported platform: {platform}"
            )
        
        # Get mock account info
        mock_account_info = {
            "facebook": {
                "page_id": "123456789",
                "page_name": "My Business Page",
                "page_url": "https://facebook.com/mybusinesspage",
                "followers_count": 1250,
                "connected_at": "2024-01-15T10:30:00Z",
                "expires_at": "2024-03-15T10:30:00Z"
            },
            "linkedin": {
                "company_id": "987654321",
                "company_name": "My Company",
                "company_url": "https://linkedin.com/company/mycompany",
                "followers_count": 850,
                "connected_at": "2024-01-14T15:45:00Z",
                "expires_at": "2024-02-14T15:45:00Z"
            }
        }
        
        account_info = mock_account_info.get(platform, {})
        if not account_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No account information found for {platform}"
            )
        
        return {
            "success": True,
            "platform": platform,
            "account_info": account_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get OAuth account info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get account info: {str(e)}"
        )
