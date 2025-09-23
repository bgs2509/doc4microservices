# Example: MongoDB Data Service

This document demonstrates the implementation of a **MongoDB Data Service** following the "Improved Hybrid Approach" architecture. This service is the single point of access to MongoDB database for all business services and implements all patterns from `docs/architecture/data-access-rules.mdc`.

## Key Characteristics
- **Technology:** FastAPI + Motor (async MongoDB driver)
- **Responsibility:** Document storage, analytics events, user behavior, aggregation pipelines
- **Interface:** RESTful HTTP API with RFC 7807 error handling and OpenAPI documentation
- **Isolation:** Complete MongoDB interaction encapsulation with repository pattern
- **Features:** Aggregation pipelines, indexing, validation, proper error handling, health checks

---

## 1. Project Structure (db_mongo_service)

```
services/db_mongo_service/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── analytics.py
│   │       ├── user_behavior.py
│   │       └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── middleware.py      # Request tracking middleware
│   │   └── errors.py          # RFC 7807 error handling
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py           # Base document model
│   │   ├── analytics.py      # Analytics event model
│   │   └── user_behavior.py  # User behavior model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── analytics.py      # Pydantic schemas
│   │   ├── user_behavior.py  # User behavior schemas
│   │   ├── common.py         # Common schemas (pagination, filters)
│   │   └── errors.py         # RFC 7807 error schemas
│   └── repositories/
│       ├── __init__.py
│       ├── base_repository.py       # Base repository with aggregation
│       ├── analytics_repository.py  # Analytics operations
│       └── user_behavior_repository.py # User behavior operations
├── tests/
│   ├── conftest.py           # Test configuration with testcontainers
│   ├── test_analytics_repository.py
│   └── test_analytics_api.py
├── collections/
│   ├── analytics_events.json # Collection schema and indexes
│   └── user_behavior.json    # Collection schema and indexes
└── Dockerfile
```

---

## 2. Database Models

### Base Document Model (`src/models/base.py`)
Base document model with common fields and utilities.

```python
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId

class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class TimestampMixin(BaseModel):
    """Mixin for adding timestamp fields."""

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Document creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Document last update timestamp"
    )

class BaseDocument(TimestampMixin):
    """Base document model with ID and timestamps."""

    id: Optional[PyObjectId] = Field(
        default_factory=PyObjectId,
        alias="_id",
        description="Document unique identifier"
    )

    class Config:
        """Pydantic configuration."""
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
```

### Analytics Event Model (`src/models/analytics.py`)
Analytics event model with proper validation and indexing.

```python
from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import Field, validator
from .base import BaseDocument

class EventType(str, Enum):
    """Analytics event types."""
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    BUSINESS_EVENT = "business_event"
    ERROR_EVENT = "error_event"

class EventCategory(str, Enum):
    """Event categories for analytics."""
    AUTHENTICATION = "authentication"
    NAVIGATION = "navigation"
    INTERACTION = "interaction"
    PERFORMANCE = "performance"
    ERROR = "error"

class AnalyticsEvent(BaseDocument):
    """Analytics event document."""

    # Event identification
    event_type: EventType = Field(
        ...,
        description="Type of analytics event"
    )
    event_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Specific event name",
        example="user_login"
    )
    category: EventCategory = Field(
        ...,
        description="Event category for grouping"
    )

    # User and session context
    user_id: Optional[str] = Field(
        None,
        description="User identifier if authenticated",
        example="user_12345"
    )
    session_id: Optional[str] = Field(
        None,
        description="Session identifier",
        example="session_abcdef"
    )
    request_id: str = Field(
        ...,
        description="Request correlation identifier",
        example="req_uuid_12345"
    )

    # Event data and metadata
    properties: Dict[str, Any] = Field(
        default_factory=dict,
        description="Event-specific properties and data"
    )
    user_agent: Optional[str] = Field(
        None,
        max_length=500,
        description="User agent string"
    )
    ip_address: Optional[str] = Field(
        None,
        description="Client IP address (anonymized)"
    )

    # Performance and timing
    duration_ms: Optional[int] = Field(
        None,
        ge=0,
        description="Event duration in milliseconds"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Event occurrence timestamp"
    )

    # Source and environment
    source_service: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Service that generated the event",
        example="api_service"
    )
    environment: str = Field(
        default="production",
        description="Environment where event occurred"
    )

    @validator("properties")
    def validate_properties_size(cls, v):
        """Validate properties don't exceed reasonable size."""
        import json
        if len(json.dumps(v)) > 10000:  # 10KB limit
            raise ValueError("Properties data too large (max 10KB)")
        return v

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "event_type": "user_action",
                "event_name": "button_click",
                "category": "interaction",
                "user_id": "user_12345",
                "session_id": "session_abcdef",
                "request_id": "req_uuid_12345",
                "properties": {
                    "button_id": "submit_form",
                    "page_url": "/dashboard",
                    "form_data": {"field_count": 5}
                },
                "duration_ms": 150,
                "source_service": "api_service",
                "environment": "production"
            }
        }
```

