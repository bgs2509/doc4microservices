# Push Notifications Implementation

Comprehensive guide for implementing push notifications across multiple platforms including FCM, APNs, web push, email, and SMS with queue management and delivery tracking.

## Prerequisites

- [FastAPI Basic Setup](../services/fastapi/basic-setup.md)
- [Redis Integration](../integrations/redis/connection-management.md)
- [RabbitMQ Integration](../integrations/rabbitmq/connection-management.md)
- [Communication APIs](../external-integrations/communication-apis.md)

## Core Push Notification System

### Notification Service Architecture

```python
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import json
import uuid
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class NotificationChannel(Enum):
    PUSH_MOBILE = "push_mobile"
    PUSH_WEB = "push_web"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    SLACK = "slack"
    WEBHOOK = "webhook"

class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    EXPIRED = "expired"
    CLICKED = "clicked"

@dataclass
class NotificationPayload:
    title: str
    body: str
    data: Dict[str, Any] = field(default_factory=dict)
    image_url: Optional[str] = None
    action_url: Optional[str] = None
    actions: List[Dict[str, str]] = field(default_factory=list)

@dataclass
class NotificationTarget:
    user_id: str
    device_tokens: List[str] = field(default_factory=list)
    email: Optional[str] = None
    phone_number: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationRequest:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    payload: NotificationPayload = None
    targets: List[NotificationTarget] = field(default_factory=list)
    channels: List[NotificationChannel] = field(default_factory=list)
    priority: NotificationPriority = NotificationPriority.NORMAL
    schedule_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    retry_config: Dict[str, Any] = field(default_factory=dict)
    tracking_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class NotificationResult:
    notification_id: str
    channel: NotificationChannel
    target_id: str
    status: NotificationStatus
    provider_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None

class NotificationProvider(ABC):
    """Abstract base class for notification providers"""

    @abstractmethod
    async def send_notification(
        self,
        payload: NotificationPayload,
        target: NotificationTarget,
        options: Dict[str, Any] = None
    ) -> NotificationResult:
        """Send notification via this provider"""
        pass

    @abstractmethod
    async def validate_target(self, target: NotificationTarget) -> bool:
        """Validate if target is valid for this provider"""
        pass

class NotificationService:
    """Main notification service orchestrator"""

    def __init__(self, redis_client, message_queue, db_session):
        self.redis = redis_client
        self.message_queue = message_queue
        self.db_session = db_session
        self.providers: Dict[NotificationChannel, NotificationProvider] = {}
        self.templates = {}
        self.user_preferences = {}

    def register_provider(self, channel: NotificationChannel, provider: NotificationProvider):
        """Register notification provider for specific channel"""
        self.providers[channel] = provider
        logger.info(f"Registered provider for {channel.value}")

    async def send_notification(self, request: NotificationRequest) -> List[NotificationResult]:
        """Send notification through specified channels"""
        results = []

        # Validate request
        if not request.payload or not request.targets:
            raise ValueError("Notification payload and targets are required")

        # Process each target
        for target in request.targets:
            # Get user preferences
            user_prefs = await self._get_user_preferences(target.user_id)

            # Filter channels based on user preferences
            allowed_channels = self._filter_channels_by_preferences(
                request.channels, user_prefs, request.priority
            )

            # Send through each allowed channel
            for channel in allowed_channels:
                if channel not in self.providers:
                    logger.warning(f"No provider registered for {channel.value}")
                    continue

                try:
                    # Check if immediate send or schedule
                    if request.schedule_at and request.schedule_at > datetime.utcnow():
                        # Schedule for later
                        await self._schedule_notification(request, target, channel)
                        result = NotificationResult(
                            notification_id=request.id,
                            channel=channel,
                            target_id=target.user_id,
                            status=NotificationStatus.PENDING
                        )
                    else:
                        # Send immediately
                        result = await self._send_immediate(request, target, channel)

                    results.append(result)

                except Exception as e:
                    logger.error(f"Failed to send notification via {channel.value}: {e}")
                    result = NotificationResult(
                        notification_id=request.id,
                        channel=channel,
                        target_id=target.user_id,
                        status=NotificationStatus.FAILED,
                        error_message=str(e)
                    )
                    results.append(result)

        # Store results
        await self._store_notification_results(request, results)

        return results

    async def _send_immediate(
        self,
        request: NotificationRequest,
        target: NotificationTarget,
        channel: NotificationChannel
    ) -> NotificationResult:
        """Send notification immediately"""
        provider = self.providers[channel]

        # Validate target for this channel
        if not await provider.validate_target(target):
            return NotificationResult(
                notification_id=request.id,
                channel=channel,
                target_id=target.user_id,
                status=NotificationStatus.FAILED,
                error_message="Invalid target for channel"
            )

        # Send notification
        result = await provider.send_notification(
            request.payload,
            target,
            {
                "priority": request.priority,
                "tracking_enabled": request.tracking_enabled,
                "retry_config": request.retry_config
            }
        )

        return result

    async def _schedule_notification(
        self,
        request: NotificationRequest,
        target: NotificationTarget,
        channel: NotificationChannel
    ):
        """Schedule notification for later delivery"""
        task_data = {
            "notification_id": request.id,
            "payload": request.payload.__dict__,
            "target": target.__dict__,
            "channel": channel.value,
            "options": {
                "priority": request.priority.value,
                "tracking_enabled": request.tracking_enabled,
                "retry_config": request.retry_config
            }
        }

        # Schedule in message queue
        await self.message_queue.schedule_task(
            "send_notification",
            task_data,
            schedule_at=request.schedule_at
        )

    def _filter_channels_by_preferences(
        self,
        channels: List[NotificationChannel],
        user_prefs: Dict[str, Any],
        priority: NotificationPriority
    ) -> List[NotificationChannel]:
        """Filter channels based on user preferences"""
        allowed_channels = []

        for channel in channels:
            channel_key = f"allow_{channel.value}"

            # Check if user allows this channel
            if user_prefs.get(channel_key, True):
                allowed_channels.append(channel)
            elif priority == NotificationPriority.CRITICAL:
                # Critical notifications override preferences
                allowed_channels.append(channel)

        return allowed_channels

    async def _get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user notification preferences"""
        # Try cache first
        cache_key = f"user_prefs:{user_id}"
        cached_prefs = await self.redis.get(cache_key)

        if cached_prefs:
            return json.loads(cached_prefs)

        # Get from database
        # Implementation depends on your database structure
        prefs = await self._fetch_user_preferences_from_db(user_id)

        # Cache for 1 hour
        await self.redis.setex(cache_key, 3600, json.dumps(prefs))

        return prefs

    async def _fetch_user_preferences_from_db(self, user_id: str) -> Dict[str, Any]:
        """Fetch user preferences from database"""
        # Default preferences
        return {
            "allow_push_mobile": True,
            "allow_push_web": True,
            "allow_email": True,
            "allow_sms": False,
            "allow_in_app": True,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "timezone": "UTC"
        }

    async def _store_notification_results(
        self,
        request: NotificationRequest,
        results: List[NotificationResult]
    ):
        """Store notification results for tracking"""
        # Store in database for analytics and tracking
        # Implementation depends on your database structure
        pass
```

