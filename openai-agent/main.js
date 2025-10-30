import bodyParser from "body-parser";
import express from "express";
import { OpenAI } from "openai";
import winston from "winston";

// --- OpenTelemetry ---
import { metrics, trace } from "@opentelemetry/api";
// import { Resource } from "@opentelemetry/resources";
import pkg from '@opentelemetry/resources';
import { ConsoleMetricExporter, PeriodicExportingMetricReader } from "@opentelemetry/sdk-metrics";
import { NodeSDK } from "@opentelemetry/sdk-node";
import { ConsoleSpanExporter } from "@opentelemetry/sdk-trace-base";
import { SemanticResourceAttributes } from "@opentelemetry/semantic-conventions";
const { Resource } = pkg;

// ---------------- CONFIG ----------------
const SERVICE_NAME = "simple-ai-agent";

// Winston logger
const logger = winston.createLogger({
  level: "info",
  format: winston.format.json(),
  transports: [new winston.transports.Console()],
});

// OpenTelemetry SDK setup
const sdk = new NodeSDK({
  resource: Resource.default().merge( 
  new Resource({
    [SemanticResourceAttributes.SERVICE_NAME]: SERVICE_NAME,
  }),
),
  traceExporter: new ConsoleSpanExporter(),
  metricReader: new PeriodicExportingMetricReader({
    exporter: new ConsoleMetricExporter(),
    exportIntervalMillis: 3000,
  }),
});

await sdk.start();
logger.info("✅ OpenTelemetry initialized");

// OTEL handles
const tracer = trace.getTracer("agent-tracer");
const meter = metrics.getMeter("agent-meter");

// Custom metrics
const questionsCounter = meter.createCounter("questions_total");
const latencyHistogram = meter.createHistogram("response_latency_ms");

// OpenAI client
const client = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// ---------------- Express App ----------------
const app = express();
app.use(bodyParser.json());

// POST /ask endpoint
app.post("/ask", async (req, res) => {
  const { text } = req.body;

  return tracer.startActiveSpan("ask_question", async (span) => {
    const start = Date.now();
    span.setAttribute("user.question", text);
    logger.info({ event: "question_received", question: text });

    try {
      const response = await client.chat.completions.create({
        model: "gpt-4o-mini",
        messages: [{ role: "user", content: text }],
      });

      const answer = response.choices[0].message.content;
      const duration = Date.now() - start;

      // Metrics + trace attrs
      questionsCounter.add(1);
      latencyHistogram.record(duration);
      span.setAttribute("response.latency_ms", duration);
      span.setAttribute("response.answer_preview", answer.slice(0, 50));

      logger.info({ event: "answer_produced", latency_ms: duration });
      span.end();

      return res.json({ answer, latency_ms: duration });
    } catch (err) {
      logger.error({ event: "openai_error", error: err.message });
      span.recordException(err);
      span.end();
      return res.status(500).json({ error: "llm_failed" });
    }
  });
});

// Health check
app.get("/health", (req, res) => {
  logger.info("Health check OK");
  res.json({ ok: true, service: SERVICE_NAME });
});

// Start server
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
  logger.info(`🚀 Server running on http://localhost:${PORT}`);
});
