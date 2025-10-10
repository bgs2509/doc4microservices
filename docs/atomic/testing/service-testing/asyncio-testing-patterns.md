# AsyncIO Service Testing Patterns

Test AsyncIO workers, background tasks, concurrent operations, and event-driven patterns to verify task execution, cancellation handling, queue processing, and timeout behavior. Service-level AsyncIO tests validate worker logic and concurrent processing without running production event loops.

This document covers testing patterns for AsyncIO-based worker services using pytest-asyncio, testing background task execution, concurrent operations, queue processing, and resource cleanup. AsyncIO service tests ensure your workers handle tasks correctly under async conditions.

Testing AsyncIO workers validates that tasks execute correctly, cancellation is handled gracefully, queues process messages reliably, and timeouts prevent hanging operations. These tests run quickly while providing confidence in async worker behavior.

## Setup and Configuration

### Basic AsyncIO Test Setup

```python
# tests/service/test_worker.py
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock


# CORRECT: Mark async tests
@pytest.mark.asyncio
async def test_async_function():
    """Test async function executes correctly."""
    result = await some_async_function()
    assert result == expected_value


# CORRECT: Use pytest-asyncio fixtures
@pytest.fixture
async def async_client():
    """Provide async client with cleanup."""
    client = AsyncClient()
    await client.connect()
    yield client
    await client.disconnect()
```

### Configuring pytest-asyncio

```python
# pytest.ini
[pytest]
asyncio_mode = auto
markers =
    asyncio: mark test as requiring asyncio
    service: mark test as service-level test
```

## Testing Async Functions

### Basic Async Function Testing

```python
# CORRECT: Test async function
@pytest.mark.asyncio
async def test_fetch_user_data():
    """Test async function fetches user data."""
    from finance_lending_worker.services.user_service import fetch_user_data

    user_data = await fetch_user_data(user_id="user-123")

    assert user_data["id"] == "user-123"
    assert "email" in user_data
    assert "credit_score" in user_data


# CORRECT: Test async function with mocked dependencies
@pytest.mark.asyncio
async def test_fetch_user_data_mocked():
    """Test async function with mocked HTTP client."""
    from finance_lending_worker.services.user_service import UserService
    from unittest.mock import AsyncMock

    mock_http_client = AsyncMock()
    mock_http_client.get.return_value = {"id": "user-123", "email": "test@example.com"}

    service = UserService(http_client=mock_http_client)
    user_data = await service.fetch_user_data("user-123")

    assert user_data["id"] == "user-123"
    mock_http_client.get.assert_called_once_with("/users/user-123")
```

### Testing Async Exceptions

```python
# CORRECT: Test async function raises exception
@pytest.mark.asyncio
async def test_fetch_user_not_found():
    """Test async function raises exception for missing user."""
    from finance_lending_worker.services.user_service import fetch_user_data, UserNotFoundError

    with pytest.raises(UserNotFoundError, match="user-999"):
        await fetch_user_data(user_id="user-999")


# CORRECT: Test async function error handling
@pytest.mark.asyncio
async def test_fetch_user_handles_http_error():
    """Test async function handles HTTP errors gracefully."""
    from finance_lending_worker.services.user_service import UserService
    from unittest.mock import AsyncMock
    import httpx

    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.HTTPStatusError(
        message="Not Found",
        request=Mock(),
        response=Mock(status_code=404)
    )

    service = UserService(http_client=mock_client)

    with pytest.raises(httpx.HTTPStatusError):
        await service.fetch_user_data("user-123")
```

## Testing Background Tasks

### Task Execution Testing

```python
# CORRECT: Test background task execution
@pytest.mark.asyncio
async def test_background_task_processes_job():
    """Test background task processes job correctly."""
    from finance_lending_worker.tasks.loan_processor import process_loan_application

    job_data = {
        "loan_id": "loan-123",
        "user_id": "user-456",
        "amount": 10000
    }

    result = await process_loan_application(job_data)

    assert result["status"] == "completed"
    assert result["loan_id"] == "loan-123"


# CORRECT: Test task with multiple operations
@pytest.mark.asyncio
async def test_background_task_workflow():
    """Test background task executes full workflow."""
    from finance_lending_worker.tasks.onboarding import onboard_new_user
    from unittest.mock import AsyncMock

    mock_db = AsyncMock()
    mock_email = AsyncMock()

    await onboard_new_user(
        user_id="user-123",
        email="newuser@example.com",
        db=mock_db,
        email_service=mock_email
    )

    # Verify all steps executed
    mock_db.create_user_profile.assert_called_once()
    mock_email.send_welcome_email.assert_called_once()
```

