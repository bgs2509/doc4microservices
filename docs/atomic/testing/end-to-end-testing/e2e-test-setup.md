# End-to-End Test Setup

Configure end-to-end testing infrastructure with Playwright or Selenium to verify complete user workflows across multiple services, databases, and frontend interfaces. E2E tests validate that the entire system works together correctly in realistic conditions.

This document covers E2E test environment setup using Docker Compose for service orchestration, Playwright for browser automation, pytest integration, CI/CD configuration, and artifact management. E2E test infrastructure ensures your complete system can be tested reliably and repeatably.

E2E testing infrastructure validates system integration from user perspective by running real services, databases, and browsers together. These tests catch issues that unit and integration tests miss by exercising complete workflows end-to-end.

## Overview

### When to Use E2E Tests

**Use E2E tests for:**
- Critical user journeys (signup, login, core transactions)
- Multi-service workflows (API → Worker → Bot notification)
- Payment and transaction flows
- Authentication and authorization flows
- Data consistency across services
- Frontend-to-backend integration

**Don't use E2E tests for:**
- Unit-level logic (use unit tests)
- Database queries (use integration tests)
- Internal API contracts (use service tests)
- Detailed edge cases (use lower-level tests)

## Test Infrastructure Setup

### Docker Compose Configuration

```yaml
# docker-compose.e2e.yml
version: '3.8'

services:
  # PostgreSQL database
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U testuser"]
      interval: 5s
      timeout: 5s
      retries: 5

  # MongoDB database
  mongo:
    image: mongo:7-jammy
    environment:
      MONGO_INITDB_ROOT_USERNAME: testuser
      MONGO_INITDB_ROOT_PASSWORD: testpass
    ports:
      - "27018:27017"
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 5s
      timeout: 5s
      retries: 5

  # Redis cache
  redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  # RabbitMQ message broker
  rabbitmq:
    image: rabbitmq:3-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: testuser
      RABBITMQ_DEFAULT_PASS: testpass
    ports:
      - "5673:5672"
      - "15673:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Data service (PostgreSQL API)
  data_service:
    build:
      context: ./services/finance_data_postgres_api
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql+asyncpg://testuser:testpass@postgres:5432/testdb
      REDIS_URL: redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8001:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Business API service
  business_api:
    build:
      context: ./services/finance_lending_api
      dockerfile: Dockerfile
    environment:
      DATA_SERVICE_URL: http://data_service:8000
      RABBITMQ_URL: amqp://testuser:testpass@rabbitmq:5672/
      REDIS_URL: redis://redis:6379/0
    depends_on:
      data_service:
        condition: service_healthy
      rabbitmq:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Frontend (if applicable)
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      API_URL: http://business_api:8000
    depends_on:
      business_api:
        condition: service_healthy
    ports:
      - "3000:3000"
```

### Playwright Setup

```bash
# Install Playwright
pip install playwright pytest-playwright

# Install browser drivers
playwright install chromium firefox webkit
```

### Pytest Configuration

```ini
# pytest.ini
[pytest]
markers =
    e2e: mark test as end-to-end test
    slow: mark test as slow-running
    chrome: run test in Chrome only
    firefox: run test in Firefox only
    webkit: run test in WebKit only

# E2E test configuration
testpaths = tests/e2e
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Playwright configuration
asyncio_mode = auto
```

### Conftest Configuration

```python
# tests/e2e/conftest.py
import pytest
import subprocess
import time
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="session")
def docker_compose():
    """Start Docker Compose services for E2E tests."""
    # Start services
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.e2e.yml", "up", "-d"],
        check=True
    )

    # Wait for services to be healthy
    time.sleep(30)

    yield

    # Teardown: stop services
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.e2e.yml", "down", "-v"],
        check=True
    )


@pytest.fixture(scope="session")
def browser_context(docker_compose):
    """Provide browser context for tests."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir="test-results/videos/",
            record_video_size={"width": 1920, "height": 1080}
        )
        yield context
        context.close()
        browser.close()


@pytest.fixture
def page(browser_context):
    """Provide new page for each test."""
    page = browser_context.new_page()
    yield page
    # Screenshot on failure handled by pytest-playwright
    page.close()


@pytest.fixture
def api_client():
    """Provide HTTP client for API calls."""
    import httpx
    return httpx.Client(base_url="http://localhost:8000")
```

