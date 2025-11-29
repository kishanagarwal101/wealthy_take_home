from celery import Celery
import os

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import View, ExplicitBucketHistogramAggregation
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.sdk.resources import Resource

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "prime_generator",
    broker=redis_url,
    backend=redis_url,
)

resource = Resource.create({"service.name": "prime-generator-worker"})
trace.set_tracer_provider(TracerProvider(resource=resource))
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
otlp_trace_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
span_processor = BatchSpanProcessor(otlp_trace_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

otlp_metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)
metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter, export_interval_millis=5000)

# Configure custom histogram buckets for prime_task_duration_milliseconds (in milliseconds)
# Buckets: 10ms, 25ms, 50ms, 100ms, 250ms, 500ms, 1000ms, 2500ms, 5000ms, 10000ms, 30000ms, 60000ms
custom_buckets = [10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 2500.0, 5000.0, 10000.0, 30000.0, 60000.0]
custom_histogram_view = View(
    instrument_name="prime_task_duration_milliseconds",
    aggregation=ExplicitBucketHistogramAggregation(boundaries=custom_buckets)
)

meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[metric_reader],
    views=[custom_histogram_view]
)
metrics.set_meter_provider(meter_provider)

CeleryInstrumentor().instrument()

from . import prime_logic  