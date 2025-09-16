#!/usr/bin/env python3
"""
Comprehensive test suite for Budget Guard System.
Tests every line of function systematically.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.ai.budget_guard import BudgetGuard
from app.models.ai_budget import AIBudget


class TestBudgetGuard:
    """Comprehensive tests for BudgetGuard class."""

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        db = Mock()
        db.query.return_value.filter.return_value.first.return_value = None
        db.query.return_value.filter.return_value.scalars.return_value.all.return_value = []
        return db

    @pytest.fixture
    def budget_guard(self, mock_db_session):
        """Create BudgetGuard instance."""
        return BudgetGuard(mock_db_session)

    @pytest.fixture
    def sample_budget(self):
        """Create sample AI budget."""
        return AIBudget(
            id="budget_123",
            org_id="org_123",
            daily_token_limit=10000,
            daily_cost_limit_gbp=5.0,
            tokens_used_today=0,
            cost_used_today_gbp=0.0,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    def test_initialization(self, mock_db_session):
        """Test BudgetGuard initialization."""
        guard = BudgetGuard(mock_db_session)
        
        assert guard.db == mock_db_session
        assert guard.settings is not None

    @pytest.mark.asyncio
    async def test_get_or_create_budget_existing_budget(self, budget_guard, mock_db_session, sample_budget):
        """Test getting existing budget."""
        # Mock database to return existing budget
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_budget
        
        result = await budget_guard.get_or_create_budget("org_123")
        
        assert result == sample_budget
        mock_db_session.query.assert_called_once_with(AIBudget)

    @pytest.mark.asyncio
    async def test_get_or_create_budget_create_new(self, budget_guard, mock_db_session):
        """Test creating new budget when none exists."""
        # Mock database to return no existing budget
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        with patch('app.models.ai_budget.AIBudget') as mock_budget_class:
            mock_budget_instance = Mock()
            mock_budget_class.return_value = mock_budget_instance
            
            result = await budget_guard.get_or_create_budget("org_123")
            
            assert result == mock_budget_instance
            mock_budget_class.assert_called_once()
            mock_db_session.add.assert_called_once_with(mock_budget_instance)
            mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_or_create_budget_with_defaults(self, budget_guard, mock_db_session):
        """Test creating budget with default values."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        with patch('app.models.ai_budget.AIBudget') as mock_budget_class:
            mock_budget_instance = Mock()
            mock_budget_class.return_value = mock_budget_instance
            
            await budget_guard.get_or_create_budget("org_123")
            
            # Verify AIBudget was created with correct parameters
            call_args = mock_budget_class.call_args[1]
            assert call_args['org_id'] == "org_123"
            assert call_args['daily_token_limit'] == 10000  # Default
            assert call_args['daily_cost_limit_gbp'] == 5.0  # Default
            assert call_args['is_active'] is True

    def test_can_use_hosted_model_no_budget(self, budget_guard, mock_db_session):
        """Test when no budget exists (should allow hosted model)."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        can_use, reason = budget_guard.can_use_hosted_model("org_123", "caption")
        
        assert can_use is True
        assert reason == "No budget limits set"

    def test_can_use_hosted_model_critical_task_within_soft_limit(self, budget_guard, mock_db_session, sample_budget):
        """Test critical task within soft limit (should allow hosted model)."""
        # Set budget to be within soft limit
        sample_budget.tokens_used_today = 5000  # Half of limit
        sample_budget.cost_used_today_gbp = 2.5  # Half of limit
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_budget
        
        with patch.object(sample_budget, 'is_over_limit', return_value=False):
            can_use, reason = budget_guard.can_use_hosted_model("org_123", "safety_check")
            
            assert can_use is True
            assert reason == "Critical task - using hosted model"

    def test_can_use_hosted_model_critical_task_over_soft_limit(self, budget_guard, mock_db_session, sample_budget):
        """Test critical task over soft limit (should deny hosted model)."""
        # Set budget to be over soft limit
        sample_budget.tokens_used_today = 15000  # Over limit
        sample_budget.cost_used_today_gbp = 7.5  # Over limit
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_budget
        
        with patch.object(sample_budget, 'is_over_limit') as mock_over_limit:
            mock_over_limit.return_value = True
            
            can_use, reason = budget_guard.can_use_hosted_model("org_123", "safety_check")
            
            assert can_use is False
            assert "Budget exceeded by" in reason
            assert "for critical task" in reason
            mock_over_limit.assert_called_once_with(2.0)  # Soft limit multiplier

    def test_can_use_hosted_model_non_critical_within_limit(self, budget_guard, mock_db_session, sample_budget):
        """Test non-critical task within limit (should allow hosted model)."""
        sample_budget.tokens_used_today = 5000  # Half of limit
        sample_budget.cost_used_today_gbp = 2.5  # Half of limit
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_budget
        
        with patch.object(sample_budget, 'is_over_limit', return_value=False):
            can_use, reason = budget_guard.can_use_hosted_model("org_123", "caption")
            
            assert can_use is True
            assert reason == "Within budget - using hosted model"

    def test_can_use_hosted_model_non_critical_over_limit(self, budget_guard, mock_db_session, sample_budget):
        """Test non-critical task over limit (should deny hosted model)."""
        sample_budget.tokens_used_today = 15000  # Over limit
        sample_budget.cost_used_today_gbp = 7.5  # Over limit
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_budget
        
        with patch.object(sample_budget, 'is_over_limit') as mock_over_limit:
            mock_over_limit.return_value = True
            
            can_use, reason = budget_guard.can_use_hosted_model("org_123", "caption")
            
            assert can_use is False
            assert reason == "Budget exceeded - using open model"
            mock_over_limit.assert_called_once_with(1.0)  # Normal limit

    def test_can_use_hosted_model_critical_tasks_list(self, budget_guard, mock_db_session, sample_budget):
        """Test that all critical task types are recognized."""
        critical_tasks = ["ads_copy", "brand_voice", "safety_check"]
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_budget
        
        with patch.object(sample_budget, 'is_over_limit', return_value=False):
            for task in critical_tasks:
                can_use, reason = budget_guard.can_use_hosted_model("org_123", task)
                assert can_use is True
                assert reason == "Critical task - using hosted model"

    def test_record_usage_existing_budget(self, budget_guard, mock_db_session, sample_budget):
        """Test recording usage for existing budget."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_budget
        
        with patch.object(sample_budget, 'add_usage') as mock_add_usage:
            budget_guard.record_usage("org_123", 1000, 0.5)
            
            mock_add_usage.assert_called_once_with(1000, 0.5)
            mock_db_session.commit.assert_called_once()

    def test_record_usage_create_budget(self, budget_guard, mock_db_session):
        """Test recording usage when budget doesn't exist (should create one)."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        with patch.object(budget_guard, 'get_or_create_budget', return_value=Mock()) as mock_get_budget:
            mock_budget = Mock()
            mock_get_budget.return_value = mock_budget
            
            budget_guard.record_usage("org_123", 1000, 0.5)
            
            mock_get_budget.assert_called_once_with("org_123")
            mock_budget.add_usage.assert_called_once_with(1000, 0.5)
            mock_db_session.commit.assert_called_once()

    def test_get_usage_stats_existing_budget(self, budget_guard, mock_db_session, sample_budget):
        """Test getting usage stats for existing budget."""
        sample_budget.tokens_used_today = 5000
        sample_budget.cost_used_today_gbp = 2.5
        sample_budget.daily_token_limit = 10000
        sample_budget.daily_cost_limit_gbp = 5.0
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_budget
        
        stats = budget_guard.get_usage_stats("org_123")
        
        expected_stats = {
            "tokens_used": 5000,
            "tokens_limit": 10000,
            "tokens_remaining": 5000,
            "cost_used_gbp": 2.5,
            "cost_limit_gbp": 5.0,
            "cost_remaining_gbp": 2.5,
            "tokens_usage_pct": 50.0,
            "cost_usage_pct": 50.0,
            "is_over_limit": False
        }
        
        assert stats == expected_stats

    def test_get_usage_stats_no_budget(self, budget_guard, mock_db_session):
        """Test getting usage stats when no budget exists."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        stats = budget_guard.get_usage_stats("org_123")
        
        expected_stats = {
            "tokens_used": 0,
            "tokens_limit": 0,
            "tokens_remaining": 0,
            "cost_used_gbp": 0.0,
            "cost_limit_gbp": 0.0,
            "cost_remaining_gbp": 0.0,
            "tokens_usage_pct": 0.0,
            "cost_usage_pct": 0.0,
            "is_over_limit": False
        }
        
        assert stats == expected_stats

    def test_get_usage_stats_over_limit(self, budget_guard, mock_db_session, sample_budget):
        """Test getting usage stats when over limit."""
        sample_budget.tokens_used_today = 12000  # Over limit
        sample_budget.cost_used_today_gbp = 6.0  # Over limit
        sample_budget.daily_token_limit = 10000
        sample_budget.daily_cost_limit_gbp = 5.0
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_budget
        
        stats = budget_guard.get_usage_stats("org_123")
        
        assert stats["is_over_limit"] is True
        assert stats["tokens_usage_pct"] == 120.0
        assert stats["cost_usage_pct"] == 120.0

    def test_get_usage_stats_zero_limits(self, budget_guard, mock_db_session, sample_budget):
        """Test getting usage stats with zero limits (avoid division by zero)."""
        sample_budget.tokens_used_today = 1000
        sample_budget.cost_used_today_gbp = 0.5
        sample_budget.daily_token_limit = 0
        sample_budget.daily_cost_limit_gbp = 0.0
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_budget
        
        stats = budget_guard.get_usage_stats("org_123")
        
        assert stats["tokens_usage_pct"] == 0.0
        assert stats["cost_usage_pct"] == 0.0

    def test_get_usage_stats_negative_remaining(self, budget_guard, mock_db_session, sample_budget):
        """Test getting usage stats when usage exceeds limits."""
        sample_budget.tokens_used_today = 15000
        sample_budget.cost_used_today_gbp = 7.5
        sample_budget.daily_token_limit = 10000
        sample_budget.daily_cost_limit_gbp = 5.0
        
        mock_db_session.query.return_value.filter.return_value.first.return_value = sample_budget
        
        stats = budget_guard.get_usage_stats("org_123")
        
        assert stats["tokens_remaining"] == -5000
        assert stats["cost_remaining_gbp"] == -2.5

    def test_budget_guard_settings_integration(self, mock_db_session):
        """Test that BudgetGuard uses settings correctly."""
        with patch('app.core.config.get_settings') as mock_get_settings:
            mock_settings = Mock()
            mock_settings.ai_budget_soft_limit_multiplier = 3.0
            mock_get_settings.return_value = mock_settings
            
            guard = BudgetGuard(mock_db_session)
            
            assert guard.settings == mock_settings
            assert guard.settings.ai_budget_soft_limit_multiplier == 3.0

    def test_budget_guard_database_integration(self, mock_db_session):
        """Test that BudgetGuard integrates with database correctly."""
        guard = BudgetGuard(mock_db_session)
        
        # Test that database session is stored
        assert guard.db == mock_db_session
        
        # Test that queries use the correct session
        guard.can_use_hosted_model("org_123", "caption")
        mock_db_session.query.assert_called()

    @pytest.mark.asyncio
    async def test_get_or_create_budget_database_error_handling(self, budget_guard, mock_db_session):
        """Test error handling in get_or_create_budget."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        mock_db_session.add.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            await budget_guard.get_or_create_budget("org_123")

    def test_record_usage_database_error_handling(self, budget_guard, mock_db_session):
        """Test error handling in record_usage."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        mock_db_session.commit.side_effect = Exception("Database error")
        
        with patch.object(budget_guard, 'get_or_create_budget', return_value=Mock()):
            with pytest.raises(Exception, match="Database error"):
                budget_guard.record_usage("org_123", 1000, 0.5)

    def test_can_use_hosted_model_database_error_handling(self, budget_guard, mock_db_session):
        """Test error handling in can_use_hosted_model."""
        mock_db_session.query.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            budget_guard.can_use_hosted_model("org_123", "caption")

    def test_get_usage_stats_database_error_handling(self, budget_guard, mock_db_session):
        """Test error handling in get_usage_stats."""
        mock_db_session.query.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            budget_guard.get_usage_stats("org_123")