## Firebase Cloud Messaging (FCM) Provider

### FCM Implementation

```python
import aiohttp
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request

class FCMProvider(NotificationProvider):
    """Firebase Cloud Messaging provider"""

    def __init__(self, service_account_file: str, project_id: str):
        self.project_id = project_id
        self.credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        self.fcm_url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"

    async def send_notification(
        self,
        payload: NotificationPayload,
        target: NotificationTarget,
        options: Dict[str, Any] = None
    ) -> NotificationResult:
        """Send FCM notification"""
        options = options or {}

        try:
            # Get access token
            access_token = await self._get_access_token()

            # Send to each device token
            results = []
            for device_token in target.device_tokens:
                result = await self._send_to_device(
                    device_token, payload, target, access_token, options
                )
                results.append(result)

            # Return result for the first device (or aggregate results)
            return results[0] if results else NotificationResult(
                notification_id="",
                channel=NotificationChannel.PUSH_MOBILE,
                target_id=target.user_id,
                status=NotificationStatus.FAILED,
                error_message="No device tokens"
            )

        except Exception as e:
            logger.error(f"FCM send error: {e}")
            return NotificationResult(
                notification_id="",
                channel=NotificationChannel.PUSH_MOBILE,
                target_id=target.user_id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def _send_to_device(
        self,
        device_token: str,
        payload: NotificationPayload,
        target: NotificationTarget,
        access_token: str,
        options: Dict[str, Any]
    ) -> NotificationResult:
        """Send FCM message to specific device"""

        # Build FCM message
        message = {
            "message": {
                "token": device_token,
                "notification": {
                    "title": payload.title,
                    "body": payload.body
                },
                "data": {
                    **payload.data,
                    "click_action": payload.action_url or "",
                    "user_id": target.user_id
                },
                "android": {
                    "priority": self._get_android_priority(options.get("priority")),
                    "notification": {
                        "channel_id": "default",
                        "sound": "default",
                        "click_action": payload.action_url
                    }
                },
                "apns": {
                    "payload": {
                        "aps": {
                            "alert": {
                                "title": payload.title,
                                "body": payload.body
                            },
                            "sound": "default",
                            "badge": 1
                        }
                    }
                },
                "webpush": {
                    "notification": {
                        "title": payload.title,
                        "body": payload.body,
                        "icon": payload.image_url,
                        "data": payload.data
                    }
                }
            }
        }

        # Add image if provided
        if payload.image_url:
            message["message"]["notification"]["image"] = payload.image_url

        # Send request
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.fcm_url,
                headers=headers,
                json=message
            ) as response:

                response_data = await response.json()

                if response.status == 200:
                    return NotificationResult(
                        notification_id=response_data.get("name", ""),
                        channel=NotificationChannel.PUSH_MOBILE,
                        target_id=target.user_id,
                        status=NotificationStatus.SENT,
                        provider_response=response_data,
                        sent_at=datetime.utcnow()
                    )
                else:
                    error_msg = response_data.get("error", {}).get("message", "Unknown error")
                    return NotificationResult(
                        notification_id="",
                        channel=NotificationChannel.PUSH_MOBILE,
                        target_id=target.user_id,
                        status=NotificationStatus.FAILED,
                        error_message=error_msg,
                        provider_response=response_data
                    )

    async def _get_access_token(self) -> str:
        """Get OAuth2 access token for FCM"""
        # Refresh credentials if needed
        if not self.credentials.valid:
            self.credentials.refresh(Request())

        return self.credentials.token

    def _get_android_priority(self, priority: NotificationPriority) -> str:
        """Convert priority to Android priority"""
        if priority == NotificationPriority.CRITICAL:
            return "high"
        elif priority == NotificationPriority.HIGH:
            return "high"
        else:
            return "normal"

    async def validate_target(self, target: NotificationTarget) -> bool:
        """Validate FCM target"""
        return bool(target.device_tokens)

class APNsProvider(NotificationProvider):
    """Apple Push Notification service provider"""

    def __init__(self, key_file: str, key_id: str, team_id: str, bundle_id: str, production: bool = False):
        self.key_file = key_file
        self.key_id = key_id
        self.team_id = team_id
        self.bundle_id = bundle_id
        self.apns_url = "https://api.push.apple.com" if production else "https://api.development.push.apple.com"

    async def send_notification(
        self,
        payload: NotificationPayload,
        target: NotificationTarget,
        options: Dict[str, Any] = None
    ) -> NotificationResult:
        """Send APNs notification"""
        options = options or {}

        try:
            # Generate JWT token
            jwt_token = self._generate_jwt_token()

            # Build APNs payload
            apns_payload = {
                "aps": {
                    "alert": {
                        "title": payload.title,
                        "body": payload.body
                    },
                    "sound": "default",
                    "badge": 1
                },
                **payload.data
            }

            # Add category for actions
            if payload.actions:
                apns_payload["aps"]["category"] = "ACTION_CATEGORY"

            # Send to each device token
            results = []
            for device_token in target.device_tokens:
                result = await self._send_to_apns_device(
                    device_token, apns_payload, target, jwt_token, options
                )
                results.append(result)

            return results[0] if results else NotificationResult(
                notification_id="",
                channel=NotificationChannel.PUSH_MOBILE,
                target_id=target.user_id,
                status=NotificationStatus.FAILED,
                error_message="No device tokens"
            )

        except Exception as e:
            logger.error(f"APNs send error: {e}")
            return NotificationResult(
                notification_id="",
                channel=NotificationChannel.PUSH_MOBILE,
                target_id=target.user_id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def _send_to_apns_device(
        self,
        device_token: str,
        payload: Dict[str, Any],
        target: NotificationTarget,
        jwt_token: str,
        options: Dict[str, Any]
    ) -> NotificationResult:
        """Send to specific APNs device"""

        url = f"{self.apns_url}/3/device/{device_token}"

        headers = {
            "Authorization": f"bearer {jwt_token}",
            "apns-topic": self.bundle_id,
            "apns-priority": "10" if options.get("priority") == NotificationPriority.HIGH else "5",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:

                if response.status == 200:
                    apns_id = response.headers.get("apns-id", "")
                    return NotificationResult(
                        notification_id=apns_id,
                        channel=NotificationChannel.PUSH_MOBILE,
                        target_id=target.user_id,
                        status=NotificationStatus.SENT,
                        sent_at=datetime.utcnow()
                    )
                else:
                    error_data = await response.json() if response.content_type == 'application/json' else {}
                    return NotificationResult(
                        notification_id="",
                        channel=NotificationChannel.PUSH_MOBILE,
                        target_id=target.user_id,
                        status=NotificationStatus.FAILED,
                        error_message=error_data.get("reason", f"HTTP {response.status}"),
                        provider_response=error_data
                    )

    def _generate_jwt_token(self) -> str:
        """Generate JWT token for APNs authentication"""
        import jwt
        from datetime import datetime, timedelta

        # Read private key
        with open(self.key_file, 'rb') as f:
            private_key = f.read()

        # Create JWT payload
        payload = {
            "iss": self.team_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }

        headers = {
            "alg": "ES256",
            "kid": self.key_id
        }

        return jwt.encode(payload, private_key, algorithm="ES256", headers=headers)

    async def validate_target(self, target: NotificationTarget) -> bool:
        """Validate APNs target"""
        return bool(target.device_tokens)
```