### User Behavior Model (`src/models/user_behavior.py`)
User behavior tracking with session management.

```python
from typing import Optional, List, Dict, Any
from pydantic import Field, validator
from .base import BaseDocument

class UserSession(BaseDocument):
    """User session tracking document."""

    user_id: str = Field(
        ...,
        description="User identifier",
        example="user_12345"
    )
    session_id: str = Field(
        ...,
        description="Unique session identifier",
        example="session_abcdef"
    )

    # Session timing
    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Session start timestamp"
    )
    last_activity_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last activity timestamp"
    )
    ended_at: Optional[datetime] = Field(
        None,
        description="Session end timestamp"
    )

    # Session context
    ip_address: Optional[str] = Field(
        None,
        description="Session IP address (anonymized)"
    )
    user_agent: Optional[str] = Field(
        None,
        max_length=500,
        description="User agent string"
    )
    device_type: Optional[str] = Field(
        None,
        description="Device type (mobile, desktop, tablet)"
    )

    # Activity tracking
    page_views: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of page views in session"
    )
    actions_count: int = Field(
        default=0,
        ge=0,
        description="Total actions performed in session"
    )
    duration_seconds: Optional[int] = Field(
        None,
        ge=0,
        description="Session duration in seconds"
    )

    # Session metadata
    is_active: bool = Field(
        default=True,
        description="Whether session is currently active"
    )
    source_service: str = Field(
        ...,
        description="Service that created the session"
    )

class UserBehaviorSummary(BaseDocument):
    """Daily user behavior summary."""

    user_id: str = Field(
        ...,
        description="User identifier"
    )
    date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Date in YYYY-MM-DD format",
        example="2025-01-15"
    )

    # Activity metrics
    sessions_count: int = Field(
        default=0,
        ge=0,
        description="Number of sessions"
    )
    total_duration_seconds: int = Field(
        default=0,
        ge=0,
        description="Total time spent"
    )
    page_views_count: int = Field(
        default=0,
        ge=0,
        description="Total page views"
    )
    actions_count: int = Field(
        default=0,
        ge=0,
        description="Total actions performed"
    )

    # Engagement metrics
    avg_session_duration: Optional[float] = Field(
        None,
        ge=0,
        description="Average session duration in seconds"
    )
    bounce_rate: Optional[float] = Field(
        None,
        ge=0,
        le=1,
        description="Bounce rate (0-1)"
    )

    # Most visited pages
    top_pages: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Most visited pages with counts"
    )

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "user_id": "user_12345",
                "date": "2025-01-15",
                "sessions_count": 3,
                "total_duration_seconds": 1800,
                "page_views_count": 25,
                "actions_count": 15,
                "avg_session_duration": 600.0,
                "bounce_rate": 0.33,
                "top_pages": [
                    {"url": "/dashboard", "views": 8},
                    {"url": "/profile", "views": 5}
                ]
            }
        }
```

## 3. Schemas with Aggregation (`src/schemas/common.py`)

Common schemas for pagination and aggregation operations.

