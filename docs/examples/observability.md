## Наблюдаемость (Observability)

Наблюдаемость — это способность понимать внутреннее состояние системы по ее внешним выходным данным. Три столпа наблюдаемости — это **логи (Logs)**, **метрики (Metrics)** и **трассировки (Traces)**. В этом разделе мы рассмотрим, как реализовать их в наших сервисах.

### 1. Структурированное логирование с Correlation ID

Структурированные логи (например, в формате JSON) легко парсить и анализировать. `Correlation ID` — это уникальный идентификатор, который присваивается запросу и передается через все сервисы, которые этот запрос затрагивает. Это позволяет отследить полный путь запроса в распределенной системе.

Мы будем использовать `structlog` и кастомный middleware для FastAPI.

#### Установка
```bash
pip install structlog "uvicorn[standard]"
```

#### Реализация

`src/middlewares/correlation_id.py`
```python
from __future__ import annotations

import uuid
from contextvars import ContextVar

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

# Контекстная переменная для хранения ID запроса
CORRELATION_ID_CTX_KEY = "correlation_id"
correlation_id_ctx: ContextVar[str] = ContextVar(CORRELATION_ID_CTX_KEY, default=None)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Пытаемся получить ID из заголовка или генерируем новый
        correlation_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Устанавливаем ID в контекстную переменную
        token = correlation_id_ctx.set(correlation_id)

        response = await call_next(request)
        
        # Добавляем ID в заголовок ответа
        response.headers["X-Request-ID"] = correlation_id

        # Сбрасываем контекстную переменную
        correlation_id_ctx.reset(token)

        return response
```

#### Настройка `structlog`

Теперь настроим `structlog` для добавления `correlation_id` в каждую запись лога.

`src/logging_config.py`
```python
import logging
import structlog

from .middlewares.correlation_id import correlation_id_ctx

def setup_logging():
    """Настройка структурированного логирования."""
    
    def add_correlation_id(logger, method_name, event_dict):
        """Добавить correlation_id в запись лога, если он есть в контексте."""
        correlation_id = correlation_id_ctx.get()
        if correlation_id:
            event_dict["correlation_id"] = correlation_id
        return event_dict

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_correlation_id,
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
```

#### Подключение в `main.py`
```python
from .logging_config import setup_logging
from .middlewares.correlation_id import CorrelationIdMiddleware

# Вызываем в самом начале
setup_logging()

app = FastAPI(...)
app.add_middleware(CorrelationIdMiddleware)
```

### 2. Метрики с Prometheus

Prometheus — стандарт де-факто для сбора метрик. Мы можем легко добавить эндпоинт `/metrics` в наше FastAPI приложение.

#### Установка
```bash
pip install prometheus-fastapi-instrumentator
```

#### Реализация

`src/main.py`
```python
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(...)

# ... (middleware)

# Добавляем инструментор Prometheus
Instrumentator().instrument(app).expose(app)

# ... (routers)
```

Теперь, если запустить приложение, по адресу `/metrics` будет доступен эндпоинт с базовыми метриками (задержка запросов, количество и т.д.).

#### Добавление кастомных метрик

```python
# src/services/user_service.py
from prometheus_client import Counter

# Создаем счетчик для созданных пользователей
USERS_CREATED_COUNTER = Counter("users_created_total", "Total number of users created", ["source"])

class UserService:
    # ...
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        # ...
        created_user = await self.user_repository.create(user)
        
        # Увеличиваем счетчик
        USERS_CREATED_COUNTER.labels(source="api").inc()
        
        # ...
        return UserResponse.model_validate(created_user)
```

### 3. Распределенная трассировка с OpenTelemetry

Трассировка позволяет визуализировать полный путь запроса через несколько сервисов. OpenTelemetry — это стандарт для сбора трассировок.

#### Установка
```bash
pip install opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-instrumentation-httpx
```

#### Реализация

Настроим экспорт трассировок в консоль (в реальном проекте это будет Jaeger, Zipkin или другой коллектор).

`src/tracing_config.py`
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

def setup_tracing(app: FastAPI):
    """Настройка распределенной трассировки."""
    # Устанавливаем провайдер трассировок
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    # Настраиваем экспорт в консоль
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)

    # Инструментируем FastAPI приложение
    FastAPIInstrumentor.instrument_app(app)
    
    # Инструментируем HTTPX клиент для проброса заголовков трассировки
    HTTPXClientInstrumentor().instrument()

    print("OpenTelemetry tracing configured.")
```

#### Подключение в `main.py`
```python
from .tracing_config import setup_tracing

app = FastAPI(...)

# ... (middleware)

# Настраиваем трассировку
setup_tracing(app)

# ... (routers)
```

Теперь при каждом запросе к API в консоли будут появляться спаны трассировки. Если из одного сервиса будет сделан HTTP-запрос в другой (также инструментированный), OpenTelemetry автоматически свяжет их в единую трассировку благодаря `HTTPXClientInstrumentor`.