### Testing Task Cancellation

```python
# CORRECT: Test task cancellation handling
@pytest.mark.asyncio
async def test_task_handles_cancellation():
    """Test task cleans up on cancellation."""
    import asyncio
    from finance_lending_worker.tasks.long_running import process_large_dataset

    cleanup_called = []

    async def monitored_task():
        try:
            await process_large_dataset()
        except asyncio.CancelledError:
            cleanup_called.append(True)
            raise

    task = asyncio.create_task(monitored_task())

    # Let task start
    await asyncio.sleep(0.1)

    # Cancel task
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    # Verify cleanup executed
    assert len(cleanup_called) == 1


# CORRECT: Test graceful shutdown
@pytest.mark.asyncio
async def test_worker_graceful_shutdown():
    """Test worker shuts down gracefully."""
    from finance_lending_worker.worker import Worker

    worker = Worker()
    worker_task = asyncio.create_task(worker.run())

    # Let worker start
    await asyncio.sleep(0.1)

    # Request shutdown
    await worker.shutdown()

    # Verify worker stopped
    await asyncio.wait_for(worker_task, timeout=5)
    assert worker.is_stopped()
```

## Testing Concurrent Operations

### Parallel Task Execution

```python
# CORRECT: Test concurrent task execution
@pytest.mark.asyncio
async def test_process_multiple_jobs_concurrently():
    """Test worker processes multiple jobs in parallel."""
    from finance_lending_worker.tasks.processor import process_jobs

    jobs = [
        {"id": "job-1", "data": "task1"},
        {"id": "job-2", "data": "task2"},
        {"id": "job-3", "data": "task3"},
    ]

    results = await process_jobs(jobs, max_concurrent=3)

    assert len(results) == 3
    assert all(r["status"] == "completed" for r in results)


# CORRECT: Test asyncio.gather for concurrent operations
@pytest.mark.asyncio
async def test_gather_multiple_operations():
    """Test gathering results from concurrent operations."""
    from finance_lending_worker.services.data_fetcher import fetch_user, fetch_loans, fetch_credit_score

    user_id = "user-123"

    # Execute concurrently
    user, loans, credit_score = await asyncio.gather(
        fetch_user(user_id),
        fetch_loans(user_id),
        fetch_credit_score(user_id)
    )

    assert user["id"] == user_id
    assert isinstance(loans, list)
    assert isinstance(credit_score, int)


# CORRECT: Test error handling in concurrent tasks
@pytest.mark.asyncio
async def test_gather_handles_partial_failure():
    """Test gather with return_exceptions handles failures."""
    from finance_lending_worker.services.api_client import call_api

    results = await asyncio.gather(
        call_api("endpoint1"),  # Succeeds
        call_api("failing_endpoint"),  # Fails
        call_api("endpoint3"),  # Succeeds
        return_exceptions=True
    )

    # First and third succeed, second is exception
    assert results[0]["status"] == "ok"
    assert isinstance(results[1], Exception)
    assert results[2]["status"] == "ok"
```

## Testing Timeouts

### Operation Timeout Testing

```python
# CORRECT: Test operation respects timeout
@pytest.mark.asyncio
async def test_fetch_with_timeout():
    """Test operation times out after limit."""
    from finance_lending_worker.services.api_client import fetch_data_with_timeout
    import asyncio

    with pytest.raises(asyncio.TimeoutError):
        await fetch_data_with_timeout(url="http://slow-api.com", timeout=1)


# CORRECT: Test timeout with asyncio.wait_for
@pytest.mark.asyncio
async def test_wait_for_timeout():
    """Test asyncio.wait_for enforces timeout."""
    async def slow_operation():
        await asyncio.sleep(10)
        return "result"

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(slow_operation(), timeout=1)


# CORRECT: Test timeout with fallback
@pytest.mark.asyncio
async def test_operation_with_timeout_fallback():
    """Test operation falls back on timeout."""
    from finance_lending_worker.services.cache import get_cached_or_fetch

    async def slow_fetch():
        await asyncio.sleep(10)
        return "fresh data"

    result = await get_cached_or_fetch(
        key="user:123",
        fetch_func=slow_fetch,
        timeout=1,
        fallback="cached data"
    )

    assert result == "cached data"
```

