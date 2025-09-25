# Dockerfile Patterns

Produce small, secure images that align with the platform runtime.

## Guidelines

- Use official Python 3.12 slim images as the base.
- Install build dependencies separately from runtime dependencies; clean up caches to keep images small.
- Set the working directory to `/app` and copy only necessary files.
- Pin OS packages to avoid nondeterministic builds.
- Run as non-root (`USER app`) and create the user in the Dockerfile.
- Expose ports via configuration variables rather than hard-coded values.

## Example Skeleton

```dockerfile
FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv \
    && uv pip install --system -r requirements.txt

COPY src ./src
CMD ["python", "-m", "src.main"]
```

## Security

- Use multi-stage builds to exclude dev tooling.
- Scan images regularly (Trivy, Grype) and fail CI on critical vulnerabilities.
- Keep base images updated; patch vulnerabilities promptly.

## Related Documents

- `docs/atomic/infrastructure/containerization/multi-stage-builds.md`
- `docs/atomic/infrastructure/deployment/production-deployment.md`
