# AsyncIO Worker Service Template for AI Code Generation
# Template variables are marked with {{variable_name}} format

"""
{{worker_service_name}} - AsyncIO Background Workers

This service implements background processing for {{business_domain}}
following the Improved Hybrid Approach architecture pattern.

Generated from business requirements:
{{business_requirements}}
"""

import asyncio
import signal
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import json

import httpx
import aio_pika
from aio_pika import Message, DeliveryMode
import structlog

# Configuration
from .config import WorkerSettings
from .models import {{worker_model_imports}}

# Initialize structured logging
logger = structlog.get_logger(__name__)

# Settings
settings = WorkerSettings()

# Global clients
http_client: Optional[httpx.AsyncClient] = None
rabbitmq_connection: Optional[aio_pika.Connection] = None
rabbitmq_channel: Optional[aio_pika.Channel] = None

# Shutdown event
shutdown_event = asyncio.Event()

class WorkerDataServiceClient:
    """Client for workers to communicate with data services"""

    def __init__(self):
        self.postgres_url = settings.postgres_service_url
        self.mongo_url = settings.mongo_service_url

    async def postgres_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make request to PostgreSQL data service"""
        url = f"{self.postgres_url}{endpoint}"

        try:
            response = await http_client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error("worker_postgres_service_error", error=str(e), endpoint=endpoint)
            raise
        except httpx.HTTPStatusError as e:
            logger.error("worker_postgres_service_http_error", status_code=e.response.status_code, endpoint=endpoint)
            raise

    async def mongo_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make request to MongoDB data service"""
        url = f"{self.mongo_url}{endpoint}"

        try:
            response = await http_client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error("worker_mongo_service_error", error=str(e), endpoint=endpoint)
            raise
        except httpx.HTTPStatusError as e:
            logger.error("worker_mongo_service_http_error", status_code=e.response.status_code, endpoint=endpoint)
            raise

    async def bulk_postgres_request(self, endpoint: str, data_list: List[Dict]) -> Dict[str, Any]:
        """Make bulk request to PostgreSQL data service"""
        return await self.postgres_request(
            "POST",
            f"{endpoint}/bulk",
            json={"items": data_list}
        )

    async def bulk_mongo_request(self, endpoint: str, data_list: List[Dict]) -> Dict[str, Any]:
        """Make bulk request to MongoDB data service"""
        return await self.mongo_request(
            "POST",
            f"{endpoint}/bulk",
            json={"items": data_list}
        )

# Global data client
data_client = WorkerDataServiceClient()

# RabbitMQ utilities
async def setup_rabbitmq():
    """Setup RabbitMQ connection and channel"""
    global rabbitmq_connection, rabbitmq_channel

    try:
        rabbitmq_connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        rabbitmq_channel = await rabbitmq_connection.channel()

        # Set up quality of service
        await rabbitmq_channel.set_qos(prefetch_count=settings.worker_prefetch_count)

        logger.info("rabbitmq_connected")

        # Declare exchanges and queues for {{business_domain}}
        {{rabbitmq_setup}}

    except Exception as e:
        logger.error("rabbitmq_connection_failed", error=str(e))
        raise

async def publish_event(exchange_name: str, routing_key: str, message_data: Dict[str, Any]):
    """Publish event to RabbitMQ"""
    try:
        exchange = await rabbitmq_channel.get_exchange(exchange_name)

        message = Message(
            json.dumps(message_data).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            headers={
                "timestamp": datetime.utcnow().isoformat(),
                "service": "{{worker_service_name}}",
            }
        )

        await exchange.publish(message, routing_key=routing_key)

        logger.info(
            "event_published",
            exchange=exchange_name,
            routing_key=routing_key,
            message_id=message_data.get("id")
        )

    except Exception as e:
        logger.error(
            "event_publish_failed",
            exchange=exchange_name,
            routing_key=routing_key,
            error=str(e)
        )
        raise

# Worker task decorators and utilities
def background_task(task_name: str):
    """Decorator for background tasks"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            logger.info("task_started", task_name=task_name)

            try:
                result = await func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.info("task_completed", task_name=task_name, duration_seconds=duration)
                return result

            except Exception as e:
                duration = (datetime.utcnow() - start_time).total_seconds()
                logger.error("task_failed", task_name=task_name, duration_seconds=duration, error=str(e))
                raise

        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator for retry logic"""
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error("task_failed_permanently", task=func.__name__, attempts=attempt + 1, error=str(e))
                        raise
                    else:
                        wait_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning("task_retry", task=func.__name__, attempt=attempt + 1, wait_seconds=wait_time)
                        await asyncio.sleep(wait_time)

        return wrapper
    return decorator

