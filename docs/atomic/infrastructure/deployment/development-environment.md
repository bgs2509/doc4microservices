# Development Environment Setup

Provide a consistent local environment for all contributors.

## Tooling

- Install Python 3.12+, uv/pip, Docker, and Docker Compose.
- Configure pre-commit hooks (ruff, mypy, markdownlint) to catch issues early.
- Use VS Code or PyCharm settings stored in `.editorconfig`/`.vscode` where appropriate.

## Workflow

- Start dependencies via `docker-compose up` (PostgreSQL, Redis, RabbitMQ).
- Run `uv pip install --sync` to align dependencies with `uv.lock`.
- Execute `make test` / `make lint` (or equivalent scripts) before committing.

## Environment Variables

- Copy `.env.example` to `.env` and fill in local values.
- Avoid committing `.env`; use `.env.local` overrides for machine-specific settings.

## DX Enhancements

- Enable auto-reload for FastAPI services using `uvicorn --reload`.
- Use Telepresence or port-forwarding to test against remote dependencies when required.

## Related Documents

- `docs/atomic/infrastructure/containerization/docker-compose-setup.md`
- `docs/atomic/architecture/quality-standards.md`
