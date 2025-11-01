import os
import time
import logging
import json
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import uvicorn

# --- OpenTelemetry Core ---
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

# Traces
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter

# Logs
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry._logs import set_logger_provider

# OTLP exporters
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter


# ---------------- CONFIG ----------------
SERVICE = "Open-AI Q/A Agent"
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load ~/.a2a/config.json for collector ports if available
config_path = os.path.expanduser("~/.a2a/config.json")
collector_endpoint = "localhost:4317"
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        cfg = json.load(f)
        if "collector" in cfg and "endpointGrpc" in cfg["collector"]:
            collector_endpoint = cfg["collector"]["endpointGrpc"].replace("http://", "")
            print("collectorendpoint:", collector_endpoint)

resource = Resource(attributes={SERVICE_NAME: SERVICE})

# --- Traces ---
trace_provider = TracerProvider(resource=resource)
otlp_span_exporter = OTLPSpanExporter(endpoint=collector_endpoint, insecure=True)
trace_provider.add_span_processor(BatchSpanProcessor(otlp_span_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

# --- Metrics ---
otlp_metric_exporter = OTLPMetricExporter(endpoint=collector_endpoint, insecure=True)
console_metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[console_metric_reader],
)
metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter, export_interval_millis=5000)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)
questions_counter = meter.create_counter("questions_total")
latency_histogram = meter.create_histogram("response_latency_ms")

# --- Logs ---
logger_provider = LoggerProvider(resource=resource)
otlp_log_exporter = OTLPLogExporter(endpoint=collector_endpoint, insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_log_exporter))
set_logger_provider(logger_provider)

# Hook OTEL logger into Python logging
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger("agent")


# ---------------- FastAPI ----------------
app = FastAPI()

class Question(BaseModel):
    text: str

@app.get("/health")
def health():
    logger.info("Health check OK")
    return {"ok": True, "service": SERVICE}

@app.post("/ask")
async def ask_question(q: Question):
    with tracer.start_as_current_span("ask_question") as span:
        start = time.time()
        span.set_attribute("user.question", q.text)
        logger.info(f"Received question: {q.text}")

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": q.text}],
            )
            answer = response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI call failed: {e}")
            span.record_exception(e)
            return {"error": "llm_failed"}

        duration = (time.time() - start) * 1000
        questions_counter.add(1)
        latency_histogram.record(duration)
        span.set_attribute("response.latency_ms", duration)
        span.set_attribute("response.answer_preview", answer[:50])

        logger.info(f"Answer produced in {duration:.2f} ms")
        return {"answer": answer, "latency_ms": duration}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, access_log=False)