# Event-driven workers for {{business_domain}}
{{event_driven_workers}}

# Scheduled workers for {{business_domain}}
{{scheduled_workers}}

# Batch processing workers
{{batch_processing_workers}}

# Example event handler
async def handle_example_event(message: aio_pika.IncomingMessage):
    """Example event handler"""
    async with message.process():
        try:
            event_data = json.loads(message.body.decode())
            logger.info("processing_example_event", event_data=event_data)

            # Process the event
            # Example: update analytics, send notifications, etc.

            logger.info("example_event_processed", event_id=event_data.get("id"))

        except Exception as e:
            logger.error("example_event_processing_failed", error=str(e))
            raise

# Scheduled task runner
class ScheduledTaskRunner:
    """Runs scheduled tasks at specified intervals"""

    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.running = False

    def add_task(self, name: str, func: Callable, interval_seconds: int, run_immediately: bool = False):
        """Add a scheduled task"""
        self.tasks[name] = {
            "func": func,
            "interval": interval_seconds,
            "next_run": datetime.utcnow() if run_immediately else datetime.utcnow() + timedelta(seconds=interval_seconds),
            "last_run": None,
        }

    async def start(self):
        """Start the scheduled task runner"""
        self.running = True
        logger.info("scheduled_task_runner_started")

        while self.running and not shutdown_event.is_set():
            try:
                current_time = datetime.utcnow()

                for task_name, task_info in self.tasks.items():
                    if current_time >= task_info["next_run"]:
                        logger.info("running_scheduled_task", task_name=task_name)

                        try:
                            await task_info["func"]()
                            task_info["last_run"] = current_time
                            task_info["next_run"] = current_time + timedelta(seconds=task_info["interval"])
                            logger.info("scheduled_task_completed", task_name=task_name)

                        except Exception as e:
                            logger.error("scheduled_task_failed", task_name=task_name, error=str(e))
                            # Still schedule next run even if this one failed
                            task_info["next_run"] = current_time + timedelta(seconds=task_info["interval"])

                # Check every 10 seconds
                await asyncio.sleep(10)

            except Exception as e:
                logger.error("scheduled_task_runner_error", error=str(e))
                await asyncio.sleep(10)

        logger.info("scheduled_task_runner_stopped")

    def stop(self):
        """Stop the scheduled task runner"""
        self.running = False

# Business-specific workers for {{business_domain}}
{{business_workers}}

# Health monitoring
@background_task("health_check")
async def health_check_task():
    """Periodic health check"""
    try:
        # Check data services
        await data_client.postgres_request("GET", "/health")
        await data_client.mongo_request("GET", "/health")

        # Check RabbitMQ
        if not rabbitmq_connection or rabbitmq_connection.is_closed:
            raise Exception("RabbitMQ connection lost")

        logger.info("worker_health_check_passed")
        return True

    except Exception as e:
        logger.error("worker_health_check_failed", error=str(e))
        return False

# Signal handlers
def setup_signal_handlers():
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(signum, frame):
        logger.info("shutdown_signal_received", signal=signum)
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

# Main worker function
async def main():
    """Main worker function"""
    global http_client

    setup_signal_handlers()

    # Initialize HTTP client
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(60.0),  # Longer timeout for worker operations
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
    )

    try:
        logger.info("starting_{{worker_service_name}}")

        # Setup RabbitMQ
        await setup_rabbitmq()

        # Verify data service connections
        await data_client.postgres_request("GET", "/health")
        await data_client.mongo_request("GET", "/health")
        logger.info("data_services_connected")

        # Setup scheduled tasks
        scheduler = ScheduledTaskRunner()
        {{scheduled_task_setup}}

        # Start event consumers
        {{event_consumer_setup}}

        # Start scheduled task runner
        scheduler_task = asyncio.create_task(scheduler.start())

        logger.info("worker_service_started")

        # Wait for shutdown signal
        await shutdown_event.wait()

        logger.info("initiating_graceful_shutdown")

        # Stop scheduler
        scheduler.stop()
        await scheduler_task

        logger.info("worker_service_stopped")

    except Exception as e:
        logger.error("worker_service_failed", error=str(e))
        sys.exit(1)
    finally:
        # Cleanup
        if rabbitmq_connection and not rabbitmq_connection.is_closed:
            await rabbitmq_connection.close()
        if http_client:
            await http_client.aclose()

if __name__ == "__main__":
    asyncio.run(main())