## Environment Variables

### Test Environment Configuration

```bash
# .env.e2e
# Database
DATABASE_URL=postgresql+asyncpg://testuser:testpass@localhost:5433/testdb
MONGO_URL=mongodb://testuser:testpass@localhost:27018/testdb

# Redis
REDIS_URL=redis://localhost:6380/0

# RabbitMQ
RABBITMQ_URL=amqp://testuser:testpass@localhost:5673/

# Services
DATA_SERVICE_URL=http://localhost:8001
BUSINESS_API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Test configuration
HEADLESS=true
SLOW_MO=0
SCREENSHOT_ON_FAILURE=true
VIDEO_ON_FAILURE=true
```

## Running E2E Tests

### Local Execution

```bash
# Start infrastructure
docker-compose -f docker-compose.e2e.yml up -d

# Wait for services to be healthy
docker-compose -f docker-compose.e2e.yml ps

# Run all E2E tests
pytest tests/e2e -v -m e2e

# Run specific test file
pytest tests/e2e/test_user_registration.py -v

# Run with headed browser (visible)
HEADLESS=false pytest tests/e2e -v

# Run in specific browser
pytest tests/e2e -v --browser chromium
pytest tests/e2e -v --browser firefox
pytest tests/e2e -v --browser webkit

# Stop infrastructure
docker-compose -f docker-compose.e2e.yml down -v
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest tests/e2e -v -n 4 -m e2e

# Each worker gets isolated browser context
```

## CI/CD Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements-test.txt
          playwright install --with-deps chromium

      - name: Start services
        run: |
          docker-compose -f docker-compose.e2e.yml up -d
          sleep 30

      - name: Wait for services
        run: |
          chmod +x scripts/wait-for-services.sh
          ./scripts/wait-for-services.sh

      - name: Run E2E tests
        run: |
          pytest tests/e2e -v -m e2e \
            --video on \
            --screenshot on \
            --tracing on

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-test-results
          path: |
            test-results/
            screenshots/
            videos/

      - name: Stop services
        if: always()
        run: docker-compose -f docker-compose.e2e.yml down -v
```

### Wait for Services Script

```bash
#!/bin/bash
# scripts/wait-for-services.sh

set -e

services=(
  "http://localhost:8001/health"
  "http://localhost:8000/health"
  "http://localhost:3000"
)

for service in "${services[@]}"; do
  echo "Waiting for $service..."
  timeout 60 bash -c "
    until curl -f -s $service > /dev/null; do
      echo 'Waiting...'
      sleep 2
    done
  "
  echo "$service is ready!"
done

echo "All services are ready!"
```

## Screenshots and Videos

### Automatic Capture on Failure

```python
# Playwright automatically captures on failure
@pytest.mark.e2e
def test_user_login_failure(page):
    """Test captures screenshot and video on failure."""
    page.goto("http://localhost:3000/login")
    page.fill("#email", "user@example.com")
    page.fill("#password", "wrongpassword")
    page.click("#login-button")

    # This assertion will fail and trigger screenshot
    assert page.locator(".error-message").is_visible()
    # Screenshot saved to test-results/screenshots/
    # Video saved to test-results/videos/
```

### Manual Screenshot Capture

```python
# CORRECT: Capture screenshot at specific points
@pytest.mark.e2e
def test_checkout_flow(page):
    """Test captures screenshots at key steps."""
    page.goto("http://localhost:3000/products")
    page.screenshot(path="test-results/step1-products.png")

    page.click("#product-1")
    page.screenshot(path="test-results/step2-product-detail.png")

    page.click("#add-to-cart")
    page.screenshot(path="test-results/step3-cart.png")

    page.click("#checkout")
    page.screenshot(path="test-results/step4-checkout.png")
```

## Test Data Management

### Database Seeding

```python
# tests/e2e/helpers/seed_data.py
import asyncio
import httpx


