from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Awaitable
from enum import Enum

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.models.rules import Rule, RuleRun, RuleStatus
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class TriggerType(str, Enum):
    """Available trigger types for rules."""
    POST_PERFORMANCE = "post_performance"
    WEEKLY_BRIEF_GENERATED = "weekly_brief_generated"
    INBOX_MESSAGE_RECEIVED = "inbox_message_received"
    CAMPAIGN_CREATED = "campaign_created"
    SCHEDULE_POSTED = "schedule_posted"


class ActionType(str, Enum):
    """Available action types for rules."""
    CLONE_CONTENT_AND_RESCHEDULE = "clone_content_and_reschedule"
    INCREASE_BUDGET_PCT = "increase_budget_pct"
    PAUSE_UNDERPERFORMER = "pause_underperformer"
    SEND_NOTIFICATION = "send_notification"
    PAUSE_CAMPAIGN = "pause_campaign"
    RESUME_CAMPAIGN = "resume_campaign"


class RulesEngine:
    """Engine for evaluating and executing automation rules."""
    
    def __init__(self):
        self.settings = get_settings()
        self._triggers: Dict[TriggerType, List[Callable]] = {}
        self._actions: Dict[ActionType, Callable] = {}
        
        # Register default actions
        self._register_default_actions()
    
    def register_trigger(self, trigger_type: TriggerType, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Register a trigger handler."""
        if trigger_type not in self._triggers:
            self._triggers[trigger_type] = []
        self._triggers[trigger_type].append(handler)
        logger.info(f"Registered trigger handler for {trigger_type}")
    
    def register_action(self, action_type: ActionType, handler: Callable[[Dict[str, Any], Session], Awaitable[Dict[str, Any]]]):
        """Register an action handler."""
        self._actions[action_type] = handler
        logger.info(f"Registered action handler for {action_type}")
    
    async def process_trigger(self, trigger_type: TriggerType, payload: Dict[str, Any], db: Session) -> int:
        """Process a trigger event and execute matching rules."""
        if not self.settings.automations_enabled:
            logger.debug("Automations disabled, skipping trigger processing")
            return 0
        
        logger.info(f"Processing trigger {trigger_type} with payload: {payload}")
        
        # Get enabled rules for this trigger
        rules = db.execute(
            select(Rule).where(
                and_(
                    Rule.trigger == trigger_type.value,
                    Rule.enabled == True
                )
            )
        ).scalars().all()
        
        executed_count = 0
        
        for rule in rules:
            try:
                # Check cooldown period
                if self._is_in_cooldown(rule, db):
                    logger.debug(f"Rule {rule.id} is in cooldown, skipping")
                    continue
                
                # Evaluate condition
                if await self._evaluate_condition(rule.condition_json, payload):
                    logger.info(f"Rule {rule.id} condition met, executing action")
                    
                    # Execute action
                    result = await self._execute_action(rule.action_json, payload, db)
                    
                    # Record rule run
                    await self._record_rule_run(rule, RuleStatus.SUCCESS, result, db)
                    executed_count += 1
                else:
                    logger.debug(f"Rule {rule.id} condition not met")
                    
            except Exception as e:
                logger.error(f"Error executing rule {rule.id}: {e}")
                await self._record_rule_run(rule, RuleStatus.FAILED, {"error": str(e)}, db)
        
        return executed_count
    
    async def _evaluate_condition(self, condition: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        """Evaluate a JSON logic condition against the payload."""
        try:
            return self._evaluate_json_logic(condition, payload)
        except Exception as e:
            logger.error(f"Error evaluating condition: {e}")
            return False
    
    def _evaluate_json_logic(self, condition: Dict[str, Any], payload: Dict[str, Any]) -> bool:
        """Evaluate JSON logic expression."""
        if not isinstance(condition, dict):
            return False
        
        operator = condition.get("operator")
        if not operator:
            return False
        
        if operator == "eq":
            field = condition.get("field")
            value = condition.get("value")
            return self._get_nested_value(payload, field) == value
        
        elif operator == "gt":
            field = condition.get("field")
            value = condition.get("value")
            return self._get_nested_value(payload, field) > value
        
        elif operator == "lt":
            field = condition.get("field")
            value = condition.get("value")
            return self._get_nested_value(payload, field) < value
        
        elif operator == "in":
            field = condition.get("field")
            values = condition.get("value", [])
            return self._get_nested_value(payload, field) in values
        
        elif operator == "and":
            conditions = condition.get("conditions", [])
            return all(self._evaluate_json_logic(c, payload) for c in conditions)
        
        elif operator == "or":
            conditions = condition.get("conditions", [])
            return any(self._evaluate_json_logic(c, payload) for c in conditions)
        
        return False
    
    def _get_nested_value(self, data: Dict[str, Any], field: str) -> Any:
        """Get nested value from dictionary using dot notation."""
        keys = field.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        return value
    
    async def _execute_action(self, action: Dict[str, Any], payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Execute an action."""
        action_type = action.get("type")
        if not action_type:
            raise ValueError("Action type not specified")
        
        action_handler = self._actions.get(ActionType(action_type))
        if not action_handler:
            raise ValueError(f"Unknown action type: {action_type}")
        
        return await action_handler(action, payload, db)
    
    def _is_in_cooldown(self, rule: Rule, db: Session) -> bool:
        """Check if rule is in cooldown period."""
        cooldown_minutes = self.settings.rules_cooldown_minutes
        cutoff_time = datetime.utcnow() - timedelta(minutes=cooldown_minutes)
        
        recent_run = db.execute(
            select(RuleRun).where(
                and_(
                    RuleRun.rule_id == rule.id,
                    RuleRun.last_run_at >= cutoff_time,
                    RuleRun.status.in_([RuleStatus.SUCCESS, RuleStatus.FAILED])
                )
            ).order_by(RuleRun.last_run_at.desc())
        ).scalar_one_or_none()
        
        return recent_run is not None
    
    async def _record_rule_run(self, rule: Rule, status: RuleStatus, meta: Dict[str, Any], db: Session):
        """Record a rule run."""
        rule_run = RuleRun(
            id=f"rule_run_{rule.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            rule_id=rule.id,
            status=status,
            last_run_at=datetime.utcnow(),
            meta_json=meta,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow() if status in [RuleStatus.SUCCESS, RuleStatus.FAILED] else None
        )
        db.add(rule_run)
        db.commit()
    
    def _register_default_actions(self):
        """Register default action handlers."""
        self.register_action(ActionType.CLONE_CONTENT_AND_RESCHEDULE, self._clone_content_action)
        self.register_action(ActionType.INCREASE_BUDGET_PCT, self._increase_budget_action)
        self.register_action(ActionType.PAUSE_UNDERPERFORMER, self._pause_underperformer_action)
        self.register_action(ActionType.SEND_NOTIFICATION, self._send_notification_action)
        self.register_action(ActionType.PAUSE_CAMPAIGN, self._pause_campaign_action)
        self.register_action(ActionType.RESUME_CAMPAIGN, self._resume_campaign_action)
    
    async def _clone_content_action(self, action: Dict[str, Any], payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Clone content and reschedule action."""
        # This would integrate with the content cloning system
        logger.info("Executing clone_content_and_reschedule action")
        return {"action": "clone_content", "status": "executed"}
    
    async def _increase_budget_action(self, action: Dict[str, Any], payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Increase budget percentage action."""
        # This would integrate with the ads system
        logger.info("Executing increase_budget_pct action")
        return {"action": "increase_budget", "status": "executed"}
    
    async def _pause_underperformer_action(self, action: Dict[str, Any], payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Pause underperformer action."""
        logger.info("Executing pause_underperformer action")
        return {"action": "pause_underperformer", "status": "executed"}
    
    async def _send_notification_action(self, action: Dict[str, Any], payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Send notification action."""
        logger.info("Executing send_notification action")
        return {"action": "send_notification", "status": "executed"}
    
    async def _pause_campaign_action(self, action: Dict[str, Any], payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Pause campaign action."""
        logger.info("Executing pause_campaign action")
        return {"action": "pause_campaign", "status": "executed"}
    
    async def _resume_campaign_action(self, action: Dict[str, Any], payload: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """Resume campaign action."""
        logger.info("Executing resume_campaign action")
        return {"action": "resume_campaign", "status": "executed"}


# Global rules engine instance
rules_engine = RulesEngine()
