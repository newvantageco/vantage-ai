from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.content import Schedule, ContentStatus
from app.models.entities import Channel, Organization
from app.models.optimiser import ScheduleMetrics, OptimiserState
from workers.optimiser_worker import tick_once


@pytest.fixture
def test_org(db_session: Session) -> Organization:
    """Create a test organization."""
    org = Organization(
        id="test-org-123",
        name="Test Organization",
        created_at=datetime.utcnow()
    )
    db_session.add(org)
    db_session.commit()
    return org


@pytest.fixture
def test_channel(db_session: Session, test_org: Organization) -> Channel:
    """Create a test channel."""
    channel = Channel(
        id="test-channel-123",
        org_id=test_org.id,
        provider="linkedin",
        account_ref="test-page-123",
        access_token="test-token-123",
        created_at=datetime.utcnow()
    )
    db_session.add(channel)
    db_session.commit()
    return channel


@pytest.fixture
def test_schedule(db_session: Session, test_org: Organization, test_channel: Channel) -> Schedule:
    """Create a test schedule."""
    schedule = Schedule(
        id="test-schedule-123",
        org_id=test_org.id,
        channel_id=test_channel.id,
        content_item_id="test-content-123",
        status=ContentStatus.posted,
        scheduled_at=datetime.utcnow() - timedelta(hours=1),
        created_at=datetime.utcnow() - timedelta(hours=2)
    )
    db_session.add(schedule)
    db_session.commit()
    return schedule


@pytest.fixture
def test_schedule_metrics(db_session: Session, test_schedule: Schedule) -> ScheduleMetrics:
    """Create test schedule metrics."""
    metrics = ScheduleMetrics(
        schedule_id=test_schedule.id,
        ctr=0.05,
        engagement_rate=0.12,
        reach_norm=0.8,
        conv_rate=0.01,
        applied=False
    )
    db_session.add(metrics)
    db_session.commit()
    return metrics


@pytest.mark.asyncio
async def test_optimiser_worker_updates_only_once_per_schedule(
    db_session: Session, 
    test_org: Organization, 
    test_channel: Channel, 
    test_schedule: Schedule, 
    test_schedule_metrics: ScheduleMetrics
):
    """Test that optimiser state is updated only once per schedule when metrics are complete."""
    
    # First run should update the optimiser state
    updated_count = await tick_once(db_session)
    assert updated_count == 1
    
    # Verify the metrics are marked as applied
    db_session.refresh(test_schedule_metrics)
    assert test_schedule_metrics.applied is True
    
    # Verify optimiser state was created
    optimiser_state = db_session.query(OptimiserState).filter_by(
        org_id=test_org.id,
        key=f"{test_channel.provider}:post:{test_schedule.scheduled_at.strftime('%a')}:{test_schedule.scheduled_at.hour:02d}"
    ).first()
    assert optimiser_state is not None
    assert optimiser_state.pulls == 1
    assert optimiser_state.rewards > 0
    
    # Second run should not update the same schedule again
    updated_count = await tick_once(db_session)
    assert updated_count == 0
    
    # Verify optimiser state was not updated again
    db_session.refresh(optimiser_state)
    assert optimiser_state.pulls == 1  # Should still be 1, not 2


@pytest.mark.asyncio
async def test_optimiser_worker_skips_schedules_without_metrics(
    db_session: Session, 
    test_org: Organization, 
    test_channel: Channel, 
    test_schedule: Schedule
):
    """Test that schedules without metrics are skipped."""
    
    # Run without creating metrics
    updated_count = await tick_once(db_session)
    assert updated_count == 0
    
    # Verify no optimiser state was created
    optimiser_states = db_session.query(OptimiserState).filter_by(org_id=test_org.id).all()
    assert len(optimiser_states) == 0


@pytest.mark.asyncio
async def test_optimiser_worker_skips_already_applied_metrics(
    db_session: Session, 
    test_org: Organization, 
    test_channel: Channel, 
    test_schedule: Schedule
):
    """Test that schedules with already applied metrics are skipped."""
    
    # Create metrics that are already applied
    metrics = ScheduleMetrics(
        schedule_id=test_schedule.id,
        ctr=0.05,
        engagement_rate=0.12,
        reach_norm=0.8,
        conv_rate=0.01,
        applied=True  # Already applied
    )
    db_session.add(metrics)
    db_session.commit()
    
    # Run should not update anything
    updated_count = await tick_once(db_session)
    assert updated_count == 0


@pytest.mark.asyncio
async def test_optimiser_worker_skips_old_schedules(
    db_session: Session, 
    test_org: Organization, 
    test_channel: Channel
):
    """Test that schedules older than 72 hours are skipped."""
    
    # Create an old schedule (older than 72 hours)
    old_schedule = Schedule(
        id="old-schedule-123",
        org_id=test_org.id,
        channel_id=test_channel.id,
        content_item_id="test-content-123",
        status=ContentStatus.posted,
        scheduled_at=datetime.utcnow() - timedelta(hours=100),  # Very old
        created_at=datetime.utcnow() - timedelta(hours=100)
    )
    db_session.add(old_schedule)
    
    # Create metrics for the old schedule
    old_metrics = ScheduleMetrics(
        schedule_id=old_schedule.id,
        ctr=0.05,
        engagement_rate=0.12,
        reach_norm=0.8,
        conv_rate=0.01,
        applied=False
    )
    db_session.add(old_metrics)
    db_session.commit()
    
    # Run should not update the old schedule
    updated_count = await tick_once(db_session)
    assert updated_count == 0


@pytest.mark.asyncio
async def test_optimiser_worker_handles_invalid_rewards(
    db_session: Session, 
    test_org: Organization, 
    test_channel: Channel, 
    test_schedule: Schedule
):
    """Test that schedules with invalid rewards are skipped."""
    
    # Create metrics with invalid values that would result in None reward
    metrics = ScheduleMetrics(
        schedule_id=test_schedule.id,
        ctr=None,  # Invalid - should result in None reward
        engagement_rate=0.12,
        reach_norm=0.8,
        conv_rate=0.01,
        applied=False
    )
    db_session.add(metrics)
    db_session.commit()
    
    # Run should not update anything due to invalid reward
    updated_count = await tick_once(db_session)
    assert updated_count == 0
