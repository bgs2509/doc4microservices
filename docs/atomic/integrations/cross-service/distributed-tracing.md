# Distributed Tracing

Distributed tracing reveals end-to-end latency across services.

## Instrumentation

- Use OpenTelemetry SDK with auto-instrumentation for FastAPI, httpx, and aio-pika.
- Start spans around business-critical operations when auto-instrumentation is insufficient.
- Attach request IDs and user identifiers as span attributes, respecting privacy rules.

## Propagation

- Forward `traceparent` / `tracestate` headers across HTTP boundaries.
- Add trace headers to RabbitMQ messages (store in message headers) so background workers extend the same trace.

## Exporters

- Use OTLP exporters to send spans to Jaeger, Tempo, or Honeycomb.
- Configure batching and timeouts to avoid blocking request paths.

## Observability

- Correlate traces with logs and metrics using consistent request IDs.
- Set latency SLOs for key transactions and alert when budgets are exceeded.

## Related Documents

- `docs/atomic/observability/tracing/opentelemetry-setup.md`
- `docs/atomic/integrations/http-communication/request-tracing.md`
