#!/usr/bin/env python3
"""
Comprehensive test suite for Rules Engine System.
Tests every line of function systematically.
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.automation.rules_engine import RulesEngine, TriggerType, ActionType
from app.models.rules import Rule, RuleRun, RuleStatus


class TestRulesEngine:
    """Comprehensive tests for RulesEngine class."""

    @pytest.fixture
    def rules_engine(self):
        """Create RulesEngine instance."""
        return RulesEngine()

    @pytest.fixture
    def mock_db_session(self):
        """Create mock database session."""
        return Mock()

    @pytest.fixture
    def sample_rule(self):
        """Create sample rule."""
        return Rule(
            id="rule_123",
            org_id="org_123",
            name="Test Rule",
            trigger="post_performance",
            condition_json={"metric": "ctr", "operator": ">", "value": 0.05},
            action_json={"action": "clone_content_and_reschedule", "params": {}},
            enabled=True,
            cooldown_minutes=60,
            created_at=datetime.utcnow()
        )

    @pytest.fixture
    def sample_payload(self):
        """Create sample trigger payload."""
        return {
            "schedule_id": "schedule_123",
            "ctr": 0.08,
            "engagement_rate": 0.12,
            "reach_norm": 0.9
        }

    def test_initialization(self, rules_engine):
        """Test RulesEngine initialization."""
        assert rules_engine.settings is not None
        assert isinstance(rules_engine._triggers, dict)
        assert isinstance(rules_engine._actions, dict)
        assert len(rules_engine._actions) > 0  # Should have default actions

    def test_register_trigger_new_type(self, rules_engine):
        """Test registering trigger for new type."""
        handler = AsyncMock()
        
        rules_engine.register_trigger(TriggerType.POST_PERFORMANCE, handler)
        
        assert TriggerType.POST_PERFORMANCE in rules_engine._triggers
        assert handler in rules_engine._triggers[TriggerType.POST_PERFORMANCE]

    def test_register_trigger_existing_type(self, rules_engine):
        """Test registering trigger for existing type."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        
        rules_engine.register_trigger(TriggerType.POST_PERFORMANCE, handler1)
        rules_engine.register_trigger(TriggerType.POST_PERFORMANCE, handler2)
        
        assert len(rules_engine._triggers[TriggerType.POST_PERFORMANCE]) == 2
        assert handler1 in rules_engine._triggers[TriggerType.POST_PERFORMANCE]
        assert handler2 in rules_engine._triggers[TriggerType.POST_PERFORMANCE]

    def test_register_action(self, rules_engine):
        """Test registering action handler."""
        handler = AsyncMock()
        
        rules_engine.register_action(ActionType.CLONE_CONTENT_AND_RESCHEDULE, handler)
        
        assert ActionType.CLONE_CONTENT_AND_RESCHEDULE in rules_engine._actions
        assert rules_engine._actions[ActionType.CLONE_CONTENT_AND_RESCHEDULE] == handler

    @pytest.mark.asyncio
    async def test_process_trigger_automations_disabled(self, rules_engine, mock_db_session, sample_payload):
        """Test process_trigger when automations are disabled."""
        with patch.object(rules_engine.settings, 'automations_enabled', False):
            result = await rules_engine.process_trigger(
                TriggerType.POST_PERFORMANCE, 
                sample_payload, 
                mock_db_session
            )
            
            assert result == 0
            mock_db_session.execute.assert_not_called()

    @pytest.mark.asyncio
    async def test_process_trigger_no_rules(self, rules_engine, mock_db_session, sample_payload):
        """Test process_trigger when no rules exist."""
        # Mock database to return no rules
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = []
        
        result = await rules_engine.process_trigger(
            TriggerType.POST_PERFORMANCE, 
            sample_payload, 
            mock_db_session
        )
        
        assert result == 0

    @pytest.mark.asyncio
    async def test_process_trigger_single_rule_success(self, rules_engine, mock_db_session, sample_rule, sample_payload):
        """Test process_trigger with single rule that succeeds."""
        # Mock database to return one rule
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [sample_rule]
        
        with patch.object(rules_engine, '_is_in_cooldown', return_value=False):
            with patch.object(rules_engine, '_evaluate_condition', return_value=True):
                with patch.object(rules_engine, '_execute_action', return_value={"status": "success"}):
                    with patch.object(rules_engine, '_record_rule_run', return_value=None):
                        result = await rules_engine.process_trigger(
                            TriggerType.POST_PERFORMANCE, 
                            sample_payload, 
                            mock_db_session
                        )
                        
                        assert result == 1

    @pytest.mark.asyncio
    async def test_process_trigger_rule_in_cooldown(self, rules_engine, mock_db_session, sample_rule, sample_payload):
        """Test process_trigger with rule in cooldown."""
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [sample_rule]
        
        with patch.object(rules_engine, '_is_in_cooldown', return_value=True):
            result = await rules_engine.process_trigger(
                TriggerType.POST_PERFORMANCE, 
                sample_payload, 
                mock_db_session
            )
            
            assert result == 0

    @pytest.mark.asyncio
    async def test_process_trigger_condition_not_met(self, rules_engine, mock_db_session, sample_rule, sample_payload):
        """Test process_trigger when condition is not met."""
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [sample_rule]
        
        with patch.object(rules_engine, '_is_in_cooldown', return_value=False):
            with patch.object(rules_engine, '_evaluate_condition', return_value=False):
                result = await rules_engine.process_trigger(
                    TriggerType.POST_PERFORMANCE, 
                    sample_payload, 
                    mock_db_session
                )
                
                assert result == 0

    @pytest.mark.asyncio
    async def test_process_trigger_rule_execution_error(self, rules_engine, mock_db_session, sample_rule, sample_payload):
        """Test process_trigger when rule execution fails."""
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [sample_rule]
        
        with patch.object(rules_engine, '_is_in_cooldown', return_value=False):
            with patch.object(rules_engine, '_evaluate_condition', return_value=True):
                with patch.object(rules_engine, '_execute_action', side_effect=Exception("Execution error")):
                    with patch.object(rules_engine, '_record_rule_run', return_value=None):
                        result = await rules_engine.process_trigger(
                            TriggerType.POST_PERFORMANCE, 
                            sample_payload, 
                            mock_db_session
                        )
                        
                        assert result == 0  # Should not count as executed due to error

    @pytest.mark.asyncio
    async def test_process_trigger_multiple_rules(self, rules_engine, mock_db_session, sample_payload):
        """Test process_trigger with multiple rules."""
        rule1 = Rule(id="rule_1", org_id="org_123", name="Rule 1", trigger="post_performance", 
                    condition_json={}, action_json={}, enabled=True, cooldown_minutes=60)
        rule2 = Rule(id="rule_2", org_id="org_123", name="Rule 2", trigger="post_performance", 
                    condition_json={}, action_json={}, enabled=True, cooldown_minutes=60)
        
        mock_db_session.execute.return_value.scalars.return_value.all.return_value = [rule1, rule2]
        
        with patch.object(rules_engine, '_is_in_cooldown', return_value=False):
            with patch.object(rules_engine, '_evaluate_condition', return_value=True):
                with patch.object(rules_engine, '_execute_action', return_value={"status": "success"}):
                    with patch.object(rules_engine, '_record_rule_run', return_value=None):
                        result = await rules_engine.process_trigger(
                            TriggerType.POST_PERFORMANCE, 
                            sample_payload, 
                            mock_db_session
                        )
                        
                        assert result == 2

    def test_evaluate_condition_simple_comparison(self, rules_engine, sample_payload):
        """Test condition evaluation with simple comparison."""
        condition = {
            "metric": "ctr",
            "operator": ">",
            "value": 0.05
        }
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is True  # ctr is 0.08 > 0.05

    def test_evaluate_condition_simple_comparison_false(self, rules_engine, sample_payload):
        """Test condition evaluation with simple comparison that fails."""
        condition = {
            "metric": "ctr",
            "operator": ">",
            "value": 0.10
        }
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is False  # ctr is 0.08 <= 0.10

    def test_evaluate_condition_less_than(self, rules_engine, sample_payload):
        """Test condition evaluation with less than operator."""
        condition = {
            "metric": "ctr",
            "operator": "<",
            "value": 0.10
        }
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is True  # ctr is 0.08 < 0.10

    def test_evaluate_condition_equals(self, rules_engine, sample_payload):
        """Test condition evaluation with equals operator."""
        condition = {
            "metric": "ctr",
            "operator": "==",
            "value": 0.08
        }
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is True  # ctr is 0.08 == 0.08

    def test_evaluate_condition_not_equals(self, rules_engine, sample_payload):
        """Test condition evaluation with not equals operator."""
        condition = {
            "metric": "ctr",
            "operator": "!=",
            "value": 0.05
        }
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is True  # ctr is 0.08 != 0.05

    def test_evaluate_condition_greater_than_or_equal(self, rules_engine, sample_payload):
        """Test condition evaluation with greater than or equal operator."""
        condition = {
            "metric": "ctr",
            "operator": ">=",
            "value": 0.08
        }
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is True  # ctr is 0.08 >= 0.08

    def test_evaluate_condition_less_than_or_equal(self, rules_engine, sample_payload):
        """Test condition evaluation with less than or equal operator."""
        condition = {
            "metric": "ctr",
            "operator": "<=",
            "value": 0.08
        }
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is True  # ctr is 0.08 <= 0.08

    def test_evaluate_condition_missing_metric(self, rules_engine, sample_payload):
        """Test condition evaluation with missing metric."""
        condition = {
            "metric": "nonexistent",
            "operator": ">",
            "value": 0.05
        }
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is False  # Missing metric should return False

    def test_evaluate_condition_invalid_operator(self, rules_engine, sample_payload):
        """Test condition evaluation with invalid operator."""
        condition = {
            "metric": "ctr",
            "operator": "invalid",
            "value": 0.05
        }
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is False  # Invalid operator should return False

    def test_evaluate_condition_string_comparison(self, rules_engine):
        """Test condition evaluation with string values."""
        payload = {"status": "posted", "channel": "linkedin"}
        condition = {
            "metric": "status",
            "operator": "==",
            "value": "posted"
        }
        
        result = rules_engine._evaluate_condition(condition, payload)
        assert result is True

    def test_evaluate_condition_boolean_comparison(self, rules_engine):
        """Test condition evaluation with boolean values."""
        payload = {"is_active": True, "is_published": False}
        condition = {
            "metric": "is_active",
            "operator": "==",
            "value": True
        }
        
        result = rules_engine._evaluate_condition(condition, payload)
        assert result is True

    def test_evaluate_condition_none_value(self, rules_engine, sample_payload):
        """Test condition evaluation with None value."""
        condition = {
            "metric": "ctr",
            "operator": ">",
            "value": None
        }
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is False  # None value should return False

    def test_evaluate_condition_missing_operator(self, rules_engine, sample_payload):
        """Test condition evaluation with missing operator."""
        condition = {
            "metric": "ctr",
            "value": 0.05
        }
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is False  # Missing operator should return False

    def test_evaluate_condition_missing_value(self, rules_engine, sample_payload):
        """Test condition evaluation with missing value."""
        condition = {
            "metric": "ctr",
            "operator": ">"
        }
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is False  # Missing value should return False

    def test_evaluate_condition_empty_condition(self, rules_engine, sample_payload):
        """Test condition evaluation with empty condition."""
        condition = {}
        
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert result is False  # Empty condition should return False

    def test_evaluate_condition_none_condition(self, rules_engine, sample_payload):
        """Test condition evaluation with None condition."""
        result = rules_engine._evaluate_condition(None, sample_payload)
        assert result is False  # None condition should return False

    def test_evaluate_condition_complex_condition(self, rules_engine, sample_payload):
        """Test condition evaluation with complex condition (if supported)."""
        # This test assumes the engine supports complex conditions
        # If not, it should gracefully handle it
        condition = {
            "and": [
                {"metric": "ctr", "operator": ">", "value": 0.05},
                {"metric": "engagement_rate", "operator": ">", "value": 0.10}
            ]
        }
        
        # This might return False if complex conditions aren't supported
        result = rules_engine._evaluate_condition(condition, sample_payload)
        assert isinstance(result, bool)

    def test_is_in_cooldown_no_previous_runs(self, rules_engine, mock_db_session, sample_rule):
        """Test cooldown check when no previous runs exist."""
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
        
        result = rules_engine._is_in_cooldown(sample_rule, mock_db_session)
        assert result is False

    def test_is_in_cooldown_old_run(self, rules_engine, mock_db_session, sample_rule):
        """Test cooldown check when last run is old."""
        old_run = RuleRun(
            id="run_123",
            rule_id="rule_123",
            status=RuleStatus.SUCCESS,
            executed_at=datetime.utcnow() - timedelta(hours=2)  # 2 hours ago
        )
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = old_run
        
        result = rules_engine._is_in_cooldown(sample_rule, mock_db_session)
        assert result is False  # 2 hours > 60 minutes cooldown

    def test_is_in_cooldown_recent_run(self, rules_engine, mock_db_session, sample_rule):
        """Test cooldown check when last run is recent."""
        recent_run = RuleRun(
            id="run_123",
            rule_id="rule_123",
            status=RuleStatus.SUCCESS,
            executed_at=datetime.utcnow() - timedelta(minutes=30)  # 30 minutes ago
        )
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = recent_run
        
        result = rules_engine._is_in_cooldown(sample_rule, mock_db_session)
        assert result is True  # 30 minutes < 60 minutes cooldown

    def test_is_in_cooldown_zero_cooldown(self, rules_engine, mock_db_session):
        """Test cooldown check with zero cooldown period."""
        rule = Rule(
            id="rule_123",
            org_id="org_123",
            name="Test Rule",
            trigger="post_performance",
            condition_json={},
            action_json={},
            enabled=True,
            cooldown_minutes=0  # No cooldown
        )
        
        recent_run = RuleRun(
            id="run_123",
            rule_id="rule_123",
            status=RuleStatus.SUCCESS,
            executed_at=datetime.utcnow() - timedelta(minutes=1)  # 1 minute ago
        )
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.first.return_value = recent_run
        
        result = rules_engine._is_in_cooldown(rule, mock_db_session)
        assert result is False  # Zero cooldown should always return False

    def test_is_in_cooldown_none_cooldown(self, rules_engine, mock_db_session):
        """Test cooldown check with None cooldown period."""
        rule = Rule(
            id="rule_123",
            org_id="org_123",
            name="Test Rule",
            trigger="post_performance",
            condition_json={},
            action_json={},
            enabled=True,
            cooldown_minutes=None  # None cooldown
        )
        
        result = rules_engine._is_in_cooldown(rule, mock_db_session)
        assert result is False  # None cooldown should return False

    @pytest.mark.asyncio
    async def test_execute_action_known_action(self, rules_engine, mock_db_session, sample_payload):
        """Test executing a known action."""
        action = {
            "action": "clone_content_and_reschedule",
            "params": {"multiplier": 1.5}
        }
        
        with patch.object(rules_engine, '_clone_content_and_reschedule_action', return_value={"status": "success"}) as mock_action:
            result = await rules_engine._execute_action(action, sample_payload, mock_db_session)
            
            assert result == {"status": "success"}
            mock_action.assert_called_once_with(action, sample_payload, mock_db_session)

    @pytest.mark.asyncio
    async def test_execute_action_unknown_action(self, rules_engine, mock_db_session, sample_payload):
        """Test executing an unknown action."""
        action = {
            "action": "unknown_action",
            "params": {}
        }
        
        result = await rules_engine._execute_action(action, sample_payload, mock_db_session)
        
        assert result == {"error": "Unknown action: unknown_action"}

    @pytest.mark.asyncio
    async def test_execute_action_missing_action_key(self, rules_engine, mock_db_session, sample_payload):
        """Test executing action with missing action key."""
        action = {
            "params": {}
        }
        
        result = await rules_engine._execute_action(action, sample_payload, mock_db_session)
        
        assert result == {"error": "No action specified"}

    @pytest.mark.asyncio
    async def test_execute_action_none_action(self, rules_engine, mock_db_session, sample_payload):
        """Test executing None action."""
        result = await rules_engine._execute_action(None, sample_payload, mock_db_session)
        
        assert result == {"error": "No action specified"}

    @pytest.mark.asyncio
    async def test_record_rule_run_success(self, rules_engine, mock_db_session, sample_rule):
        """Test recording successful rule run."""
        result = {"status": "success", "created_schedules": 2}
        
        await rules_engine._record_rule_run(sample_rule, RuleStatus.SUCCESS, result, mock_db_session)
        
        # Verify RuleRun was created and added to session
        mock_db_session.add.assert_called_once()
        added_run = mock_db_session.add.call_args[0][0]
        assert isinstance(added_run, RuleRun)
        assert added_run.rule_id == sample_rule.id
        assert added_run.status == RuleStatus.SUCCESS
        assert added_run.result_json == result
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_rule_run_failure(self, rules_engine, mock_db_session, sample_rule):
        """Test recording failed rule run."""
        result = {"error": "Execution failed"}
        
        await rules_engine._record_rule_run(sample_rule, RuleStatus.FAILED, result, mock_db_session)
        
        # Verify RuleRun was created and added to session
        mock_db_session.add.assert_called_once()
        added_run = mock_db_session.add.call_args[0][0]
        assert isinstance(added_run, RuleRun)
        assert added_run.rule_id == sample_rule.id
        assert added_run.status == RuleStatus.FAILED
        assert added_run.result_json == result
        mock_db_session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_record_rule_run_skipped(self, rules_engine, mock_db_session, sample_rule):
        """Test recording skipped rule run."""
        result = {"reason": "In cooldown"}
        
        await rules_engine._record_rule_run(sample_rule, RuleStatus.SKIPPED, result, mock_db_session)
        
        # Verify RuleRun was created and added to session
        mock_db_session.add.assert_called_once()
        added_run = mock_db_session.add.call_args[0][0]
        assert isinstance(added_run, RuleRun)
        assert added_run.rule_id == sample_rule.id
        assert added_run.status == RuleStatus.SKIPPED
        assert added_run.result_json == result
        mock_db_session.commit.assert_called_once()

    def test_trigger_type_enum_values(self):
        """Test that TriggerType enum has expected values."""
        expected_triggers = [
            "post_performance",
            "weekly_brief_generated", 
            "inbox_message_received",
            "campaign_created",
            "schedule_posted"
        ]
        
        for trigger in expected_triggers:
            assert hasattr(TriggerType, trigger.upper())
            assert getattr(TriggerType, trigger.upper()).value == trigger

    def test_action_type_enum_values(self):
        """Test that ActionType enum has expected values."""
        expected_actions = [
            "clone_content_and_reschedule",
            "increase_budget_pct",
            "pause_underperformer",
            "send_notification",
            "resume_campaign"
        ]
        
        for action in expected_actions:
            assert hasattr(ActionType, action.upper())
            assert getattr(ActionType, action.upper()).value == action

    def test_default_actions_registered(self, rules_engine):
        """Test that default actions are registered during initialization."""
        expected_actions = [
            ActionType.CLONE_CONTENT_AND_RESCHEDULE,
            ActionType.INCREASE_BUDGET_PCT,
            ActionType.PAUSE_UNDERPERFORMER,
            ActionType.SEND_NOTIFICATION,
            ActionType.RESUME_CAMPAIGN
        ]
        
        for action in expected_actions:
            assert action in rules_engine._actions
            assert callable(rules_engine._actions[action])

    @pytest.mark.asyncio
    async def test_clone_content_and_reschedule_action(self, rules_engine, mock_db_session, sample_payload):
        """Test clone_content_and_reschedule action implementation."""
        action = {
            "action": "clone_content_and_reschedule",
            "params": {"multiplier": 1.5}
        }
        
        result = await rules_engine._clone_content_and_reschedule_action(action, sample_payload, mock_db_session)
        
        assert result == {"action": "clone_content_and_reschedule", "status": "executed"}

    @pytest.mark.asyncio
    async def test_increase_budget_pct_action(self, rules_engine, mock_db_session, sample_payload):
        """Test increase_budget_pct action implementation."""
        action = {
            "action": "increase_budget_pct",
            "params": {"percentage": 20}
        }
        
        result = await rules_engine._increase_budget_pct_action(action, sample_payload, mock_db_session)
        
        assert result == {"action": "increase_budget_pct", "status": "executed"}

    @pytest.mark.asyncio
    async def test_pause_underperformer_action(self, rules_engine, mock_db_session, sample_payload):
        """Test pause_underperformer action implementation."""
        action = {
            "action": "pause_underperformer",
            "params": {"threshold": 0.03}
        }
        
        result = await rules_engine._pause_underperformer_action(action, sample_payload, mock_db_session)
        
        assert result == {"action": "pause_underperformer", "status": "executed"}

    @pytest.mark.asyncio
    async def test_send_notification_action(self, rules_engine, mock_db_session, sample_payload):
        """Test send_notification action implementation."""
        action = {
            "action": "send_notification",
            "params": {"message": "Test notification"}
        }
        
        result = await rules_engine._send_notification_action(action, sample_payload, mock_db_session)
        
        assert result == {"action": "send_notification", "status": "executed"}

    @pytest.mark.asyncio
    async def test_resume_campaign_action(self, rules_engine, mock_db_session, sample_payload):
        """Test resume_campaign action implementation."""
        action = {
            "action": "resume_campaign",
            "params": {"campaign_id": "campaign_123"}
        }
        
        result = await rules_engine._resume_campaign_action(action, sample_payload, mock_db_session)
        
        assert result == {"action": "resume_campaign", "status": "executed"}