## Web Push Provider

### Web Push Implementation

```python
from pywebpush import webpush, WebPushException

class WebPushProvider(NotificationProvider):
    """Web Push notification provider"""

    def __init__(self, vapid_private_key: str, vapid_claims: Dict[str, str]):
        self.vapid_private_key = vapid_private_key
        self.vapid_claims = vapid_claims  # {"sub": "mailto:admin@example.com"}

    async def send_notification(
        self,
        payload: NotificationPayload,
        target: NotificationTarget,
        options: Dict[str, Any] = None
    ) -> NotificationResult:
        """Send Web Push notification"""
        options = options or {}

        try:
            # Build web push payload
            push_payload = {
                "title": payload.title,
                "body": payload.body,
                "icon": payload.image_url or "/default-icon.png",
                "badge": "/badge-icon.png",
                "data": {
                    **payload.data,
                    "url": payload.action_url
                },
                "actions": payload.actions,
                "requireInteraction": options.get("priority") == NotificationPriority.HIGH,
                "tag": f"notification-{target.user_id}",
                "timestamp": int(datetime.utcnow().timestamp() * 1000)
            }

            # Send to each subscription
            results = []
            for subscription_info in target.device_tokens:  # Web push subscriptions stored as device tokens
                try:
                    subscription = json.loads(subscription_info)
                    result = await self._send_to_subscription(
                        subscription, push_payload, target, options
                    )
                    results.append(result)

                except json.JSONDecodeError:
                    logger.error(f"Invalid subscription format: {subscription_info}")
                    continue

            return results[0] if results else NotificationResult(
                notification_id="",
                channel=NotificationChannel.PUSH_WEB,
                target_id=target.user_id,
                status=NotificationStatus.FAILED,
                error_message="No valid subscriptions"
            )

        except Exception as e:
            logger.error(f"Web Push send error: {e}")
            return NotificationResult(
                notification_id="",
                channel=NotificationChannel.PUSH_WEB,
                target_id=target.user_id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def _send_to_subscription(
        self,
        subscription: Dict[str, Any],
        payload: Dict[str, Any],
        target: NotificationTarget,
        options: Dict[str, Any]
    ) -> NotificationResult:
        """Send to specific web push subscription"""

        try:
            # Send web push
            response = webpush(
                subscription_info=subscription,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims,
                timeout=10
            )

            return NotificationResult(
                notification_id=str(uuid.uuid4()),
                channel=NotificationChannel.PUSH_WEB,
                target_id=target.user_id,
                status=NotificationStatus.SENT,
                provider_response={"status_code": response.status_code},
                sent_at=datetime.utcnow()
            )

        except WebPushException as e:
            # Handle specific web push errors
            error_msg = str(e)
            if "410" in error_msg:  # Gone - subscription expired
                # Mark subscription as invalid
                await self._mark_subscription_invalid(subscription, target.user_id)

            return NotificationResult(
                notification_id="",
                channel=NotificationChannel.PUSH_WEB,
                target_id=target.user_id,
                status=NotificationStatus.FAILED,
                error_message=error_msg
            )

    async def _mark_subscription_invalid(self, subscription: Dict[str, Any], user_id: str):
        """Mark web push subscription as invalid"""
        # Implementation to remove invalid subscription from database
        pass

    async def validate_target(self, target: NotificationTarget) -> bool:
        """Validate web push target"""
        if not target.device_tokens:
            return False

        # Validate subscription format
        for subscription_info in target.device_tokens:
            try:
                subscription = json.loads(subscription_info)
                required_keys = ["endpoint", "keys"]
                if not all(key in subscription for key in required_keys):
                    return False
            except json.JSONDecodeError:
                return False

        return True
```