## Testing AsyncIO Queues

### Queue Processing Testing

```python
# CORRECT: Test queue consumer
@pytest.mark.asyncio
async def test_queue_consumer_processes_messages():
    """Test queue consumer processes all messages."""
    from finance_lending_worker.queue.consumer import consume_queue
    import asyncio

    queue = asyncio.Queue()
    processed = []

    async def processor(item):
        processed.append(item)

    # Add items to queue
    for i in range(5):
        await queue.put(f"message-{i}")

    # Add sentinel to stop consumer
    await queue.put(None)

    # Consume queue
    await consume_queue(queue, processor)

    assert len(processed) == 5
    assert processed[0] == "message-0"
    assert processed[4] == "message-4"


# CORRECT: Test queue producer-consumer pattern
@pytest.mark.asyncio
async def test_producer_consumer_pattern():
    """Test producer-consumer queue pattern."""
    import asyncio

    queue = asyncio.Queue(maxsize=10)
    consumed = []

    async def producer():
        for i in range(5):
            await queue.put(f"item-{i}")
            await asyncio.sleep(0.01)
        await queue.put(None)  # Sentinel

    async def consumer():
        while True:
            item = await queue.get()
            if item is None:
                break
            consumed.append(item)
            queue.task_done()

    await asyncio.gather(producer(), consumer())

    assert len(consumed) == 5
    assert queue.empty()


# CORRECT: Test queue with timeout
@pytest.mark.asyncio
async def test_queue_get_with_timeout():
    """Test queue.get with timeout."""
    import asyncio

    queue = asyncio.Queue()

    with pytest.raises(asyncio.TimeoutError):
        await asyncio.wait_for(queue.get(), timeout=1)
```

## Testing Locks and Synchronization

### Lock Testing

```python
# CORRECT: Test asyncio.Lock prevents concurrent access
@pytest.mark.asyncio
async def test_lock_prevents_concurrent_access():
    """Test lock prevents concurrent resource access."""
    import asyncio

    lock = asyncio.Lock()
    access_log = []

    async def access_resource(worker_id: int):
        async with lock:
            access_log.append(f"start-{worker_id}")
            await asyncio.sleep(0.1)
            access_log.append(f"end-{worker_id}")

    # Run 3 workers concurrently
    await asyncio.gather(
        access_resource(1),
        access_resource(2),
        access_resource(3)
    )

    # Verify no overlap (start/end pairs are sequential)
    assert access_log[0] == "start-1"
    assert access_log[1] == "end-1"
    assert access_log[2] == "start-2"
    assert access_log[3] == "end-2"


# CORRECT: Test semaphore limits concurrent access
@pytest.mark.asyncio
async def test_semaphore_limits_concurrency():
    """Test semaphore limits concurrent operations."""
    import asyncio

    semaphore = asyncio.Semaphore(2)  # Max 2 concurrent
    active_count = []
    max_active = 0

    async def worker(worker_id: int):
        nonlocal max_active
        async with semaphore:
            active_count.append(worker_id)
            max_active = max(max_active, len(active_count))
            await asyncio.sleep(0.1)
            active_count.remove(worker_id)

    # Run 5 workers
    await asyncio.gather(*[worker(i) for i in range(5)])

    # Verify max 2 concurrent
    assert max_active == 2
```

## Testing Event-Driven Patterns

### AsyncIO Event Testing

```python
# CORRECT: Test asyncio.Event coordination
@pytest.mark.asyncio
async def test_event_coordinates_tasks():
    """Test asyncio.Event coordinates task execution."""
    import asyncio

    ready_event = asyncio.Event()
    results = []

    async def waiter(worker_id: int):
        await ready_event.wait()
        results.append(f"worker-{worker_id}")

    # Start waiters
    tasks = [asyncio.create_task(waiter(i)) for i in range(3)]

    # Let waiters start
    await asyncio.sleep(0.1)

    # No results yet
    assert len(results) == 0

    # Signal ready
    ready_event.set()

    # Wait for all tasks
    await asyncio.gather(*tasks)

    # All workers executed
    assert len(results) == 3


# CORRECT: Test condition variable
@pytest.mark.asyncio
async def test_condition_variable():
    """Test asyncio.Condition for producer-consumer."""
    import asyncio

    condition = asyncio.Condition()
    items = []

    async def producer():
        async with condition:
            items.append("item")
            condition.notify()

    async def consumer():
        async with condition:
            await condition.wait()
            return items.pop()

    producer_task = asyncio.create_task(producer())
    consumer_task = asyncio.create_task(consumer())

    await asyncio.gather(producer_task, consumer_task)

    item = consumer_task.result()
    assert item == "item"
    assert len(items) == 0
```

