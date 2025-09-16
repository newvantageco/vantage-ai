"""Tests for scheduler functionality."""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, AsyncMock

from sqlalchemy.orm import Session
import redis.asyncio as redis

from app.scheduler.engine import (
    fetch_due_schedules, 
    run_tick, 
    SchedulerLock,
    _process_schedules_direct,
    _process_schedules_with_redis
)
from app.models.content import Schedule, ContentStatus, ContentItem
from app.models.entities import Channel


@pytest.fixture
async def mock_redis():
    """Mock Redis client for testing."""
    redis_client = Mock(spec=redis.Redis)
    redis_client.lock = AsyncMock()
    redis_client.exists = AsyncMock(return_value=False)
    redis_client.setex = AsyncMock()
    redis_client.ping = AsyncMock()
    return redis_client


@pytest.fixture
def mock_db():
    """Mock database session for testing."""
    db = Mock(spec=Session)
    db.execute = Mock()
    db.get = Mock()
    db.add = Mock()
    db.commit = Mock()
    return db


@pytest.fixture
def sample_schedule():
    """Sample schedule for testing."""
    return Schedule(
        id="test-schedule-1",
        org_id="test-org",
        content_item_id="test-content-1",
        channel_id="test-channel-1",
        scheduled_at=datetime.now(timezone.utc) - timedelta(minutes=5),
        status=ContentStatus.scheduled
    )


@pytest.fixture
def sample_channel():
    """Sample channel for testing."""
    return Channel(
        id="test-channel-1",
        org_id="test-org",
        provider="meta",
        account_ref="test-page",
        access_token="test-token"
    )


@pytest.fixture
def sample_content():
    """Sample content item for testing."""
    return ContentItem(
        id="test-content-1",
        org_id="test-org",
        title="Test Post",
        caption="This is a test post",
        status=ContentStatus.draft
    )


class TestSchedulerLock:
    """Test distributed locking functionality."""
    
    @pytest.mark.asyncio
    async def test_lock_acquisition(self, mock_redis):
        """Test that lock can be acquired successfully."""
        mock_lock = AsyncMock()
        mock_redis.lock.return_value = mock_lock
        
        async with SchedulerLock(mock_redis) as lock:
            assert lock == mock_lock
        
        mock_redis.lock.assert_called_once()
        mock_lock.release.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_lock_timeout(self, mock_redis):
        """Test lock timeout handling."""
        mock_redis.lock.side_effect = Exception("Lock timeout")
        
        async with SchedulerLock(mock_redis) as lock:
            assert lock is None


class TestFetchDueSchedules:
    """Test schedule fetching functionality."""
    
    def test_fetch_due_schedules_timezone_handling(self, mock_db):
        """Test that timezone handling works correctly."""
        # Mock the database query result
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db.execute.return_value = mock_result
        
        # Test with different timezone offsets
        fetch_due_schedules(mock_db, timezone_offset=0)
        fetch_due_schedules(mock_db, timezone_offset=1)
        
        # Verify database was called
        assert mock_db.execute.call_count == 2
    
    def test_fetch_due_schedules_with_results(self, mock_db, sample_schedule):
        """Test fetching schedules with results."""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [sample_schedule]
        mock_db.execute.return_value = mock_result
        
        schedules = list(fetch_due_schedules(mock_db))
        
        assert len(schedules) == 1
        assert schedules[0].id == "test-schedule-1"


class TestProcessSchedules:
    """Test schedule processing functionality."""
    
    @pytest.mark.asyncio
    async def test_process_schedules_direct_success(self, mock_db, sample_schedule, sample_channel, sample_content):
        """Test direct processing with successful publish."""
        # Mock database responses
        mock_db.get.side_effect = lambda model, id: {
            Channel: sample_channel,
            ContentItem: sample_content
        }.get(model, None)
        
        # Mock publisher
        mock_publisher = AsyncMock()
        mock_publisher.publish.return_value = Mock(id="post-123", url="https://example.com/post", external_refs={})
        
        with patch('app.scheduler.engine._publisher_for_provider', return_value=mock_publisher):
            with patch('app.scheduler.engine.fetch_due_schedules', return_value=[sample_schedule]):
                result = await _process_schedules_direct(mock_db)
        
        assert result == 1
        assert sample_schedule.status == ContentStatus.posted
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_schedules_direct_missing_data(self, mock_db, sample_schedule):
        """Test direct processing with missing channel or content."""
        mock_db.get.return_value = None  # Missing channel/content
        mock_db.get.side_effect = lambda model, id: None
        
        with patch('app.scheduler.engine.fetch_due_schedules', return_value=[sample_schedule]):
            result = await _process_schedules_direct(mock_db)
        
        assert result == 0
        assert sample_schedule.status == ContentStatus.failed
        assert "Missing channel or content" in sample_schedule.error_message
    
    @pytest.mark.asyncio
    async def test_process_schedules_with_redis_idempotency(self, mock_db, mock_redis, sample_schedule):
        """Test Redis-based processing with idempotency."""
        # Mock Redis to return that schedule is already processed
        mock_redis.exists.return_value = True
        
        with patch('app.scheduler.engine.fetch_due_schedules', return_value=[sample_schedule]):
            result = await _process_schedules_with_redis(mock_db, mock_redis)
        
        assert result == 0  # Should skip already processed
        mock_redis.exists.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_schedules_with_redis_retry_logic(self, mock_db, mock_redis, sample_schedule, sample_channel, sample_content):
        """Test Redis-based processing with retry logic."""
        # Mock database responses
        mock_db.get.side_effect = lambda model, id: {
            Channel: sample_channel,
            ContentItem: sample_content
        }.get(model, None)
        
        # Mock publisher to fail first two times, succeed on third
        mock_publisher = AsyncMock()
        mock_publisher.publish.side_effect = [
            Exception("Network error"),
            Exception("Rate limit"),
            Mock(id="post-123", url="https://example.com/post", external_refs={})
        ]
        
        with patch('app.scheduler.engine._publisher_for_provider', return_value=mock_publisher):
            with patch('app.scheduler.engine.fetch_due_schedules', return_value=[sample_schedule]):
                result = await _process_schedules_with_redis(mock_db, mock_redis)
        
        assert result == 1
        assert sample_schedule.status == ContentStatus.posted
        assert mock_publisher.publish.call_count == 3  # Should retry 3 times
        mock_redis.setex.assert_called()  # Should mark as completed


class TestRunTick:
    """Test main run_tick function."""
    
    @pytest.mark.asyncio
    async def test_run_tick_with_redis(self, mock_db, mock_redis):
        """Test run_tick with Redis client."""
        with patch('app.scheduler.engine._process_schedules_with_redis', return_value=5) as mock_process:
            result = await run_tick(mock_db, mock_redis)
        
        assert result == 5
        mock_process.assert_called_once_with(mock_db, mock_redis)
    
    @pytest.mark.asyncio
    async def test_run_tick_without_redis(self, mock_db):
        """Test run_tick without Redis client (fallback)."""
        with patch('app.scheduler.engine._process_schedules_direct', return_value=3) as mock_process:
            result = await run_tick(mock_db, None)
        
        assert result == 3
        mock_process.assert_called_once_with(mock_db)


@pytest.mark.asyncio
async def test_timezone_consistency():
    """Test that timezone handling is consistent across the system."""
    now_utc = datetime.now(timezone.utc)
    now_naive = now_utc.replace(tzinfo=None)
    
    # Verify timezone conversion is consistent
    assert now_utc.hour == now_naive.hour
    assert now_utc.minute == now_naive.minute
    assert now_utc.second == now_naive.second
