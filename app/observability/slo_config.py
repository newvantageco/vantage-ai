"""
Service Level Objectives (SLO) configuration for the VANTAGE AI platform.
"""

from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum


class SLOTarget(Enum):
    """SLO target types."""
    AVAILABILITY = "availability"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"


@dataclass
class SLOConfig:
    """SLO configuration for a service."""
    target: float  # Target percentage (0-100)
    threshold: float  # Threshold value
    window_days: int  # Time window in days
    description: str


# Default SLO configuration
DEFAULT_SLO_CONFIG = {
    "api": {
        SLOTarget.AVAILABILITY: SLOConfig(
            target=99.9,
            threshold=0.1,  # 0.1% downtime allowed
            window_days=30,
            description="API availability over 30 days"
        ),
        SLOTarget.LATENCY: SLOConfig(
            target=95.0,
            threshold=2.0,  # 2 seconds
            window_days=30,
            description="95% of requests under 2s over 30 days"
        ),
        SLOTarget.ERROR_RATE: SLOConfig(
            target=99.5,
            threshold=0.5,  # 0.5% error rate
            window_days=30,
            description="Error rate under 0.5% over 30 days"
        )
    },
    "workers": {
        SLOTarget.AVAILABILITY: SLOConfig(
            target=99.5,
            threshold=0.5,  # 0.5% downtime allowed
            window_days=30,
            description="Worker availability over 30 days"
        ),
        SLOTarget.LATENCY: SLOConfig(
            target=95.0,
            threshold=300.0,  # 5 minutes
            window_days=30,
            description="95% of jobs processed under 5 minutes"
        ),
        SLOTarget.ERROR_RATE: SLOConfig(
            target=90.0,
            threshold=10.0,  # 10% error rate
            window_days=30,
            description="Job success rate over 90% over 30 days"
        )
    },
    "scheduler": {
        SLOTarget.AVAILABILITY: SLOConfig(
            target=99.0,
            threshold=1.0,  # 1% downtime allowed
            window_days=30,
            description="Scheduler availability over 30 days"
        ),
        SLOTarget.LATENCY: SLOConfig(
            target=99.0,
            threshold=300.0,  # 5 minutes
            window_days=30,
            description="99% of jobs executed within 5 minutes of schedule"
        ),
        SLOTarget.ERROR_RATE: SLOConfig(
            target=95.0,
            threshold=5.0,  # 5% error rate
            window_days=30,
            description="Scheduled job success rate over 95% over 30 days"
        )
    },
    "database": {
        SLOTarget.AVAILABILITY: SLOConfig(
            target=99.9,
            threshold=0.1,  # 0.1% downtime allowed
            window_days=30,
            description="Database availability over 30 days"
        ),
        SLOTarget.LATENCY: SLOConfig(
            target=95.0,
            threshold=1.0,  # 1 second
            window_days=30,
            description="95% of queries under 1s over 30 days"
        ),
        SLOTarget.ERROR_RATE: SLOConfig(
            target=99.9,
            threshold=0.1,  # 0.1% error rate
            window_days=30,
            description="Database error rate under 0.1% over 30 days"
        )
    }
}


class SLOErrorBudget:
    """Calculate and track error budgets for SLOs."""
    
    def __init__(self, slo_config: SLOConfig):
        self.slo_config = slo_config
        self.window_seconds = slo_config.window_days * 24 * 60 * 60
        self.max_errors = self.window_seconds * (slo_config.threshold / 100)
    
    def calculate_budget_remaining(self, current_errors: int, time_elapsed: float) -> float:
        """Calculate remaining error budget."""
        if time_elapsed <= 0:
            return 100.0
        
        # Calculate expected errors at current rate
        expected_errors = (current_errors / time_elapsed) * self.window_seconds
        
        # Calculate remaining budget
        if expected_errors <= self.max_errors:
            return 100.0
        
        remaining_errors = max(0, self.max_errors - current_errors)
        return (remaining_errors / self.max_errors) * 100.0
    
    def calculate_burn_rate(self, current_errors: int, time_elapsed: float) -> float:
        """Calculate error budget burn rate."""
        if time_elapsed <= 0:
            return 0.0
        
        # Calculate current error rate
        current_rate = current_errors / time_elapsed
        
        # Calculate expected rate for full window
        expected_rate = self.max_errors / self.window_seconds
        
        # Calculate burn rate
        if expected_rate <= 0:
            return 0.0
        
        return current_rate / expected_rate
    
    def is_budget_exhausted(self, current_errors: int, time_elapsed: float) -> bool:
        """Check if error budget is exhausted."""
        return self.calculate_budget_remaining(current_errors, time_elapsed) <= 0
    
    def is_burn_rate_high(self, current_errors: int, time_elapsed: float, threshold: float = 2.0) -> bool:
        """Check if burn rate is high (above threshold)."""
        return self.calculate_burn_rate(current_errors, time_elapsed) > threshold


def get_slo_config(service: str, target: SLOTarget) -> SLOConfig:
    """Get SLO configuration for a service and target."""
    return DEFAULT_SLO_CONFIG[service][target]


def get_all_slo_configs() -> Dict[str, Dict[SLOTarget, SLOConfig]]:
    """Get all SLO configurations."""
    return DEFAULT_SLO_CONFIG


def create_error_budget(service: str, target: SLOTarget) -> SLOErrorBudget:
    """Create an error budget tracker for a service and target."""
    config = get_slo_config(service, target)
    return SLOErrorBudget(config)


# Error budget burn rate thresholds
BURN_RATE_WARNING = 2.0  # 50% of budget consumed in half the time
BURN_RATE_CRITICAL = 10.0  # 90% of budget consumed in 10% of the time


def get_burn_rate_alert_level(burn_rate: float) -> str:
    """Get alert level based on burn rate."""
    if burn_rate >= BURN_RATE_CRITICAL:
        return "critical"
    elif burn_rate >= BURN_RATE_WARNING:
        return "warning"
    else:
        return "ok"


def calculate_slo_performance(
    service: str, 
    target: SLOTarget, 
    current_value: float, 
    time_window_seconds: float
) -> Dict[str, Any]:
    """Calculate SLO performance metrics."""
    config = get_slo_config(service, target)
    error_budget = create_error_budget(service, target)
    
    # Calculate performance percentage
    if target == SLOTarget.AVAILABILITY:
        performance = min(100.0, (1.0 - current_value) * 100.0)
    elif target == SLOTarget.LATENCY:
        performance = min(100.0, (config.threshold / current_value) * 100.0) if current_value > 0 else 100.0
    elif target == SLOTarget.ERROR_RATE:
        performance = max(0.0, (1.0 - current_value / 100.0) * 100.0)
    else:
        performance = 100.0
    
    # Calculate error budget metrics
    budget_remaining = error_budget.calculate_budget_remaining(current_value, time_window_seconds)
    burn_rate = error_budget.calculate_burn_rate(current_value, time_window_seconds)
    alert_level = get_burn_rate_alert_level(burn_rate)
    
    return {
        "service": service,
        "target": target.value,
        "current_value": current_value,
        "target_value": config.target,
        "threshold": config.threshold,
        "performance_percentage": performance,
        "budget_remaining": budget_remaining,
        "burn_rate": burn_rate,
        "alert_level": alert_level,
        "is_meeting_slo": performance >= config.target,
        "description": config.description
    }