## Email and SMS Providers

### Email Provider

```python
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

class EmailProvider(NotificationProvider):
    """Email notification provider"""

    def __init__(self, smtp_config: Dict[str, Any], templates_dir: str = None):
        self.smtp_config = smtp_config
        self.templates_dir = templates_dir

    async def send_notification(
        self,
        payload: NotificationPayload,
        target: NotificationTarget,
        options: Dict[str, Any] = None
    ) -> NotificationResult:
        """Send email notification"""
        options = options or {}

        try:
            if not target.email:
                return NotificationResult(
                    notification_id="",
                    channel=NotificationChannel.EMAIL,
                    target_id=target.user_id,
                    status=NotificationStatus.FAILED,
                    error_message="No email address"
                )

            # Build email message
            message = await self._build_email_message(payload, target, options)

            # Send email
            await self._send_email(message, target.email)

            return NotificationResult(
                notification_id=str(uuid.uuid4()),
                channel=NotificationChannel.EMAIL,
                target_id=target.user_id,
                status=NotificationStatus.SENT,
                sent_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"Email send error: {e}")
            return NotificationResult(
                notification_id="",
                channel=NotificationChannel.EMAIL,
                target_id=target.user_id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def _build_email_message(
        self,
        payload: NotificationPayload,
        target: NotificationTarget,
        options: Dict[str, Any]
    ) -> MIMEMultipart:
        """Build email message"""
        message = MIMEMultipart("alternative")
        message["Subject"] = payload.title
        message["From"] = self.smtp_config["from_email"]
        message["To"] = target.email

        # Create text version
        text_content = payload.body
        if payload.action_url:
            text_content += f"\n\nClick here: {payload.action_url}"

        text_part = MIMEText(text_content, "plain")
        message.attach(text_part)

        # Create HTML version
        html_content = await self._build_html_content(payload, target, options)
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        return message

    async def _build_html_content(
        self,
        payload: NotificationPayload,
        target: NotificationTarget,
        options: Dict[str, Any]
    ) -> str:
        """Build HTML email content"""
        # Simple HTML template
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{payload.title}</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
                <h2 style="color: #333; margin-top: 0;">{payload.title}</h2>
                <p style="color: #666; line-height: 1.6;">{payload.body}</p>

                {f'<img src="{payload.image_url}" alt="Notification Image" style="max-width: 100%; height: auto; border-radius: 4px;">' if payload.image_url else ''}

                {f'<a href="{payload.action_url}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block; margin-top: 20px;">View Details</a>' if payload.action_url else ''}
            </div>

            <p style="color: #999; font-size: 12px; margin-top: 20px;">
                This email was sent to {target.email}.
                <a href="#" style="color: #007bff;">Unsubscribe</a>
            </p>
        </body>
        </html>
        """
        return html_template

    async def _send_email(self, message: MIMEMultipart, to_email: str):
        """Send email via SMTP"""
        smtp = aiosmtplib.SMTP(
            hostname=self.smtp_config["host"],
            port=self.smtp_config["port"],
            use_tls=self.smtp_config.get("use_tls", True)
        )

        await smtp.connect()

        if self.smtp_config.get("username"):
            await smtp.login(
                self.smtp_config["username"],
                self.smtp_config["password"]
            )

        await smtp.send_message(message)
        await smtp.quit()

    async def validate_target(self, target: NotificationTarget) -> bool:
        """Validate email target"""
        return bool(target.email and "@" in target.email)

class SMSProvider(NotificationProvider):
    """SMS notification provider using Twilio"""

    def __init__(self, twilio_account_sid: str, twilio_auth_token: str, from_number: str):
        self.account_sid = twilio_account_sid
        self.auth_token = twilio_auth_token
        self.from_number = from_number

    async def send_notification(
        self,
        payload: NotificationPayload,
        target: NotificationTarget,
        options: Dict[str, Any] = None
    ) -> NotificationResult:
        """Send SMS notification"""
        try:
            from twilio.rest import Client

            if not target.phone_number:
                return NotificationResult(
                    notification_id="",
                    channel=NotificationChannel.SMS,
                    target_id=target.user_id,
                    status=NotificationStatus.FAILED,
                    error_message="No phone number"
                )

            # Create Twilio client
            client = Client(self.account_sid, self.auth_token)

            # Build SMS content
            sms_content = f"{payload.title}\n\n{payload.body}"
            if payload.action_url:
                sms_content += f"\n\n{payload.action_url}"

            # Send SMS
            message = client.messages.create(
                body=sms_content,
                from_=self.from_number,
                to=target.phone_number
            )

            return NotificationResult(
                notification_id=message.sid,
                channel=NotificationChannel.SMS,
                target_id=target.user_id,
                status=NotificationStatus.SENT,
                provider_response={"sid": message.sid},
                sent_at=datetime.utcnow()
            )

        except Exception as e:
            logger.error(f"SMS send error: {e}")
            return NotificationResult(
                notification_id="",
                channel=NotificationChannel.SMS,
                target_id=target.user_id,
                status=NotificationStatus.FAILED,
                error_message=str(e)
            )

    async def validate_target(self, target: NotificationTarget) -> bool:
        """Validate SMS target"""
        return bool(target.phone_number and len(target.phone_number) > 5)
```

