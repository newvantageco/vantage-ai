from __future__ import annotations

import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.content import Schedule, ContentStatus, ContentItem
from app.models.entities import Channel, Organization
from app.models.external_refs import ScheduleExternal
from app.core.config import get_settings
from app.scheduler.engine import _process_schedules_direct


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
def test_content_item(db_session: Session, test_org: Organization) -> ContentItem:
    """Create a test content item."""
    content = ContentItem(
        id="test-content-123",
        org_id=test_org.id,
        title="Test Content",
        caption="Test caption for E2E mock testing",
        created_at=datetime.utcnow()
    )
    db_session.add(content)
    db_session.commit()
    return content


@pytest.fixture
def test_schedule(db_session: Session, test_org: Organization, test_channel: Channel, test_content_item: ContentItem) -> Schedule:
    """Create a test schedule."""
    schedule = Schedule(
        id="test-schedule-123",
        org_id=test_org.id,
        channel_id=test_channel.id,
        content_item_id=test_content_item.id,
        status=ContentStatus.scheduled,
        scheduled_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )
    db_session.add(schedule)
    db_session.commit()
    return schedule


def test_e2e_mocks_creates_schedule_external_when_enabled(db_session: Session, test_schedule: Schedule, test_channel: Channel):
    """Test that E2E mocks create schedule_external entries when enabled."""
    
    # Mock the settings to enable E2E mocks
    original_settings = get_settings()
    
    class MockSettings:
        e2e_mocks = True
    
    # Replace the settings temporarily
    import app.scheduler.engine
    original_get_settings = app.scheduler.engine.get_settings
    app.scheduler.engine.get_settings = lambda: MockSettings()
    
    try:
        # Process the schedule
        processed = await _process_schedules_direct(db_session)
        
        # Should have processed 1 schedule
        assert processed == 1
        
        # Check that schedule_external was created
        external_refs = db_session.query(ScheduleExternal).filter_by(
            schedule_id=test_schedule.id
        ).all()
        
        assert len(external_refs) == 1
        
        external_ref = external_refs[0]
        assert external_ref.schedule_id == test_schedule.id
        assert external_ref.provider == test_channel.provider.lower()
        assert external_ref.ref_id.startswith("mock_")
        assert external_ref.ref_url.startswith("https://mock.")
        
    finally:
        # Restore original settings
        app.scheduler.engine.get_settings = original_get_settings


def test_e2e_mocks_does_not_create_duplicate_external_refs(db_session: Session, test_schedule: Schedule, test_channel: Channel):
    """Test that E2E mocks don't create duplicate external refs."""
    
    # Create an existing external ref
    existing_ref = ScheduleExternal(
        id="existing-ref-123",
        schedule_id=test_schedule.id,
        ref_id="existing_ref_123",
        ref_url="https://existing.com/post/123",
        provider=test_channel.provider.lower()
    )
    db_session.add(existing_ref)
    db_session.commit()
    
    # Mock the settings to enable E2E mocks
    class MockSettings:
        e2e_mocks = True
    
    # Replace the settings temporarily
    import app.scheduler.engine
    original_get_settings = app.scheduler.engine.get_settings
    app.scheduler.engine.get_settings = lambda: MockSettings()
    
    try:
        # Process the schedule
        processed = await _process_schedules_direct(db_session)
        
        # Should have processed 1 schedule
        assert processed == 1
        
        # Check that only one external ref exists (the original one)
        external_refs = db_session.query(ScheduleExternal).filter_by(
            schedule_id=test_schedule.id
        ).all()
        
        assert len(external_refs) == 1
        assert external_refs[0].ref_id == "existing_ref_123"
        
    finally:
        # Restore original settings
        app.scheduler.engine.get_settings = original_get_settings