```python
from typing import Optional, Dict, Any, List, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field, validator

T = TypeVar('T')

class PaginationParams(BaseModel):
    """Pagination parameters for MongoDB queries."""

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of items per page (1-100)"
    )
    skip: int = Field(
        default=0,
        ge=0,
        description="Number of items to skip"
    )

class SortParams(BaseModel):
    """Sorting parameters for MongoDB queries."""

    sort_by: Optional[str] = Field(
        default="created_at",
        description="Field to sort by"
    )
    sort_order: Optional[int] = Field(
        default=-1,
        description="Sort order: 1 for ascending, -1 for descending"
    )

    @validator("sort_order")
    def validate_sort_order(cls, v):
        """Validate sort order is 1 or -1."""
        if v not in [1, -1]:
            raise ValueError("Sort order must be 1 (ascending) or -1 (descending)")
        return v

class DateRangeFilter(BaseModel):
    """Date range filter for time-based queries."""

    start_date: Optional[datetime] = Field(
        None,
        description="Start date for filtering"
    )
    end_date: Optional[datetime] = Field(
        None,
        description="End date for filtering"
    )

    @validator("end_date")
    def validate_date_range(cls, v, values):
        """Ensure end_date is after start_date."""
        if v and values.get("start_date") and v <= values["start_date"]:
            raise ValueError("End date must be after start date")
        return v

class AggregationParams(BaseModel):
    """Parameters for aggregation queries."""

    group_by: str = Field(
        ...,
        description="Field to group by for aggregation"
    )
    time_bucket: Optional[str] = Field(
        None,
        description="Time bucket for time-based aggregation (hour, day, week, month)"
    )
    metrics: List[str] = Field(
        default_factory=lambda: ["count"],
        description="Metrics to calculate (count, sum, avg, min, max)"
    )

    @validator("time_bucket")
    def validate_time_bucket(cls, v):
        """Validate time bucket values."""
        if v and v not in ["hour", "day", "week", "month"]:
            raise ValueError("Time bucket must be one of: hour, day, week, month")
        return v

class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response for MongoDB collections."""

    items: List[T] = Field(
        ...,
        description="List of items"
    )
    total: int = Field(
        ...,
        description="Total number of items"
    )
    limit: int = Field(
        ...,
        description="Items per page"
    )
    skip: int = Field(
        ...,
        description="Items skipped"
    )
    has_next: bool = Field(
        ...,
        description="Whether there are more items"
    )
    has_prev: bool = Field(
        ...,
        description="Whether there are previous items"
    )

class AggregationResult(BaseModel):
    """Result of aggregation query."""

    group_key: Any = Field(
        ...,
        description="The value that items were grouped by"
    )
    metrics: Dict[str, Any] = Field(
        ...,
        description="Calculated metrics for the group"
    )
    item_count: int = Field(
        ...,
        description="Number of items in this group"
    )
```

## 4. Base Repository (`src/repositories/base_repository.py`)

Base repository with MongoDB-specific operations and aggregation support.

```python
from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId
from datetime import datetime

from ..schemas.common import PaginationParams, SortParams, PaginatedResponse, AggregationParams, AggregationResult
from ..models.base import BaseDocument

DocumentType = TypeVar("DocumentType", bound=BaseDocument)

class BaseRepository(Generic[DocumentType]):
    """Base repository with common MongoDB operations and aggregation."""

    def __init__(self, collection: AsyncIOMotorCollection, model: Type[DocumentType]):
        self.collection = collection
        self.model = model

    async def find_by_id(self, document_id: str) -> Optional[DocumentType]:
        """Find document by ID."""
        if not ObjectId.is_valid(document_id):
            return None

        document = await self.collection.find_one({"_id": ObjectId(document_id)})
        return self.model(**document) if document else None

    async def find_many(
        self,
        filter_dict: Dict[str, Any],
        pagination: PaginationParams,
        sort: SortParams
    ) -> PaginatedResponse[DocumentType]:
        """Find multiple documents with pagination and sorting."""

        # Count total documents
        total = await self.collection.count_documents(filter_dict)

        # Build sort specification
        sort_spec = [(sort.sort_by, sort.sort_order)]

        # Find documents with pagination
        cursor = self.collection.find(filter_dict)
        cursor = cursor.sort(sort_spec).skip(pagination.skip).limit(pagination.limit)

        documents = await cursor.to_list(length=pagination.limit)
        items = [self.model(**doc) for doc in documents]

        return PaginatedResponse(
            items=items,
            total=total,
            limit=pagination.limit,
            skip=pagination.skip,
            has_next=(pagination.skip + pagination.limit) < total,
            has_prev=pagination.skip > 0
        )

    async def create(self, document: DocumentType) -> DocumentType:
        """Create new document."""
        document_dict = document.dict(by_alias=True, exclude_unset=True)

        # Set timestamps
        now = datetime.utcnow()
        document_dict["created_at"] = now
        document_dict["updated_at"] = now

        result = await self.collection.insert_one(document_dict)
        document_dict["_id"] = result.inserted_id

        return self.model(**document_dict)

    async def update(self, document_id: str, update_data: Dict[str, Any]) -> Optional[DocumentType]:
        """Update document by ID."""
        if not ObjectId.is_valid(document_id):
            return None

        # Add update timestamp
        update_data["updated_at"] = datetime.utcnow()

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(document_id)},
            {"$set": update_data},
            return_document=True
        )

        return self.model(**result) if result else None

    async def delete(self, document_id: str) -> bool:
        """Delete document by ID."""
        if not ObjectId.is_valid(document_id):
            return False

        result = await self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0

    async def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute aggregation pipeline."""
        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def count_documents(self, filter_dict: Dict[str, Any]) -> int:
        """Count documents matching filter."""
        return await self.collection.count_documents(filter_dict)

    async def distinct(self, field: str, filter_dict: Optional[Dict[str, Any]] = None) -> List[Any]:
        """Get distinct values for a field."""
        return await self.collection.distinct(field, filter_dict or {})

    def build_text_search_filter(self, search_term: str, fields: List[str]) -> Dict[str, Any]:
        """Build text search filter for multiple fields."""
        if not search_term:
            return {}

        # Create regex pattern for partial matching
        regex_pattern = {"$regex": search_term, "$options": "i"}

        return {
            "$or": [
                {field: regex_pattern} for field in fields
            ]
        }

    def build_date_range_filter(self, field: str, start_date: Optional[datetime], end_date: Optional[datetime]) -> Dict[str, Any]:
        """Build date range filter."""
        date_filter = {}

        if start_date or end_date:
            date_conditions = {}
            if start_date:
                date_conditions["$gte"] = start_date
            if end_date:
                date_conditions["$lte"] = end_date

            date_filter[field] = date_conditions

        return date_filter
```

