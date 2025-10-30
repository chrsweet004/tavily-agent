
# A2A Agent Telemetry Setup

This agent has been linked to your A2A dashboard.

To enable OpenTelemetry instrumentation, copy one of the snippets below into your agent's entry point.  
The OTLP endpoint is prefilled from your A2A config: `http://localhost:46817`.

---

## Node.js Example

```js
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import { BatchSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";

import { MeterProvider, PeriodicExportingMetricReader } from "@opentelemetry/sdk-metrics";
import { OTLPMetricExporter } from "@opentelemetry/exporter-metrics-otlp-http";

import { LoggerProvider, BatchLogRecordProcessor, logs } from "@opentelemetry/sdk-logs";
import { OTLPLogExporter } from "@opentelemetry/exporter-logs-otlp-http";

import { Resource } from "@opentelemetry/resources";
import { SemanticResourceAttributes as S } from "@opentelemetry/semantic-conventions";

const OTEL_ENDPOINT = "http://localhost:46817";

const resource = new Resource({
  [S.SERVICE_NAME]: "Open-AI Q/A Agent",
  [S.SERVICE_VERSION]: "0.1.0",
  "agent.id": "agent://uuid/7df9bc60-8757-4f24-af43-fa58e468a91b"
});

// ---- Traces ----
const tracerProvider = new NodeTracerProvider({ resource });
tracerProvider.addSpanProcessor(
  new BatchSpanProcessor(new OTLPTraceExporter({ url: `${OTEL_ENDPOINT}/v1/traces` }))
);
tracerProvider.register();
export const tracer = tracerProvider.getTracer("Open-AI Q/A Agent");

// ---- Metrics ----
const metricExporter = new OTLPMetricExporter({ url: `${OTEL_ENDPOINT}/v1/metrics` });
const metricReader = new PeriodicExportingMetricReader({
  exporter: metricExporter,
  exportIntervalMillis: 5000
});
const meterProvider = new MeterProvider({ resource });
meterProvider.addMetricReader(metricReader);
export const meter = meterProvider.getMeter("Open-AI Q/A Agent");

// ---- Logs ----
const loggerProvider = new LoggerProvider({ resource });
loggerProvider.addLogRecordProcessor(
  new BatchLogRecordProcessor(new OTLPLogExporter({ url: `${OTEL_ENDPOINT}/v1/logs` }))
);
logs.setGlobalLoggerProvider(loggerProvider);
export const logger = loggerProvider.getLogger("Open-AI Q/A Agent");
```
---

Now run your agent. Telemetry will flow into your A2A dashboard.
