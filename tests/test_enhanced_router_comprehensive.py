#!/usr/bin/env python3
"""
Comprehensive test suite for Enhanced AI Router.
Tests every line of function systematically.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.ai.enhanced_router import EnhancedAIRouter, GenerationRequest, GenerationResult
from app.ai.budget_guard import BudgetGuard
from app.models.ai_budget import AIBudget


class TestEnhancedAIRouter:
    """Comprehensive tests for EnhancedAIRouter class."""

    @pytest.fixture
    def router(self):
        """Create router instance for testing."""
        return EnhancedAIRouter()

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        return Mock()

    @pytest.fixture
    def sample_request(self):
        """Create sample generation request."""
        return GenerationRequest(
            task="caption",
            prompt="Write a caption about our new product",
            system="You are a social media assistant",
            org_id="test_org_123",
            is_critical=False,
            model_preference=None
        )

    def test_estimate_tokens_basic(self, router):
        """Test token estimation with basic text."""
        # Test case 1: Normal text
        text = "Hello world"
        expected = len(text) // 4  # 11 // 4 = 2
        result = router._estimate_tokens(text)
        assert result == expected
        
        # Test case 2: Empty string
        result = router._estimate_tokens("")
        assert result == 0
        
        # Test case 3: Long text
        long_text = "A" * 1000
        expected = 1000 // 4  # 250
        result = router._estimate_tokens(long_text)
        assert result == expected

    def test_estimate_tokens_edge_cases(self, router):
        """Test token estimation edge cases."""
        # Test case 1: Single character
        result = router._estimate_tokens("a")
        assert result == 0  # 1 // 4 = 0
        
        # Test case 2: Exactly 4 characters
        result = router._estimate_tokens("test")
        assert result == 1  # 4 // 4 = 1
        
        # Test case 3: Unicode characters
        unicode_text = "Hello 世界 🌍"
        result = router._estimate_tokens(unicode_text)
        assert result > 0

    def test_estimate_cost_openai_gpt4o_mini(self, router):
        """Test cost estimation for OpenAI GPT-4o-mini."""
        provider = "openai:gpt-4o-mini"
        tokens_in = 1000
        tokens_out = 500
        
        result = router._estimate_cost(provider, tokens_in, tokens_out)
        
        # Expected: (1000/1000 * 0.00015) + (500/1000 * 0.0006) = 0.00015 + 0.0003 = 0.00045
        expected = 0.00015 + 0.0003
        assert abs(result - expected) < 0.00001

    def test_estimate_cost_openai_gpt4o(self, router):
        """Test cost estimation for OpenAI GPT-4o."""
        provider = "openai:gpt-4o"
        tokens_in = 1000
        tokens_out = 500
        
        result = router._estimate_cost(provider, tokens_in, tokens_out)
        
        # Expected: (1000/1000 * 0.005) + (500/1000 * 0.015) = 0.005 + 0.0075 = 0.0125
        expected = 0.005 + 0.0075
        assert abs(result - expected) < 0.00001

    def test_estimate_cost_ollama_free(self, router):
        """Test cost estimation for free Ollama model."""
        provider = "ollama:llama3.1"
        tokens_in = 1000
        tokens_out = 500
        
        result = router._estimate_cost(provider, tokens_in, tokens_out)
        assert result == 0.0

    def test_estimate_cost_unknown_provider(self, router):
        """Test cost estimation for unknown provider (falls back to 'open')."""
        provider = "unknown:model"
        tokens_in = 1000
        tokens_out = 500
        
        result = router._estimate_cost(provider, tokens_in, tokens_out)
        
        # Should use 'open' costs: (1000/1000 * 0.0001) + (500/1000 * 0.0001) = 0.00015
        expected = 0.00015
        assert abs(result - expected) < 0.00001

    def test_estimate_cost_zero_tokens(self, router):
        """Test cost estimation with zero tokens."""
        provider = "openai:gpt-4o-mini"
        tokens_in = 0
        tokens_out = 0
        
        result = router._estimate_cost(provider, tokens_in, tokens_out)
        assert result == 0.0

    def test_make_cache_key_basic(self, router, sample_request):
        """Test cache key generation for basic request."""
        result = router._make_cache_key(sample_request)
        
        # Should be in format: ai:caption:hash
        assert result.startswith("ai:caption:")
        assert len(result) == len("ai:caption:") + 16  # 16 char hash

    def test_make_cache_key_personalized_content(self, router):
        """Test cache key generation for personalized content (should return None)."""
        request = GenerationRequest(
            task="caption",
            prompt="Write a caption about our new product",
            system="You are a social media assistant",
            org_id="test_org_123",
            is_critical=True  # Critical task should not be cached
        )
        
        result = router._make_cache_key(request)
        assert result is None

    def test_make_cache_key_no_org_id(self, router):
        """Test cache key generation without org_id."""
        request = GenerationRequest(
            task="caption",
            prompt="Write a caption about our new product",
            system="You are a social media assistant",
            org_id=None,
            is_critical=False
        )
        
        result = router._make_cache_key(request)
        assert result is not None
        assert result.startswith("ai:caption:")

    def test_make_cache_key_different_prompts(self, router):
        """Test that different prompts generate different cache keys."""
        request1 = GenerationRequest(
            task="caption",
            prompt="Write a caption about product A",
            system="You are a social media assistant"
        )
        request2 = GenerationRequest(
            task="caption",
            prompt="Write a caption about product B",
            system="You are a social media assistant"
        )
        
        key1 = router._make_cache_key(request1)
        key2 = router._make_cache_key(request2)
        
        assert key1 != key2

    def test_make_cache_key_same_prompts(self, router):
        """Test that identical prompts generate same cache keys."""
        request1 = GenerationRequest(
            task="caption",
            prompt="Write a caption about our new product",
            system="You are a social media assistant"
        )
        request2 = GenerationRequest(
            task="caption",
            prompt="Write a caption about our new product",
            system="You are a social media assistant"
        )
        
        key1 = router._make_cache_key(request1)
        key2 = router._make_cache_key(request2)
        
        assert key1 == key2

    @pytest.mark.asyncio
    async def test_get_from_cache_miss(self, router):
        """Test cache miss scenario."""
        cache_key = "test_key"
        
        with patch('app.cache.redis.cache.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            
            result = await router._get_from_cache(cache_key)
            
            assert result is None
            mock_get.assert_called_once_with("ai_generation", cache_key)

    @pytest.mark.asyncio
    async def test_get_from_cache_hit(self, router):
        """Test cache hit scenario."""
        cache_key = "test_key"
        cached_data = {
            "text": "Test cached response",
            "provider": "openai:gpt-4o-mini",
            "tokens_in": 100,
            "tokens_out": 50,
            "cost_gbp": 0.001,
            "duration_ms": 500
        }
        
        with patch('app.cache.redis.cache.get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = cached_data
            
            result = await router._get_from_cache(cache_key)
            
            assert result is not None
            assert isinstance(result, GenerationResult)
            assert result.text == "Test cached response"
            assert result.provider == "openai:gpt-4o-mini"
            assert result.tokens_in == 100
            assert result.tokens_out == 50
            assert result.cost_gbp == 0.001
            assert result.duration_ms == 500
            assert result.from_cache is True

    @pytest.mark.asyncio
    async def test_save_to_cache(self, router):
        """Test saving to cache."""
        cache_key = "test_key"
        result = GenerationResult(
            text="Test response",
            provider="openai:gpt-4o-mini",
            tokens_in=100,
            tokens_out=50,
            cost_gbp=0.001,
            duration_ms=500
        )
        
        with patch('app.cache.redis.cache.set', new_callable=AsyncMock) as mock_set:
            await router._save_to_cache(cache_key, result)
            
            expected_data = {
                "text": "Test response",
                "provider": "openai:gpt-4o-mini",
                "tokens_in": 100,
                "tokens_out": 50,
                "cost_gbp": 0.001,
                "duration_ms": 500
            }
            
            mock_set.assert_called_once_with("ai_generation", cache_key, expected_data)

    @pytest.mark.asyncio
    async def test_generate_single_with_budget_guard_over_limit(self, router, sample_request, mock_db_session):
        """Test generation when budget guard is over limit."""
        # Setup router with budget guard
        router.budget_guard = BudgetGuard(mock_db_session)
        
        # Mock budget guard to return over limit
        with patch.object(router.budget_guard, 'can_use_hosted_model', return_value=(False, "Budget exceeded")):
            with patch.object(router.ai_router, '_open_complete', new_callable=AsyncMock) as mock_open:
                mock_open.return_value = "Open model response"
                
                result = await router._generate_single(sample_request)
                
                assert result.text == "Open model response"
                assert result.provider == "open"
                mock_open.assert_called_once_with(sample_request.system, sample_request.prompt)

    @pytest.mark.asyncio
    async def test_generate_single_with_budget_guard_within_limit(self, router, sample_request, mock_db_session):
        """Test generation when budget guard is within limit."""
        # Setup router with budget guard
        router.budget_guard = BudgetGuard(mock_db_session)
        
        # Mock budget guard to return within limit
        with patch.object(router.budget_guard, 'can_use_hosted_model', return_value=(True, "Within budget")):
            with patch.object(router.model_router, 'complete', new_callable=AsyncMock) as mock_complete:
                mock_complete.return_value = "Hosted model response"
                
                result = await router._generate_single(sample_request)
                
                assert result.text == "Hosted model response"
                assert result.provider == "openai:gpt-4o-mini"  # Default provider
                mock_complete.assert_called_once_with(sample_request.prompt, sample_request.system)

    @pytest.mark.asyncio
    async def test_generate_single_critical_task_over_budget(self, router, mock_db_session):
        """Test generation for critical task when over budget (should still use hosted)."""
        critical_request = GenerationRequest(
            task="safety_check",
            prompt="Check this content for safety",
            system="You are a safety checker",
            org_id="test_org_123",
            is_critical=True
        )
        
        router.budget_guard = BudgetGuard(mock_db_session)
        
        # Mock budget guard to return over limit but allow critical tasks
        with patch.object(router.budget_guard, 'can_use_hosted_model', return_value=(True, "Critical task")):
            with patch.object(router.model_router, 'complete', new_callable=AsyncMock) as mock_complete:
                mock_complete.return_value = "Hosted model response"
                
                result = await router._generate_single(critical_request)
                
                assert result.text == "Hosted model response"
                assert result.provider == "openai:gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_generate_single_without_budget_guard(self, router, sample_request):
        """Test generation without budget guard."""
        router.budget_guard = None
        
        with patch.object(router.model_router, 'complete', new_callable=AsyncMock) as mock_complete:
            mock_complete.return_value = "Default model response"
            
            result = await router._generate_single(sample_request)
            
            assert result.text == "Default model response"
            assert result.provider == "openai:gpt-4o-mini"

    @pytest.mark.asyncio
    async def test_generate_single_records_usage(self, router, sample_request, mock_db_session):
        """Test that usage is recorded when budget guard is present."""
        router.budget_guard = BudgetGuard(mock_db_session)
        
        with patch.object(router.budget_guard, 'can_use_hosted_model', return_value=(True, "Within budget")):
            with patch.object(router.model_router, 'complete', new_callable=AsyncMock) as mock_complete:
                mock_complete.return_value = "Test response"
                
                with patch.object(router.budget_guard, 'record_usage') as mock_record:
                    await router._generate_single(sample_request)
                    
                    # Verify record_usage was called
                    mock_record.assert_called_once()
                    args = mock_record.call_args[0]
                    assert args[0] == sample_request.org_id
                    assert args[1] > 0  # tokens
                    assert args[2] > 0  # cost

    @pytest.mark.asyncio
    async def test_generate_single_token_estimation(self, router, sample_request):
        """Test token estimation in generation."""
        router.budget_guard = None
        
        with patch.object(router.model_router, 'complete', new_callable=AsyncMock) as mock_complete:
            mock_complete.return_value = "Test response with some content"
            
            result = await router._generate_single(sample_request)
            
            # Verify token estimation
            expected_input_tokens = router._estimate_tokens(f"{sample_request.system or ''}\n{sample_request.prompt}")
            expected_output_tokens = router._estimate_tokens("Test response with some content")
            
            assert result.tokens_in == expected_input_tokens
            assert result.tokens_out == expected_output_tokens

    @pytest.mark.asyncio
    async def test_generate_single_cost_calculation(self, router, sample_request):
        """Test cost calculation in generation."""
        router.budget_guard = None
        
        with patch.object(router.model_router, 'complete', new_callable=AsyncMock) as mock_complete:
            mock_complete.return_value = "Test response"
            
            result = await router._generate_single(sample_request)
            
            # Verify cost calculation
            expected_cost = router._estimate_cost(
                result.provider, 
                result.tokens_in, 
                result.tokens_out
            )
            
            assert result.cost_gbp == expected_cost

    @pytest.mark.asyncio
    async def test_generate_single_duration_tracking(self, router, sample_request):
        """Test duration tracking in generation."""
        router.budget_guard = None
        
        with patch.object(router.model_router, 'complete', new_callable=AsyncMock) as mock_complete:
            mock_complete.return_value = "Test response"
            
            result = await router._generate_single(sample_request)
            
            # Verify duration is tracked
            assert result.duration_ms >= 0
            assert isinstance(result.duration_ms, int)

    @pytest.mark.asyncio
    async def test_generate_with_cache_hit(self, router, sample_request):
        """Test generation with cache hit."""
        cache_key = "test_cache_key"
        
        with patch.object(router, '_make_cache_key', return_value=cache_key):
            with patch.object(router, '_get_from_cache', new_callable=AsyncMock) as mock_get:
                cached_result = GenerationResult(
                    text="Cached response",
                    provider="openai:gpt-4o-mini",
                    tokens_in=100,
                    tokens_out=50,
                    cost_gbp=0.001,
                    duration_ms=100,
                    from_cache=True
                )
                mock_get.return_value = cached_result
                
                result = await router.generate(sample_request)
                
                assert result == cached_result
                mock_get.assert_called_once_with(cache_key)

    @pytest.mark.asyncio
    async def test_generate_with_cache_miss(self, router, sample_request):
        """Test generation with cache miss."""
        cache_key = "test_cache_key"
        
        with patch.object(router, '_make_cache_key', return_value=cache_key):
            with patch.object(router, '_get_from_cache', new_callable=AsyncMock) as mock_get:
                with patch.object(router, '_generate_single', new_callable=AsyncMock) as mock_generate:
                    with patch.object(router, '_save_to_cache', new_callable=AsyncMock) as mock_save:
                        mock_get.return_value = None
                        
                        generated_result = GenerationResult(
                            text="Generated response",
                            provider="openai:gpt-4o-mini",
                            tokens_in=100,
                            tokens_out=50,
                            cost_gbp=0.001,
                            duration_ms=500
                        )
                        mock_generate.return_value = generated_result
                        
                        result = await router.generate(sample_request)
                        
                        assert result == generated_result
                        mock_get.assert_called_once_with(cache_key)
                        mock_generate.assert_called_once_with(sample_request)
                        mock_save.assert_called_once_with(cache_key, generated_result)

    @pytest.mark.asyncio
    async def test_generate_no_cache_key(self, router, sample_request):
        """Test generation when no cache key is generated (personalized content)."""
        with patch.object(router, '_make_cache_key', return_value=None):
            with patch.object(router, '_generate_single', new_callable=AsyncMock) as mock_generate:
                generated_result = GenerationResult(
                    text="Generated response",
                    provider="openai:gpt-4o-mini",
                    tokens_in=100,
                    tokens_out=50,
                    cost_gbp=0.001,
                    duration_ms=500
                )
                mock_generate.return_value = generated_result
                
                result = await router.generate(sample_request)
                
                assert result == generated_result
                mock_generate.assert_called_once_with(sample_request)

    @pytest.mark.asyncio
    async def test_batch_generate_empty_list(self, router):
        """Test batch generation with empty request list."""
        result = await router.batch_generate([])
        assert result == []

    @pytest.mark.asyncio
    async def test_batch_generate_multiple_requests(self, router):
        """Test batch generation with multiple requests."""
        requests = [
            GenerationRequest(task="caption", prompt="Prompt 1"),
            GenerationRequest(task="hashtags", prompt="Prompt 2"),
            GenerationRequest(task="caption", prompt="Prompt 3")
        ]
        
        with patch.object(router, 'generate', new_callable=AsyncMock) as mock_generate:
            mock_results = [
                GenerationResult(text="Result 1", provider="openai:gpt-4o-mini", tokens_in=10, tokens_out=5, cost_gbp=0.001, duration_ms=100),
                GenerationResult(text="Result 2", provider="openai:gpt-4o-mini", tokens_in=10, tokens_out=5, cost_gbp=0.001, duration_ms=100),
                GenerationResult(text="Result 3", provider="openai:gpt-4o-mini", tokens_in=10, tokens_out=5, cost_gbp=0.001, duration_ms=100)
            ]
            mock_generate.side_effect = mock_results
            
            result = await router.batch_generate(requests)
            
            assert len(result) == 3
            assert result == mock_results
            assert mock_generate.call_count == 3

    def test_router_initialization(self):
        """Test router initialization."""
        router = EnhancedAIRouter()
        
        assert router.model_router is not None
        assert router.ai_router is not None
        assert router.settings is not None
        assert router.budget_guard is None

    def test_router_initialization_with_db(self, mock_db_session):
        """Test router initialization with database session."""
        router = EnhancedAIRouter(db_session=mock_db_session)
        
        assert router.budget_guard is not None
        assert router.budget_guard.db == mock_db_session