## Notification Templates and Personalization

### Template Engine

```python
from jinja2 import Environment, FileSystemLoader, Template

class NotificationTemplateEngine:
    """Template engine for notification personalization"""

    def __init__(self, templates_dir: str):
        self.env = Environment(loader=FileSystemLoader(templates_dir))
        self.templates = {}

    def register_template(self, template_id: str, template_data: Dict[str, str]):
        """Register notification template"""
        self.templates[template_id] = {
            "title": Template(template_data["title"]),
            "body": Template(template_data["body"]),
            "html_body": Template(template_data.get("html_body", "")),
            "data": template_data.get("data", {})
        }

    async def render_notification(
        self,
        template_id: str,
        context: Dict[str, Any],
        target: NotificationTarget
    ) -> NotificationPayload:
        """Render notification from template"""
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")

        template = self.templates[template_id]

        # Add user context
        full_context = {
            **context,
            "user_id": target.user_id,
            "email": target.email,
            "phone_number": target.phone_number,
            "preferences": target.preferences
        }

        # Render template
        title = template["title"].render(**full_context)
        body = template["body"].render(**full_context)
        html_body = template["html_body"].render(**full_context) if template["html_body"] else None

        return NotificationPayload(
            title=title,
            body=body,
            data={
                **template["data"],
                "html_body": html_body
            }
        )

class PersonalizationService:
    """Service for personalizing notifications"""

    def __init__(self, template_engine: NotificationTemplateEngine, db_session):
        self.template_engine = template_engine
        self.db_session = db_session

    async def create_personalized_notification(
        self,
        template_id: str,
        user_ids: List[str],
        context: Dict[str, Any],
        channels: List[NotificationChannel],
        priority: NotificationPriority = NotificationPriority.NORMAL
    ) -> List[NotificationRequest]:
        """Create personalized notifications for multiple users"""
        requests = []

        for user_id in user_ids:
            # Get user data for personalization
            user_data = await self._get_user_data(user_id)
            target = NotificationTarget(
                user_id=user_id,
                device_tokens=user_data.get("device_tokens", []),
                email=user_data.get("email"),
                phone_number=user_data.get("phone_number"),
                preferences=user_data.get("preferences", {})
            )

            # Render personalized content
            personalized_context = {
                **context,
                **user_data
            }

            payload = await self.template_engine.render_notification(
                template_id, personalized_context, target
            )

            # Create notification request
            request = NotificationRequest(
                payload=payload,
                targets=[target],
                channels=channels,
                priority=priority
            )

            requests.append(request)

        return requests

    async def _get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Get user data for personalization"""
        # Implementation depends on your database structure
        return {
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com",
            "device_tokens": [],
            "preferences": {}
        }

# Example template registration
template_engine = NotificationTemplateEngine("templates/")

# Welcome notification template
template_engine.register_template("user_welcome", {
    "title": "Welcome to {{ app_name }}, {{ name }}!",
    "body": "Hi {{ name }}, welcome to {{ app_name }}. We're excited to have you on board!",
    "html_body": """
    <h2>Welcome to {{ app_name }}, {{ name }}!</h2>
    <p>Hi {{ name }},</p>
    <p>Welcome to {{ app_name }}. We're excited to have you on board!</p>
    <p>Get started by exploring our features:</p>
    <ul>
        <li>Feature 1</li>
        <li>Feature 2</li>
        <li>Feature 3</li>
    </ul>
    """,
    "data": {
        "category": "welcome",
        "action_url": "/onboarding"
    }
})

# Order notification template
template_engine.register_template("order_confirmed", {
    "title": "Order #{{ order_number }} Confirmed",
    "body": "Your order for {{ item_count }} items totaling ${{ total_amount }} has been confirmed.",
    "html_body": """
    <h2>Order Confirmed!</h2>
    <p>Hi {{ name }},</p>
    <p>Your order #{{ order_number }} has been confirmed.</p>
    <p><strong>Order Details:</strong></p>
    <ul>
        <li>Items: {{ item_count }}</li>
        <li>Total: ${{ total_amount }}</li>
        <li>Delivery: {{ delivery_date }}</li>
    </ul>
    """,
    "data": {
        "category": "order",
        "order_id": "{{ order_id }}"
    }
})
```