async def seed_test_users():
    """Seed test users via API."""
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        users = [
            {"email": "user1@test.com", "name": "Test User 1"},
            {"email": "user2@test.com", "name": "Test User 2"},
            {"email": "admin@test.com", "name": "Admin User"},
        ]
        for user in users:
            await client.post("/api/users", json=user)


async def cleanup_test_data():
    """Clean up test data after tests."""
    async with httpx.AsyncClient(base_url="http://localhost:8001") as client:
        await client.delete("/api/users?test=true")
```

### Using Seeds in Tests

```python
@pytest.fixture(scope="session")
async def test_data(docker_compose):
    """Seed test data before tests."""
    from tests.e2e.helpers.seed_data import seed_test_users, cleanup_test_data

    await seed_test_users()
    yield
    await cleanup_test_data()
```

## Best Practices

### DO: Use Page Object Pattern

```python
# CORRECT: Use page objects for maintainability
# tests/e2e/pages/login_page.py
class LoginPage:
    """Page object for login page."""

    def __init__(self, page):
        self.page = page
        self.email_input = "#email"
        self.password_input = "#password"
        self.login_button = "#login-button"
        self.error_message = ".error-message"

    def goto(self):
        """Navigate to login page."""
        self.page.goto("http://localhost:3000/login")

    def login(self, email: str, password: str):
        """Perform login action."""
        self.page.fill(self.email_input, email)
        self.page.fill(self.password_input, password)
        self.page.click(self.login_button)

    def get_error_message(self) -> str:
        """Get error message text."""
        return self.page.locator(self.error_message).text_content()


# Use in tests
@pytest.mark.e2e
def test_login(page):
    """Test login with page object."""
    login_page = LoginPage(page)
    login_page.goto()
    login_page.login("user@example.com", "password123")
    assert page.url.endswith("/dashboard")
```

### DO: Wait for Elements Properly

```python
# CORRECT: Wait for elements before interacting
@pytest.mark.e2e
def test_wait_for_elements(page):
    """Wait for dynamic content."""
    page.goto("http://localhost:3000/dashboard")

    # Wait for element to be visible
    page.wait_for_selector("#data-loaded", state="visible", timeout=5000)

    # Wait for API response
    with page.expect_response("**/api/users") as response_info:
        page.click("#load-users")
    response = response_info.value
    assert response.status == 200
```

### DON'T: Hardcode Timeouts

```python
# INCORRECT: Hardcoded sleep
@pytest.mark.e2e
def test_with_hardcoded_sleep(page):
    """WRONG: Using time.sleep."""
    page.goto("http://localhost:3000")
    time.sleep(5)  # Bad: arbitrary wait
    page.click("#button")


# CORRECT: Wait for specific conditions
@pytest.mark.e2e
def test_with_proper_wait(page):
    """Use Playwright's waiting mechanisms."""
    page.goto("http://localhost:3000")
    page.wait_for_load_state("networkidle")
    page.wait_for_selector("#button", state="visible")
    page.click("#button")
```

## Checklist

- [ ] Docker Compose configuration for all services
- [ ] Health checks for all containers
- [ ] Playwright/Selenium installed with browser drivers
- [ ] pytest configuration with E2E markers
- [ ] Fixtures for browser context and pages
- [ ] Environment variables for test configuration
- [ ] CI/CD pipeline with E2E test step
- [ ] Screenshot capture on test failure
- [ ] Video recording for debugging
- [ ] Test data seeding and cleanup
- [ ] Page object pattern for UI tests
- [ ] Proper waits instead of hardcoded sleeps
- [ ] Parallel execution configuration

## Related Documents

- `docs/atomic/testing/end-to-end-testing/user-journey-testing.md` — Testing complete user workflows
- `docs/atomic/testing/end-to-end-testing/performance-testing.md` — Load and performance testing
- `docs/atomic/infrastructure/docker/docker-compose-patterns.md` — Docker Compose best practices
- `docs/atomic/testing/integration-testing/testcontainers-setup.md` — Container-based integration tests
