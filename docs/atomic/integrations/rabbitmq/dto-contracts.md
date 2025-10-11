# DTO Contracts

Standardise message payloads using Pydantic models to keep producers and consumers aligned.

## Guidelines

- Define DTOs in `src/shared/events/` with descriptive names (`PhotoReceivedEvent`).
- Include schema version to support backward compatibility.
- Keep payloads minimal: identifiers, metadata, and links to large artifacts rather than embedding binaries.
- Validate DTOs before publishing and after consuming to prevent silent contract drift.

## Example

```python
from pydantic import BaseModel, Field
from uuid import UUID


class PhotoReceivedEvent(BaseModel):
    event_id: UUID = Field(..., description="Unique event identifier")
    user_id: int = Field(..., description="Telegram user id")
    file_path: str = Field(..., description="Temporary file storage path")
    occurred_at: str = Field(..., description="ISO 8601 timestamp")
```

## Documentation

- Maintain an event catalogue describing routing keys, DTOs, and consumers.
- Version DTOs using suffixes (`PhotoReceivedEventV2`) when breaking fields change; run dual publishing during migration.

## Related Documents

- `docs/atomic/services/data-services/repository-patterns.md`
- `docs/atomic/architecture/ddd-hexagonal-principles.md`