## 5. Analytics Repository (`src/repositories/analytics_repository.py`)

Analytics-specific repository with aggregation operations.

```python
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorCollection

from .base_repository import BaseRepository
from ..models.analytics import AnalyticsEvent, EventType, EventCategory
from ..schemas.common import PaginationParams, SortParams, DateRangeFilter, AggregationResult

class AnalyticsRepository(BaseRepository[AnalyticsEvent]):
    """Repository for analytics events with aggregation capabilities."""

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, AnalyticsEvent)

    async def create_event(self, event_data: dict) -> AnalyticsEvent:
        """Create new analytics event."""
        event = AnalyticsEvent(**event_data)
        return await self.create(event)

    async def find_events_by_user(
        self,
        user_id: str,
        pagination: PaginationParams,
        date_range: Optional[DateRangeFilter] = None
    ) -> List[AnalyticsEvent]:
        """Find events by user ID with optional date filtering."""
        filter_dict = {"user_id": user_id}

        # Add date range filter
        if date_range:
            date_filter = self.build_date_range_filter(
                "timestamp",
                date_range.start_date,
                date_range.end_date
            )
            filter_dict.update(date_filter)

        sort = SortParams(sort_by="timestamp", sort_order=-1)
        result = await self.find_many(filter_dict, pagination, sort)
        return result.items

    async def find_events_by_type(
        self,
        event_type: EventType,
        pagination: PaginationParams,
        date_range: Optional[DateRangeFilter] = None
    ) -> List[AnalyticsEvent]:
        """Find events by type."""
        filter_dict = {"event_type": event_type}

        if date_range:
            date_filter = self.build_date_range_filter(
                "timestamp",
                date_range.start_date,
                date_range.end_date
            )
            filter_dict.update(date_filter)

        sort = SortParams(sort_by="timestamp", sort_order=-1)
        result = await self.find_many(filter_dict, pagination, sort)
        return result.items

    async def get_event_counts_by_type(
        self,
        date_range: Optional[DateRangeFilter] = None
    ) -> List[AggregationResult]:
        """Get event counts grouped by event type."""
        pipeline = []

        # Add date range match if specified
        if date_range:
            match_conditions = {}
            if date_range.start_date:
                match_conditions["timestamp"] = {"$gte": date_range.start_date}
            if date_range.end_date:
                if "timestamp" in match_conditions:
                    match_conditions["timestamp"]["$lte"] = date_range.end_date
                else:
                    match_conditions["timestamp"] = {"$lte": date_range.end_date}

            if match_conditions:
                pipeline.append({"$match": match_conditions})

        # Group by event type and count
        pipeline.extend([
            {
                "$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1},
                    "avg_duration": {"$avg": "$duration_ms"},
                    "unique_users": {"$addToSet": "$user_id"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "event_type": "$_id",
                    "count": 1,
                    "avg_duration_ms": {"$round": ["$avg_duration", 2]},
                    "unique_users_count": {"$size": "$unique_users"}
                }
            },
            {"$sort": {"count": -1}}
        ])

        results = await self.aggregate(pipeline)

        return [
            AggregationResult(
                group_key=result["event_type"],
                metrics={
                    "count": result["count"],
                    "avg_duration_ms": result.get("avg_duration_ms"),
                    "unique_users_count": result["unique_users_count"]
                },
                item_count=result["count"]
            )
            for result in results
        ]

    async def get_daily_event_summary(
        self,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get daily event summary for the last N days."""
        start_date = datetime.utcnow() - timedelta(days=days)

        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": {
                        "year": {"$year": "$timestamp"},
                        "month": {"$month": "$timestamp"},
                        "day": {"$dayOfMonth": "$timestamp"}
                    },
                    "total_events": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"},
                    "event_types": {"$addToSet": "$event_type"},
                    "avg_duration": {"$avg": "$duration_ms"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "date": {
                        "$dateFromParts": {
                            "year": "$_id.year",
                            "month": "$_id.month",
                            "day": "$_id.day"
                        }
                    },
                    "total_events": 1,
                    "unique_users_count": {"$size": "$unique_users"},
                    "unique_event_types": {"$size": "$event_types"},
                    "avg_duration_ms": {"$round": ["$avg_duration", 2]}
                }
            },
            {"$sort": {"date": 1}}
        ]

        return await self.aggregate(pipeline)

    async def get_user_activity_summary(
        self,
        user_id: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """Get activity summary for a specific user."""
        start_date = datetime.utcnow() - timedelta(days=days)

        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "timestamp": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_events": {"$sum": 1},
                    "event_types": {"$addToSet": "$event_type"},
                    "categories": {"$addToSet": "$category"},
                    "total_duration": {"$sum": "$duration_ms"},
                    "sessions": {"$addToSet": "$session_id"},
                    "first_event": {"$min": "$timestamp"},
                    "last_event": {"$max": "$timestamp"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "user_id": user_id,
                    "period_days": days,
                    "total_events": 1,
                    "unique_event_types": {"$size": "$event_types"},
                    "unique_categories": {"$size": "$categories"},
                    "total_duration_ms": "$total_duration",
                    "unique_sessions": {"$size": "$sessions"},
                    "first_event_at": "$first_event",
                    "last_event_at": "$last_event"
                }
            }
        ]

        results = await self.aggregate(pipeline)
        return results[0] if results else {}

    async def get_popular_events(
        self,
        limit: int = 10,
        date_range: Optional[DateRangeFilter] = None
    ) -> List[Dict[str, Any]]:
        """Get most popular events by name."""
        pipeline = []

        # Add date range filter if specified
        if date_range:
            match_conditions = self.build_date_range_filter(
                "timestamp",
                date_range.start_date,
                date_range.end_date
            )
            if match_conditions:
                pipeline.append({"$match": match_conditions})

        pipeline.extend([
            {
                "$group": {
                    "_id": {
                        "event_name": "$event_name",
                        "category": "$category"
                    },
                    "count": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"},
                    "avg_duration": {"$avg": "$duration_ms"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "event_name": "$_id.event_name",
                    "category": "$_id.category",
                    "count": 1,
                    "unique_users_count": {"$size": "$unique_users"},
                    "avg_duration_ms": {"$round": ["$avg_duration", 2]}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ])

        return await self.aggregate(pipeline)
```

