"""
Shared DTOs for Task Management System Use Case.

This module contains all data transfer objects (DTOs) and event schemas
used for inter-service communication in the task management system.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from uuid import UUID

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task status enumeration."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ActionType(str, Enum):
    """Task action types for analytics."""
    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ATTACHMENT_ADDED = "attachment_added"


# Base DTOs
class TaskBase(BaseModel):
    """Base task DTO with common fields."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Task status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    due_date: Optional[datetime] = Field(None, description="Task due date")


class TaskCreate(TaskBase):
    """DTO for creating a new task."""
    pass


class TaskUpdate(BaseModel):
    """DTO for updating an existing task."""
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="New task title")
    description: Optional[str] = Field(None, max_length=2000, description="New task description")
    status: Optional[TaskStatus] = Field(None, description="New task status")
    priority: Optional[TaskPriority] = Field(None, description="New task priority")
    due_date: Optional[datetime] = Field(None, description="New task due date")


class TaskResponse(TaskBase):
    """DTO for task responses."""
    id: int = Field(..., description="Task ID")
    user_id: int = Field(..., description="Task owner user ID")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Task last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Task completion timestamp")

    class Config:
        from_attributes = True


# Event DTOs
class TaskEventBase(BaseModel):
    """Base class for task events."""
    task_id: int = Field(..., description="Task ID")
    user_id: int = Field(..., description="User ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    request_id: Optional[str] = Field(None, description="Request ID for tracing")


class TaskCreatedEvent(TaskEventBase):
    """Event published when a task is created."""
    event_type: str = Field(default="task.created", description="Event type")
    task_data: TaskResponse = Field(..., description="Created task data")


class TaskUpdatedEvent(TaskEventBase):
    """Event published when a task is updated."""
    event_type: str = Field(default="task.updated", description="Event type")
    previous_data: Dict[str, Any] = Field(..., description="Previous task data")
    new_data: Dict[str, Any] = Field(..., description="Updated task data")
    changes: Dict[str, Any] = Field(..., description="What changed")


class TaskCompletedEvent(TaskEventBase):
    """Event published when a task is completed."""
    event_type: str = Field(default="task.completed", description="Event type")
    task_data: TaskResponse = Field(..., description="Completed task data")
    completion_time: datetime = Field(default_factory=datetime.utcnow, description="Completion timestamp")


class TaskDueSoonEvent(TaskEventBase):
    """Event published when a task is due soon."""
    event_type: str = Field(default="task.due_soon", description="Event type")
    task_data: TaskResponse = Field(..., description="Task due soon data")
    due_in_minutes: int = Field(..., description="Minutes until due")


class TaskOverdueEvent(TaskEventBase):
    """Event published when a task becomes overdue."""
    event_type: str = Field(default="task.overdue", description="Event type")
    task_data: TaskResponse = Field(..., description="Overdue task data")
    overdue_minutes: int = Field(..., description="Minutes overdue")


# Reminder DTOs
class ReminderRequest(BaseModel):
    """DTO for creating task reminders."""
    task_id: int = Field(..., description="Task ID")
    user_id: int = Field(..., description="User ID")
    remind_at: datetime = Field(..., description="When to send reminder")
    message: Optional[str] = Field(None, description="Custom reminder message")


class ReminderEvent(BaseModel):
    """Event for sending reminders."""
    event_type: str = Field(default="reminder.send", description="Event type")
    task_id: int = Field(..., description="Task ID")
    user_id: int = Field(..., description="User ID")
    message: str = Field(..., description="Reminder message")
    telegram_user_id: Optional[int] = Field(None, description="Telegram user ID for bot notifications")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Reminder timestamp")


# Analytics DTOs
class TaskActivity(BaseModel):
    """DTO for task activity analytics."""
    task_id: int = Field(..., description="Task ID")
    user_id: int = Field(..., description="User ID")
    action: ActionType = Field(..., description="Action performed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Activity timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional activity data")
    session_id: Optional[str] = Field(None, description="User session ID")
    source: str = Field(..., description="Source of action (api, bot, worker)")


class ProductivityStats(BaseModel):
    """DTO for user productivity statistics."""
    user_id: int = Field(..., description="User ID")
    period_start: datetime = Field(..., description="Statistics period start")
    period_end: datetime = Field(..., description="Statistics period end")
    total_tasks: int = Field(..., description="Total tasks in period")
    completed_tasks: int = Field(..., description="Completed tasks")
    cancelled_tasks: int = Field(..., description="Cancelled tasks")
    overdue_tasks: int = Field(..., description="Tasks that became overdue")
    completion_rate: float = Field(..., description="Task completion rate (0-1)")
    average_completion_time_hours: Optional[float] = Field(None, description="Average time to complete tasks")
    most_productive_hour: Optional[int] = Field(None, description="Hour of day with most completions (0-23)")
    tasks_by_priority: Dict[str, int] = Field(..., description="Task count by priority level")
    tasks_by_status: Dict[str, int] = Field(..., description="Current task count by status")


# Bot-specific DTOs
class BotTaskCreateRequest(BaseModel):
    """DTO for creating tasks via bot."""
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: Optional[TaskPriority] = Field(None, description="Task priority")
    due_date_text: Optional[str] = Field(None, description="Due date in natural language")


class BotCommandResponse(BaseModel):
    """DTO for bot command responses."""
    success: bool = Field(..., description="Command success status")
    message: str = Field(..., description="Response message for user")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")


# Attachment DTOs
class AttachmentInfo(BaseModel):
    """DTO for task attachments."""
    id: str = Field(..., description="Attachment ID")
    task_id: int = Field(..., description="Associated task ID")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="File content type")
    size: int = Field(..., description="File size in bytes")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    telegram_file_id: Optional[str] = Field(None, description="Telegram file ID if uploaded via bot")


