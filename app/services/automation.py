"""
Automation Service
Handles automation rules, workflows, recommendations, and A/B testing logic
"""

from __future__ import annotations

import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_, desc, func

from app.models.rules import Rule, RuleRun, RuleStatus
from app.models.automation import (
    Workflow, WorkflowExecution, WorkflowStatus, WorkflowTriggerType, WorkflowStepType,
    Recommendation, RecommendationType, RecommendationStatus,
    ABTest, ABTestVariant, ABTestResult, ABTestStatus, ABTestVariantStatus
)
from app.schemas.automation import (
    RuleCreate, RuleUpdate, WorkflowCreate, WorkflowUpdate,
    RecommendationUpdate, ABTestCreate, ABTestUpdate,
    AutomationValidator
)
from app.services.ai.performance_predictor import PerformancePredictor
from app.services.analytics.analytics_service import AnalyticsService
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AutomationService:
    """Service for managing automation features."""
    
    def __init__(self, db: Session):
        self.db = db
        self.performance_predictor = PerformancePredictor()
        self.analytics_service = AnalyticsService(db)
    
    # Rule Management
    async def create_rule(self, org_id: str, rule_data: RuleCreate) -> Rule:
        """Create a new automation rule."""
        rule_id = str(uuid.uuid4())
        
        rule = Rule(
            id=rule_id,
            org_id=org_id,
            name=rule_data.name,
            description=rule_data.description,
            trigger=rule_data.trigger,
            condition_json=rule_data.condition_json,
            action_json=rule_data.action_json,
            enabled=rule_data.enabled
        )
        
        self.db.add(rule)
        self.db.commit()
        self.db.refresh(rule)
        
        logger.info(f"Created rule {rule_id} for organization {org_id}")
        return rule
    
    async def update_rule(self, rule_id: str, org_id: str, rule_data: RuleUpdate) -> Rule:
        """Update an automation rule."""
        rule = self.db.execute(
            select(Rule).where(
                and_(Rule.id == rule_id, Rule.org_id == org_id)
            )
        ).scalar_one_or_none()
        
        if not rule:
            raise ValueError("Rule not found")
        
        update_data = rule_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(rule, field, value)
        
        rule.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(rule)
        
        logger.info(f"Updated rule {rule_id}")
        return rule
    
    async def delete_rule(self, rule_id: str, org_id: str) -> None:
        """Delete an automation rule."""
        rule = self.db.execute(
            select(Rule).where(
                and_(Rule.id == rule_id, Rule.org_id == org_id)
            )
        ).scalar_one_or_none()
        
        if not rule:
            raise ValueError("Rule not found")
        
        self.db.delete(rule)
        self.db.commit()
        
        logger.info(f"Deleted rule {rule_id}")
    
    async def toggle_rule(self, rule_id: str, org_id: str, enabled: bool) -> Rule:
        """Enable or disable an automation rule."""
        rule = self.db.execute(
            select(Rule).where(
                and_(Rule.id == rule_id, Rule.org_id == org_id)
            )
        ).scalar_one_or_none()
        
        if not rule:
            raise ValueError("Rule not found")
        
        rule.enabled = enabled
        rule.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(rule)
        
        logger.info(f"Toggled rule {rule_id} to {'enabled' if enabled else 'disabled'}")
        return rule
    
    # Workflow Management
    async def create_workflow(self, org_id: str, workflow_data: WorkflowCreate) -> Workflow:
        """Create a new workflow."""
        # Validate workflow steps
        validated_steps = AutomationValidator.validate_workflow_steps(workflow_data.steps)
        
        workflow_id = str(uuid.uuid4())
        
        # Convert steps to dict format for storage
        steps_data = [step.dict() for step in validated_steps]
        
        workflow = Workflow(
            id=workflow_id,
            org_id=org_id,
            name=workflow_data.name,
            description=workflow_data.description,
            trigger_type=workflow_data.trigger_type,
            trigger_config=workflow_data.trigger_config,
            steps=steps_data,
            enabled=workflow_data.enabled
        )
        
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        
        logger.info(f"Created workflow {workflow_id} for organization {org_id}")
        return workflow
    
    async def update_workflow(self, workflow_id: str, org_id: str, workflow_data: WorkflowUpdate) -> Workflow:
        """Update a workflow."""
        workflow = self.db.execute(
            select(Workflow).where(
                and_(Workflow.id == workflow_id, Workflow.org_id == org_id)
            )
        ).scalar_one_or_none()
        
        if not workflow:
            raise ValueError("Workflow not found")
        
        update_data = workflow_data.dict(exclude_unset=True)
        
        # Validate steps if provided
        if 'steps' in update_data and update_data['steps']:
            validated_steps = AutomationValidator.validate_workflow_steps(update_data['steps'])
            update_data['steps'] = [step.dict() for step in validated_steps]
        
        for field, value in update_data.items():
            setattr(workflow, field, value)
        
        workflow.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(workflow)
        
        logger.info(f"Updated workflow {workflow_id}")
        return workflow
    
    async def delete_workflow(self, workflow_id: str, org_id: str) -> None:
        """Delete a workflow."""
        workflow = self.db.execute(
            select(Workflow).where(
                and_(Workflow.id == workflow_id, Workflow.org_id == org_id)
            )
        ).scalar_one_or_none()
        
        if not workflow:
            raise ValueError("Workflow not found")
        
        self.db.delete(workflow)
        self.db.commit()
        
        logger.info(f"Deleted workflow {workflow_id}")
    
    async def execute_workflow(self, workflow_id: str, org_id: str, trigger_data: Optional[Dict[str, Any]] = None) -> WorkflowExecution:
        """Execute a workflow manually."""
        workflow = self.db.execute(
            select(Workflow).where(
                and_(Workflow.id == workflow_id, Workflow.org_id == org_id)
            )
        ).scalar_one_or_none()
        
        if not workflow:
            raise ValueError("Workflow not found")
        
        if not workflow.enabled:
            raise ValueError("Workflow is disabled")
        
        execution_id = str(uuid.uuid4())
        
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            status=WorkflowStatus.RUNNING,
            trigger_data=trigger_data,
            started_at=datetime.utcnow()
        )
        
        self.db.add(execution)
        self.db.commit()
        
        try:
            # Execute workflow steps
            result = await self._execute_workflow_steps(workflow, trigger_data or {})
            
            execution.status = WorkflowStatus.COMPLETED
            execution.execution_data = result
            execution.completed_at = datetime.utcnow()
            
            # Update workflow statistics
            workflow.run_count += 1
            workflow.success_count += 1
            workflow.last_run_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            
            # Update workflow statistics
            workflow.run_count += 1
            workflow.failure_count += 1
            workflow.last_run_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(execution)
        
        logger.info(f"Executed workflow {workflow_id}, status: {execution.status}")
        return execution
    
    async def _execute_workflow_steps(self, workflow: Workflow, trigger_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow steps in sequence."""
        results = {}
        current_step = None
        
        # Find the first step (position 0)
        first_step = next((step for step in workflow.steps if step.get('position') == 0), None)
        if not first_step:
            raise ValueError("No starting step found in workflow")
        
        current_step = first_step
        step_results = {}
        
        while current_step:
            step_type = current_step.get('step_type')
            step_config = current_step.get('config', {})
            step_name = current_step.get('name', 'Unknown')
            
            logger.info(f"Executing workflow step: {step_name} ({step_type})")
            
            try:
                if step_type == WorkflowStepType.CONDITION:
                    result = await self._execute_condition_step(current_step, trigger_data, step_results)
                elif step_type == WorkflowStepType.ACTION:
                    result = await self._execute_action_step(current_step, trigger_data, step_results)
                elif step_type == WorkflowStepType.DELAY:
                    result = await self._execute_delay_step(current_step, trigger_data, step_results)
                elif step_type == WorkflowStepType.WEBHOOK:
                    result = await self._execute_webhook_step(current_step, trigger_data, step_results)
                elif step_type == WorkflowStepType.AI_TASK:
                    result = await self._execute_ai_task_step(current_step, trigger_data, step_results)
                elif step_type == WorkflowStepType.NOTIFICATION:
                    result = await self._execute_notification_step(current_step, trigger_data, step_results)
                else:
                    raise ValueError(f"Unknown step type: {step_type}")
                
                step_results[current_step.get('position')] = result
                
                # Determine next step
                next_steps = current_step.get('next_steps', [])
                if next_steps:
                    # For now, take the first next step (could be enhanced for branching logic)
                    next_position = next_steps[0]
                    current_step = next((step for step in workflow.steps if step.get('position') == next_position), None)
                else:
                    current_step = None
                    
            except Exception as e:
                logger.error(f"Error executing step {step_name}: {e}")
                raise
        
        return {
            'step_results': step_results,
            'total_steps': len(workflow.steps),
            'completed_at': datetime.utcnow().isoformat()
        }
    
    async def _execute_condition_step(self, step: Dict[str, Any], trigger_data: Dict[str, Any], step_results: Dict[int, Any]) -> Dict[str, Any]:
        """Execute a condition step."""
        # This would implement JSON logic evaluation similar to rules engine
        return {"condition_result": True, "evaluated_at": datetime.utcnow().isoformat()}
    
    async def _execute_action_step(self, step: Dict[str, Any], trigger_data: Dict[str, Any], step_results: Dict[int, Any]) -> Dict[str, Any]:
        """Execute an action step."""
        # This would integrate with existing action handlers
        return {"action_result": "completed", "executed_at": datetime.utcnow().isoformat()}
    
    async def _execute_delay_step(self, step: Dict[str, Any], trigger_data: Dict[str, Any], step_results: Dict[int, Any]) -> Dict[str, Any]:
        """Execute a delay step."""
        delay_seconds = step.get('config', {}).get('delay_seconds', 0)
        # In a real implementation, this would be handled by a task queue
        return {"delay_completed": True, "delay_seconds": delay_seconds}
    
    async def _execute_webhook_step(self, step: Dict[str, Any], trigger_data: Dict[str, Any], step_results: Dict[int, Any]) -> Dict[str, Any]:
        """Execute a webhook step."""
        # This would make HTTP requests to external webhooks
        return {"webhook_result": "sent", "executed_at": datetime.utcnow().isoformat()}
    
    async def _execute_ai_task_step(self, step: Dict[str, Any], trigger_data: Dict[str, Any], step_results: Dict[int, Any]) -> Dict[str, Any]:
        """Execute an AI task step."""
        # This would integrate with AI services
        return {"ai_task_result": "completed", "executed_at": datetime.utcnow().isoformat()}
    
    async def _execute_notification_step(self, step: Dict[str, Any], trigger_data: Dict[str, Any], step_results: Dict[int, Any]) -> Dict[str, Any]:
        """Execute a notification step."""
        # This would send notifications via email, SMS, etc.
        return {"notification_sent": True, "executed_at": datetime.utcnow().isoformat()}
    
    # Recommendation Management
    async def generate_recommendations(
        self, 
        org_id: str, 
        content_id: Optional[str] = None, 
        campaign_id: Optional[str] = None,
        types: Optional[List[RecommendationType]] = None
    ) -> List[Recommendation]:
        """Generate smart recommendations based on performance data."""
        recommendations = []
        
        # Get performance data for analysis
        performance_data = await self.analytics_service.get_performance_summary(org_id)
        
        # Generate different types of recommendations
        recommendation_types = types or [
            RecommendationType.CONTENT_OPTIMIZATION,
            RecommendationType.POSTING_TIME,
            RecommendationType.HASHTAG_SUGGESTION,
            RecommendationType.AUDIENCE_TARGETING
        ]
        
        for rec_type in recommendation_types:
            try:
                if rec_type == RecommendationType.CONTENT_OPTIMIZATION:
                    recs = await self._generate_content_optimization_recommendations(org_id, performance_data)
                elif rec_type == RecommendationType.POSTING_TIME:
                    recs = await self._generate_posting_time_recommendations(org_id, performance_data)
                elif rec_type == RecommendationType.HASHTAG_SUGGESTION:
                    recs = await self._generate_hashtag_recommendations(org_id, performance_data)
                elif rec_type == RecommendationType.AUDIENCE_TARGETING:
                    recs = await self._generate_audience_targeting_recommendations(org_id, performance_data)
                else:
                    continue
                
                recommendations.extend(recs)
                
            except Exception as e:
                logger.error(f"Error generating {rec_type} recommendations: {e}")
                continue
        
        # Save recommendations to database
        for rec in recommendations:
            self.db.add(rec)
        
        self.db.commit()
        
        logger.info(f"Generated {len(recommendations)} recommendations for organization {org_id}")
        return recommendations
    
    async def _generate_content_optimization_recommendations(self, org_id: str, performance_data: Dict[str, Any]) -> List[Recommendation]:
        """Generate content optimization recommendations."""
        recommendations = []
        
        # Analyze top performing content
        top_content = performance_data.get('top_performing_content', [])
        if not top_content:
            return recommendations
        
        # Find patterns in successful content
        avg_engagement = sum(item.get('engagement_rate', 0) for item in top_content) / len(top_content)
        
        if avg_engagement > 0.05:  # 5% engagement threshold
            rec_id = str(uuid.uuid4())
            recommendation = Recommendation(
                id=rec_id,
                org_id=org_id,
                type=RecommendationType.CONTENT_OPTIMIZATION,
                title="Optimize Content Length",
                description=f"Your top-performing content averages {avg_engagement:.1%} engagement. Consider creating more content with similar characteristics.",
                confidence_score=0.8,
                data={
                    "avg_engagement": avg_engagement,
                    "sample_size": len(top_content),
                    "recommended_actions": [
                        "Maintain similar content length",
                        "Use similar tone and style",
                        "Post at similar times"
                    ]
                },
                priority=3,
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_posting_time_recommendations(self, org_id: str, performance_data: Dict[str, Any]) -> List[Recommendation]:
        """Generate posting time recommendations."""
        recommendations = []
        
        # Analyze performance by hour of day
        hourly_performance = performance_data.get('hourly_performance', {})
        if not hourly_performance:
            return recommendations
        
        # Find best performing hours
        best_hours = sorted(hourly_performance.items(), key=lambda x: x[1].get('engagement_rate', 0), reverse=True)[:3]
        
        if best_hours:
            rec_id = str(uuid.uuid4())
            best_hour, best_metrics = best_hours[0]
            
            recommendation = Recommendation(
                id=rec_id,
                org_id=org_id,
                type=RecommendationType.POSTING_TIME,
                title="Optimize Posting Schedule",
                description=f"Your content performs best at {best_hour}:00 with {best_metrics.get('engagement_rate', 0):.1%} engagement rate.",
                confidence_score=0.7,
                data={
                    "best_hours": [hour for hour, _ in best_hours],
                    "engagement_rates": {hour: metrics.get('engagement_rate', 0) for hour, metrics in best_hours},
                    "recommended_schedule": f"Post between {best_hour}:00-{int(best_hour)+1}:00"
                },
                priority=2,
                expires_at=datetime.utcnow() + timedelta(days=14)
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_hashtag_recommendations(self, org_id: str, performance_data: Dict[str, Any]) -> List[Recommendation]:
        """Generate hashtag recommendations."""
        recommendations = []
        
        # Analyze hashtag performance
        hashtag_performance = performance_data.get('hashtag_performance', {})
        if not hashtag_performance:
            return recommendations
        
        # Find top performing hashtags
        top_hashtags = sorted(hashtag_performance.items(), key=lambda x: x[1].get('engagement_rate', 0), reverse=True)[:5]
        
        if top_hashtags:
            rec_id = str(uuid.uuid4())
            
            recommendation = Recommendation(
                id=rec_id,
                org_id=org_id,
                type=RecommendationType.HASHTAG_SUGGESTION,
                title="Use High-Performing Hashtags",
                description=f"These hashtags drive the highest engagement: {', '.join([tag for tag, _ in top_hashtags[:3]])}",
                confidence_score=0.6,
                data={
                    "top_hashtags": [{"tag": tag, "engagement_rate": metrics.get('engagement_rate', 0)} for tag, metrics in top_hashtags],
                    "recommended_hashtags": [tag for tag, _ in top_hashtags[:5]]
                },
                priority=2,
                expires_at=datetime.utcnow() + timedelta(days=10)
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _generate_audience_targeting_recommendations(self, org_id: str, performance_data: Dict[str, Any]) -> List[Recommendation]:
        """Generate audience targeting recommendations."""
        recommendations = []
        
        # Analyze audience demographics
        audience_data = performance_data.get('audience_demographics', {})
        if not audience_data:
            return recommendations
        
        # Find most engaged demographics
        top_demographics = sorted(audience_data.items(), key=lambda x: x[1].get('engagement_rate', 0), reverse=True)[:3]
        
        if top_demographics:
            rec_id = str(uuid.uuid4())
            top_demo, top_metrics = top_demographics[0]
            
            recommendation = Recommendation(
                id=rec_id,
                org_id=org_id,
                type=RecommendationType.AUDIENCE_TARGETING,
                title="Focus on High-Engagement Demographics",
                description=f"Your {top_demo} audience shows {top_metrics.get('engagement_rate', 0):.1%} engagement rate. Consider creating more content for this segment.",
                confidence_score=0.75,
                data={
                    "top_demographics": [{"segment": demo, "engagement_rate": metrics.get('engagement_rate', 0)} for demo, metrics in top_demographics],
                    "recommended_focus": top_demo
                },
                priority=3,
                expires_at=datetime.utcnow() + timedelta(days=21)
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    async def update_recommendation(self, recommendation_id: str, org_id: str, recommendation_data: RecommendationUpdate) -> Recommendation:
        """Update a recommendation."""
        recommendation = self.db.execute(
            select(Recommendation).where(
                and_(Recommendation.id == recommendation_id, Recommendation.org_id == org_id)
            )
        ).scalar_one_or_none()
        
        if not recommendation:
            raise ValueError("Recommendation not found")
        
        update_data = recommendation_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(recommendation, field, value)
        
        recommendation.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(recommendation)
        
        logger.info(f"Updated recommendation {recommendation_id}")
        return recommendation
    
    # A/B Testing
    async def create_ab_test(self, org_id: str, ab_test_data: ABTestCreate) -> ABTest:
        """Create a new A/B test."""
        # Validate variants
        validated_variants = AutomationValidator.validate_ab_test_variants(ab_test_data.variants)
        
        ab_test_id = str(uuid.uuid4())
        
        ab_test = ABTest(
            id=ab_test_id,
            org_id=org_id,
            name=ab_test_data.name,
            description=ab_test_data.description,
            hypothesis=ab_test_data.hypothesis,
            test_type=ab_test_data.test_type,
            traffic_allocation=ab_test_data.traffic_allocation,
            minimum_sample_size=ab_test_data.minimum_sample_size,
            significance_level=ab_test_data.significance_level,
            planned_duration_days=ab_test_data.planned_duration_days
        )
        
        self.db.add(ab_test)
        self.db.flush()  # Flush to get the ID
        
        # Create variants
        variants = []
        for variant_data in validated_variants:
            variant_id = str(uuid.uuid4())
            variant = ABTestVariant(
                id=variant_id,
                ab_test_id=ab_test_id,
                name=variant_data.name,
                description=variant_data.description,
                variant_data=variant_data.variant_data,
                traffic_percentage=variant_data.traffic_percentage
            )
            variants.append(variant)
            self.db.add(variant)
        
        self.db.commit()
        self.db.refresh(ab_test)
        
        logger.info(f"Created A/B test {ab_test_id} with {len(variants)} variants")
        return ab_test
    
    async def update_ab_test(self, ab_test_id: str, org_id: str, ab_test_data: ABTestUpdate) -> ABTest:
        """Update an A/B test."""
        ab_test = self.db.execute(
            select(ABTest).where(
                and_(ABTest.id == ab_test_id, ABTest.org_id == org_id)
            )
        ).scalar_one_or_none()
        
        if not ab_test:
            raise ValueError("A/B test not found")
        
        update_data = ab_test_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(ab_test, field, value)
        
        ab_test.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(ab_test)
        
        logger.info(f"Updated A/B test {ab_test_id}")
        return ab_test
    
    async def delete_ab_test(self, ab_test_id: str, org_id: str) -> None:
        """Delete an A/B test."""
        ab_test = self.db.execute(
            select(ABTest).where(
                and_(ABTest.id == ab_test_id, ABTest.org_id == org_id)
            )
        ).scalar_one_or_none()
        
        if not ab_test:
            raise ValueError("A/B test not found")
        
        self.db.delete(ab_test)
        self.db.commit()
        
        logger.info(f"Deleted A/B test {ab_test_id}")
    
    async def start_ab_test(self, ab_test_id: str, org_id: str) -> ABTest:
        """Start an A/B test."""
        ab_test = self.db.execute(
            select(ABTest).where(
                and_(ABTest.id == ab_test_id, ABTest.org_id == org_id)
            )
        ).scalar_one_or_none()
        
        if not ab_test:
            raise ValueError("A/B test not found")
        
        if ab_test.status != ABTestStatus.DRAFT:
            raise ValueError("A/B test is not in draft status")
        
        ab_test.status = ABTestStatus.RUNNING
        ab_test.start_date = datetime.utcnow()
        ab_test.end_date = datetime.utcnow() + timedelta(days=ab_test.planned_duration_days)
        ab_test.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(ab_test)
        
        logger.info(f"Started A/B test {ab_test_id}")
        return ab_test
    
    async def stop_ab_test(self, ab_test_id: str, org_id: str) -> ABTest:
        """Stop an A/B test."""
        ab_test = self.db.execute(
            select(ABTest).where(
                and_(ABTest.id == ab_test_id, ABTest.org_id == org_id)
            )
        ).scalar_one_or_none()
        
        if not ab_test:
            raise ValueError("A/B test not found")
        
        if ab_test.status != ABTestStatus.RUNNING:
            raise ValueError("A/B test is not running")
        
        ab_test.status = ABTestStatus.COMPLETED
        ab_test.end_date = datetime.utcnow()
        ab_test.updated_at = datetime.utcnow()
        
        # Calculate results and determine winner
        await self._calculate_ab_test_results(ab_test)
        
        self.db.commit()
        self.db.refresh(ab_test)
        
        logger.info(f"Stopped A/B test {ab_test_id}")
        return ab_test
    
    async def _calculate_ab_test_results(self, ab_test: ABTest) -> None:
        """Calculate A/B test results and determine winner."""
        # Get all variants for this test
        variants = self.db.execute(
            select(ABTestVariant).where(ABTestVariant.ab_test_id == ab_test.id)
        ).scalars().all()
        
        if not variants:
            return
        
        # Calculate metrics for each variant
        variant_metrics = []
        for variant in variants:
            # In a real implementation, this would calculate actual metrics
            # For now, we'll use placeholder calculations
            conversion_rate = variant.conversions / max(variant.impressions, 1)
            engagement_rate = variant.clicks / max(variant.impressions, 1)
            
            variant_metrics.append({
                'variant': variant,
                'conversion_rate': conversion_rate,
                'engagement_rate': engagement_rate,
                'sample_size': variant.impressions
            })
        
        # Find winner based on conversion rate
        if variant_metrics:
            winner_metrics = max(variant_metrics, key=lambda x: x['conversion_rate'])
            winner_variant = winner_metrics['variant']
            
            ab_test.winner_variant_id = winner_variant.id
            ab_test.confidence_level = 0.95  # Placeholder
            ab_test.p_value = 0.03  # Placeholder
            
            # Update variant statuses
            for variant in variants:
                if variant.id == winner_variant.id:
                    variant.status = ABTestVariantStatus.WINNER
                else:
                    variant.status = ABTestVariantStatus.LOSER