## 6. API Endpoints (`src/api/v1/analytics.py`)

Analytics endpoints with proper HTTP interface and validation.

```python
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from ...core.database import get_database
from ...repositories.analytics_repository import AnalyticsRepository
from ...schemas.analytics import (
    AnalyticsEventCreate,
    AnalyticsEventResponse,
    EventSummaryResponse,
    UserActivitySummaryResponse
)
from ...schemas.common import (
    PaginationParams,
    SortParams,
    DateRangeFilter,
    PaginatedResponse
)
from ...models.analytics import EventType, EventCategory

router = APIRouter()

def get_analytics_repository(db: AsyncIOMotorDatabase = Depends(get_database)) -> AnalyticsRepository:
    """Get analytics repository dependency."""
    return AnalyticsRepository(db.analytics_events)

@router.post("/events", response_model=AnalyticsEventResponse, status_code=201)
async def create_analytics_event(
    event_data: AnalyticsEventCreate,
    repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Create new analytics event."""
    try:
        event = await repo.create_event(event_data.dict())
        return AnalyticsEventResponse.from_orm(event)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create event: {str(e)}")

@router.get("/events", response_model=PaginatedResponse[AnalyticsEventResponse])
async def list_analytics_events(
    pagination: PaginationParams = Depends(),
    sort: SortParams = Depends(),
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    category: Optional[EventCategory] = Query(None, description="Filter by category"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """List analytics events with filtering and pagination."""

    # Build filter conditions
    filter_dict = {}
    if event_type:
        filter_dict["event_type"] = event_type
    if category:
        filter_dict["category"] = category
    if user_id:
        filter_dict["user_id"] = user_id

    # Add date range filter
    if start_date or end_date:
        date_filter = repo.build_date_range_filter("timestamp", start_date, end_date)
        filter_dict.update(date_filter)

    result = await repo.find_many(filter_dict, pagination, sort)

    return PaginatedResponse(
        items=[AnalyticsEventResponse.from_orm(event) for event in result.items],
        total=result.total,
        limit=result.limit,
        skip=result.skip,
        has_next=result.has_next,
        has_prev=result.has_prev
    )

@router.get("/events/{event_id}", response_model=AnalyticsEventResponse)
async def get_analytics_event(
    event_id: str,
    repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get analytics event by ID."""
    event = await repo.find_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Analytics event not found")

    return AnalyticsEventResponse.from_orm(event)

@router.get("/events/user/{user_id}", response_model=List[AnalyticsEventResponse])
async def get_user_events(
    user_id: str,
    pagination: PaginationParams = Depends(),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get analytics events for a specific user."""
    date_range = None
    if start_date or end_date:
        date_range = DateRangeFilter(start_date=start_date, end_date=end_date)

    events = await repo.find_events_by_user(user_id, pagination, date_range)
    return [AnalyticsEventResponse.from_orm(event) for event in events]

@router.get("/summary/events-by-type", response_model=List[EventSummaryResponse])
async def get_events_summary_by_type(
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get event counts grouped by event type."""
    date_range = None
    if start_date or end_date:
        date_range = DateRangeFilter(start_date=start_date, end_date=end_date)

    results = await repo.get_event_counts_by_type(date_range)

    return [
        EventSummaryResponse(
            event_type=result.group_key,
            count=result.metrics["count"],
            avg_duration_ms=result.metrics.get("avg_duration_ms"),
            unique_users_count=result.metrics["unique_users_count"]
        )
        for result in results
    ]

@router.get("/summary/daily", response_model=List[dict])
async def get_daily_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to include"),
    repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get daily event summary for the last N days."""
    return await repo.get_daily_event_summary(days)

@router.get("/summary/user/{user_id}", response_model=UserActivitySummaryResponse)
async def get_user_activity_summary(
    user_id: str,
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get activity summary for a specific user."""
    summary = await repo.get_user_activity_summary(user_id, days)

    if not summary:
        raise HTTPException(status_code=404, detail="No activity found for user")

    return UserActivitySummaryResponse(**summary)

@router.get("/summary/popular-events", response_model=List[dict])
async def get_popular_events(
    limit: int = Query(10, ge=1, le=50, description="Number of popular events to return"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    repo: AnalyticsRepository = Depends(get_analytics_repository)
):
    """Get most popular events by occurrence count."""
    date_range = None
    if start_date or end_date:
        date_range = DateRangeFilter(start_date=start_date, end_date=end_date)

    return await repo.get_popular_events(limit, date_range)
```

