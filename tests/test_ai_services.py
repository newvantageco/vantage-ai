"""
Comprehensive tests for AI services: AI Router, Budget Guard, and Safety Service
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import date, datetime

from app.services.ai_router import ai_router, AIResponse, ProviderType
from app.services.budget_guard import BudgetGuard, BudgetViolation, LimitType
from app.services.safety import safety_service, SafetyResult, SafetyViolation, ViolationType, SafetyLevel


class TestAIRouter:
    """Test AI Router with provider fallback logic"""
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response"""
        return {
            "choices": [{"message": {"content": "Test response"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20}
        }
    
    @pytest.fixture
    def mock_anthropic_response(self):
        """Mock Anthropic API response"""
        return {
            "content": [{"text": "Test response"}]
        }
    
    @pytest.fixture
    def mock_cohere_response(self):
        """Mock Cohere API response"""
        return {
            "generations": [{"text": "Test response"}],
            "meta": {
                "billed_tokens": {
                    "input_tokens": 10,
                    "output_tokens": 20
                }
            }
        }
    
    @pytest.fixture
    def mock_ollama_response(self):
        """Mock Ollama API response"""
        return {
            "response": "Test response"
        }
    
    @pytest.mark.asyncio
    async def test_openai_provider_success(self, mock_openai_response):
        """Test OpenAI provider successful completion"""
        with patch('app.services.ai_router.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_client.chat.completions.create = AsyncMock(return_value=Mock(**mock_openai_response))
            mock_openai.return_value = mock_client
            
            # Test with OpenAI provider
            router = ai_router
            router.providers[ProviderType.OPENAI] = router.providers[ProviderType.OPENAI]
            
            response = await router.complete(
                prompt="Test prompt",
                system="Test system",
                temperature=0.7,
                max_tokens=100,
                json_mode=False,
                preferred_provider="openai"
            )
            
            assert response.text == "Test response"
            assert "openai" in response.provider
            assert response.tokens_in == 10
            assert response.tokens_out == 20
            assert response.ms_elapsed > 0
            assert response.cost_usd_estimate > 0
    
    @pytest.mark.asyncio
    async def test_provider_fallback_logic(self):
        """Test provider fallback when primary fails"""
        router = ai_router
        
        # Mock OpenAI to fail
        with patch.object(router.providers[ProviderType.OPENAI], 'complete', side_effect=Exception("OpenAI failed")):
            # Mock Ollama to succeed
            with patch.object(router.providers[ProviderType.OLLAMA], 'complete', return_value=AIResponse(
                text="Fallback response",
                provider="ollama:llama3.1",
                tokens_in=5,
                tokens_out=15,
                ms_elapsed=100,
                cost_usd_estimate=0.0
            )):
                response = await router.complete(
                    prompt="Test prompt",
                    preferred_provider="openai"  # Try OpenAI first, should fallback to Ollama
                )
                
                assert response.text == "Fallback response"
                assert "ollama" in response.provider
    
    @pytest.mark.asyncio
    async def test_all_providers_fail(self):
        """Test behavior when all providers fail"""
        router = ai_router
        
        # Mock all providers to fail
        for provider in router.providers.values():
            provider.complete = AsyncMock(side_effect=Exception("Provider failed"))
        
        with pytest.raises(Exception, match="All AI providers failed"):
            await router.complete(prompt="Test prompt")
    
    @pytest.mark.asyncio
    async def test_batch_completion(self):
        """Test batch completion functionality"""
        router = ai_router
        
        # Mock successful completion
        mock_response = AIResponse(
            text="Batch response",
            provider="openai:gpt-4o-mini",
            tokens_in=10,
            tokens_out=20,
            ms_elapsed=100,
            cost_usd_estimate=0.01
        )
        
        with patch.object(router, 'complete', return_value=mock_response):
            requests = [
                {"prompt": "Test 1"},
                {"prompt": "Test 2"},
                {"prompt": "Test 3"}
            ]
            
            results = await router.batch_complete(requests)
            
            assert len(results) == 3
            for result in results:
                assert result.text == "Batch response"
                assert "openai" in result.provider
    
    def test_get_available_providers(self):
        """Test getting available providers"""
        router = ai_router
        providers = router.get_available_providers()
        
        assert isinstance(providers, list)
        assert len(providers) > 0
        assert "openai" in providers or "ollama" in providers
    
    def test_get_provider_costs(self):
        """Test getting provider cost information"""
        router = ai_router
        costs = router.get_provider_costs()
        
        assert isinstance(costs, dict)
        for provider, cost_info in costs.items():
            assert "input_per_1k" in cost_info
            assert "output_per_1k" in cost_info
            assert cost_info["input_per_1k"] >= 0
            assert cost_info["output_per_1k"] >= 0


class TestBudgetGuard:
    """Test Budget Guard with per-org and per-user caps"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session"""
        return Mock()
    
    @pytest.fixture
    def budget_guard(self, mock_db_session):
        """Create BudgetGuard instance with mock DB"""
        return BudgetGuard(mock_db_session)
    
    def test_check_org_budget_within_limits(self, budget_guard):
        """Test org budget check when within limits"""
        # Mock org limits and usage
        with patch.object(budget_guard, '_get_org_limits', return_value=Mock(
            daily_tokens=100000,
            daily_cost_usd=50.0,
            monthly_tokens=2000000,
            monthly_cost_usd=1000.0
        )):
            with patch.object(budget_guard, '_get_org_usage', return_value=Mock(
                daily_tokens_used=1000,
                daily_cost_used=1.0,
                monthly_tokens_used=10000,
                monthly_cost_used=10.0,
                daily_percentage=1.0,
                monthly_percentage=0.5
            )):
                violation = budget_guard.check_org_budget("org123", 1000, 1.0)
                
                assert not violation.is_violated
                assert violation.limit_type is None
    
    def test_check_org_budget_daily_exceeded(self, budget_guard):
        """Test org budget check when daily limit exceeded"""
        with patch.object(budget_guard, '_get_org_limits', return_value=Mock(
            daily_tokens=1000,
            daily_cost_usd=5.0,
            monthly_tokens=20000,
            monthly_cost_usd=100.0
        )):
            with patch.object(budget_guard, '_get_org_usage', return_value=Mock(
                daily_tokens_used=900,
                daily_cost_used=4.0,
                monthly_tokens_used=5000,
                monthly_cost_used=20.0,
                daily_percentage=90.0,
                monthly_percentage=25.0
            )):
                violation = budget_guard.check_org_budget("org123", 200, 2.0)
                
                assert violation.is_violated
                assert violation.limit_type == LimitType.DAILY
                assert "Daily AI usage limit reached" in violation.friendly_message
                assert "Upgrade to Pro plan" in violation.upgrade_suggestion
    
    def test_check_user_budget_monthly_exceeded(self, budget_guard):
        """Test user budget check when monthly limit exceeded"""
        with patch.object(budget_guard, '_get_user_limits', return_value=Mock(
            daily_tokens=1000,
            daily_cost_usd=5.0,
            monthly_tokens=10000,
            monthly_cost_usd=50.0
        )):
            with patch.object(budget_guard, '_get_user_usage', return_value=Mock(
                daily_tokens_used=100,
                daily_cost_used=0.5,
                monthly_tokens_used=9500,
                monthly_cost_used=45.0,
                daily_percentage=10.0,
                monthly_percentage=95.0
            )):
                violation = budget_guard.check_user_budget("user123", 1000, 10.0)
                
                assert violation.is_violated
                assert violation.limit_type == LimitType.MONTHLY
                assert "monthly AI usage limit reached" in violation.friendly_message
                assert "ask your admin to upgrade" in violation.upgrade_suggestion
    
    def test_can_make_request_success(self, budget_guard):
        """Test can_make_request when both org and user are within limits"""
        with patch.object(budget_guard, 'check_org_budget', return_value=Mock(is_violated=False)):
            with patch.object(budget_guard, 'check_user_budget', return_value=Mock(is_violated=False)):
                can_make, violation = budget_guard.can_make_request("org123", "user123", 100, 1.0)
                
                assert can_make is True
                assert violation is None
    
    def test_can_make_request_org_violation(self, budget_guard):
        """Test can_make_request when org budget is violated"""
        org_violation = Mock(is_violated=True, limit_type=LimitType.DAILY)
        with patch.object(budget_guard, 'check_org_budget', return_value=org_violation):
            with patch.object(budget_guard, 'check_user_budget', return_value=Mock(is_violated=False)):
                can_make, violation = budget_guard.can_make_request("org123", "user123", 100, 1.0)
                
                assert can_make is False
                assert violation == org_violation
    
    def test_record_usage(self, budget_guard, mock_db_session):
        """Test recording usage"""
        budget_guard.record_usage(
            org_id="org123",
            user_id="user123",
            tokens_used=100,
            cost_gbp=0.5,
            model_name="openai:gpt-4o-mini",
            operation_type="content_generation"
        )
        
        # Verify database operations
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
    
    def test_get_org_budget_status(self, budget_guard):
        """Test getting org budget status"""
        mock_limits = Mock(
            daily_tokens=100000,
            daily_cost_usd=50.0,
            monthly_tokens=2000000,
            monthly_cost_usd=1000.0
        )
        mock_usage = Mock(
            daily_tokens_used=10000,
            daily_cost_used=5.0,
            monthly_tokens_used=100000,
            monthly_cost_used=50.0,
            daily_percentage=10.0,
            monthly_percentage=5.0
        )
        
        with patch.object(budget_guard, '_get_org_limits', return_value=mock_limits):
            with patch.object(budget_guard, '_get_org_usage', return_value=mock_usage):
                status = budget_guard.get_org_budget_status("org123")
                
                assert "limits" in status
                assert "usage" in status
                assert "status" in status
                assert status["limits"]["daily_tokens"] == 100000
                assert status["usage"]["daily_tokens_used"] == 10000
                assert status["status"]["daily_remaining"] == 90000


class TestSafetyService:
    """Test Safety Service with moderation and brand guide checks"""
    
    @pytest.fixture
    def safety_service_instance(self):
        """Create SafetyService instance"""
        return safety_service
    
    @pytest.fixture
    def mock_brand_guide(self):
        """Mock brand guide"""
        return Mock(
            blocked_terms=["competitor", "cheap", "expensive"],
            tone_requirements={"professional": True, "positive": True},
            length_limits={"twitter": 280, "facebook": 2200},
            style_guidelines=["Use active voice", "Be concise"],
            forbidden_topics=["politics", "religion"]
        )
    
    @pytest.mark.asyncio
    async def test_check_content_safe(self, safety_service_instance):
        """Test safety check for safe content"""
        content = "This is a professional and positive message about our product."
        
        result = await safety_service_instance.check_content(
            content=content,
            platform="twitter",
            brand_guide_id=None,
            user_id="user123"
        )
        
        assert result.is_safe is True
        assert len(result.violations) == 0
        assert len(result.warnings) == 0
    
    @pytest.mark.asyncio
    async def test_check_content_with_violations(self, safety_service_instance, mock_brand_guide):
        """Test safety check for content with violations"""
        content = "This is a cheap competitor product that sucks!"
        
        with patch.object(safety_service_instance, '_load_brand_guide', return_value=mock_brand_guide):
            result = await safety_service_instance.check_content(
                content=content,
                platform="twitter",
                brand_guide_id="brand123",
                user_id="user123"
            )
            
            assert result.is_safe is False
            assert len(result.violations) > 0
            assert any("cheap" in v.message for v in result.violations)
            assert any("competitor" in v.message for v in result.violations)
    
    @pytest.mark.asyncio
    async def test_check_content_length_violation(self, safety_service_instance, mock_brand_guide):
        """Test safety check for content exceeding length limits"""
        # Create content longer than Twitter limit
        content = "This is a very long message that exceeds the Twitter character limit. " * 10
        
        with patch.object(safety_service_instance, '_load_brand_guide', return_value=mock_brand_guide):
            result = await safety_service_instance.check_content(
                content=content,
                platform="twitter",
                brand_guide_id="brand123",
                user_id="user123"
            )
            
            assert result.is_safe is False
            assert any("exceeds" in v.message and "character limit" in v.message for v in result.violations)
    
    @pytest.mark.asyncio
    async def test_check_content_tone_violation(self, safety_service_instance, mock_brand_guide):
        """Test safety check for content with tone violations"""
        content = "OMG this is so awesome!!! WTF is going on here???"
        
        with patch.object(safety_service_instance, '_load_brand_guide', return_value=mock_brand_guide):
            result = await safety_service_instance.check_content(
                content=content,
                platform="facebook",
                brand_guide_id="brand123",
                user_id="user123"
            )
            
            # Should have warnings for unprofessional tone
            assert any("professional" in w for w in result.warnings)
    
    @pytest.mark.asyncio
    async def test_check_content_forbidden_topic(self, safety_service_instance, mock_brand_guide):
        """Test safety check for content with forbidden topics"""
        content = "Let's discuss politics and religion in our marketing content."
        
        with patch.object(safety_service_instance, '_load_brand_guide', return_value=mock_brand_guide):
            result = await safety_service_instance.check_content(
                content=content,
                platform="linkedin",
                brand_guide_id="brand123",
                user_id="user123"
            )
            
            assert result.is_safe is False
            assert any("forbidden topic" in v.message for v in result.violations)
    
    @pytest.mark.asyncio
    async def test_check_batch_content(self, safety_service_instance):
        """Test batch content checking"""
        contents = [
            "This is safe content.",
            "This content has problems and issues.",
            "Another safe message."
        ]
        
        results = await safety_service_instance.check_batch_content(
            contents=contents,
            platform="twitter",
            brand_guide_id=None
        )
        
        assert len(results) == 3
        assert results[0].is_safe is True
        assert results[2].is_safe is True
        # Second content might have warnings about negative tone
    
    def test_get_safety_guidelines(self, safety_service_instance):
        """Test getting safety guidelines"""
        guidelines = safety_service_instance.get_safety_guidelines()
        
        assert "general" in guidelines
        assert "platforms" in guidelines
        assert "twitter" in guidelines["platforms"]
        assert guidelines["platforms"]["twitter"]["max_length"] == 280
    
    def test_get_safety_guidelines_with_brand_guide(self, safety_service_instance, mock_brand_guide):
        """Test getting safety guidelines with brand guide"""
        with patch.object(safety_service_instance, '_load_brand_guide', return_value=mock_brand_guide):
            guidelines = safety_service_instance.get_safety_guidelines("brand123")
            
            assert "brand_guide" in guidelines
            assert guidelines["brand_guide"]["blocked_terms"] == ["competitor", "cheap", "expensive"]
            assert guidelines["brand_guide"]["tone_requirements"]["professional"] is True


class TestIntegration:
    """Integration tests for AI services working together"""
    
    @pytest.mark.asyncio
    async def test_ai_complete_with_budget_and_safety(self):
        """Test AI complete endpoint with budget and safety integration"""
        # This would be an integration test that mocks the database
        # and tests the full flow from API endpoint through all services
        pass
    
    @pytest.mark.asyncio
    async def test_publish_preview_with_safety(self):
        """Test publish preview endpoint with safety integration"""
        # This would test the publish preview flow with safety checks
        pass


if __name__ == "__main__":
    pytest.main([__file__])
