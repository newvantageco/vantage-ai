from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.content import Schedule, ContentStatus
from app.models.entities import Channel, Organization
from app.models.external_refs import ScheduleExternal
from app.models.post_metrics import PostMetrics
from workers.insights_poller import InsightsPoller


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
        name="Test LinkedIn Channel",
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
def test_external_ref(db_session: Session, test_schedule: Schedule, test_channel: Channel) -> ScheduleExternal:
    """Create a test external reference."""
    external_ref = ScheduleExternal(
        id="test-external-ref-123",
        schedule_id=test_schedule.id,
        ref_id="test_ref_123",
        ref_url="https://test.com/post/123",
        provider=test_channel.provider.lower()
    )
    db_session.add(external_ref)
    db_session.commit()
    return external_ref


@pytest.fixture
def insights_poller() -> InsightsPoller:
    """Create an insights poller instance."""
    return InsightsPoller()


async def test_upsert_post_metrics_prevents_duplicates(insights_poller: InsightsPoller, db_session: Session, test_schedule: Schedule):
    """Test that upsert prevents duplicate PostMetrics for the same schedule and date."""
    
    # Create initial PostMetrics
    initial_metrics = PostMetrics(
        id=f"{test_schedule.id}_linkedin_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        schedule_id=test_schedule.id,
        impressions=100,
        reach=80,
        likes=10,
        comments=2,
        shares=1,
        clicks=5,
        video_views=None,
        saves=None,
        cost_cents=None,
        fetched_at=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    )
    
    # Upsert the initial metrics
    await insights_poller._upsert_post_metrics(initial_metrics, db_session)
    db_session.commit()
    
    # Verify initial metrics were inserted
    initial_count = db_session.query(PostMetrics).filter_by(schedule_id=test_schedule.id).count()
    assert initial_count == 1
    
    # Create updated metrics for the same schedule and date
    updated_metrics = PostMetrics(
        id=f"{test_schedule.id}_linkedin_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_updated",
        schedule_id=test_schedule.id,
        impressions=150,  # Updated value
        reach=120,  # Updated value
        likes=15,  # Updated value
        comments=3,  # Updated value
        shares=2,  # Updated value
        clicks=8,  # Updated value
        video_views=None,
        saves=None,
        cost_cents=None,
        fetched_at=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)  # Same date
    )
    
    # Upsert the updated metrics
    await insights_poller._upsert_post_metrics(updated_metrics, db_session)
    db_session.commit()
    
    # Verify only one record exists (updated, not duplicated)
    final_count = db_session.query(PostMetrics).filter_by(schedule_id=test_schedule.id).count()
    assert final_count == 1
    
    # Verify the record was updated with new values
    final_metrics = db_session.query(PostMetrics).filter_by(schedule_id=test_schedule.id).first()
    assert final_metrics.impressions == 150
    assert final_metrics.reach == 120
    assert final_metrics.likes == 15
    assert final_metrics.comments == 3
    assert final_metrics.shares == 2
    assert final_metrics.clicks == 8


def test_upsert_post_metrics_allows_different_dates(insights_poller: InsightsPoller, db_session: Session, test_schedule: Schedule):
    """Test that upsert allows different PostMetrics for different dates."""
    
    # Create metrics for today
    today_metrics = PostMetrics(
        id=f"{test_schedule.id}_linkedin_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        schedule_id=test_schedule.id,
        impressions=100,
        reach=80,
        likes=10,
        comments=2,
        shares=1,
        clicks=5,
        video_views=None,
        saves=None,
        cost_cents=None,
        fetched_at=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    )
    
    # Upsert today's metrics
    await insights_poller._upsert_post_metrics(today_metrics, db_session)
    db_session.commit()
    
    # Create metrics for yesterday
    yesterday = datetime.utcnow() - timedelta(days=1)
    yesterday_metrics = PostMetrics(
        id=f"{test_schedule.id}_linkedin_{yesterday.strftime('%Y%m%d_%H%M%S')}",
        schedule_id=test_schedule.id,
        impressions=80,
        reach=60,
        likes=8,
        comments=1,
        shares=0,
        clicks=3,
        video_views=None,
        saves=None,
        cost_cents=None,
        fetched_at=yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    )
    
    # Upsert yesterday's metrics
    await insights_poller._upsert_post_metrics(yesterday_metrics, db_session)
    db_session.commit()
    
    # Verify both records exist
    total_count = db_session.query(PostMetrics).filter_by(schedule_id=test_schedule.id).count()
    assert total_count == 2
    
    # Verify both records have correct dates
    all_metrics = db_session.query(PostMetrics).filter_by(schedule_id=test_schedule.id).all()
    dates = [m.fetched_at.date() for m in all_metrics]
    assert datetime.utcnow().date() in dates
    assert yesterday.date() in dates


