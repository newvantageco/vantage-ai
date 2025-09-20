import os
import logging

# Safe telemetry imports with fallback
DISABLE_TELEMETRY = os.getenv("DISABLE_TELEMETRY") == "1"

try:
    if not DISABLE_TELEMETRY:
        from opentelemetry import trace, metrics
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        from opentelemetry.exporter.prometheus import PrometheusMetricReader
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.metrics import MeterProvider
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.instrumentation.requests import RequestsInstrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        _TELEMETRY_OK = True
    else:
        _TELEMETRY_OK = False
except Exception:
    _TELEMETRY_OK = False

from app.core.config import Settings

logger = logging.getLogger(__name__)


def _safe_tracer():
    """Get a safe tracer that works even when telemetry is disabled."""
    if _TELEMETRY_OK:
        return trace.get_tracer("vantage-ai")
    
    class _NoopTracer:
        def start_as_current_span(self, *a, **k):
            from contextlib import nullcontext
            return nullcontext()
    
    return _NoopTracer()


def init_telemetry():
    """Initialize OpenTelemetry with proper configuration."""
    if os.getenv("DISABLE_TELEMETRY") == "1":
        logger.info("Telemetry disabled via DISABLE_TELEMETRY=1")
        return

    try:
        from opentelemetry import trace, metrics
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.exporter.prometheus import PrometheusMetricReader

        service_name = os.getenv("OTEL_SERVICE_NAME", "vantage-api")
        resource = Resource.create({"service.name": service_name})

        # Tracer
        tp = TracerProvider(resource=resource)
        trace.set_tracer_provider(tp)

        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if otlp_endpoint:
            tp.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{otlp_endpoint}/v1/traces"))
            )

        # Metrics
        if os.getenv("ENABLE_PROMETHEUS_METRICS") == "1":
            reader = PrometheusMetricReader()
            mp = metrics.MeterProvider(resource=resource, metric_readers=[reader])
            metrics.set_meter_provider(mp)

        logger.info(f"OpenTelemetry initialized for service: {service_name}")

    except Exception as e:
        logger.error(f"[otel] disabled or failed to init: {e}")


def setup_telemetry():
    """Setup OpenTelemetry instrumentation (legacy function for compatibility)."""
    init_telemetry()
    
    if not _TELEMETRY_OK:
        return
    
    try:
        # Instrument FastAPI
        FastAPIInstrumentor.instrument()
        
        # Instrument SQLAlchemy
        SQLAlchemyInstrumentor().instrument()
        
        # Instrument requests
        RequestsInstrumentor().instrument()
        
        # Instrument Redis
        RedisInstrumentor().instrument()
        
        logger.info("OpenTelemetry instrumentation setup complete")
        
    except Exception as e:
        logger.error(f"Failed to setup OpenTelemetry instrumentation: {e}")


def get_tracer(name: str):
    """Get a tracer instance."""
    if _TELEMETRY_OK:
        return trace.get_tracer(name)
    return _safe_tracer()


def get_meter(name: str):
    """Get a meter instance."""
    if _TELEMETRY_OK:
        return metrics.get_meter(name)
    
    class _NoopMeter:
        def create_counter(self, *a, **k):
            return _NoopCounter()
        def create_histogram(self, *a, **k):
            return _NoopHistogram()
        def create_up_down_counter(self, *a, **k):
            return _NoopUpDownCounter()
        def create_gauge(self, *a, **k):
            return _NoopGauge()
    
    return _NoopMeter()


class _NoopCounter:
    def add(self, *a, **k): pass

class _NoopHistogram:
    def record(self, *a, **k): pass

class _NoopUpDownCounter:
    def add(self, *a, **k): pass
    def set(self, *a, **k): pass

class _NoopGauge:
    def set(self, *a, **k): pass


# Global tracer and meter instances
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Define common metrics
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total number of HTTP requests",
    unit="1"
)

request_duration = meter.create_histogram(
    name="http_request_duration_seconds",
    description="HTTP request duration in seconds",
    unit="s"
)

active_connections = meter.create_up_down_counter(
    name="http_connections_active",
    description="Number of active HTTP connections",
    unit="1"
)

