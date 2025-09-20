"""
Unit tests for AI Content API
"""

import pytest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient


class TestAIContentAPI:
    """Test AI Content endpoints"""
    
    def test_ai_complete_success(self, client: TestClient, mock_user, mock_jwt_decode, mock_celery_task):
        """Test successful AI content completion"""
        with patch("app.api.deps.get_current_user", return_value=mock_user), \
             patch("app.core.security.verify_clerk_jwt", return_value={"sub": "test_user_123"}):
            response = client.post(
                "/api/v1/ai/complete",
                json={
                    "prompt": "Write a social media post about AI",
                    "brand_guide_id": None,
                    "locale": "en-US"
                },
                headers={"Authorization": "Bearer test_token"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "text" in data
            assert "token_usage" in data
            assert "provider" in data
            assert data["provider"] == "openai"
    
    def test_ai_complete_with_brand_guide(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test AI content completion with brand guide"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/ai/complete",
                json={
                    "prompt": "Write a social media post about AI",
                    "brand_guide_id": 1,
                    "locale": "en-US"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "text" in data
            assert "token_usage" in data
    
    def test_ai_batch_success(self, client: TestClient, mock_user, mock_jwt_decode, mock_celery_task):
        """Test successful batch AI content processing"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/ai/batch",
                json={
                    "prompts": [
                        "Write a social media post about AI",
                        "Create content about machine learning",
                        "Generate a post about data science"
                    ],
                    "brand_guide_id": None,
                    "locale": "en-US"
                }
            )
            
            assert response.status_code == 202
            data = response.json()
            assert "job_id" in data
            assert "status" in data
            assert "total_prompts" in data
            assert data["total_prompts"] == 3
            assert "status_url" in data
    
    def test_ai_batch_too_many_prompts(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test batch AI content with too many prompts"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            prompts = [f"Prompt {i}" for i in range(51)]  # 51 prompts (max is 50)
            
            response = client.post(
                "/api/v1/ai/batch",
                json={
                    "prompts": prompts,
                    "brand_guide_id": None,
                    "locale": "en-US"
                }
            )
            
            assert response.status_code == 422  # Validation error
    
    def test_ai_optimize_success(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test successful content optimization"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.post(
                "/api/v1/ai/optimize",
                json={
                    "platform": "facebook",
                    "draft_content": "This is a very long post that needs to be optimized for Facebook platform",
                    "brand_guide_id": None
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "optimized_text" in data
            assert "constraints_applied" in data
            assert "character_count" in data
            assert "hashtag_count" in data
            assert data["platform"] == "facebook"
    
    def test_ai_optimize_different_platforms(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test content optimization for different platforms"""
        platforms = ["facebook", "instagram", "linkedin", "twitter"]
        
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            for platform in platforms:
                response = client.post(
                    "/api/v1/ai/optimize",
                    json={
                        "platform": platform,
                        "draft_content": "Test content for optimization",
                        "brand_guide_id": None
                    }
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["platform"] == platform
                assert "constraints_applied" in data
    
    def test_ai_requests_list(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing AI requests"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/ai/requests")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_ai_optimizations_list(self, client: TestClient, mock_user, mock_jwt_decode):
        """Test listing AI optimizations"""
        with patch("app.api.deps.get_current_user", return_value=mock_user):
            response = client.get("/api/v1/ai/optimizations")
            
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
    
    def test_ai_complete_unauthorized(self, client: TestClient):
        """Test AI complete endpoint without authentication"""
        response = client.post(
            "/api/v1/ai/complete",
            json={
                "prompt": "Write a social media post about AI",
                "brand_guide_id": None,
                "locale": "en-US"
            }
        )
        
        assert response.status_code == 401
    
    def test_ai_batch_unauthorized(self, client: TestClient):
        """Test AI batch endpoint without authentication"""
        response = client.post(
            "/api/v1/ai/batch",
            json={
                "prompts": ["Test prompt"],
                "brand_guide_id": None,
                "locale": "en-US"
            }
        )
        
        assert response.status_code == 401
    
    def test_ai_optimize_unauthorized(self, client: TestClient):
        """Test AI optimize endpoint without authentication"""
        response = client.post(
            "/api/v1/ai/optimize",
            json={
                "platform": "facebook",
                "draft_content": "Test content",
                "brand_guide_id": None
            }
        )
        
        assert response.status_code == 401
