# DDD and Hexagonal Principles

The Improved Hybrid Approach relies on Domain-Driven Design (DDD) and Hexagonal Architecture to keep services modular and testable. This document summarises how those concepts map to the project structure.

## Layering Model

```
┌──────────────┐
│   Interfaces │  (FastAPI routers, bot handlers, CLI)
├──────────────┤
│ Application  │  (Use cases, orchestrators, service classes)
├──────────────┤
│    Domain    │  (Entities, value objects, domain services)
├──────────────┤
│ Infrastructure │ (Repositories, HTTP clients, messaging adapters)
└──────────────┘
```

- **Interfaces** convert transport-specific payloads to domain requests/responses.
- **Application layer** coordinates domain operations; it contains minimal logic, delegating to domain services.
- **Domain layer** models business rules and invariants. It has no dependencies on frameworks.
- **Infrastructure layer** provides implementations for persistence, messaging, and external systems.

## Implementation Guidelines

- Keep routers thin: no direct database calls or complex branching logic.
- Domain services enforce invariants; repositories must not “fix” invalid states.
- Use interfaces or protocols for repositories and external gateways to enable mocking in tests.
- Name modules after domain contexts (`users`, `orders`), not technical layers.
- Keep each domain type in its own file to respect the “minimum atomic file size” requirement.

## DTO and Mapping Strategy

- Define DTOs in `schemas/` with descriptive suffixes (`UserCreate`, `OrderPublic`).
- Implement mapping functions or classes in the application layer to convert between DTOs and domain types.
- Avoid leaking ORM models outside infrastructure; domain objects are plain Python classes or Pydantic models that represent intent, not persistence.

## Ports and Adapters

- **Ports** are abstract interfaces defined by the domain/application layers (e.g., `UserRepository`, `PaymentGateway`).
- **Adapters** live in infrastructure and implement those ports (e.g., `SqlAlchemyUserRepository`).
- Use dependency injection to wire adapters at runtime.

## Testing Implications

- Unit tests focus on the domain/application layers by mocking ports.
- Integration tests exercise adapters against real dependencies (DB, message brokers).
- Contract tests verify that adapters honour expectations published by external systems.

## Anti-Corruption Layer (ACL)

- Introduce ACLs where legacy systems or third-party APIs supply inconsistent payloads.
- ACLs translate external DTOs into domain types, ensuring the domain remains clean.

## Related Documents

- `docs/atomic/architecture/project-structure-patterns.md`
- `docs/atomic/services/fastapi/application-factory.md`
- `docs/atomic/services/data-services/repository-patterns.md`
