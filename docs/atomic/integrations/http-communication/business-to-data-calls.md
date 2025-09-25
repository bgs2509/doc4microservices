# Business → Data Service Calls

Business services call data services exclusively over HTTP. Keep clients typed, resilient, and observability-friendly.

## Client Responsibilities

- Serialize requests and responses with Pydantic models shared between producer and consumer.
- Propagate headers: `X-Request-ID`, `X-User-ID`, auth tokens.
- Translate HTTP errors into domain-specific exceptions with enough context for callers.

## Workflow

```python
class UserDataClient:
    def __init__(self, client: AsyncClient, settings: Settings) -> None:
        self._client = client
        self._base_url = settings.data_service_url

    async def get_user(self, user_id: str) -> UserPublic:
        response = await self._client.get(f"{self._base_url}/api/v1/users/{user_id}")
        response.raise_for_status()
        return UserPublic.model_validate_json(response.text)
```

## Validation

- Verify contracts in integration tests using real data services (Testcontainers).
- Snap OpenAPI specs to detect incompatible changes.

## Observability

- Tag logs with target service name and request duration.
- Emit metrics per endpoint call (success rate, latency percentiles).

## Related Documents

- `docs/atomic/services/data-services/http-api-design.md`
- `docs/atomic/integrations/http-communication/http-client-patterns.md`
