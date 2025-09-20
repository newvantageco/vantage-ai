"""
Safe tracer utility for Vantage AI.

This module provides a safe tracer that gracefully handles cases where
OpenTelemetry is disabled or not available.
"""

import os

DISABLE_TELEMETRY = os.getenv("DISABLE_TELEMETRY") == "1"

try:
    if not DISABLE_TELEMETRY:
        from opentelemetry.trace import get_tracer
        _TRACING_OK = True
    else:
        _TRACING_OK = False
except Exception:
    _TRACING_OK = False


def _tracer():
    """Get a safe tracer that works even when telemetry is disabled."""
    if _TRACING_OK:
        return get_tracer("vantage-ai")
    
    class _NoopTracer:
        def start_as_current_span(self, *a, **k):
            from contextlib import nullcontext
            return nullcontext()
    
    return _NoopTracer()


# Export the safe tracer
tracer = _tracer()
