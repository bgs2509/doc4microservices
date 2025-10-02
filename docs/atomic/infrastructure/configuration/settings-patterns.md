# Settings Patterns

Centralise configuration logic to keep services predictable.

## BaseSettings

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "template_business_api"
    data_service_url: str
    redis_url: str

    class Config:
        env_prefix = "API_"
        case_sensitive = False
```

- Instantiate settings once at startup (`get_settings()` with `lru_cache`).
- Support environment-specific prefixes to avoid clashes.
- Validate values with Pydantic constraints (URLs, enums, ranges).

## Hierarchical Config

- Compose settings: global settings + service overrides + feature-specific settings (e.g., `RabbitMQSettings`).
- Provide typed accessors for nested configs to reduce stringly typed usage.

## Testing

- Override environment variables within tests using `monkeypatch`.
- Provide factory helpers to create `Settings` with sensible defaults for unit tests.

## Related Documents

- `docs/atomic/infrastructure/configuration/environment-variables.md`
- `docs/atomic/infrastructure/configuration/configuration-validation.md`
