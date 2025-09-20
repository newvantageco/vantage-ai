"""
Simple OpenTelemetry initialization for Vantage AI.

This module provides a clean, minimal way to initialize OpenTelemetry
with proper configuration and graceful fallback.
"""

import os

def init_telemetry():
    """Initialize OpenTelemetry with proper configuration."""
    if os.getenv("DISABLE_TELEMETRY") == "1":
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

    except Exception as e:
        print(f"[otel] disabled or failed to init: {e}")
