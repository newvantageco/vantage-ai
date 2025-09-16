from __future__ import annotations

import pytest
import math
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.optimiser import ScheduleMetrics
from app.analytics.reward import compute_reward, _safe_normalize_metric


@pytest.fixture
def test_schedule_metrics(db_session: Session) -> ScheduleMetrics:
    """Create test schedule metrics."""
    metrics = ScheduleMetrics(
        schedule_id="test-schedule-123",
        ctr=0.05,
        engagement_rate=0.12,
        reach_norm=0.8,
        conv_rate=0.01,
        applied=False
    )
    db_session.add(metrics)
    db_session.commit()
    return metrics


def test_compute_reward_returns_valid_range():
    """Test that compute_reward always returns values in [0.0, 1.0] range."""
    
    # Test with valid metrics
    metrics = ScheduleMetrics(
        schedule_id="test-schedule-123",
        ctr=0.05,
        engagement_rate=0.12,
        reach_norm=0.8,
        conv_rate=0.01,
        applied=False
    )
    
    # Mock the database session
    class MockDB:
        def get(self, model, schedule_id):
            if model == ScheduleMetrics and schedule_id == "test-schedule-123":
                return metrics
            return None
    
    db = MockDB()
    reward = compute_reward("test-schedule-123", db)
    
    assert reward is not None
    assert 0.0 <= reward <= 1.0


def test_compute_reward_handles_nan_values():
    """Test that compute_reward handles NaN values safely."""
    
    # Test with NaN values
    metrics = ScheduleMetrics(
        schedule_id="test-schedule-123",
        ctr=float('nan'),
        engagement_rate=0.12,
        reach_norm=0.8,
        conv_rate=0.01,
        applied=False
    )
    
    class MockDB:
        def get(self, model, schedule_id):
            if model == ScheduleMetrics and schedule_id == "test-schedule-123":
                return metrics
            return None
    
    db = MockDB()
    reward = compute_reward("test-schedule-123", db)
    
    # Should return None for invalid metrics
    assert reward is None


def test_compute_reward_handles_infinity_values():
    """Test that compute_reward handles infinity values safely."""
    
    # Test with infinity values
    metrics = ScheduleMetrics(
        schedule_id="test-schedule-123",
        ctr=float('inf'),
        engagement_rate=0.12,
        reach_norm=0.8,
        conv_rate=0.01,
        applied=False
    )
    
    class MockDB:
        def get(self, model, schedule_id):
            if model == ScheduleMetrics and schedule_id == "test-schedule-123":
                return metrics
            return None
    
    db = MockDB()
    reward = compute_reward("test-schedule-123", db)
    
    # Should return None for invalid metrics
    assert reward is None


def test_compute_reward_handles_none_values():
    """Test that compute_reward handles None values safely."""
    
    # Test with None values
    metrics = ScheduleMetrics(
        schedule_id="test-schedule-123",
        ctr=None,
        engagement_rate=0.12,
        reach_norm=0.8,
        conv_rate=0.01,
        applied=False
    )
    
    class MockDB:
        def get(self, model, schedule_id):
            if model == ScheduleMetrics and schedule_id == "test-schedule-123":
                return metrics
            return None
    
    db = MockDB()
    reward = compute_reward("test-schedule-123", db)
    
    # Should return None for incomplete metrics
    assert reward is None


def test_compute_reward_handles_missing_metrics():
    """Test that compute_reward handles missing metrics safely."""
    
    class MockDB:
        def get(self, model, schedule_id):
            return None
    
    db = MockDB()
    reward = compute_reward("test-schedule-123", db)
    
    # Should return None for missing metrics
    assert reward is None


def test_compute_reward_clamps_values_to_valid_range():
    """Test that compute_reward clamps values to [0.0, 1.0] range."""
    
    # Test with values outside valid range
    metrics = ScheduleMetrics(
        schedule_id="test-schedule-123",
        ctr=2.0,  # Above 1.0
        engagement_rate=-0.5,  # Below 0.0
        reach_norm=1.5,  # Above 1.0
        conv_rate=0.01,
        applied=False
    )
    
    class MockDB:
        def get(self, model, schedule_id):
            if model == ScheduleMetrics and schedule_id == "test-schedule-123":
                return metrics
            return None
    
    db = MockDB()
    reward = compute_reward("test-schedule-123", db)
    
    assert reward is not None
    assert 0.0 <= reward <= 1.0