## Testing Worker Services

### Worker Lifecycle Testing

```python
# CORRECT: Test worker startup and shutdown
@pytest.mark.asyncio
async def test_worker_lifecycle():
    """Test worker starts and stops correctly."""
    from finance_lending_worker.worker import Worker

    worker = Worker()

    # Start worker
    worker_task = asyncio.create_task(worker.run())
    await asyncio.sleep(0.1)

    assert worker.is_running()

    # Stop worker
    await worker.stop()
    await worker_task

    assert not worker.is_running()


# CORRECT: Test worker processes jobs
@pytest.mark.asyncio
async def test_worker_processes_jobs():
    """Test worker consumes and processes jobs."""
    from finance_lending_worker.worker import Worker
    import asyncio

    worker = Worker()
    job_queue = asyncio.Queue()

    # Add jobs
    await job_queue.put({"id": "job-1", "action": "process"})
    await job_queue.put({"id": "job-2", "action": "process"})
    await job_queue.put(None)  # Stop signal

    results = await worker.process_queue(job_queue)

    assert len(results) == 2
    assert results[0]["id"] == "job-1"
```

## Best Practices

### DO: Use pytest-asyncio

```python
# CORRECT: Mark async tests properly
@pytest.mark.asyncio
async def test_async_operation():
    """Use @pytest.mark.asyncio for async tests."""
    result = await async_function()
    assert result is not None


# INCORRECT: Don't use asyncio.run in pytest
def test_async_wrong():
    """WRONG: Don't use asyncio.run in pytest."""
    # This creates a new event loop, causing issues
    result = asyncio.run(async_function())
```

### DO: Test Cancellation Handling

```python
# CORRECT: Test graceful cancellation
@pytest.mark.asyncio
async def test_cancellation_cleanup():
    """Test task cleans up on cancellation."""
    cleanup_done = []

    async def task_with_cleanup():
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            cleanup_done.append(True)
            raise

    task = asyncio.create_task(task_with_cleanup())
    await asyncio.sleep(0.1)
    task.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task

    assert len(cleanup_done) == 1
```

### DON'T: Block the Event Loop

```python
# INCORRECT: Don't use blocking sleep
@pytest.mark.asyncio
async def test_with_blocking_sleep():
    """WRONG: Blocks event loop."""
    import time
    time.sleep(1)  # Blocks event loop!
    result = await async_operation()


# CORRECT: Use asyncio.sleep
@pytest.mark.asyncio
async def test_with_async_sleep():
    """Use asyncio.sleep instead."""
    await asyncio.sleep(1)
    result = await async_operation()
```

## Checklist

- [ ] Test async functions with await
- [ ] Test background task execution
- [ ] Test task cancellation handling
- [ ] Test concurrent operations with gather
- [ ] Test timeouts with asyncio.wait_for
- [ ] Test queue producer-consumer patterns
- [ ] Test locks and semaphores prevent races
- [ ] Test event coordination patterns
- [ ] Test worker lifecycle (start/stop)
- [ ] Use `@pytest.mark.asyncio` for async tests
- [ ] Mock async dependencies with AsyncMock
- [ ] Test exception handling in async code

## Related Documents

- `docs/atomic/testing/unit-testing/mocking-strategies.md` — Mocking async functions with AsyncMock
- `docs/atomic/testing/unit-testing/fixture-patterns.md` — Async fixture patterns
- `docs/atomic/services/asyncio-service/worker-patterns.md` — AsyncIO worker implementation
- `docs/atomic/services/asyncio-service/task-management.md` — Background task patterns
- `docs/atomic/services/asyncio-service/concurrency-patterns.md` — Concurrent execution patterns
