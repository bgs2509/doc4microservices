# OpenAPI Documentation

FastAPI auto-generates OpenAPI schemas; refine them to stay contract-first.

## Metadata

Set global metadata in `create_app()`:

```python
app = FastAPI(
    title=settings.service_name,
    version=settings.version,
    description="HTTP API for managing user accounts",
    contact={"name": "Platform Team", "email": "platform@example.com"},
    license_info={"name": "Proprietary"},
)
```

## Tags and Summaries

- Group endpoints by router tags (e.g., `users`, `orders`).
- Provide concise `summary` and detailed `description` for each endpoint.
- Use `deprecated=True` to mark endpoints scheduled for removal.

## Schema Customisation

- Define reusable enums and models; avoid `Any`.
- Document error responses by adding `responses` parameter on routes.

```python
error_responses = {
    404: {"description": "User not found", "model": ProblemDetails},
    409: {"description": "Conflict", "model": ProblemDetails},
}

@router.post("", responses=error_responses)
async def create_user(...):
    ...
```

## Documentation Workflow

1. Generate schema during CI (`poetry run uvicorn src.main:app --reload` or `python -m scripts.export_openapi`).
2. Review diff in pull requests; breaking changes require API version bump.
3. Publish schema to the developer portal or `docs/reference` as needed.

## Testing

- Snap test the OpenAPI spec to prevent accidental contract drift.
- Validate schema with `openapi-spec-validator` in CI.

## Related Documents

- `docs/atomic/services/fastapi/schema-validation.md`
- `docs/atomic/architecture/improved-hybrid-overview.md`
- Legacy reference: `docs/legacy/services/fastapi_rules.mdc`
