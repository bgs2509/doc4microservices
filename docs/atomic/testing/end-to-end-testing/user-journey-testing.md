# User Journey Testing

Test complete user workflows end-to-end across multiple services, databases, and interfaces to verify business-critical flows work correctly in realistic conditions. User journey tests validate that users can successfully complete key tasks without errors or data inconsistencies.

This document covers testing patterns for complete user journeys in microservices, including multi-step workflows, cross-service communication, state persistence, and data consistency verification. User journey tests ensure your system delivers value to real users.

Testing user journeys validates that business-critical workflows execute correctly from user perspective, data flows properly between services, and system state remains consistent throughout complex operations. These tests catch integration issues that unit and service tests cannot detect.

## Common User Journeys

### Critical Journeys to Test

**Authentication & Onboarding:**
- User registration → Email verification → Profile setup
- User login → Session management → Password reset

**Core Business Flows:**
- Loan application → Credit check → Approval/Rejection → Notification
- Payment processing → Transaction confirmation → Receipt generation

**Multi-Service Workflows:**
- API request → Worker processing → Bot notification
- Frontend action → API call → Database update → Event publishing

## Testing Registration Flow

### Complete Registration Journey

```python
# tests/e2e/test_user_registration.py
import pytest
from tests.e2e.pages.registration_page import RegistrationPage
from tests.e2e.pages.email_verification_page import EmailVerificationPage
from tests.e2e.pages.profile_page import ProfilePage


@pytest.mark.e2e
@pytest.mark.slow
def test_complete_user_registration_journey(page, api_client):
    """Test user completes full registration journey."""

    # Step 1: Navigate to registration page
    reg_page = RegistrationPage(page)
    reg_page.goto()

    # Step 2: Fill registration form
    user_email = "newuser@test.com"
    reg_page.fill_registration_form(
        email=user_email,
        password="SecurePass123!",
        full_name="Test User"
    )
    reg_page.submit()

    # Step 3: Verify success message
    assert reg_page.get_success_message() == "Registration successful! Check your email."

    # Step 4: Verify user created in database via API
    response = api_client.get(f"/api/users?email={user_email}")
    assert response.status_code == 200
    users = response.json()["users"]
    assert len(users) == 1
    assert users[0]["email"] == user_email
    assert users[0]["verified"] is False

    # Step 5: Simulate email verification (get token from DB/email)
    verification_token = get_verification_token_from_db(user_email)
    verify_page = EmailVerificationPage(page)
    verify_page.goto_with_token(verification_token)

    # Step 6: Verify account activated
    assert verify_page.get_confirmation_message() == "Email verified successfully!"

    # Step 7: Verify database updated
    response = api_client.get(f"/api/users?email={user_email}")
    users = response.json()["users"]
    assert users[0]["verified"] is True

    # Step 8: Login with new account
    reg_page.goto_login()
    reg_page.login(user_email, "SecurePass123!")

    # Step 9: Verify redirected to dashboard
    assert page.url.endswith("/dashboard")
```

## Testing Loan Application Flow

### Multi-Service Loan Journey

```python
@pytest.mark.e2e
@pytest.mark.slow
async def test_loan_application_journey(page, api_client, rabbitmq_client):
    """Test complete loan application from request to notification."""

    # Step 1: User logs in
    page.goto("http://localhost:3000/login")
    page.fill("#email", "borrower@test.com")
    page.fill("#password", "password123")
    page.click("#login-button")
    page.wait_for_url("**/dashboard")

    # Step 2: Navigate to loan application
    page.click("#apply-for-loan")
    page.wait_for_url("**/loans/apply")

    # Step 3: Fill loan application form
    page.fill("#loan-amount", "10000")
    page.select_option("#loan-purpose", "business")
    page.fill("#loan-term", "24")
    page.click("#submit-application")

    # Step 4: Verify application submitted
    page.wait_for_selector(".success-message")
    assert "Application submitted" in page.locator(".success-message").text_content()

    # Step 5: Get loan application ID
    loan_id = page.locator("#loan-id").text_content()

    # Step 6: Verify loan created in database via API
    response = api_client.get(f"/api/loans/{loan_id}")
    assert response.status_code == 200
    loan = response.json()
    assert loan["amount"] == 10000
    assert loan["status"] == "pending"

    # Step 7: Verify event published to RabbitMQ
    await asyncio.sleep(1)  # Allow event to be published
    message = await rabbitmq_client.consume_one("loan.application.submitted")
    assert message["loan_id"] == loan_id
    assert message["amount"] == 10000

    # Step 8: Wait for worker to process (credit check)
    await asyncio.sleep(5)  # Worker processing time

    # Step 9: Verify loan status updated
    response = api_client.get(f"/api/loans/{loan_id}")
    loan = response.json()
    assert loan["status"] in ["approved", "rejected"]

    # Step 10: Verify notification sent (check bot or email log)
    notifications = api_client.get(f"/api/notifications?user_id={loan['user_id']}")
    assert len(notifications.json()["notifications"]) > 0
    assert loan_id in notifications.json()["notifications"][0]["content"]
```