## 7. Main Application (`src/main.py`)

FastAPI application with proper MongoDB integration and lifecycle management.

```python
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from .core.config import settings
from .core.database import connect_to_mongo, close_mongo_connection
from .core.middleware import RequestTrackingMiddleware, ErrorHandlingMiddleware
from .core.errors import (
    validation_error_handler,
    mongodb_error_handler,
    MongoDBError
)
from .api.v1 import analytics, user_behavior

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    logger.info("Starting MongoDB Data Service...")

    # Connect to MongoDB
    await connect_to_mongo()
    logger.info("MongoDB Data Service started successfully")

    yield

    # Cleanup
    logger.info("Shutting down MongoDB Data Service...")
    await close_mongo_connection()
    logger.info("MongoDB Data Service shutdown complete")

def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title="MongoDB Data Service",
        description="Centralized MongoDB data access service for analytics and document storage",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None
    )

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestTrackingMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)

    # Add exception handlers
    app.add_exception_handler(ValueError, validation_error_handler)
    app.add_exception_handler(MongoDBError, mongodb_error_handler)

    # Include routers
    app.include_router(
        analytics.router,
        prefix="/api/v1/analytics",
        tags=["Analytics"]
    )
    app.include_router(
        user_behavior.router,
        prefix="/api/v1/user-behavior",
        tags=["User Behavior"]
    )

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        from .core.database import mongodb_client

        # Check MongoDB connection
        try:
            await mongodb_client.admin.command('ping')
            db_status = "healthy"
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            db_status = "unhealthy"

        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "service": "db_mongo_service",
            "version": "1.0.0",
            "database": db_status
        }

    @app.get("/ready")
    async def readiness_check():
        """Readiness check endpoint."""
        from .core.database import mongodb_client

        try:
            # Verify we can perform database operations
            await mongodb_client.admin.command('ping')
            return {"status": "ready", "service": "db_mongo_service"}
        except Exception as e:
            logger.error(f"MongoDB readiness check failed: {e}")
            from fastapi import HTTPException
            raise HTTPException(status_code=503, detail="Service not ready")

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None  # Use structlog configuration
    )
```

