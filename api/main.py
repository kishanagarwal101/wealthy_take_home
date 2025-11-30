from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
import uuid
import os

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource

from .celery_app import celery_app
from .prime_logic import prime_task

# Initialize OpenTelemetry
resource = Resource.create({"service.name": "prime-generator-api"})

# Configure Tracing
trace.set_tracer_provider(TracerProvider(resource=resource))
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
otlp_trace_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
span_processor = BatchSpanProcessor(otlp_trace_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Configure Metrics
otlp_metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)
metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter, export_interval_millis=5000)
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

app = FastAPI()

templates = Jinja2Templates(directory="api/templates")

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)

class GenerateResponse(BaseModel):
    request_id: str

class StatusResponse(BaseModel):
    status: str
    result: List[int] | None = None
    
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_model=GenerateResponse)
async def generate_primes(n: int):
    if n <= 0:
        raise HTTPException(status_code=400, detail="n must be a positive integer")
    
    request_id = str(uuid.uuid4())
    task = prime_task.delay(n, request_id)
    return GenerateResponse(request_id=task.id)

@app.get("/status/{request_id}", response_model=StatusResponse)
async def get_status(request_id: str):
    task = celery_app.AsyncResult(request_id)
    
    if task.state == 'PENDING':
        return StatusResponse(status="pending")
    elif task.state == 'SUCCESS':
        return StatusResponse(status="complete", result=task.result)
    else:
        # For other states like 'FAILURE', 'RETRY', etc.
        return StatusResponse(status=task.state.lower())