## Testing Bot Interaction Flow

### Telegram Bot User Journey

```python
@pytest.mark.e2e
async def test_telegram_bot_loan_application_journey(bot_client, api_client):
    """Test loan application via Telegram bot."""

    # Step 1: User sends /start command
    update = create_bot_update(text="/start", user_id=123456)
    response = await bot_client.send_update(update)
    assert "Welcome" in response.text

    # Step 2: User sends /apply_loan command
    update = create_bot_update(text="/apply_loan", user_id=123456)
    response = await bot_client.send_update(update)
    assert "How much would you like to borrow?" in response.text

    # Step 3: User provides loan amount
    update = create_bot_update(text="10000", user_id=123456)
    response = await bot_client.send_update(update)
    assert "What is the purpose" in response.text

    # Step 4: User provides purpose
    update = create_bot_update(text="Business expansion", user_id=123456)
    response = await bot_client.send_update(update)
    assert "How many months" in response.text

    # Step 5: User provides term
    update = create_bot_update(text="24", user_id=123456)
    response = await bot_client.send_update(update)
    assert "application submitted" in response.text.lower()

    # Step 6: Verify loan created via API
    loans = api_client.get("/api/loans?telegram_user_id=123456")
    assert len(loans.json()["loans"]) == 1
    loan = loans.json()["loans"][0]
    assert loan["amount"] == 10000
    assert loan["purpose"] == "Business expansion"
    assert loan["term_months"] == 24
```

## Testing Cross-Service Communication

### API → Worker → Bot Notification Flow

```python
@pytest.mark.e2e
async def test_cross_service_notification_flow(api_client, rabbitmq_client, bot_client):
    """Test notification flows from API through worker to bot."""

    # Step 1: Trigger action via API (loan approved)
    response = api_client.post("/api/loans/loan-123/approve")
    assert response.status_code == 200

    # Step 2: Verify event published to RabbitMQ
    await asyncio.sleep(0.5)
    message = await rabbitmq_client.consume_one("loan.approved")
    assert message["loan_id"] == "loan-123"

    # Step 3: Wait for worker to process event
    await asyncio.sleep(2)

    # Step 4: Verify notification record created
    notifications = api_client.get("/api/notifications?loan_id=loan-123")
    assert len(notifications.json()["notifications"]) > 0
    notification = notifications.json()["notifications"][0]
    assert notification["type"] == "loan_approved"

    # Step 5: Verify bot sent message to user
    await asyncio.sleep(1)
    sent_messages = await bot_client.get_sent_messages(user_id=notification["user_id"])
    assert len(sent_messages) > 0
    assert "approved" in sent_messages[-1]["text"].lower()
```

## Testing Data Consistency

### Verify Data Across Services

```python
@pytest.mark.e2e
def test_data_consistency_across_services(api_client):
    """Test data remains consistent across multiple services."""

    # Step 1: Create user via API
    response = api_client.post("/api/users", json={
        "email": "consistency@test.com",
        "name": "Consistency Test"
    })
    user_id = response.json()["id"]

    # Step 2: Create loan for user
    response = api_client.post("/api/loans", json={
        "user_id": user_id,
        "amount": 5000,
        "purpose": "test"
    })
    loan_id = response.json()["id"]

    # Step 3: Verify user shows loan in their profile
    response = api_client.get(f"/api/users/{user_id}")
    user = response.json()
    assert loan_id in [loan["id"] for loan in user["loans"]]

    # Step 4: Verify loan shows correct user
    response = api_client.get(f"/api/loans/{loan_id}")
    loan = response.json()
    assert loan["user_id"] == user_id
    assert loan["user_email"] == "consistency@test.com"

    # Step 5: Update loan status
    api_client.patch(f"/api/loans/{loan_id}", json={"status": "approved"})

    # Step 6: Verify user's loan list reflects update
    response = api_client.get(f"/api/users/{user_id}/loans")
    loans = response.json()["loans"]
    loan_from_user = next(l for l in loans if l["id"] == loan_id)
    assert loan_from_user["status"] == "approved"
```

## Testing Error Recovery

### Handle Failures Gracefully