## Queue Management and Retry Logic

### Message Queue Integration

```python
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class NotificationQueue:
    """Message queue for notification processing"""

    def __init__(self, redis_client, max_retries: int = 3):
        self.redis = redis_client
        self.max_retries = max_retries
        self.workers = {}

    async def start_workers(self, worker_count: int = 5):
        """Start notification processing workers"""
        for i in range(worker_count):
            worker = asyncio.create_task(self._worker(f"worker_{i}"))
            self.workers[f"worker_{i}"] = worker

        logger.info(f"Started {worker_count} notification workers")

    async def stop_workers(self):
        """Stop all notification workers"""
        for worker_id, worker in self.workers.items():
            worker.cancel()

        await asyncio.gather(*self.workers.values(), return_exceptions=True)
        self.workers.clear()

    async def enqueue_notification(
        self,
        request: NotificationRequest,
        delay_seconds: int = 0,
        priority: int = 1
    ):
        """Enqueue notification for processing"""
        task_data = {
            "id": request.id,
            "request": self._serialize_request(request),
            "retry_count": 0,
            "enqueued_at": datetime.utcnow().isoformat(),
            "priority": priority
        }

        if delay_seconds > 0:
            # Schedule for later
            execute_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
            await self.redis.zadd(
                "notification_scheduled",
                {json.dumps(task_data): execute_at.timestamp()}
            )
        else:
            # Add to immediate queue
            await self.redis.lpush("notification_queue", json.dumps(task_data))

    async def _worker(self, worker_id: str):
        """Worker process for handling notifications"""
        logger.info(f"Notification worker {worker_id} started")

        while True:
            try:
                # Check for scheduled notifications
                await self._process_scheduled_notifications()

                # Process immediate queue
                task_data = await self.redis.brpop("notification_queue", timeout=1)

                if task_data:
                    queue_name, task_json = task_data
                    await self._process_notification_task(task_json, worker_id)

            except asyncio.CancelledError:
                logger.info(f"Notification worker {worker_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(1)

    async def _process_scheduled_notifications(self):
        """Move scheduled notifications to immediate queue"""
        current_time = datetime.utcnow().timestamp()

        # Get notifications ready for processing
        ready_notifications = await self.redis.zrangebyscore(
            "notification_scheduled",
            0,
            current_time,
            withscores=True
        )

        for notification_data, score in ready_notifications:
            # Move to immediate queue
            await self.redis.lpush("notification_queue", notification_data)

            # Remove from scheduled queue
            await self.redis.zrem("notification_scheduled", notification_data)

    async def _process_notification_task(self, task_json: str, worker_id: str):
        """Process individual notification task"""
        try:
            task_data = json.loads(task_json)
            request = self._deserialize_request(task_data["request"])

            logger.info(f"Worker {worker_id} processing notification {request.id}")

            # Process notification through notification service
            notification_service = NotificationService(self.redis, self, None)
            results = await notification_service.send_notification(request)

            # Check for failures and retry if needed
            failed_results = [r for r in results if r.status == NotificationStatus.FAILED]

            if failed_results and task_data["retry_count"] < self.max_retries:
                await self._retry_notification(task_data, failed_results)
            else:
                # Store final results
                await self._store_final_results(request.id, results)

        except Exception as e:
            logger.error(f"Error processing notification task: {e}")

    async def _retry_notification(self, task_data: Dict[str, Any], failed_results: List[NotificationResult]):
        """Retry failed notification"""
        retry_count = task_data["retry_count"] + 1
        delay_seconds = 2 ** retry_count  # Exponential backoff

        # Update task data
        task_data["retry_count"] = retry_count
        task_data["retry_at"] = (datetime.utcnow() + timedelta(seconds=delay_seconds)).isoformat()

        # Schedule retry
        execute_at = datetime.utcnow() + timedelta(seconds=delay_seconds)
        await self.redis.zadd(
            "notification_scheduled",
            {json.dumps(task_data): execute_at.timestamp()}
        )

        logger.info(f"Scheduled retry {retry_count} for notification {task_data['id']} in {delay_seconds}s")

    def _serialize_request(self, request: NotificationRequest) -> Dict[str, Any]:
        """Serialize notification request for storage"""
        return {
            "id": request.id,
            "payload": {
                "title": request.payload.title,
                "body": request.payload.body,
                "data": request.payload.data,
                "image_url": request.payload.image_url,
                "action_url": request.payload.action_url,
                "actions": request.payload.actions
            },
            "targets": [
                {
                    "user_id": t.user_id,
                    "device_tokens": t.device_tokens,
                    "email": t.email,
                    "phone_number": t.phone_number,
                    "preferences": t.preferences
                }
                for t in request.targets
            ],
            "channels": [c.value for c in request.channels],
            "priority": request.priority.value,
            "schedule_at": request.schedule_at.isoformat() if request.schedule_at else None,
            "expires_at": request.expires_at.isoformat() if request.expires_at else None,
            "retry_config": request.retry_config,
            "tracking_enabled": request.tracking_enabled,
            "created_at": request.created_at.isoformat()
        }

    def _deserialize_request(self, data: Dict[str, Any]) -> NotificationRequest:
        """Deserialize notification request from storage"""
        payload = NotificationPayload(
            title=data["payload"]["title"],
            body=data["payload"]["body"],
            data=data["payload"]["data"],
            image_url=data["payload"]["image_url"],
            action_url=data["payload"]["action_url"],
            actions=data["payload"]["actions"]
        )

        targets = [
            NotificationTarget(
                user_id=t["user_id"],
                device_tokens=t["device_tokens"],
                email=t["email"],
                phone_number=t["phone_number"],
                preferences=t["preferences"]
            )
            for t in data["targets"]
        ]

        return NotificationRequest(
            id=data["id"],
            payload=payload,
            targets=targets,
            channels=[NotificationChannel(c) for c in data["channels"]],
            priority=NotificationPriority(data["priority"]),
            schedule_at=datetime.fromisoformat(data["schedule_at"]) if data["schedule_at"] else None,
            expires_at=datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None,
            retry_config=data["retry_config"],
            tracking_enabled=data["tracking_enabled"],
            created_at=datetime.fromisoformat(data["created_at"])
        )
```

