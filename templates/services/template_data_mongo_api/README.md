# MongoDB Data Service Template

**Status**: 🚧 In Development
**Purpose**: HTTP-only data access service for MongoDB database

## Overview

This template provides a FastAPI-based HTTP data service that exposes MongoDB database operations following the framework's Improved Hybrid Approach architecture.

## Key Features

- HTTP-only data access (no direct DB access from business services)
- RESTful CRUD operations for documents
- Motor async MongoDB driver
- Schema validation with Pydantic
- Aggregation pipeline support
- Full-text search capabilities
- Health check endpoints

## Architecture Compliance

Following the mandatory Improved Hybrid Approach:
- Business services call this service via HTTP
- No direct database connections from business layer
- Stateless HTTP API design
- MongoDB for document storage

## Service Structure

```
template_data_mongo_api/
├── src/
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── database.py          # MongoDB connection setup
│   ├── models/              # Pydantic models
│   ├── repositories/        # Data access layer
│   │   ├── base.py         # Base repository
│   │   └── document_repo.py # Document operations
│   └── routers/             # API endpoints
│       ├── health.py        # Health checks
│       └── documents.py     # Document CRUD
├── tests/                   # Unit and integration tests
├── Dockerfile               # Container definition
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Usage

When using this template:

1. **Rename the service**: Replace `template_data_mongo_api` with your actual service name (e.g., `analytics_data_mongo_api`)
2. **Configure MongoDB**: Update connection settings in config.py
3. **Define models**: Create Pydantic models for your documents
4. **Implement repositories**: Add data access methods
5. **Define API endpoints**: Create routers for your collections
6. **Setup indexes**: Configure MongoDB indexes for performance

## Example Endpoints

- `GET /health` - Service health check
- `GET /ready` - MongoDB readiness check
- `POST /documents` - Create document
- `GET /documents/{id}` - Get document by ID
- `PUT /documents/{id}` - Update document
- `DELETE /documents/{id}` - Delete document
- `GET /documents` - List documents with pagination
- `POST /documents/search` - Full-text search
- `POST /documents/aggregate` - Run aggregation pipeline

## Environment Variables

```env
MONGODB_URL=mongodb://mongo:27017
DATABASE_NAME=microservices
SERVICE_PORT=8002
LOG_LEVEL=INFO
MAX_POOL_SIZE=20
MIN_POOL_SIZE=5
```

## MongoDB Collections

```javascript
// Example collection structure
{
  users: {
    indexes: [
      { email: 1 },           // Single field index
      { created_at: -1 },     // Descending index
      { "$**": "text" }       // Text search index
    ]
  },
  events: {
    indexes: [
      { timestamp: -1 },
      { user_id: 1, event_type: 1 }  // Compound index
    ],
    options: {
      capped: true,
      size: 10485760  // 10MB capped collection
    }
  }
}
```

## Query Examples

```python
# Basic CRUD
await repo.create({"name": "John", "email": "john@example.com"})
doc = await repo.find_by_id(doc_id)
await repo.update(doc_id, {"$set": {"name": "Jane"}})
await repo.delete(doc_id)

# Aggregation
pipeline = [
    {"$match": {"status": "active"}},
    {"$group": {"_id": "$category", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
result = await repo.aggregate(pipeline)
```

## Related Documentation

- MongoDB Patterns - See framework documentation
- [Data Access Architecture](../../../docs/atomic/architecture/data-access-architecture.md)
- [HTTP Communication](../../../docs/atomic/integrations/http-communication/)
- NoSQL Best Practices - See framework documentation

---

**Note**: This is a template. Full implementation coming soon.