---

## 8. Database Configuration (`src/core/database.py`)

MongoDB connection management with proper async patterns.

```python
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from .config import settings

logger = logging.getLogger(__name__)

# Global MongoDB client
mongodb_client: Optional[AsyncIOMotorClient] = None
mongodb_database: Optional[AsyncIOMotorDatabase] = None

async def connect_to_mongo() -> None:
    """Create database connection."""
    global mongodb_client, mongodb_database

    try:
        # Create MongoDB client
        mongodb_client = AsyncIOMotorClient(
            settings.MONGODB_URL,
            maxPoolSize=settings.MONGODB_MAX_POOL_SIZE,
            minPoolSize=settings.MONGODB_MIN_POOL_SIZE,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            socketTimeoutMS=10000,
        )

        # Get database
        mongodb_database = mongodb_client[settings.MONGODB_DATABASE_NAME]

        # Test connection
        await mongodb_client.admin.command('ping')
        logger.info(f"Connected to MongoDB database: {settings.MONGODB_DATABASE_NAME}")

        # Create indexes
        await create_indexes()

    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection() -> None:
    """Close database connection."""
    global mongodb_client

    if mongodb_client:
        mongodb_client.close()
        logger.info("Disconnected from MongoDB")

async def get_database() -> AsyncIOMotorDatabase:
    """Get database dependency."""
    if not mongodb_database:
        raise RuntimeError("Database not initialized")
    return mongodb_database

async def create_indexes() -> None:
    """Create database indexes for performance."""
    if not mongodb_database:
        return

    try:
        # Analytics events collection indexes
        analytics_collection = mongodb_database.analytics_events

        # Compound indexes for common queries
        await analytics_collection.create_index([
            ("user_id", 1),
            ("timestamp", -1)
        ])

        await analytics_collection.create_index([
            ("event_type", 1),
            ("timestamp", -1)
        ])

        await analytics_collection.create_index([
            ("category", 1),
            ("timestamp", -1)
        ])

        await analytics_collection.create_index([
            ("source_service", 1),
            ("timestamp", -1)
        ])

        # Request ID for tracing
        await analytics_collection.create_index("request_id")

        # Session ID for session tracking
        await analytics_collection.create_index("session_id")

        # User behavior collection indexes
        user_behavior_collection = mongodb_database.user_sessions

        await user_behavior_collection.create_index([
            ("user_id", 1),
            ("started_at", -1)
        ])

        await user_behavior_collection.create_index("session_id", unique=True)
        await user_behavior_collection.create_index("is_active")

        # User behavior summary indexes
        behavior_summary_collection = mongodb_database.user_behavior_summary

        await behavior_summary_collection.create_index([
            ("user_id", 1),
            ("date", -1)
        ], unique=True)

        logger.info("MongoDB indexes created successfully")

    except Exception as e:
        logger.error(f"Failed to create MongoDB indexes: {e}")
        # Don't raise - indexes are optimization, not critical
```

---

## 9. Testing Examples

### Repository Test (`tests/test_analytics_repository.py`)

