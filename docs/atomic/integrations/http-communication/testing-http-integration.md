# HTTP Integration Testing

Validate inter-service HTTP calls end-to-end to prevent contract regressions.

## Strategy

- Spin up dependent services locally (Testcontainers) or use dedicated staging endpoints.
- Seed known data in data services before calling business APIs.
- Assert HTTP status codes, response bodies, and headers (including tracing and caching directives).

## Tooling

- Use `httpx.AsyncClient` inside tests for async compatibility.
- Capture OpenAPI schemas in artifacts to detect breaking changes.
- Run contract tests (for example, Pact) when consumers and providers are maintained by different teams.

## Failure Modes

- Simulate timeouts and ensure retry/backoff logic behaves as expected.
- Inject malformed payloads to confirm the service returns RFC 7807 Problem Details.

## Automation

- Integrate tests into CI pipelines and tag them as integration to allow parallelism.
- Publish logs and metrics snapshots from test runs for quick diagnostics.

## Related Documents

- `docs/atomic/integrations/http-communication/error-handling-strategies.md`
- `docs/atomic/testing/integration-testing/http-integration-testing.md`
