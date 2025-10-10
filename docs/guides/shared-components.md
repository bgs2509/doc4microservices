# Guide to Shared Components

## Introduction

In a microservice architecture, it is crucial to have a single source of truth for code and data contracts that are used by multiple services. This prevents code duplication, reduces errors, and simplifies system maintenance. In our project, the `src/shared/` directory serves this purpose.

This document describes the types of shared components, the rules for their use, and how to integrate them into services.

## Structure of the `src/shared/` Directory

According to the [Project Structure](../LINKS_REFERENCE.md#developer-guides), the shared directory contains the following components:

- `dtos/`: A package for shared Data Transfer Objects (DTOs), grouped by domain area (e.g., `user_dtos.py`, `product_dtos.py`).
- `events/`: A package for event schemas, also grouped by domain (e.g., `user_events.py`).
- `utils/`: A package for common utility functions, grouped by category (e.g., `cache.py`, `formatters.py`).

## Types of Shared Components

### 1. DTOs and Event Schemas (`dtos/` and `events/`)

These are the most important shared components, as they define the **data contracts** between services.

- **Technology**: All DTOs and event schemas must be implemented using `pydantic.BaseModel`.
- **Purpose**:
    - **Ensuring Consistency**: All services "speak" the same language, using identical data structures.
    - **Validation**: Pydantic automatically validates data upon creation or receipt, which increases system reliability.
    - **Self-documentation**: The code for Pydantic models serves as excellent documentation for the data contracts.
- **Naming Rules**:
    - The naming of these models **MUST** strictly follow the rules outlined in the [Naming Conventions](../LINKS_REFERENCE.md#ide-rules-and-patterns) document.
    - The key principle is **naming by purpose**:
        - `...Base`: for base models.
        - `...Create`: for creating entities.
        - `...Update`: for partial updates.
        - `...Public`: for public API responses.
        - `...Payload`: for messages in a message broker.

### 2. Common Utilities (`utils/`)

This package is intended for small, reusable helper functions that can be used in any service. Functions should be grouped by category into separate files.

- **Key Requirement**: Functions in the `utils/` package must be **pure** and **stateless**. This means they must not depend on external state and must not access databases, the network, or the file system.

- **Example structure of the `utils/` package**:
    - `utils/cache.py`: Utilities for working with the cache.
    - `utils/formatters.py`: Functions for data formatting.
    - `utils/validators.py`: Common, reusable validators.

- **What should NOT be in `utils/`**:
    - Business logic specific to a single service.
    - Functions that import anything from a specific service (e.g., from `template_business_api`).
    - Any code that performs I/O operations.

## Usage and Import in Services

Shared components should be imported into services using absolute paths from the `src/` root.

**Rule #1: Shared components are never redefined locally.**

If a service needs an extended or modified version of a shared component, it must **create a new, internal class** that inherits from or transforms the shared component, but it must not modify the shared component itself.

### Example of Import and Usage

Suppose `template_business_worker` needs to process a user and use a shared utility for it.

**`src/shared/dtos/user_dtos.py`**
```python
from pydantic import BaseModel
import uuid
from datetime import datetime

class UserPublic(BaseModel):
    id: int
    email: str
```

**`src/shared/utils/generators.py`**
```python
import uuid

def generate_processing_id(user_id: int, task_name: str) -> str:
    return f"{task_name}_{user_id}_{uuid.uuid4()}"
```

**`src/template_business_worker/tasks.py`**
```python
# Import shared components from packages
from shared.dtos.user_dtos import UserPublic
from shared.utils.generators import generate_processing_id

def process_user_task(user: UserPublic):
    # Use the shared components
    processing_id = generate_processing_id(user.id, "send_email")
    
    print(f"Starting task {processing_id} for user {user.email}")
    # ... rest of the logic
```
This approach ensures a clean, predictable, and easily maintainable codebase.