```python
import pytest
from datetime import datetime, timedelta
from testcontainers.mongodb import MongoDbContainer

from src.repositories.analytics_repository import AnalyticsRepository
from src.models.analytics import AnalyticsEvent, EventType, EventCategory
from src.schemas.common import PaginationParams, DateRangeFilter

@pytest.fixture(scope="session")
async def mongodb_container():
    """Setup test MongoDB container."""
    with MongoDbContainer("mongo:7.0.9") as mongo_container:
        connection_url = mongo_container.get_connection_url()
        yield connection_url

@pytest.fixture
async def analytics_repository(mongodb_container):
    """Setup analytics repository for testing."""
    from motor.motor_asyncio import AsyncIOMotorClient

    client = AsyncIOMotorClient(mongodb_container)
    database = client.test_db
    collection = database.analytics_events

    repo = AnalyticsRepository(collection)

    # Clean up before test
    await collection.delete_many({})

    yield repo

    # Clean up after test
    await collection.delete_many({})
    client.close()

@pytest.mark.asyncio
async def test_create_analytics_event(analytics_repository):
    """Test creating analytics event."""
    event_data = {
        "event_type": EventType.USER_ACTION,
        "event_name": "button_click",
        "category": EventCategory.INTERACTION,
        "user_id": "user_123",
        "session_id": "session_abc",
        "request_id": "req_123",
        "properties": {"button_id": "submit"},
        "source_service": "api_service"
    }

    event = await analytics_repository.create_event(event_data)

    assert event.id is not None
    assert event.event_type == EventType.USER_ACTION
    assert event.event_name == "button_click"
    assert event.user_id == "user_123"
    assert event.created_at is not None

@pytest.mark.asyncio
async def test_find_events_by_user(analytics_repository):
    """Test finding events by user ID."""
    # Create test events
    events_data = [
        {
            "event_type": EventType.USER_ACTION,
            "event_name": "login",
            "category": EventCategory.AUTHENTICATION,
            "user_id": "user_123",
            "request_id": "req_1",
            "source_service": "api_service"
        },
        {
            "event_type": EventType.USER_ACTION,
            "event_name": "page_view",
            "category": EventCategory.NAVIGATION,
            "user_id": "user_123",
            "request_id": "req_2",
            "source_service": "api_service"
        },
        {
            "event_type": EventType.USER_ACTION,
            "event_name": "logout",
            "category": EventCategory.AUTHENTICATION,
            "user_id": "user_456",
            "request_id": "req_3",
            "source_service": "api_service"
        }
    ]

    for event_data in events_data:
        await analytics_repository.create_event(event_data)

    # Find events for user_123
    pagination = PaginationParams(limit=10, skip=0)
    events = await analytics_repository.find_events_by_user("user_123", pagination)

    assert len(events) == 2
    assert all(event.user_id == "user_123" for event in events)

@pytest.mark.asyncio
async def test_event_counts_by_type(analytics_repository):
    """Test getting event counts by type."""
    # Create test events
    events_data = [
        {
            "event_type": EventType.USER_ACTION,
            "event_name": "click",
            "category": EventCategory.INTERACTION,
            "user_id": "user_1",
            "request_id": "req_1",
            "source_service": "api_service"
        },
        {
            "event_type": EventType.USER_ACTION,
            "event_name": "scroll",
            "category": EventCategory.INTERACTION,
            "user_id": "user_2",
            "request_id": "req_2",
            "source_service": "api_service"
        },
        {
            "event_type": EventType.SYSTEM_EVENT,
            "event_name": "startup",
            "category": EventCategory.PERFORMANCE,
            "request_id": "req_3",
            "source_service": "api_service"
        }
    ]

    for event_data in events_data:
        await analytics_repository.create_event(event_data)

    # Get counts by type
    results = await analytics_repository.get_event_counts_by_type()

    assert len(results) == 2

    # Find USER_ACTION result
    user_action_result = next(
        (r for r in results if r.group_key == EventType.USER_ACTION),
        None
    )
    assert user_action_result is not None
    assert user_action_result.metrics["count"] == 2
    assert user_action_result.metrics["unique_users_count"] == 2
```

---

This MongoDB Data Service example provides:

1. **Complete MongoDB integration** with Motor async driver
2. **Document models** with proper validation and indexing
3. **Repository pattern** with aggregation capabilities
4. **RESTful API** with comprehensive endpoints
5. **Performance optimization** through proper indexing
6. **Error handling** with RFC 7807 compliance
7. **Testing examples** using testcontainers
8. **Analytics capabilities** with real-world aggregation queries

The example follows all architectural patterns from the project and demonstrates proper implementation of the Improved Hybrid Approach for MongoDB data access.