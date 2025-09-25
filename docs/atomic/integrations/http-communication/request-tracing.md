# Request Tracing

Propagate correlation identifiers across inter-service HTTP calls for observability.

## Headers

- `X-Request-ID` – deterministic identifier for the end-to-end request. Reuse inbound value or generate a UUID.
- `traceparent` / `tracestate` – W3C trace context for distributed tracing when OpenTelemetry is enabled.
- `X-User-ID` (optional) – user-level correlation when policy allows.

## Implementation

```python
async def forward_headers(client, url, payload, context):
    headers = {
        "X-Request-ID": context.request_id,
        "traceparent": context.traceparent,
        "tracestate": context.tracestate or "",
    }
    return await client.post(url, json=payload, headers=headers)
```

## Logging

- Include request ID and target service in logs to join producer and consumer events.
- Record spans around outbound calls to measure dependency latency and populate distributed traces.

## Testing

- Assert outbound HTTP calls carry required headers using tooling such as `respx`.
- Validate traces appear in Jaeger or Tempo during integration tests.

## Related Documents

- `docs/atomic/observability/tracing/opentelemetry-setup.md`
- `docs/atomic/integrations/http-communication/http-client-patterns.md`