def test_safe_normalize_metric_handles_nan():
    """Test that _safe_normalize_metric handles NaN values."""
    
    result = _safe_normalize_metric(float('nan'), "test_metric")
    assert result is None


def test_safe_normalize_metric_handles_infinity():
    """Test that _safe_normalize_metric handles infinity values."""
    
    result = _safe_normalize_metric(float('inf'), "test_metric")
    assert result is None
    
    result = _safe_normalize_metric(float('-inf'), "test_metric")
    assert result is None


def test_safe_normalize_metric_handles_none():
    """Test that _safe_normalize_metric handles None values."""
    
    result = _safe_normalize_metric(None, "test_metric")
    assert result is None


def test_safe_normalize_metric_clamps_values():
    """Test that _safe_normalize_metric clamps values to [0.0, 1.0] range."""
    
    # Test value above 1.0
    result = _safe_normalize_metric(2.0, "test_metric")
    assert result == 1.0
    
    # Test value below 0.0
    result = _safe_normalize_metric(-0.5, "test_metric")
    assert result == 0.0
    
    # Test value in valid range
    result = _safe_normalize_metric(0.5, "test_metric")
    assert result == 0.5


def test_safe_normalize_metric_handles_edge_cases():
    """Test that _safe_normalize_metric handles edge cases."""
    
    # Test exact 0.0
    result = _safe_normalize_metric(0.0, "test_metric")
    assert result == 0.0
    
    # Test exact 1.0
    result = _safe_normalize_metric(1.0, "test_metric")
    assert result == 1.0


def test_compute_reward_formula_weights():
    """Test that compute_reward uses correct formula weights."""
    
    # Test with known values to verify formula
    metrics = ScheduleMetrics(
        schedule_id="test-schedule-123",
        ctr=0.1,  # 10%
        engagement_rate=0.2,  # 20%
        reach_norm=0.5,  # 50%
        conv_rate=0.05,  # 5%
        applied=False
    )
    
    class MockDB:
        def get(self, model, schedule_id):
            if model == ScheduleMetrics and schedule_id == "test-schedule-123":
                return metrics
            return None
    
    db = MockDB()
    reward = compute_reward("test-schedule-123", db)
    
    # Expected: 0.4*0.1 + 0.3*0.2 + 0.2*0.5 + 0.1*0.05 = 0.04 + 0.06 + 0.1 + 0.005 = 0.205
    expected = 0.4 * 0.1 + 0.3 * 0.2 + 0.2 * 0.5 + 0.1 * 0.05
    assert abs(reward - expected) < 1e-10


def test_compute_reward_never_returns_nan():
    """Test that compute_reward never returns NaN."""
    
    # Test with various edge cases
    test_cases = [
        # All zeros
        {"ctr": 0.0, "engagement_rate": 0.0, "reach_norm": 0.0, "conv_rate": 0.0},
        # All ones
        {"ctr": 1.0, "engagement_rate": 1.0, "reach_norm": 1.0, "conv_rate": 1.0},
        # Mixed valid values
        {"ctr": 0.05, "engagement_rate": 0.12, "reach_norm": 0.8, "conv_rate": 0.01},
    ]
    
    for case in test_cases:
        metrics = ScheduleMetrics(
            schedule_id="test-schedule-123",
            ctr=case["ctr"],
            engagement_rate=case["engagement_rate"],
            reach_norm=case["reach_norm"],
            conv_rate=case["conv_rate"],
            applied=False
        )
        
        class MockDB:
            def get(self, model, schedule_id):
                if model == ScheduleMetrics and schedule_id == "test-schedule-123":
                    return metrics
                return None
        
        db = MockDB()
        reward = compute_reward("test-schedule-123", db)
        
        if reward is not None:
            assert not math.isnan(reward)
            assert not math.isinf(reward)