## Testing Push Notifications

### Notification Testing Framework

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

class NotificationTester:
    """Testing utilities for notification system"""

    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    async def test_fcm_notification(self):
        """Test FCM notification sending"""
        # Mock FCM provider
        mock_fcm = AsyncMock(spec=FCMProvider)
        mock_fcm.send_notification.return_value = NotificationResult(
            notification_id="test_fcm_id",
            channel=NotificationChannel.PUSH_MOBILE,
            target_id="user123",
            status=NotificationStatus.SENT,
            sent_at=datetime.utcnow()
        )
        mock_fcm.validate_target.return_value = True

        self.notification_service.register_provider(NotificationChannel.PUSH_MOBILE, mock_fcm)

        # Create test notification
        payload = NotificationPayload(
            title="Test Notification",
            body="This is a test notification",
            data={"key": "value"}
        )

        target = NotificationTarget(
            user_id="user123",
            device_tokens=["test_device_token"]
        )

        request = NotificationRequest(
            payload=payload,
            targets=[target],
            channels=[NotificationChannel.PUSH_MOBILE]
        )

        # Send notification
        results = await self.notification_service.send_notification(request)

        # Verify results
        assert len(results) == 1
        assert results[0].status == NotificationStatus.SENT
        assert results[0].notification_id == "test_fcm_id"

        # Verify provider was called correctly
        mock_fcm.send_notification.assert_called_once()

    async def test_multi_channel_notification(self):
        """Test sending notification through multiple channels"""
        # Mock providers
        mock_fcm = AsyncMock(spec=FCMProvider)
        mock_fcm.send_notification.return_value = NotificationResult(
            notification_id="fcm_id",
            channel=NotificationChannel.PUSH_MOBILE,
            target_id="user123",
            status=NotificationStatus.SENT
        )
        mock_fcm.validate_target.return_value = True

        mock_email = AsyncMock(spec=EmailProvider)
        mock_email.send_notification.return_value = NotificationResult(
            notification_id="email_id",
            channel=NotificationChannel.EMAIL,
            target_id="user123",
            status=NotificationStatus.SENT
        )
        mock_email.validate_target.return_value = True

        self.notification_service.register_provider(NotificationChannel.PUSH_MOBILE, mock_fcm)
        self.notification_service.register_provider(NotificationChannel.EMAIL, mock_email)

        # Create test notification
        payload = NotificationPayload(
            title="Multi-channel Test",
            body="This should be sent via multiple channels"
        )

        target = NotificationTarget(
            user_id="user123",
            device_tokens=["test_token"],
            email="test@example.com"
        )

        request = NotificationRequest(
            payload=payload,
            targets=[target],
            channels=[NotificationChannel.PUSH_MOBILE, NotificationChannel.EMAIL]
        )

        # Send notification
        results = await self.notification_service.send_notification(request)

        # Verify results
        assert len(results) == 2
        assert all(r.status == NotificationStatus.SENT for r in results)

        # Verify both providers were called
        mock_fcm.send_notification.assert_called_once()
        mock_email.send_notification.assert_called_once()

    async def test_notification_with_user_preferences(self):
        """Test notification filtering based on user preferences"""
        # Mock user preferences
        user_prefs = {
            "allow_push_mobile": True,
            "allow_email": False,  # User disabled email notifications
            "allow_sms": True
        }

        with patch.object(
            self.notification_service,
            '_get_user_preferences',
            return_value=user_prefs
        ):
            # Mock providers
            mock_fcm = AsyncMock(spec=FCMProvider)
            mock_fcm.validate_target.return_value = True
            mock_fcm.send_notification.return_value = NotificationResult(
                notification_id="fcm_id",
                channel=NotificationChannel.PUSH_MOBILE,
                target_id="user123",
                status=NotificationStatus.SENT
            )

            mock_email = AsyncMock(spec=EmailProvider)
            mock_sms = AsyncMock(spec=SMSProvider)

            self.notification_service.register_provider(NotificationChannel.PUSH_MOBILE, mock_fcm)
            self.notification_service.register_provider(NotificationChannel.EMAIL, mock_email)
            self.notification_service.register_provider(NotificationChannel.SMS, mock_sms)

            # Create test notification
            payload = NotificationPayload(title="Test", body="Test message")
            target = NotificationTarget(
                user_id="user123",
                device_tokens=["token"],
                email="test@example.com",
                phone_number="+1234567890"
            )

            request = NotificationRequest(
                payload=payload,
                targets=[target],
                channels=[
                    NotificationChannel.PUSH_MOBILE,
                    NotificationChannel.EMAIL,
                    NotificationChannel.SMS
                ]
            )

            # Send notification
            results = await self.notification_service.send_notification(request)

            # Verify only allowed channels were used
            # Email should be filtered out due to user preferences
            channels_used = {r.channel for r in results}
            assert NotificationChannel.PUSH_MOBILE in channels_used
            assert NotificationChannel.EMAIL not in channels_used

            # Verify only FCM was called (email should be skipped)
            mock_fcm.send_notification.assert_called_once()
            mock_email.send_notification.assert_not_called()