class AttachmentUploadedEvent(TaskEventBase):
    """Event published when an attachment is uploaded."""
    event_type: str = Field(default="attachment.uploaded", description="Event type")
    attachment_info: AttachmentInfo = Field(..., description="Attachment information")
    file_data: Optional[bytes] = Field(None, description="File data for processing")


# Worker Command DTOs
class ProcessRemindersCommand(BaseModel):
    """Command to process due reminders."""
    command_type: str = Field(default="process_reminders", description="Command type")
    check_time: datetime = Field(default_factory=datetime.utcnow, description="Time to check for due reminders")
    look_ahead_minutes: int = Field(default=60, description="Look ahead window in minutes")


class GenerateAnalyticsCommand(BaseModel):
    """Command to generate analytics for users."""
    command_type: str = Field(default="generate_analytics", description="Command type")
    user_id: Optional[int] = Field(None, description="Specific user ID, None for all users")
    period_days: int = Field(default=7, description="Analysis period in days")


class CleanupTasksCommand(BaseModel):
    """Command to cleanup old completed tasks."""
    command_type: str = Field(default="cleanup_tasks", description="Command type")
    completed_before: datetime = Field(..., description="Cleanup tasks completed before this date")
    batch_size: int = Field(default=100, description="Number of tasks to process in one batch")


# API Response DTOs
class TaskListResponse(BaseModel):
    """DTO for task list responses."""
    tasks: list[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Tasks per page")
    has_next: bool = Field(..., description="Whether there are more pages")


class TaskStatsResponse(BaseModel):
    """DTO for task statistics responses."""
    total_tasks: int = Field(..., description="Total tasks for user")
    completed_tasks: int = Field(..., description="Completed tasks")
    pending_tasks: int = Field(..., description="Pending tasks (todo + in_progress)")
    overdue_tasks: int = Field(..., description="Overdue tasks")
    completion_rate: float = Field(..., description="Task completion rate")
    tasks_by_priority: Dict[str, int] = Field(..., description="Tasks grouped by priority")
    tasks_by_status: Dict[str, int] = Field(..., description="Tasks grouped by status")