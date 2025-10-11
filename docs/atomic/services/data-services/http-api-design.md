# HTTP API Design for Data Services

Data services expose HTTP endpoints consumed by business services. Contracts must be stable, well-documented, and domain-aware.

## Endpoint Structure

- Prefix all routes with `/api/v1` (bump version on breaking changes).
- Use nouns for resource endpoints (`/users`, `/orders/{id}`) and verbs for commands when needed (`/orders/{id}/cancel`).
- Provide domain-level operations (aggregations, projections) in addition to CRUD.

## Response Format

- Return DTOs defined in `src/schemas/` with descriptive fields.
- Use cursor-based pagination for large collections (`next_cursor`, `limit`).
- Include consistent metadata (e.g., `total_items` if available) without leaking internal IDs.

## Error Semantics

- 400 – validation errors (missing/invalid data).
- 404 – resource not found.
- 409 – conflict (duplicate keys, version mismatch).
- 422 – domain constraint violations when input is syntactically valid but semantically incorrect.
- 500 – unexpected errors (should be rare; log and alert).

Error responses follow Problem Details (`error-handling.md`).

## Idempotency

- Require `Idempotency-Key` header for non-idempotent POST/PUT when clients might retry.
- Store keys in Redis with TTL; reject duplicates with 409/Problem Details.

## Observability

- Propagate request IDs from headers; generate if absent.
- Emit metrics per endpoint (throughput, latency, error rate).
- Log payload sizes for heavy endpoints to monitor traffic growth.

## Related Documents

- `docs/atomic/services/data-services/testing-strategies.md`
- `docs/atomic/integrations/http-communication/business-to-data-calls.md`