def test_upsert_post_metrics_handles_database_errors(insights_poller: InsightsPoller, db_session: Session, test_schedule: Schedule):
    """Test that upsert handles database errors gracefully."""
    
    # Create metrics with invalid data that might cause database errors
    metrics = PostMetrics(
        id=f"{test_schedule.id}_linkedin_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        schedule_id=test_schedule.id,
        impressions=100,
        reach=80,
        likes=10,
        comments=2,
        shares=1,
        clicks=5,
        video_views=None,
        saves=None,
        cost_cents=None,
        fetched_at=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    )
    
    # Mock a database error by closing the session
    db_session.close()
    
    # This should not raise an exception, but should handle the error gracefully
    try:
        await insights_poller._upsert_post_metrics(metrics, db_session)
        # If we get here, the error was handled gracefully
        assert True
    except Exception as e:
        # If an exception is raised, it should be handled appropriately
        assert "Failed to upsert PostMetrics" in str(e) or "database" in str(e).lower()


def test_upsert_post_metrics_with_none_values(insights_poller: InsightsPoller, db_session: Session, test_schedule: Schedule):
    """Test that upsert handles None values correctly."""
    
    # Create metrics with None values
    metrics = PostMetrics(
        id=f"{test_schedule.id}_linkedin_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        schedule_id=test_schedule.id,
        impressions=None,
        reach=None,
        likes=None,
        comments=None,
        shares=None,
        clicks=None,
        video_views=None,
        saves=None,
        cost_cents=None,
        fetched_at=datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    )
    
    # Upsert should work with None values
    await insights_poller._upsert_post_metrics(metrics, db_session)
    db_session.commit()
    
    # Verify the record was inserted
    count = db_session.query(PostMetrics).filter_by(schedule_id=test_schedule.id).count()
    assert count == 1
    
    # Verify all values are None
    final_metrics = db_session.query(PostMetrics).filter_by(schedule_id=test_schedule.id).first()
    assert final_metrics.impressions is None
    assert final_metrics.reach is None
    assert final_metrics.likes is None
    assert final_metrics.comments is None
    assert final_metrics.shares is None
    assert final_metrics.clicks is None


def test_upsert_post_metrics_unique_constraint(insights_poller: InsightsPoller, db_session: Session, test_schedule: Schedule):
    """Test that upsert respects the unique constraint on schedule_id + fetched_at."""
    
    # Create metrics for a specific date
    specific_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    metrics1 = PostMetrics(
        id=f"{test_schedule.id}_linkedin_{specific_date.strftime('%Y%m%d_%H%M%S')}",
        schedule_id=test_schedule.id,
        impressions=100,
        reach=80,
        likes=10,
        comments=2,
        shares=1,
        clicks=5,
        video_views=None,
        saves=None,
        cost_cents=None,
        fetched_at=specific_date
    )
    
    # Upsert first metrics
    await insights_poller._upsert_post_metrics(metrics1, db_session)
    db_session.commit()
    
    # Create second metrics for the same schedule and date
    metrics2 = PostMetrics(
        id=f"{test_schedule.id}_linkedin_{specific_date.strftime('%Y%m%d_%H%M%S')}_2",
        schedule_id=test_schedule.id,
        impressions=200,  # Different values
        reach=160,
        likes=20,
        comments=4,
        shares=2,
        clicks=10,
        video_views=None,
        saves=None,
        cost_cents=None,
        fetched_at=specific_date  # Same date
    )
    
    # Upsert second metrics - should update, not insert
    await insights_poller._upsert_post_metrics(metrics2, db_session)
    db_session.commit()
    
    # Verify only one record exists
    count = db_session.query(PostMetrics).filter_by(schedule_id=test_schedule.id).count()
    assert count == 1
    
    # Verify the record has the updated values from metrics2
    final_metrics = db_session.query(PostMetrics).filter_by(schedule_id=test_schedule.id).first()
    assert final_metrics.impressions == 200
    assert final_metrics.reach == 160
    assert final_metrics.likes == 20
    assert final_metrics.comments == 4
    assert final_metrics.shares == 2
    assert final_metrics.clicks == 10