```python
@pytest.mark.e2e
async def test_loan_application_with_service_failure(page, api_client, mock_service):
    """Test user journey when dependent service fails."""

    # Step 1: Start loan application
    page.goto("http://localhost:3000/loans/apply")
    page.fill("#loan-amount", "10000")
    page.click("#submit-application")

    # Step 2: Simulate credit check service failure
    mock_service.simulate_failure("credit_check_service")

    # Step 3: Verify graceful error handling
    page.wait_for_selector(".error-message")
    error_text = page.locator(".error-message").text_content()
    assert "temporarily unavailable" in error_text.lower()

    # Step 4: Verify application saved with pending status
    response = api_client.get("/api/loans?status=pending_retry")
    loans = response.json()["loans"]
    assert len(loans) > 0

    # Step 5: Restore service
    mock_service.restore("credit_check_service")

    # Step 6: Trigger retry
    page.click("#retry-button")

    # Step 7: Verify successful completion
    page.wait_for_selector(".success-message")
    assert "processed successfully" in page.locator(".success-message").text_content().lower()
```

## Testing Multi-User Scenarios

### Concurrent User Journeys

```python
@pytest.mark.e2e
async def test_multiple_users_concurrent_journeys():
    """Test multiple users performing actions concurrently."""
    import asyncio

    async def user_journey(user_id: str, email: str):
        """Simulate one user's journey."""
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Register
            response = await client.post("/api/users", json={
                "email": email,
                "name": f"User {user_id}"
            })
            assert response.status_code == 201

            # Apply for loan
            user_data = response.json()
            response = await client.post("/api/loans", json={
                "user_id": user_data["id"],
                "amount": 5000 + int(user_id) * 1000
            })
            assert response.status_code == 201

            return response.json()

    # Run 10 users concurrently
    tasks = [
        user_journey(str(i), f"user{i}@test.com")
        for i in range(10)
    ]
    results = await asyncio.gather(*tasks)

    # Verify all succeeded
    assert len(results) == 10
    assert all(r["status"] == "pending" for r in results)
```

## Best Practices

### DO: Test Complete Workflows

```python
# CORRECT: Test entire user journey
@pytest.mark.e2e
def test_complete_purchase_journey(page):
    """Test full purchase from browsing to confirmation."""
    # Browse → Select → Add to cart → Checkout → Payment → Confirmation
    page.goto("http://localhost:3000/products")
    page.click("#product-1")
    page.click("#add-to-cart")
    page.goto("http://localhost:3000/checkout")
    page.fill("#card-number", "4111111111111111")
    page.click("#complete-purchase")
    page.wait_for_selector(".confirmation")
    assert "Order confirmed" in page.text_content(".confirmation")


# INCORRECT: Test partial workflow
@pytest.mark.e2e
def test_partial_journey(page):
    """WRONG: Only tests part of journey."""
    page.goto("http://localhost:3000/checkout")
    page.click("#complete-purchase")
    # Missing: product selection, cart, payment details
```

### DO: Verify Data Consistency

```python
# CORRECT: Check data across all touchpoints
@pytest.mark.e2e
def test_order_data_consistency(page, api_client):
    """Verify order data consistent across UI, API, and database."""
    # Create order via UI
    page.goto("http://localhost:3000/products")
    page.click("#buy-now")
    order_id = page.locator("#order-id").text_content()

    # Verify via API
    response = api_client.get(f"/api/orders/{order_id}")
    api_order = response.json()
    assert api_order["status"] == "pending"

    # Verify in user's order history
    page.goto("http://localhost:3000/orders")
    assert order_id in page.text_content("body")
```

### DON'T: Test Implementation Details

```python
# INCORRECT: Testing internal implementation
@pytest.mark.e2e
def test_internal_cache_behavior(api_client):
    """WRONG: Tests internal caching logic."""
    # E2E tests should focus on user outcomes, not cache hits


# CORRECT: Test user-visible behavior
@pytest.mark.e2e
def test_fast_page_load(page):
    """Test page loads quickly (user cares about speed, not cache)."""
    start = time.time()
    page.goto("http://localhost:3000/dashboard")
    load_time = time.time() - start
    assert load_time < 2.0  # User cares: page loads in <2s
```

## Checklist

- [ ] Test complete user workflows end-to-end
- [ ] Verify multi-step journeys across services
- [ ] Test cross-service communication (API → Worker → Bot)
- [ ] Verify data consistency across all touchpoints
- [ ] Test error handling and recovery
- [ ] Test concurrent user scenarios
- [ ] Verify state persistence across steps
- [ ] Test notification delivery
- [ ] Verify authentication flows
- [ ] Test critical business transactions
- [ ] Use page objects for maintainability
- [ ] Mark tests with `@pytest.mark.e2e` and `@pytest.mark.slow`

## Related Documents

- `docs/atomic/testing/end-to-end-testing/e2e-test-setup.md` — E2E test infrastructure setup
- `docs/atomic/testing/end-to-end-testing/performance-testing.md` — Performance and load testing
- `docs/atomic/testing/service-testing/fastapi-testing-patterns.md` — API service testing
- `docs/atomic/testing/service-testing/aiogram-testing-patterns.md` — Bot testing patterns