@pytest.fixture
def notification_service():
    """Create notification service for testing"""
    redis_client = AsyncMock()
    message_queue = AsyncMock()
    db_session = AsyncMock()

    return NotificationService(redis_client, message_queue, db_session)

@pytest.fixture
def notification_tester(notification_service):
    """Create notification tester"""
    return NotificationTester(notification_service)

@pytest.mark.asyncio
async def test_fcm_notification_sending(notification_tester):
    await notification_tester.test_fcm_notification()

@pytest.mark.asyncio
async def test_multi_channel_notifications(notification_tester):
    await notification_tester.test_multi_channel_notification()

@pytest.mark.asyncio
async def test_user_preference_filtering(notification_tester):
    await notification_tester.test_notification_with_user_preferences()
```

## Related Documentation

- [WebSocket Patterns](websocket-patterns.md)
- [Server-Sent Events Implementation](sse-implementation.md)
- [Real-time Sync Patterns](real-time-sync-patterns.md)
- [Communication APIs](../external-integrations/communication-apis.md)

## Best Practices

1. **Provider Selection**:
   - Use FCM for Android and cross-platform mobile
   - Use APNs for iOS native applications
   - Use Web Push for browser notifications
   - Implement fallback mechanisms

2. **Message Design**:
   - Keep messages concise and actionable
   - Use rich media appropriately
   - Implement proper deep linking
   - Test across different devices

3. **Delivery Reliability**:
   - Implement retry mechanisms with exponential backoff
   - Use message queues for scalability
   - Track delivery status and user engagement
   - Handle provider-specific errors

4. **User Experience**:
   - Respect user notification preferences
   - Implement quiet hours
   - Provide unsubscribe options
   - Use appropriate notification priority

5. **Performance**:
   - Batch notifications where possible
   - Use background processing
   - Implement rate limiting
   - Monitor provider quotas and limits