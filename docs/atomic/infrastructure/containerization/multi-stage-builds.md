# Multi-Stage Builds

Multi-stage builds keep images lean by separating build-time dependencies from runtime artefacts.

## Pattern

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv \
    && uv pip install --system -r requirements.txt
COPY src ./src
RUN uv pip install --system .

FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /app/src ./src
USER app
CMD ["python", "-m", "src.main"]
```

## Guidelines

- Place tooling (compilers, build helpers) in the builder stage only.
- Copy only required artefacts into the runtime stage (application code, dependencies, config templates).
- Validate image size in CI to detect regressions.
- Use build arguments to toggle optional components without duplicating Dockerfiles.

## Related Documents

- `docs/atomic/infrastructure/containerization/dockerfile-patterns.md`
- `docs/atomic/infrastructure/deployment/production-deployment.md`
