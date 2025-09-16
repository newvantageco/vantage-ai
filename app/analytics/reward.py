from __future__ import annotations

import math
from typing import Optional
from sqlalchemy.orm import Session

from app.models.optimiser import ScheduleMetrics


def compute_reward(schedule_id: str, db: Session) -> Optional[float]:
	"""Compute reward 0..1 using normalized metrics if available.

	Formula: r = 0.4*CTR + 0.3*EngagementRate + 0.2*Reach_norm + 0.1*ConvRate

	Returns None if metrics missing or incomplete.
	Guarantees return value is in range [0.0, 1.0] and never NaN.
	"""
	row = db.get(ScheduleMetrics, schedule_id)
	if not row:
		return None
	if row.ctr is None or row.engagement_rate is None or row.reach_norm is None or row.conv_rate is None:
		return None
	
	# Safely extract and validate each metric
	ctr = _safe_normalize_metric(row.ctr, "CTR")
	eng = _safe_normalize_metric(row.engagement_rate, "EngagementRate")
	reach = _safe_normalize_metric(row.reach_norm, "ReachNorm")
	conv = _safe_normalize_metric(row.conv_rate, "ConvRate")
	
	# If any metric is invalid, return None
	if ctr is None or eng is None or reach is None or conv is None:
		return None
	
	# Calculate weighted reward
	reward = 0.4 * ctr + 0.3 * eng + 0.2 * reach + 0.1 * conv
	
	# Final safety check - ensure result is valid and in range
	if math.isnan(reward) or math.isinf(reward):
		return 0.0
	
	return max(0.0, min(1.0, reward))


def _safe_normalize_metric(value: float, metric_name: str) -> Optional[float]:
	"""
	Safely normalize a metric value to [0.0, 1.0] range.
	
	Args:
		value: The metric value to normalize
		metric_name: Name of the metric for logging
		
	Returns:
		Normalized value in [0.0, 1.0] or None if invalid
	"""
	if value is None:
		return None
	
	# Check for NaN or infinity
	if math.isnan(value) or math.isinf(value):
		return None
	
	# Clamp to [0.0, 1.0] range
	normalized = max(0.0, min(1.0, value))
	
	# Final validation
	if math.isnan(normalized) or math.isinf(normalized):
		return None
	
	return normalized