def test_e2e_mocks_disabled_does_not_create_mock_refs(db_session: Session, test_schedule: Schedule, test_channel: Channel):
    """Test that E2E mocks disabled doesn't create mock external refs."""
    
    # Mock the settings to disable E2E mocks
    class MockSettings:
        e2e_mocks = False
    
    # Replace the settings temporarily
    import app.scheduler.engine
    original_get_settings = app.scheduler.engine.get_settings
    app.scheduler.engine.get_settings = lambda: MockSettings()
    
    try:
        # Process the schedule
        processed = await _process_schedules_direct(db_session)
        
        # Should have processed 1 schedule
        assert processed == 1
        
        # Check that no external refs were created
        external_refs = db_session.query(ScheduleExternal).filter_by(
            schedule_id=test_schedule.id
        ).all()
        
        assert len(external_refs) == 0
        
    finally:
        # Restore original settings
        app.scheduler.engine.get_settings = original_get_settings


def test_e2e_mocks_creates_correct_provider_format(db_session: Session, test_schedule: Schedule, test_channel: Channel):
    """Test that E2E mocks create external refs with correct provider format."""
    
    # Mock the settings to enable E2E mocks
    class MockSettings:
        e2e_mocks = True
    
    # Replace the settings temporarily
    import app.scheduler.engine
    original_get_settings = app.scheduler.engine.get_settings
    app.scheduler.engine.get_settings = lambda: MockSettings()
    
    try:
        # Process the schedule
        processed = await _process_schedules_direct(db_session)
        
        # Should have processed 1 schedule
        assert processed == 1
        
        # Check external ref format
        external_refs = db_session.query(ScheduleExternal).filter_by(
            schedule_id=test_schedule.id
        ).all()
        
        assert len(external_refs) == 1
        
        external_ref = external_refs[0]
        assert external_ref.provider == test_channel.provider.lower()
        assert external_ref.ref_id == f"mock_{test_schedule.id}_{test_channel.provider.lower()}"
        assert external_ref.ref_url == f"https://mock.{test_channel.provider.lower()}.com/posts/{test_schedule.id}"
        
    finally:
        # Restore original settings
        app.scheduler.engine.get_settings = original_get_settings


def test_e2e_mocks_handles_different_providers(db_session: Session, test_org: Organization, test_content_item: ContentItem):
    """Test that E2E mocks handle different providers correctly."""
    
    providers = ["linkedin", "meta", "facebook", "instagram"]
    
    for provider in providers:
        # Create channel for this provider
        channel = Channel(
            id=f"test-channel-{provider}",
            org_id=test_org.id,
            provider=provider,
            name=f"Test {provider.title()} Channel",
            created_at=datetime.utcnow()
        )
        db_session.add(channel)
        db_session.commit()
        
        # Create schedule for this channel
        schedule = Schedule(
            id=f"test-schedule-{provider}",
            org_id=test_org.id,
            channel_id=channel.id,
            content_item_id=test_content_item.id,
            status=ContentStatus.scheduled,
            scheduled_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db_session.add(schedule)
        db_session.commit()
        
        # Mock the settings to enable E2E mocks
        class MockSettings:
            e2e_mocks = True
        
        # Replace the settings temporarily
        import app.scheduler.engine
        original_get_settings = app.scheduler.engine.get_settings
        app.scheduler.engine.get_settings = lambda: MockSettings()
        
        try:
            # Process the schedule
            processed = await _process_schedules_direct(db_session)
            
            # Should have processed 1 schedule
            assert processed == 1
            
            # Check external ref format
            external_refs = db_session.query(ScheduleExternal).filter_by(
                schedule_id=schedule.id
            ).all()
            
            assert len(external_refs) == 1
            
            external_ref = external_refs[0]
            assert external_ref.provider == provider.lower()
            assert external_ref.ref_id == f"mock_{schedule.id}_{provider.lower()}"
            assert external_ref.ref_url == f"https://mock.{provider.lower()}.com/posts/{schedule.id}"
            
        finally:
            # Restore original settings
            app.scheduler.engine.get_settings = original_get_settings