worker_jobs_processed = meter.create_counter(
    name="worker_jobs_processed_total",
    description="Total number of jobs processed by workers",
    unit="1"
)

worker_jobs_success = meter.create_counter(
    name="worker_jobs_success_total",
    description="Total number of successfully processed jobs",
    unit="1"
)

worker_queue_depth = meter.create_up_down_counter(
    name="worker_queue_depth",
    description="Current depth of the worker queue",
    unit="1"
)

worker_heartbeat = meter.create_gauge(
    name="worker_heartbeat_timestamp",
    description="Last heartbeat timestamp for workers",
    unit="s"
)

worker_memory_usage = meter.create_gauge(
    name="worker_memory_usage_bytes",
    description="Memory usage of workers in bytes",
    unit="bytes"
)

worker_job_duration = meter.create_histogram(
    name="worker_job_duration_seconds",
    description="Duration of worker job processing in seconds",
    unit="s"
)

posts_published = meter.create_counter(
    name="posts_published_total",
    description="Total number of posts published",
    unit="1"
)

ai_generations = meter.create_counter(
    name="ai_generations_total",
    description="Total number of AI generations",
    unit="1"
)

revenue_total = meter.create_counter(
    name="revenue_total",
    description="Total revenue in cents",
    unit="cents"
)

organizations_total = meter.create_up_down_counter(
    name="organizations_total",
    description="Total number of organizations",
    unit="1"
)

channels_connected = meter.create_up_down_counter(
    name="channels_connected_total",
    description="Total number of connected channels",
    unit="1"
)

user_actions = meter.create_counter(
    name="user_actions_total",
    description="Total number of user actions",
    unit="1"
)


def record_request(method: str, path: str, status_code: int, duration: float):
    """Record HTTP request metrics."""
    request_counter.add(1, {
        "method": method,
        "path": path,
        "status_code": str(status_code)
    })
    request_duration.record(duration, {
        "method": method,
        "path": path,
        "status_code": str(status_code)
    })


def record_worker_job(worker_id: str, job_type: str, success: bool, duration: float):
    """Record worker job metrics."""
    worker_jobs_processed.add(1, {
        "worker_id": worker_id,
        "job_type": job_type
    })
    
    if success:
        worker_jobs_success.add(1, {
            "worker_id": worker_id,
            "job_type": job_type
        })
    
    worker_job_duration.record(duration, {
        "worker_id": worker_id,
        "job_type": job_type
    })


def record_worker_heartbeat(worker_id: str, timestamp: float):
    """Record worker heartbeat."""
    worker_heartbeat.set(timestamp, {
        "worker_id": worker_id
    })


def record_worker_memory(worker_id: str, memory_bytes: int):
    """Record worker memory usage."""
    worker_memory_usage.set(memory_bytes, {
        "worker_id": worker_id
    })


def record_queue_depth(depth: int):
    """Record queue depth."""
    worker_queue_depth.set(depth)


def record_post_published(platform: str, org_id: str):
    """Record post published."""
    posts_published.add(1, {
        "platform": platform,
        "org_id": org_id
    })


def record_ai_generation(model: str, org_id: str, tokens: int):
    """Record AI generation."""
    ai_generations.add(1, {
        "model": model,
        "org_id": org_id
    })


def record_revenue(amount_cents: int, plan: str, org_id: str):
    """Record revenue."""
    revenue_total.add(amount_cents, {
        "plan": plan,
        "org_id": org_id
    })


def record_organization(org_id: str, plan: str, action: str = "create"):
    """Record organization metrics."""
    if action == "create":
        organizations_total.add(1, {
            "org_id": org_id,
            "plan": plan
        })
    elif action == "delete":
        organizations_total.add(-1, {
            "org_id": org_id,
            "plan": plan
        })


def record_channel_connected(platform: str, org_id: str, action: str = "connect"):
    """Record channel connection metrics."""
    if action == "connect":
        channels_connected.add(1, {
            "platform": platform,
            "org_id": org_id
        })
    elif action == "disconnect":
        channels_connected.add(-1, {
            "platform": platform,
            "org_id": org_id
        })


def record_user_action(action: str, org_id: str, user_id: str):
    """Record user action."""
    user_actions.add(1, {
        "action": action,
        "org_id": org_id,
        "user_id": user_id
    })
