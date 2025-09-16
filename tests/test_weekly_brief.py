from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.entities import Organization
from app.reports.weekly_brief import (
    generate_weekly_brief, 
    generate_weekly_brief_fake,
    build_summary,
    detect_winners_laggards,
    ChannelMetric
)


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


def test_weekly_brief_always_includes_at_least_one_action():
    """Test that weekly brief always includes at least one action."""
    
    # Test with fake data
    brief = generate_weekly_brief_fake("test-org-123")
    
    assert "actions" in brief
    assert len(brief["actions"]) >= 1
    
    # Verify all actions have required fields
    for action in brief["actions"]:
        assert "action" in action
        assert "idempotency_key" in action


def test_weekly_brief_actions_are_idempotent():
    """Test that weekly brief actions include idempotency keys."""
    
    brief = generate_weekly_brief_fake("test-org-123")
    
    # Collect all idempotency keys
    idempotency_keys = [action["idempotency_key"] for action in brief["actions"]]
    
    # Verify all keys are unique
    assert len(idempotency_keys) == len(set(idempotency_keys))
    
    # Verify keys are meaningful (not empty)
    for key in idempotency_keys:
        assert key is not None
        assert len(key) > 0


def test_weekly_brief_fallback_action():
    """Test that weekly brief provides fallback action when no specific actions are available."""
    
    # Create empty metrics to trigger fallback
    empty_metrics = []
    winners, laggards = detect_winners_laggards(empty_metrics)
    deltas = []
    
    summary = build_summary("test-org-123", empty_metrics, winners, laggards, deltas)
    
    assert "actions" in summary
    assert len(summary["actions"]) >= 1
    
    # Should have the fallback optimization action
    action_types = [action["action"] for action in summary["actions"]]
    assert "optimize_schedule" in action_types


def test_weekly_brief_with_winners_and_laggards():
    """Test weekly brief with both winners and laggards."""
    
    # Create test metrics
    metrics = [
        ChannelMetric(
            channel_id="ch1", 
            channel_provider="linkedin", 
            schedule_id="s1", 
            ctr=0.05, 
            engagement_rate=0.12, 
            reach_norm=0.8, 
            conv_rate=0.01, 
            score=0.5
        ),
        ChannelMetric(
            channel_id="ch2", 
            channel_provider="meta", 
            schedule_id="s2", 
            ctr=0.01, 
            engagement_rate=0.03, 
            reach_norm=0.5, 
            conv_rate=0.004, 
            score=0.1
        )
    ]
    
    winners, laggards = detect_winners_laggards(metrics)
    deltas = []
    
    summary = build_summary("test-org-123", metrics, winners, laggards, deltas)
    
    assert "actions" in summary
    assert len(summary["actions"]) >= 1
    
    # Should have clone_post action for winner
    action_types = [action["action"] for action in summary["actions"]]
    assert "clone_post" in action_types
    
    # Should have create_variants action for laggard
    assert "create_variants" in action_types
    
    # Should have increase_budget action
    assert "increase_budget" in action_types


def test_weekly_brief_highlights_and_issues():
    """Test that weekly brief includes highlights and issues."""
    
    brief = generate_weekly_brief_fake("test-org-123")
    
    assert "highlights" in brief
    assert "issues" in brief
    assert isinstance(brief["highlights"], list)
    assert isinstance(brief["issues"], list)


def test_weekly_brief_optimiser_deltas():
    """Test that weekly brief includes optimiser deltas."""
    
    brief = generate_weekly_brief_fake("test-org-123")
    
    assert "optimiser_deltas" in brief
    assert isinstance(brief["optimiser_deltas"], list)


def test_weekly_brief_generated_at_timestamp():
    """Test that weekly brief includes generation timestamp."""
    
    brief = generate_weekly_brief_fake("test-org-123")
    
    assert "generated_at" in brief
    assert "org_id" in brief
    
    # Verify timestamp is valid ISO format
    try:
        datetime.fromisoformat(brief["generated_at"].replace('Z', '+00:00'))
    except ValueError:
        pytest.fail("Invalid ISO timestamp format")


def test_detect_winners_laggards_with_empty_metrics():
    """Test winner/laggard detection with empty metrics."""
    
    winners, laggards = detect_winners_laggards([])
    
    assert winners == []
    assert laggards == []


def test_detect_winners_laggards_with_single_metric():
    """Test winner/laggard detection with single metric."""
    
    metrics = [
        ChannelMetric(
            channel_id="ch1", 
            channel_provider="linkedin", 
            schedule_id="s1", 
            ctr=0.05, 
            engagement_rate=0.12, 
            reach_norm=0.8, 
            conv_rate=0.01, 
            score=0.5
        )
    ]
    
    winners, laggards = detect_winners_laggards(metrics)
    
    # With single metric, it should be both winner and laggard
    assert len(winners) >= 1
    assert len(laggards) >= 1


def test_weekly_brief_idempotency_keys_format():
    """Test that idempotency keys follow expected format."""
    
    brief = generate_weekly_brief_fake("test-org-123")
    
    for action in brief["actions"]:
        key = action["idempotency_key"]
        
        # Keys should contain action type and relevant identifiers
        assert "_" in key  # Should have separators
        assert len(key) > 10  # Should be reasonably long
        assert key.isalnum() or "_" in key  # Should be alphanumeric with underscores
