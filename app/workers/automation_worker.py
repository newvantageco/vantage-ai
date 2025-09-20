"""
Automation Worker
Handles execution of automation rules, workflows, recommendations, and A/B tests
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from celery import current_task
from app.workers.celery_app import celery_app
from app.db.session import get_db
from app.services.automation import AutomationService
from app.models.rules import Rule, RuleRun, RuleStatus
from app.models.automation import (
    Workflow, WorkflowExecution, WorkflowStatus,
    Recommendation, RecommendationType, RecommendationStatus,
    ABTest, ABTestStatus
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(bind=True, max_retries=3)
def process_automation_rules(self):
    """Process all enabled automation rules."""
    try:
        db = next(get_db())
        automation_service = AutomationService(db)
        
        # Get all enabled rules
        rules = db.query(Rule).filter(Rule.enabled == True).all()
        
        processed_count = 0
        for rule in rules:
            try:
                # This would integrate with the rules engine to process triggers
                # For now, we'll just log the rule processing
                logger.info(f"Processing rule: {rule.name}")
                processed_count += 1
            except Exception as e:
                logger.error(f"Error processing rule {rule.id}: {e}")
                continue
        
        logger.info(f"Processed {processed_count} automation rules")
        return {"success": True, "processed_count": processed_count}
        
    except Exception as e:
        logger.error(f"Error in process_automation_rules: {e}")
        self.retry(exc=e)
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, max_retries=3)
def execute_workflow(self, workflow_id: str, trigger_data: Optional[Dict[str, Any]] = None):
    """Execute a specific workflow."""
    try:
        db = next(get_db())
        automation_service = AutomationService(db)
        
        # Get workflow
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if not workflow.enabled:
            raise ValueError(f"Workflow {workflow_id} is disabled")
        
        # Execute workflow
        execution = await automation_service.execute_workflow(workflow_id, workflow.org_id, trigger_data)
        
        logger.info(f"Executed workflow {workflow_id}: {execution.status}")
        return {"success": True, "execution_id": execution.id, "status": execution.status}
        
    except Exception as e:
        logger.error(f"Error executing workflow {workflow_id}: {e}")
        self.retry(exc=e)
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, max_retries=3)
def generate_smart_recommendations(self, org_id: str, content_id: Optional[str] = None, campaign_id: Optional[str] = None):
    """Generate smart recommendations for an organization."""
    try:
        db = next(get_db())
        automation_service = AutomationService(db)
        
        # Generate recommendations
        recommendations = await automation_service.generate_recommendations(
            org_id, content_id, campaign_id
        )
        
        logger.info(f"Generated {len(recommendations)} recommendations for organization {org_id}")
        return {"success": True, "recommendations_count": len(recommendations)}
        
    except Exception as e:
        logger.error(f"Error generating recommendations for org {org_id}: {e}")
        self.retry(exc=e)
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, max_retries=3)
def process_ab_test_metrics(self, ab_test_id: str):
    """Process metrics for an A/B test."""
    try:
        db = next(get_db())
        
        # Get A/B test
        ab_test = db.query(ABTest).filter(ABTest.id == ab_test_id).first()
        if not ab_test:
            raise ValueError(f"A/B test {ab_test_id} not found")
        
        if ab_test.status != ABTestStatus.RUNNING:
            logger.info(f"A/B test {ab_test_id} is not running, skipping metrics processing")
            return {"success": True, "skipped": True}
        
        # This would integrate with analytics service to collect metrics
        # For now, we'll just log the processing
        logger.info(f"Processing metrics for A/B test {ab_test_id}")
        
        # Check if test should be completed
        if ab_test.start_date and ab_test.end_date:
            if datetime.utcnow() >= ab_test.end_date:
                # Complete the test
                await automation_service.stop_ab_test(ab_test_id, ab_test.org_id)
                logger.info(f"Completed A/B test {ab_test_id}")
        
        return {"success": True, "processed": True}
        
    except Exception as e:
        logger.error(f"Error processing A/B test metrics for {ab_test_id}: {e}")
        self.retry(exc=e)
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, max_retries=3)
def cleanup_expired_recommendations(self):
    """Clean up expired recommendations."""
    try:
        db = next(get_db())
        
        # Get expired recommendations
        expired_recommendations = db.query(Recommendation).filter(
            Recommendation.expires_at < datetime.utcnow(),
            Recommendation.status == RecommendationStatus.PENDING
        ).all()
        
        # Mark as expired
        for rec in expired_recommendations:
            rec.status = RecommendationStatus.EXPIRED
            rec.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Marked {len(expired_recommendations)} recommendations as expired")
        return {"success": True, "expired_count": len(expired_recommendations)}
        
    except Exception as e:
        logger.error(f"Error cleaning up expired recommendations: {e}")
        self.retry(exc=e)
    finally:
        if 'db' in locals():
            db.close()


@celery_app.task(bind=True, max_retries=3)
def process_workflow_triggers(self):
    """Process workflow triggers and execute eligible workflows."""
    try:
        db = next(get_db())
        
        # Get active workflows
        workflows = db.query(Workflow).filter(
            Workflow.enabled == True,
            Workflow.status == WorkflowStatus.ACTIVE
        ).all()
        
        executed_count = 0
        for workflow in workflows:
            try:
                # Check if workflow should be triggered
                should_trigger = await check_workflow_trigger(workflow)
                
                if should_trigger:
                    # Execute workflow
                    execute_workflow.delay(workflow.id)
                    executed_count += 1
                    logger.info(f"Triggered workflow {workflow.id}")
                
            except Exception as e:
                logger.error(f"Error checking trigger for workflow {workflow.id}: {e}")
                continue
        
        logger.info(f"Triggered {executed_count} workflows")
        return {"success": True, "triggered_count": executed_count}
        
    except Exception as e:
        logger.error(f"Error processing workflow triggers: {e}")
        self.retry(exc=e)
    finally:
        if 'db' in locals():
            db.close()


async def check_workflow_trigger(workflow: Workflow) -> bool:
    """Check if a workflow should be triggered based on its trigger configuration."""
    try:
        trigger_type = workflow.trigger_type
        trigger_config = workflow.trigger_config
        
        if trigger_type == "scheduled":
            # Check if it's time to run based on schedule
            return await check_scheduled_trigger(trigger_config)
        elif trigger_type == "event_based":
            # Check if the event has occurred
            return await check_event_trigger(trigger_config)
        elif trigger_type == "webhook":
            # This would be handled by webhook endpoints
            return False
        elif trigger_type == "manual":
            # Manual triggers are handled by API endpoints
            return False
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking workflow trigger: {e}")
        return False


async def check_scheduled_trigger(trigger_config: Dict[str, Any]) -> bool:
    """Check if a scheduled trigger should fire."""
    try:
        schedule_type = trigger_config.get("type", "interval")
        
        if schedule_type == "interval":
            # Check if enough time has passed since last run
            interval_minutes = trigger_config.get("interval_minutes", 60)
            last_run = trigger_config.get("last_run")
            
            if not last_run:
                return True
            
            last_run_time = datetime.fromisoformat(last_run.replace('Z', '+00:00'))
            return datetime.utcnow() - last_run_time >= timedelta(minutes=interval_minutes)
        
        elif schedule_type == "cron":
            # This would integrate with a cron parser
            # For now, return False
            return False
        
        return False
        
    except Exception as e:
        logger.error(f"Error checking scheduled trigger: {e}")
        return False


async def check_event_trigger(trigger_config: Dict[str, Any]) -> bool:
    """Check if an event-based trigger should fire."""
    try:
        event_type = trigger_config.get("event_type")
        event_data = trigger_config.get("event_data", {})
        
        # This would integrate with event system
        # For now, return False
        return False
        
    except Exception as e:
        logger.error(f"Error checking event trigger: {e}")
        return False


# Beat schedule for automation tasks
celery_app.conf.beat_schedule.update({
    # Process automation rules every 5 minutes
    "process-automation-rules": {
        "task": "app.workers.automation_worker.process_automation_rules",
        "schedule": 300,  # 5 minutes
    },
    # Process workflow triggers every minute
    "process-workflow-triggers": {
        "task": "app.workers.automation_worker.process_workflow_triggers",
        "schedule": 60,  # 1 minute
    },
    # Generate recommendations every hour
    "generate-recommendations": {
        "task": "app.workers.automation_worker.generate_smart_recommendations",
        "schedule": 3600,  # 1 hour
    },
    # Process A/B test metrics every 10 minutes
    "process-ab-test-metrics": {
        "task": "app.workers.automation_worker.process_ab_test_metrics",
        "schedule": 600,  # 10 minutes
    },
    # Clean up expired recommendations daily
    "cleanup-expired-recommendations": {
        "task": "app.workers.automation_worker.cleanup_expired_recommendations",
        "schedule": 86400,  # 24 hours
    },
})
