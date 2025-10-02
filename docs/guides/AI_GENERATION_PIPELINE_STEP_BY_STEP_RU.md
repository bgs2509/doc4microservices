# Пошаговый Пайплайн AI-Генерации Кода

> **НАЗНАЧЕНИЕ**: Полное руководство для разработчиков - как взаимодействовать с AI для генерации production-ready microservices приложений. Документ показывает каждый шаг процесса, что делает AI, какие документы читает, когда задает вопросы.

---

## 📚 Содержание

- [Общая схема процесса](#общая-схема-процесса)
- [Этап 0: Инициализация AI](#этап-0-инициализация-ai)
- [Этап 1: Валидация промпта](#этап-1-валидация-промпта)
- [Этап 2: Сбор требований](#этап-2-сбор-требований)
- [Этап 3: Планирование архитектуры](#этап-3-планирование-архитектуры)
- [Этап 4: Генерация кода](#этап-4-генерация-кода)
- [Этап 5: Проверка качества](#этап-5-проверка-качества)
- [Этап 6: QA отчет и передача](#этап-6-qa-отчет-и-передача)
- [Примеры диалогов](#примеры-диалогов)

---

## Общая схема процесса

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       ПАЙПЛАЙН AI-ГЕНЕРАЦИИ КОДА                        │
│                    (от промпта до production-ready app)                 │
└─────────────────────────────────────────────────────────────────────────┘

    ПОЛЬЗОВАТЕЛЬ                           AI ДЕЙСТВИЯ
    ═══════════                           ═════════════

    Назначает задачу                      [ЭТАП 0]
         │                                Инициализация
         │                                ├─ Читает: CLAUDE.md
         │                                ├─ Читает: AGENT_CONTEXT_SUMMARY.md
         │                                └─ Читает: AI_CODE_GENERATION_MASTER_WORKFLOW.md
         ▼
    Дает промпт                           [ЭТАП 1]
    "Хочу P2P lending..."                 Валидация промпта
         │                                ├─ Читает: PROMPT_VALIDATION_GUIDE.md
         │                    ┌───────────┤
         │                    │           └─ Проверяет обязательные поля
         │                    │
         │            [ПОЛЯ НЕПОЛНЫЕ?]
         │                    │
         ├────────────────────┘
         │ ◄─ "Укажите метод аутентификации..."
         │
         ▼
    Дополняет промпт                      [ЭТАП 2]
    "JWT + 2FA, Stripe..."                Сбор требований
         │                                ├─ Читает: ARCHITECTURE_GUIDE.md
         │                                ├─ Читает: tech_stack.md
         │                                ├─ Читает: atomic/architecture/*
         │                                └─ Генерирует: Requirements Intake документ
         ▼
    Одобряет требования                   [ЭТАП 3]
         │                                Планирование
         │                                ├─ Читает: IMPLEMENTATION_PLAN_TEMPLATE.md
         │                                ├─ Читает: atomic/services/* (нужные сервисы)
         │                                ├─ Читает: atomic/integrations/*
         │                                └─ Генерирует: Implementation Plan (6 фаз)
         ▼
    Одобряет план                         [ЭТАП 4]
         │                                Генерация кода (6 подэтапов)
         │                                ├─ 4.1: Infrastructure (Docker, Makefiles)
         │                                ├─ 4.2: Data Layer (PostgreSQL, MongoDB services)
         │                                ├─ 4.3: Business Logic (FastAPI, use cases)
         │                                ├─ 4.4: Workers (background jobs)
         │                                ├─ 4.5: Telegram Bot (handlers, notifications)
         │                                └─ 4.6: Testing (unit, integration, e2e)
         │
         │                                [ЭТАП 5]
         │                                Проверка качества
         │                                ├─ Читает: AGENT_VERIFICATION_CHECKLIST.md
         │                                ├─ Запускает: ruff, mypy, bandit, pytest
         │                                └─ Генерирует: Coverage reports, checklist
         │
         │                    ┌───────────┤
         │                    │           └─ Все проверки OK?
         │            [ТЕСТЫ ФЕЙЛЯТ?]
         │                    │
         └────────────────────┘
              (возврат к Этапу 4)

         ▼
    Получает QA отчет                     [ЭТАП 6]
         │                                QA отчет и передача
         │                                ├─ Читает: QA_REPORT_TEMPLATE.md
         │                                ├─ Генерирует: Финальный QA отчет
         │                                ├─ Генерирует: Deployment guide
         │                                └─ Обновляет: DELIVERABLES_CATALOG.md
         ▼
    ✅ Production-Ready App
```

---

## Этап 0: Инициализация AI

### 🎯 Что происходит

AI начинает работу с загрузки контекста фреймворка **ДО** того как получит промпт от пользователя.

### 📖 Документы которые читает AI

1. **`CLAUDE.md`** (корень проекта)
   - Точка входа
   - Навигация по документации
   - Обзор фреймворка

2. **`docs/reference/AGENT_CONTEXT_SUMMARY.md`**
   - Критические правила (snapshot)
   - Обязательные ограничения архитектуры
   - Быстрая ориентация

3. **`docs/guides/AI_CODE_GENERATION_MASTER_WORKFLOW.md`**
   - Полный 7-этапный процесс
   - Детальные инструкции
   - Примеры

### 🧠 Что узнает AI

После чтения этих документов AI понимает:

✅ **Архитектуру**: Improved Hybrid Approach
✅ **Ограничения**: HTTP-only data access (бизнес-сервисы НЕ обращаются к БД напрямую)
✅ **Разделение сервисов**: FastAPI, Aiogram, AsyncIO workers в отдельных процессах
✅ **Обязательные компоненты**: PostgreSQL, MongoDB, Redis, RabbitMQ, Nginx
✅ **Где искать информацию**: Навигация по 157 atomic документам

### 🚫 Чего AI НЕ делает

- ❌ НЕ читает все 157 документов сразу (только on-demand)
- ❌ НЕ генерирует код
- ❌ НЕ взаимодействует с пользователем

### ⏱️ Длительность

~2-3 минуты (чтение 3 документов, ~700 строк)

### ✅ Критерий завершения

AI загрузил полный контекст фреймворка и готов к получению промпта.

---

## Этап 1: Валидация промпта

### 🎯 Что происходит

Пользователь дает начальный промпт. AI проверяет его на полноту **ПЕРЕД** началом любой работы.

### 📖 Документы которые читает AI

1. **`docs/guides/PROMPT_VALIDATION_GUIDE.md`**
   - Чеклист обязательных полей
   - Примеры полных и неполных промптов

2. **`docs/reference/PROMPT_TEMPLATES.md`** (если нужно уточнение)
   - Шаблоны вопросов для пользователя
   - Форматы уточнений

### 🔍 Что проверяет AI

AI проверяет наличие **9 обязательных полей**:

| Поле | Пример | Обязательно |
|------|--------|-------------|
| **Бизнес-контекст** | "Проблема: пользователям нужен P2P lending" | ✅ ДА |
| **Функциональные требования** | "Создание займов, оплата через Stripe" | ✅ ДА |
| **Нефункциональные ограничения** | "< 200ms latency, 99.9% uptime" | ✅ ДА |
| **🆕 Целевой уровень зрелости** | "Level 3 - Pre-Production (~15 min)" | ✅ ДА |
| **🆕 Опциональные модули** | "Workers, Bot" или "None" | ✅ ДА |
| **Зависимости и интеграции** | "Stripe, Twilio, Onfido KYC" | ✅ ДА |
| **Границы scope** | "Без вторичного рынка займов (v1)" | ✅ ДА |
| **Ожидаемые deliverables** | "Код, тесты, Docker configs, API docs" | ✅ ДА |
| **Критерии приемки** | "Coverage ≥ 80%, все тесты OK" | ✅ ДА |

### 🎚️ Выбор уровня зрелости (Maturity Level)

**ВАЖНО**: AI спрашивает пользователя выбрать уровень зрелости, который определяет сложность и время генерации:

| Уровень | Название | Время | Что включено | Кому подходит |
|---------|----------|-------|--------------|---------------|
| **1** | 🧪 PoC (Proof of Concept) | ~5 мин | Только core: FastAPI + PostgreSQL + Docker. Без логирования, метрик, Nginx, SSL. | MVP, demo, обучение |
| **2** | 🛠️ Development Ready | ~10 мин | + Структурированное логирование, health checks, error tracking | Активная разработка, staging |
| **3** | 🚀 Pre-Production | ~15 мин | + Nginx, SSL, Prometheus метрики, rate limiting | Публичная beta, малый production |
| **4** | 🏢 Production | ~30 мин | + OAuth/JWT, RBAC, ELK Stack, tracing, CI/CD, HA, backups | Enterprise, compliance |

**Опциональные модули** (доступны на любом уровне):
- Background Workers (AsyncIO)
- Telegram Bot (Aiogram)
- MongoDB (NoSQL database)
- RabbitMQ (event messaging)
- Redis (caching)
- File Storage (S3/MinIO)
- Real-Time (WebSockets)

📖 **Подробнее**: См. `docs/reference/MATURITY_LEVELS.md`

### 🤖 Действия AI

#### Вариант A: Промпт ПОЛНЫЙ

```markdown
✅ Prompt Validation: COMPLETE

Все обязательные поля присутствуют. Переход к Stage 2 (Requirements Intake).
```

AI **автоматически** переходит к Этапу 2.

#### Вариант B: Промпт НЕПОЛНЫЙ

```markdown
⚠️ Prompt Validation: INCOMPLETE

Отсутствуют обязательные поля:

❌ **Метод аутентификации**: JWT, OAuth2, magic links?
❌ **Payment gateway**: Stripe, PayPal, cryptocurrency?
❌ **Масштаб**: Ожидаемое количество пользователей в 1-й год?
❌ **Compliance**: GDPR, FCA, AML требования?

Пожалуйста, дополните промпт этими деталями.
```

AI **останавливается** и ждет ответа пользователя.

### 👤 Взаимодействие с пользователем

**Момент диалога**: Сразу после получения первого промпта

**Пример неполного промпта от пользователя**:
```
Хочу создать P2P lending платформу где пользователи могут:
- Давать займы друг другу
- Создавать заявки на займ
- Делать платежи с автоматическим расчетом процентов
- Отслеживать кредитный рейтинг
- Получать уведомления в Telegram
```

**Ответ AI**:
```markdown
## 🔍 Валидация промпта: Требуется дополнительная информация

Ваша бизнес-идея понятна, но для архитектурного планирования мне нужны детали:

### ❓ Недостающая информация:

**1. Аутентификация и безопасность:**
   - Как пользователи будут входить? (JWT токены, OAuth2, magic links?)
   - Нужна ли двухфакторная аутентификация (2FA)?
   - KYC/AML compliance требования?

**2. Обработка платежей:**
   - Какой payment gateway использовать? (Stripe, PayPal, bank transfer, crypto?)
   - Автоматические платежи или вручную?
   - Нужен ли escrow сервис?

**3. Масштаб и производительность:**
   - Сколько пользователей ожидаете в 1-й год? (100, 1K, 10K, 100K?)
   - Сколько транзакций в день? (10, 100, 1K?)
   - Географические регионы? (одна страна, worldwide?)

**4. Уведомления:**
   - Только Telegram или также email/SMS?
   - Частота уведомлений?

**5. Регулирование и compliance:**
   - Какие страны/регионы? (для определения legal requirements)
   - Сроки хранения данных?
   - GDPR compliance нужен?

**6. Кредитный скоринг:**
   - Использовать внешний API или внутренний алгоритм?
   - Какие факторы влияют на кредитоспособность?

### 📝 Как ответить:

Можете ответить в любом формате. Например:

```
1. JWT + 2FA через SMS, базовая KYC (проверка ID)
2. Stripe, автоматические ежемесячные платежи, да escrow
3. Цель 1K пользователей в 1-й год, ~50 транзакций/день, только EU
4. Telegram для срочных, email для дайджестов
5. EU + UK regulations, 7 лет хранение данных, да GDPR
6. Внутренний алгоритм: история платежей, отношение займа к доходу, возраст аккаунта
```

Или опишите своими словами - я извлеку детали.
```

**Пользователь дополняет промпт**:
```
1. JWT + 2FA через SMS, базовая KYC (сканирование государственного ID)
2. Stripe, автоматические ежемесячные платежи, escrow держит платформа
3. Начать с 1K пользователей, 50 займов/день, EU + UK
4. Telegram для мгновенных алертов, email для дневных сводок
5. EU GDPR + FCA регуляции (UK), 7-летнее хранение
6. Внутренний скоринг: история платежей (50%), loan/income ratio (30%), возраст аккаунта (20%)
7. Да marketplace, automated matching в v2, без вторичного рынка
```

**AI подтверждает**:
```markdown
✅ Validation Complete

Все обязательные поля теперь присутствуют. Переход к Stage 2 (Requirements Clarification & Intake).
```

### ⏱️ Длительность

- Если промпт полный: ~1 минута (валидация)
- Если неполный: ждет ответа пользователя (может быть часы/дни)

### ✅ Критерий завершения

Все 7 обязательных полей присутствуют в промпте.

---

## Этап 2: Сбор требований

### 🎯 Что происходит

AI анализирует промпт на соответствие архитектуре фреймворка и создает структурированный Requirements Intake документ.

### 📖 Документы которые читает AI

1. **Архитектурные документы**:
   - `docs/guides/ARCHITECTURE_GUIDE.md` — проверка совместимости
   - `docs/atomic/architecture/improved-hybrid-overview.md`
   - `docs/atomic/architecture/service-separation-principles.md`
   - `docs/atomic/architecture/data-access-architecture.md`

2. **Технические спецификации**:
   - `docs/reference/tech_stack.md` — версии технологий

3. **Шаблоны**:
   - `docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md`

### 🔍 Что анализирует AI

#### 1. **Проверка архитектурной совместимости**

AI проверяет:
```
✅ Подходит ли бизнес-идея под Improved Hybrid Approach?
✅ Можно ли использовать PostgreSQL + MongoDB?
✅ Нужен ли FastAPI сервис? (REST API)
✅ Нужен ли Telegram bot сервис? (уведомления)
✅ Нужны ли background workers? (платежи, скоринг)
✅ Есть ли архитектурные конфликты?
```

#### 2. **Маппинг на типы сервисов**

AI определяет какие сервисы нужны:

| Тип сервиса | Зачем нужен | Пример для P2P lending |
|-------------|-------------|------------------------|
| **FastAPI** (Port 8000) | REST API для web/mobile клиентов | Endpoints для создания займов, платежей |
| **Telegram Bot** | Уведомления пользователей | Алерты о новых займах, платежах |
| **AsyncIO Worker** | Background обработка | Расчет процентов, кредитный скоринг |
| **PostgreSQL Service** (Port 8001) | Транзакционные данные (ACID) | Users, loans, payments, transactions |
| **MongoDB Service** (Port 8002) | Аналитика и audit logs | User activity, audit trail, analytics |

#### 3. **Маппинг на инфраструктуру**

AI определяет компоненты:

```
✅ PostgreSQL 16 — transactional data
✅ MongoDB 7 — analytics, audit logs
✅ Redis 7 — session management, rate limiting, cache
✅ RabbitMQ 3 — event-driven workflows (loan.created, payment.processed)
✅ Nginx — API Gateway (TLS, load balancing, rate limiting)
```

### 🤖 Действия AI

#### Шаг 1: Чтение архитектурных правил

AI читает `ARCHITECTURE_GUIDE.md` и проверяет **MANDATORY constraints**:

```
✅ Data Access: Business services MUST use HTTP-only (no direct DB)
✅ Service Separation: FastAPI + Aiogram in separate containers
✅ Event Loop: Each service type in separate process
✅ Messaging: RabbitMQ for async communication
```

#### Шаг 2: Создание Requirements Intake документа

AI заполняет шаблон `REQUIREMENTS_INTAKE_TEMPLATE.md`:

```markdown
# Requirements Intake: P2P Lending Platform

**Generated:** 2025-10-01
**Framework:** doc4microservices v1.0

## 1. Business Context & Objectives

**Problem Statement:**
Users need a peer-to-peer lending platform with transparent terms and automated payment processing.

**Target Users:**
- **Borrowers**: Create loan requests, receive funds, make payments
- **Lenders**: Browse marketplace, fund loans, receive repayments + interest
- **Admins**: Platform management, dispute resolution, KYC review

**Success Metrics:**
- 1,000 users in year 1
- 50 loans/day
- API latency < 200ms (p95)
- 99.9% uptime

## 2. Functional Requirements

| Feature | Priority | Description | Acceptance Criteria |
|---------|----------|-------------|---------------------|
| User registration with KYC | Must | Government ID verification via Onfido | User can complete KYC in < 5 min |
| Loan marketplace | Must | Browse/search available loans | Filters by amount, term, interest rate |
| Loan creation | Must | Borrowers create loan requests | Max 3 active loans per borrower |
| Automated payments | Must | Monthly payments via Stripe | Webhook handling, retry logic |
| Credit scoring | Must | Internal algorithm (3 factors) | Updated after each payment |
| Telegram notifications | Must | Instant alerts for critical events | Delivery within 1 second |
| Email digest | Should | Daily summary for lenders | Sent at 9 AM user timezone |

## 3. Non-Functional Constraints

**Performance:**
- API response time: < 200ms (p95)
- Uptime SLA: 99.9%
- Max concurrent users: 1,000

**Security:**
- Authentication: JWT tokens + refresh tokens
- 2FA: SMS via Twilio
- HTTPS only (TLS 1.3)
- Data encryption at rest (PostgreSQL encryption)
- PII anonymization in logs
- Rate limiting: 100 requests/min per user

**Compliance:**
- GDPR (EU): Right to access, deletion, data portability
- FCA (UK): Anti-money laundering checks
- Data retention: 7 years for financial transactions
- Audit trail: All financial operations logged to MongoDB

**Architecture Alignment:**
- ✅ CONFIRMED: Improved Hybrid Approach compatible
- ✅ HTTP-only data access enforced
- ✅ Service separation (FastAPI, Aiogram, Workers separate)
- ✅ Event-driven with RabbitMQ

## 4. Architecture Mapping

### Services Needed:

| Service | Type | Port | Purpose |
|---------|------|------|---------|
| `api_service` | FastAPI | 8000 | REST API for web/mobile clients |
| `bot_service` | Aiogram | - | Telegram notifications and commands |
| `worker_service` | AsyncIO | - | Payment processing, credit scoring |
| `db_postgres_service` | Data Service | 8001 | Users, loans, payments, escrow (PostgreSQL) |
| `db_mongo_service` | Data Service | 8002 | Audit logs, analytics (MongoDB) |

### Infrastructure:

```
PostgreSQL 16  → Transactional data (ACID compliance)
MongoDB 7      → Analytics and audit logs
Redis 7        → Session management, rate limiting, cache
RabbitMQ 3     → Event-driven workflows
Nginx          → API Gateway (TLS, load balancing, rate limiting)
```

### Data Model (Preliminary):

**PostgreSQL tables:**
- `users` (id, email, password_hash, kyc_status, credit_score, created_at)
- `loans` (id, borrower_id, amount, duration, interest_rate, status, created_at)
- `payments` (id, loan_id, amount, due_date, paid_date, status)
- `escrow_accounts` (id, loan_id, balance, status)

**MongoDB collections:**
- `user_activities` (user actions, timestamps, IP addresses)
- `audit_logs` (all financial operations with full context)
- `credit_score_history` (snapshots of credit score calculations)

### API Endpoints (Preliminary):

**Authentication:**
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh-token
- POST /api/v1/auth/verify-2fa

**Loans:**
- GET /api/v1/loans (marketplace)
- POST /api/v1/loans (create loan request)
- GET /api/v1/loans/{id}
- POST /api/v1/loans/{id}/apply (lender applies)
- POST /api/v1/loans/{id}/approve (borrower approves lender)

**Payments:**
- GET /api/v1/payments (user's payment schedule)
- POST /api/v1/payments/{id}/pay (manual payment)

**Users:**
- GET /api/v1/users/profile
- PUT /api/v1/users/profile
- GET /api/v1/users/credit-score
- POST /api/v1/users/kyc-upload

### Events (RabbitMQ):

| Event | Trigger | Consumers |
|-------|---------|-----------|
| `user.registered` | User completes registration | Worker (send KYC email, create initial credit score) |
| `loan.created` | Borrower creates loan request | Bot (notify potential lenders) |
| `loan.funded` | Lender funds loan | Worker (transfer from escrow), Bot (notify borrower) |
| `payment.due` | Payment due date approaching | Worker + Bot (send reminder) |
| `payment.received` | Payment processed | Worker (update loan balance, recalc credit score) |
| `payment.overdue` | Payment overdue | Worker (adjust credit score), Bot (send alert) |

### External Integrations:

| Integration | Purpose | API/SDK |
|-------------|---------|---------|
| **Stripe** | Payment processing | Stripe Python SDK |
| **Telegram Bot API** | Notifications and commands | aiogram 3.x |
| **Twilio** | SMS for 2FA | Twilio Python SDK |
| **Onfido** | KYC verification | Onfido API |
| **SendGrid or AWS SES** | Email notifications | SendGrid/SES SDK |

## 5. Scope Boundaries

**In Scope (v1):**
- User registration with KYC
- Loan marketplace
- Automated payments via Stripe
- Credit scoring (internal algorithm)
- Telegram + email notifications
- Admin panel (basic)

**Out of Scope (v1):**
- Automated loan matching algorithm (planned for v2)
- Secondary market for loan contracts
- Mobile apps (web-first)
- Multi-currency support (EUR only in v1)
- Social features (borrower profiles, reviews)

## 6. Expected Deliverables

**Code:**
- 5 microservices (FastAPI, Aiogram, Worker, PostgreSQL, MongoDB)
- Docker Compose configurations (dev + prod)
- Nginx configurations

**Configuration:**
- `.env.example` with all required variables
- `Makefile` for development commands
- Alembic migrations

**Documentation:**
- README.md with setup instructions
- API documentation (OpenAPI/Swagger)
- Architecture Decision Records (ADRs) for major decisions

**Testing:**
- Unit tests (coverage ≥ 80%)
- Integration tests (with testcontainers)
- End-to-end tests

## 7. Acceptance Criteria

**Functional:**
- ✅ User can register and complete KYC
- ✅ Borrower can create loan request (max 3 active)
- ✅ Lender can browse marketplace and fund loan
- ✅ Payments processed automatically via Stripe
- ✅ Credit score updates after each payment
- ✅ Telegram notifications delivered within 1 second

**Quality:**
- ✅ Linting (Ruff): 0 errors
- ✅ Type checking (Mypy): 0 errors
- ✅ Security scan (Bandit): 0 high severity issues
- ✅ Tests: All pass
- ✅ Coverage: ≥ 80%

**Performance:**
- ✅ API response time: < 200ms (p95)
- ✅ Database queries optimized (indexes, EXPLAIN ANALYZE)

**Deployment:**
- ✅ `docker-compose up` starts all services
- ✅ Health checks pass for all services
- ✅ Migrations apply successfully

## 8. Risks & Open Questions

| Risk | Impact | Mitigation |
|------|--------|------------|
| Stripe API downtime | High | Implement retry logic + fallback to manual payment |
| KYC provider slow response | Medium | Queue KYC requests, async processing |
| Payment defaults | High | Escrow + credit scoring + max loan limits |
| GDPR violation | Critical | Regular audits + automated PII detection in logs |

**Open Questions:**
- [ ] Borrower income verification method?
- [ ] Dispute resolution process workflow?
- [ ] Automated matching algorithm details (v2)?

## 9. Next Steps

1. **Review this document** - Confirm/adjust requirements
2. **Approve** - Reply "APPROVED" to proceed to Implementation Planning
3. **Adjust** - Provide corrections/additions if needed

---

**Status:** Awaiting user approval
```

### 👤 Взаимодействие с пользователем

**Момент диалога**: После создания Requirements Intake документа

**AI отправляет пользователю**:
```markdown
## 📄 Requirements Intake Document сгенерирован

Я создал полный документ требований на основе вашего промпта.

**Ключевые моменты:**
- 5 микросервисов (API, Bot, Worker, PostgreSQL, MongoDB)
- 4 core entities (Users, Loans, Payments, Escrow)
- 15 API endpoints
- 6 типов событий (RabbitMQ)
- 4 внешние интеграции (Stripe, Telegram, Email, KYC)

### 📋 Пожалуйста, проверьте:

1. **Data Model** - покрывает ли вашу бизнес-логику?
2. **API Endpoints** - есть ли пропущенные user workflows?
3. **Events** - правильные ли триггеры?
4. **Open Questions** - нужны ответы для полной реализации

**Действие:**
- Ответьте "APPROVED" для перехода к Implementation Planning
- Или укажите коррекции/дополнения

[Full requirements document above]
```

**Пример ответа пользователя**:
```
APPROVED. Но добавьте: borrowers могут иметь несколько активных займов (макс 3)
```

**AI подтверждает**:
```markdown
✅ Requirements Updated

Добавлено ограничение: max 3 active loans per borrower.

Переход к Stage 3 (Architecture Mapping & Planning).
```

### ⏱️ Длительность

- Чтение документов: ~5 минут
- Генерация Requirements Intake: ~3 минуты
- Ожидание approval от пользователя: варьируется

### ✅ Критерий завершения

Requirements Intake документ одобрен пользователем, нет архитектурных конфликтов.

---

## Этап 3: Планирование архитектуры

### 🎯 Что происходит

AI создает детальный Implementation Plan с разбивкой на фазы, задачи, DoD (Definition of Done) и риски.

### 📖 Документы которые читает AI

1. **Шаблоны планирования**:
   - `docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md`
   - `docs/guides/USE_CASE_IMPLEMENTATION_GUIDE.md`

2. **Service-specific atomic docs** (зависит от нужных сервисов):
   - Если нужен FastAPI → читает `docs/atomic/services/fastapi/*`
   - Если нужен Aiogram → читает `docs/atomic/services/aiogram/*`
   - Если нужны Workers → читает `docs/atomic/services/asyncio-workers/*`
   - Всегда читает `docs/atomic/services/data-services/*`

3. **Integration atomic docs**:
   - `docs/atomic/integrations/redis/*`
   - `docs/atomic/integrations/rabbitmq/*`
   - `docs/atomic/integrations/http-communication/*`

4. **Tooling**:
   - `docs/reference/AGENT_TOOLBOX.md` (команды для валидации)

### 🔍 Что планирует AI

AI создает план из **6 фаз**:

#### **Phase 1: Infrastructure Setup** (Week 1)
```
Duration: 3 days

Tasks:
1. Project initialization
   - Create repo structure per PROJECT_STRUCTURE.md
   - Copy Docker Compose from templates
   - Configure .env
   - DoD: docker-compose up succeeds, all containers healthy

2. Service scaffolding
   - Generate 5 services (api, bot, worker, db_postgres, db_mongo)
   - Follow docs/atomic/services/*/basic-setup.md
   - DoD: All services respond to health checks
```

#### **Phase 2: Data Layer** (Week 2)
```
Duration: 5 days

Tasks:
1. PostgreSQL data service
   - SQLAlchemy models (User, Loan, Payment, Escrow)
   - Repositories (CRUD + active_loans_count)
   - HTTP API endpoints
   - Alembic migrations
   - DoD: curl localhost:8001/health → 200 OK

2. MongoDB data service
   - Motor models (AuditLog, CreditScoreHistory)
   - Repositories
   - HTTP API endpoints
   - DoD: curl localhost:8002/health → 200 OK
```

#### **Phase 3: Business Logic** (Week 3-4)
```
Duration: 7 days

Tasks:
1. Authentication (3 days)
   - JWT handler
   - 2FA via Twilio
   - User registration/login endpoints

2. Loans management (4 days)
   - Create loan use case (with max 3 active validation)
   - Marketplace (search/filter)
   - Loan application workflow
   - Loan approval workflow

3. Payments (3 days)
   - Payment schedule generation
   - Stripe integration
   - Webhook handling
```

#### **Phase 4: Background Workers** (Week 5)
```
Duration: 4 days

Tasks:
1. Credit score worker
   - Algorithm implementation
   - Event subscribers (payment.received, payment.overdue)

2. Payment reminder worker
   - Daily job (fetch due payments)
   - Send Telegram + email
```

#### **Phase 5: Telegram Bot** (Week 5)
```
Duration: 2 days

Tasks:
1. Bot commands (/start, /balance, /loans, /score)
2. Notification listeners (loan.created, payment.due)
```

#### **Phase 6: Testing & Quality** (Week 6)
```
Duration: 6 days

Tasks:
1. Unit tests (all layers)
2. Integration tests (testcontainers)
3. End-to-end tests
4. Security audit (Bandit)
5. Load testing (Locust)
```

### 🤖 Действия AI

AI генерирует Implementation Plan документ:

```markdown
# Implementation Plan: P2P Lending Platform

**Estimated Duration:** 6 weeks (1 developer)
**Plan Version:** 1.0
**Date:** 2025-10-01

## Summary

**Objective:** Build production-ready P2P lending platform with automated payments, credit scoring, and Telegram notifications.

**Approach:** Improved Hybrid Approach with centralized data services, HTTP-only data access, event-driven architecture.

**Key Assumptions:**
- Using framework templates (80% infrastructure ready)
- Following atomic documentation patterns
- External APIs available (Stripe, Onfido, Twilio)

## Architecture Impact

| Area | Changes | Relevant Docs |
|------|---------|---------------|
| Services | 5 new services (API, Bot, Worker, 2x Data) | `atomic/services/**/*.md` |
| Data access | HTTP-only from business services | `atomic/architecture/data-access-architecture.md` |
| Messaging | RabbitMQ for 6 event types | `atomic/integrations/rabbitmq/*.md` |
| Security | JWT + 2FA, HTTPS, encryption | `atomic/services/fastapi/security-patterns.md` |
| Compliance | GDPR + FCA requirements | Custom implementation in business logic |

## Work Plan

[... 6 phases with detailed tasks as shown above ...]

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation | Owner |
|------|--------|------------|------------|-------|
| Stripe test API rate limits | Medium | Medium | Use mock in tests, real API in integration | AI |
| KYC provider downtime | High | Low | Queue + retry logic, fallback to manual review | AI |
| Complex credit scoring | Medium | Medium | Start with simple algorithm, iterate | User + AI |
| GDPR compliance complexity | Critical | Medium | Follow atomic patterns, regular audits | AI |

## Verification Strategy

**Linting & Formatting:**
```bash
uv run ruff check .
uv run ruff format . --check
```

**Type Checking:**
```bash
uv run mypy .
```

**Security:**
```bash
uv run bandit -r .
```

**Testing:**
```bash
uv run pytest --cov=services --cov-report=html --cov-report=xml
```

**Coverage Target:** ≥ 80%

## Deliverables & Acceptance

**Expected Artifacts:**
- Source code (5 services)
- Docker Compose configurations
- API documentation (OpenAPI)
- Test suite + coverage reports
- Deployment guide
- ADRs (if architectural decisions made)

**Acceptance Criteria:**
- All functional requirements implemented
- All quality gates pass (ruff, mypy, bandit, pytest)
- Coverage ≥ 80%
- API latency < 200ms (p95)
- All services healthy in docker-compose

## Dependencies & Schedule

**External Dependencies:**
- Stripe test account (Week 1)
- Telegram bot token (Week 1)
- Onfido sandbox account (Week 2)
- Twilio account (Week 3)

**Milestones:**
- Week 1: Infrastructure ready
- Week 2: Data layer complete
- Week 4: Core business logic working
- Week 5: Background jobs + bot functional
- Week 6: All tests pass, ready for deployment

---

**Status:** Awaiting approval to start Phase 1
```

### 👤 Взаимодействие с пользователем

**Момент диалога**: После создания Implementation Plan

**AI отправляет**:
```markdown
## 📊 Implementation Plan готов

Создан детальный план из 6 фаз (6 недель).

**Ключевые добавления:**
- ✅ Добавлена валидация: max 3 active loans per borrower
- ✅ Новый endpoint: GET /loans/{id}/active-count
- ✅ Бизнес-правило в create_loan.py use case

**Структура плана:**
- **Phase 1**: Infrastructure (1 week)
- **Phase 2**: Data layer (1 week)
- **Phase 3**: Business logic (2 weeks)
- **Phase 4**: Workers (1 week)
- **Phase 5**: Telegram bot (1 week)
- **Phase 6**: Testing & deployment (1 week)

**Итого:** 22 developer-days

### 🎯 Следующие действия:

1. **Просмотрите план** - Нужны корректировки?
2. **Подтвердите timeline** - 6 недель приемлемо?
3. **Одобрите** - Ответьте "START PHASE 1" для начала реализации

Или задайте вопросы по любой фазе.
```

**Пример ответа пользователя**:
```
START PHASE 1
```

**AI подтверждает**:
```markdown
✅ Plan Approved

Начинаю Phase 1: Infrastructure Setup.

Переход к Stage 4 (Code Generation).
```

### ⏱️ Длительность

- Чтение atomic docs: ~10 минут (только нужные сервисы)
- Создание Implementation Plan: ~7 минут
- Ожидание approval: варьируется

### ✅ Критерий завершения

Implementation Plan одобрен пользователем, все фазы определены с DoD.

---

## Этап 4: Генерация кода

### 🎯 Что происходит

AI генерирует код **поэтапно** (6 подэтапов), следуя Implementation Plan. После каждого подэтапа проводится валидация.

### 📖 Документы которые читает AI

AI читает документы **on-demand** для текущего подэтапа.

#### **Подэтап 4.1: Infrastructure**

Читает:
- `docs/atomic/infrastructure/containerization/docker-compose-setup.md`
- `docs/atomic/infrastructure/containerization/dockerfile-patterns.md`
- `docs/atomic/infrastructure/configuration/environment-variables.md`

Генерирует:
- `docker-compose.yml`
- `docker-compose.dev.yml`
- `docker-compose.prod.yml`
- `.env.example`
- `Makefile`
- `services/*/Dockerfile`

Валидация:
```bash
docker-compose up -d
docker-compose ps  # All services "healthy"
```

#### **Подэтап 4.2: Data Layer**

Читает:
- `docs/atomic/services/data-services/postgres-service-setup.md`
- `docs/atomic/services/data-services/repository-patterns.md`
- `docs/atomic/services/data-services/http-api-design.md`
- `docs/atomic/databases/postgresql/sqlalchemy-integration.md`

Генерирует (PostgreSQL service):
```python
# services/db_postgres_service/src/models/user.py
"""User SQLAlchemy model."""
from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.sql import func
from .base import Base

class User(Base):
    """User entity with KYC and credit scoring."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    kyc_status = Column(String(20), default="pending")  # pending, approved, rejected
    credit_score = Column(Integer, default=0)
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

```python
# services/db_postgres_service/src/repositories/user_repository.py
"""User repository with CRUD operations."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from ..models.user import User

class UserRepository:
    """Repository for User entity."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: dict) -> User:
        """Create new user."""
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def update_credit_score(self, user_id: str, score: int) -> User:
        """Update user credit score."""
        user = await self.get_by_id(user_id)
        if user:
            user.credit_score = score
            await self.session.commit()
            await self.session.refresh(user)
        return user
```

```python
# services/db_postgres_service/src/api/v1/users_router.py
"""Users HTTP API router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from ...database import get_session
from ...repositories.user_repository import UserRepository

router = APIRouter(prefix="/users", tags=["users"])

class CreateUserRequest(BaseModel):
    """Create user request schema."""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """User response schema."""
    id: str
    email: str
    kyc_status: str
    credit_score: int
    created_at: str

    class Config:
        from_attributes = True

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    session: AsyncSession = Depends(get_session)
):
    """Create new user (HTTP endpoint for business services)."""
    repo = UserRepository(session)

    # Check if email already exists
    existing = await repo.get_by_email(request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password (simplified for example)
    import hashlib
    password_hash = hashlib.sha256(request.password.encode()).hexdigest()

    # Create user
    user = await repo.create({
        "id": str(uuid.uuid4()),
        "email": request.email,
        "password_hash": password_hash,
        "kyc_status": "pending",
        "credit_score": 0
    })

    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_session)
):
    """Get user by ID (HTTP endpoint for business services)."""
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

Валидация:
```bash
curl http://localhost:8001/health
# Returns: {"status":"ok","database":"connected"}
```

#### **Подэтап 4.3: Business Logic (FastAPI)**

Читает:
- `docs/atomic/services/fastapi/routing-patterns.md`
- `docs/atomic/services/fastapi/dependency-injection.md`
- `docs/atomic/architecture/ddd-hexagonal-principles.md`
- `docs/atomic/integrations/http-communication/business-to-data-calls.md`

Генерирует:

**Domain layer**:
```python
# services/api_service/src/domain/entities/loan.py
"""Loan domain entity with business rules."""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

@dataclass
class Loan:
    """Loan aggregate root."""
    id: str
    borrower_id: str
    amount: Decimal
    duration_months: int
    interest_rate: Decimal
    status: str  # "pending", "active", "completed", "defaulted"
    created_at: datetime

    def validate_creation(self, borrower_active_loans: int) -> None:
        """Validate loan creation business rules."""
        # Rule 1: Max 3 active loans per borrower
        if borrower_active_loans >= 3:
            raise ValueError("Borrower cannot have more than 3 active loans")

        # Rule 2: Amount limits
        if self.amount < Decimal("100") or self.amount > Decimal("50000"):
            raise ValueError("Loan amount must be between €100 and €50,000")

        # Rule 3: Duration limits
        if self.duration_months < 1 or self.duration_months > 60:
            raise ValueError("Loan duration must be between 1 and 60 months")
```

**Application layer**:
```python
# services/api_service/src/application/use_cases/create_loan.py
"""Create loan use case with business logic."""
from decimal import Decimal
from datetime import datetime
import uuid

from ...domain.entities.loan import Loan
from ...infrastructure.http_clients.postgres_client import PostgresHTTPClient
from ...infrastructure.rabbitmq.event_publisher import EventPublisher

class CreateLoanUseCase:
    """Business logic for creating a loan request."""

    def __init__(
        self,
        postgres_client: PostgresHTTPClient,
        event_publisher: EventPublisher
    ):
        self.postgres_client = postgres_client
        self.event_publisher = event_publisher

    async def execute(self, borrower_id: str, amount: Decimal, duration: int) -> Loan:
        """
        Create a loan request.

        Business rules:
        1. Borrower must have KYC approved
        2. Borrower can have max 3 active loans
        3. Amount must be within limits
        """
        # Step 1: Fetch borrower via HTTP (NO DIRECT DB ACCESS!)
        borrower = await self.postgres_client.get_user(borrower_id)

        # Step 2: Validate KYC status
        if borrower["kyc_status"] != "approved":
            raise ValueError("KYC must be approved before creating a loan")

        # Step 3: Check active loans limit (HTTP call to data service)
        active_count = await self.postgres_client.count_active_loans(borrower_id)

        # Step 4: Create loan entity
        loan = Loan(
            id=str(uuid.uuid4()),
            borrower_id=borrower_id,
            amount=amount,
            duration_months=duration,
            interest_rate=Decimal("0.05"),  # 5% default, can be customized
            status="pending",
            created_at=datetime.utcnow()
        )

        # Step 5: Validate business rules (domain logic)
        loan.validate_creation(active_count)

        # Step 6: Persist via HTTP to data service
        loan_dict = await self.postgres_client.create_loan({
            "id": loan.id,
            "borrower_id": loan.borrower_id,
            "amount": str(loan.amount),
            "duration_months": loan.duration_months,
            "interest_rate": str(loan.interest_rate),
            "status": loan.status,
            "created_at": loan.created_at.isoformat()
        })

        # Step 7: Publish event to RabbitMQ
        await self.event_publisher.publish("loan.created", {
            "loan_id": loan.id,
            "borrower_id": loan.borrower_id,
            "amount": str(loan.amount),
            "timestamp": datetime.utcnow().isoformat()
        })

        return Loan(**loan_dict)
```

**Infrastructure layer** (HTTP client):
```python
# services/api_service/src/infrastructure/http_clients/postgres_client.py
"""HTTP client for PostgreSQL data service (NO DIRECT DB!)."""
import httpx
from typing import Dict, List, Optional

class PostgresHTTPClient:
    """Client for calling PostgreSQL data service via HTTP."""

    def __init__(self, base_url: str):
        self.base_url = base_url  # http://db_postgres_service:8001
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_user(self, user_id: str) -> Dict:
        """Get user by ID via HTTP."""
        response = await self.client.get(f"{self.base_url}/users/{user_id}")
        response.raise_for_status()
        return response.json()

    async def count_active_loans(self, borrower_id: str) -> int:
        """Count active loans for borrower via HTTP."""
        response = await self.client.get(
            f"{self.base_url}/loans/count",
            params={"borrower_id": borrower_id, "status": "active"}
        )
        response.raise_for_status()
        return response.json()["count"]

    async def create_loan(self, loan_data: Dict) -> Dict:
        """Create loan via HTTP."""
        response = await self.client.post(
            f"{self.base_url}/loans",
            json=loan_data
        )
        response.raise_for_status()
        return response.json()
```

**API layer**:
```python
# services/api_service/src/api/v1/loans_router.py
"""Loans API router."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from decimal import Decimal

from ...application.use_cases.create_loan import CreateLoanUseCase
from ...infrastructure.dependencies import get_create_loan_use_case, get_current_user_id

router = APIRouter(prefix="/api/v1/loans", tags=["loans"])

class CreateLoanRequest(BaseModel):
    """Create loan request schema."""
    amount: Decimal
    duration_months: int

class LoanResponse(BaseModel):
    """Loan response schema."""
    id: str
    borrower_id: str
    amount: Decimal
    duration_months: int
    interest_rate: Decimal
    status: str
    created_at: str

@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
async def create_loan(
    request: CreateLoanRequest,
    user_id: str = Depends(get_current_user_id),
    use_case: CreateLoanUseCase = Depends(get_create_loan_use_case)
):
    """
    Create a new loan request.

    Business rules enforced:
    - User must have KYC approved
    - Max 3 active loans per borrower
    - Amount between €100 and €50,000
    """
    try:
        loan = await use_case.execute(
            borrower_id=user_id,
            amount=request.amount,
            duration=request.duration_months
        )
        return loan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

Валидация:
```bash
uv run ruff check services/api_service/
uv run mypy services/api_service/
curl -X POST http://localhost:8000/api/v1/loans -H "Content-Type: application/json" -d '{"amount": 1000, "duration_months": 12}'
```

#### **Подэтапы 4.4, 4.5, 4.6**

Аналогично генерируются:
- Workers (RabbitMQ consumers, credit scoring)
- Telegram bot (handlers, notifications)
- Tests (unit, integration, e2e)

### 👤 Взаимодействие с пользователем

**Момент диалога**: После каждого подэтапа (опционально) или после всего Этапа 4

**AI сообщает прогресс**:
```markdown
## 🚀 Phase 4.1 Complete: Infrastructure

**Сгенерировано:**
- ✅ docker-compose.yml (development)
- ✅ docker-compose.prod.yml (production)
- ✅ .env.example (23 переменных)
- ✅ Makefile (15 команд)
- ✅ 5 Dockerfiles для сервисов

**Валидация:**
```bash
$ docker-compose up -d
Creating network "p2p_lending_app_network" ... done
Creating p2p_lending_postgres ... done
Creating p2p_lending_mongodb ... done
Creating p2p_lending_redis ... done
Creating p2p_lending_rabbitmq ... done
Creating p2p_lending_db_postgres_service ... done
Creating p2p_lending_db_mongo_service ... done

$ docker-compose ps
NAME                              STATUS
p2p_lending_db_postgres_service   healthy
p2p_lending_db_mongo_service      healthy
p2p_lending_postgres              healthy
p2p_lending_redis                 healthy
p2p_lending_rabbitmq              healthy
```

✅ Все сервисы healthy. Переход к Phase 4.2 (Data Layer).
```

Пользователь может:
- Просто наблюдать (AI продолжает автоматически)
- Запросить изменения: "Измените порт PostgreSQL на 5433"
- Остановить: "STOP, покажи что уже сгенерировано"

### ⏱️ Длительность

Весь Этап 4 (все 6 подэтапов):
- Чтение atomic docs: ~30 минут (по мере необходимости)
- Генерация кода: ~20 минут
- Валидация после каждого подэтапа: ~5 минут
- **Итого**: ~55 минут

### ✅ Критерий завершения

- Весь код сгенерирован
- Все валидации пройдены
- Все тесты написаны (но могут не проходить еще - это для Этапа 5)

---

## Этап 5: Проверка качества

### 🎯 Что происходит

AI запускает **ВСЕ** обязательные проверки quality gates перед передачей кода.

### 📖 Документы которые читает AI

1. **`docs/quality/AGENT_VERIFICATION_CHECKLIST.md`** — полный чеклист проверок
2. **`docs/reference/AGENT_TOOLBOX.md`** — команды для проверок
3. **`docs/reference/troubleshooting.md`** — если возникают проблемы

### 🔍 Что проверяет AI

#### **1. Static Analysis & Security**

```bash
# Linting
uv run ruff check .
# Expected: No errors

# Formatting
uv run ruff format . --check
# Expected: No formatting drift

# Type checking
uv run mypy .
# Expected: No type errors

# Security scan
uv run bandit -r .
# Expected: No high severity issues
```

#### **2. Testing & Coverage**

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=services --cov-report=html --cov-report=xml
# Expected: Coverage ≥ 80%
```

#### **3. Artifact Validation**

- ✅ Project structure follows `PROJECT_STRUCTURE.md`
- ✅ Naming conventions correct (snake_case for code, kebab-case for network)
- ✅ All documentation updated

### 🤖 Действия AI

AI выполняет команды и собирает evidence:

```markdown
# Verification Checklist: P2P Lending Platform

**Date:** 2025-10-01
**Status:** ✅ ALL CHECKS PASSED

## Static Analysis & Security

| Check | Command | Result | Evidence |
|-------|---------|--------|----------|
| Linting | `uv run ruff check .` | ✅ PASS | 0 errors, 0 warnings |
| Formatting | `uv run ruff format . --check` | ✅ PASS | No formatting drift |
| Type checking | `uv run mypy .` | ✅ PASS | Success: no issues found in 145 source files |
| Security scan | `uv run bandit -r .` | ✅ PASS | 0 high severity, 2 low (false positives) |

## Testing & Coverage

| Check | Command | Result | Evidence |
|-------|---------|--------|----------|
| Unit tests | `uv run pytest tests/unit/` | ✅ PASS | 187 passed in 12.34s |
| Integration tests | `uv run pytest tests/integration/` | ✅ PASS | 42 passed in 45.67s |
| End-to-end tests | `uv run pytest tests/e2e/` | ✅ PASS | 12 passed in 89.01s |
| Coverage | `pytest --cov=services --cov-report=html` | ✅ 87% | htmlcov/index.html |

**Coverage Breakdown:**
```
Name                                      Stmts   Miss  Cover
-------------------------------------------------------------
services/api_service/src/__init__.py         2      0   100%
services/api_service/src/domain/...       124      8    94%
services/api_service/src/application/...  267     22    92%
services/api_service/src/infrastructure/   89     15    83%
services/api_service/src/api/...          156     31    80%
services/db_postgres_service/...          234     18    92%
services/worker_service/...               178     29    84%
-------------------------------------------------------------
TOTAL                                    1850    236    87%
```

## Artifact Validation

| Check | Result | Notes |
|-------|--------|-------|
| Project structure | ✅ PASS | Follows PROJECT_STRUCTURE.md |
| Naming conventions | ✅ PASS | snake_case for Python, kebab-case for Docker networks |
| Documentation | ✅ PASS | README.md, API docs (Swagger), deployment guide created |
| Docker health checks | ✅ PASS | All 5 services healthy |

## Performance (Quick Check)

```bash
$ ab -n 1000 -c 10 http://localhost:8000/api/v1/health
Requests per second:    234.56 [#/sec] (mean)
Time per request:       42.6 [ms] (mean)
Percentage of the requests served within a certain time (ms)
  50%     38
  66%     41
  75%     43
  80%     45
  90%     52
  95%     67
  98%     89
  99%    123
```

✅ < 200ms p95 (target met)

---

**Overall Status:** ✅ READY FOR HANDOFF

All quality gates passed. No blockers found.
```

### 👤 Взаимодействие с пользователем

**Момент диалога**: После завершения всех проверок

#### Вариант A: Все проверки прошли

```markdown
## ✅ Quality Verification Complete

Все обязательные проверки пройдены успешно!

**Результаты:**
- ✅ Linting (Ruff): 0 errors
- ✅ Type checking (Mypy): 0 errors
- ✅ Security (Bandit): 0 high severity
- ✅ Tests: 241 passed, 0 failed
- ✅ Coverage: 87% (target: ≥ 80%)
- ✅ Performance: 67ms p95 (target: < 200ms)

**Отчеты:**
- Coverage: htmlcov/index.html
- Test results: pytest-report.html

Переход к Stage 6 (QA Report & Handoff).
```

#### Вариант B: Есть проблемы

```markdown
## ⚠️ Quality Verification: Issues Found

Обнаружены проблемы которые нужно исправить:

**❌ Type Checking Failed:**
```
services/api_service/src/domain/entities/loan.py:25: error:
Argument 1 to "Decimal" has incompatible type "str"; expected "Union[Decimal, float, int]"
```

**❌ Coverage Below Threshold:**
```
services/worker_service/src/workers/credit_score_worker.py: 67% coverage (target: ≥ 80%)
Missing coverage in error handling paths.
```

**Действия:**
1. Исправляю type error в loan.py
2. Добавляю тесты для error paths в credit_score_worker.py
3. Повторяю проверку...

[AI автоматически исправляет и перезапускает проверки]

---

✅ После исправления:
- Type checking: 0 errors
- Coverage: 84%

Все проверки теперь пройдены. Переход к Stage 6.
```

### ⏱️ Длительность

- Запуск всех проверок: ~10 минут
- Исправление проблем (если есть): варьируется
- Повторные проверки: ~5 минут за итерацию

### ✅ Критерий завершения

**ВСЕ** проверки пройдены:
- ✅ 0 linting errors
- ✅ 0 type errors
- ✅ 0 high severity security issues
- ✅ All tests pass
- ✅ Coverage ≥ 80%

---

## Этап 6: QA отчет и передача

### 🎯 Что происходит

AI создает финальный QA отчет и собирает все deliverables для передачи пользователю.

### 📖 Документы которые читает AI

1. **`docs/quality/QA_REPORT_TEMPLATE.md`**
2. **`docs/reference/DELIVERABLES_CATALOG.md`**

### 🤖 Действия AI

AI генерирует финальный QA отчет:

```markdown
# QA Report: P2P Lending Platform

**Project:** P2P Lending Platform
**Date:** 2025-10-01
**Status:** ✅ READY FOR DEPLOYMENT

---

## Executive Summary

Успешно реализована production-ready P2P lending платформа по архитектуре Improved Hybrid Approach.

**Ключевые достижения:**
- 5 микросервисов (API, Bot, Worker, PostgreSQL, MongoDB)
- 24 API endpoints с полной OpenAPI документацией
- 241 тест с покрытием 87%
- Все security & quality gates пройдены
- GDPR compliance подтвержден
- Performance targets достигнуты (67ms p95 < 200ms target)

**Outstanding Issues:** Нет

**Recommendation:** ✅ APPROVED для production deployment

---

## Verification Results Summary

| Category | Status | Details |
|----------|--------|---------|
| Environment | ✅ PASS | Python 3.12.4, UV installed |
| Static analysis | ✅ PASS | Ruff: 0 errors, Mypy: 0 errors |
| Security | ✅ PASS | Bandit: 0 high severity |
| Testing | ✅ PASS | 241 tests passed, 0 failed |
| Coverage | ✅ 87% | Target: ≥ 80% (exceeded) |
| Performance | ✅ PASS | API p95: 67ms < 200ms target |
| Documentation | ✅ PASS | README, API docs, deployment guide |

---

## Test & Coverage Details

**Test Execution:**
```bash
$ uv run pytest --cov=services --cov-report=html
================= test session starts =================
platform linux -- Python 3.12.4
plugins: cov-4.1.0, asyncio-0.21.0
collected 241 items

tests/unit/test_domain.py ................... [ 28%]
tests/unit/test_use_cases.py ................ [ 45%]
tests/integration/test_repositories.py ...... [ 67%]
tests/integration/test_http_clients.py ...... [ 82%]
tests/e2e/test_loan_workflow.py ............. [100%]

================= 241 passed in 145.67s ================
```

**Coverage Report:**
- Total: 87% (1614/1850 statements covered)
- Coverage report: `htmlcov/index.html`
- XML report: `coverage.xml` (для CI/CD)

---

## Architecture Compliance

**✅ Improved Hybrid Approach:**
- Centralized data services: PostgreSQL (8001), MongoDB (8002)
- HTTP-only data access from business services (no direct DB)
- Service type separation: FastAPI, Aiogram, Workers in separate containers
- Event-driven: RabbitMQ for 6 event types

**✅ DDD/Hexagonal Architecture:**
- Domain layer: Entities with business rules
- Application layer: Use cases (orchestration)
- Infrastructure layer: HTTP clients, RabbitMQ publishers
- API layer: FastAPI routers

**✅ Security:**
- JWT + refresh tokens
- 2FA via Twilio
- HTTPS enforced (Nginx config)
- Rate limiting: 100 req/min per user
- PII anonymization in logs

---

## Deliverables Summary

| Deliverable | Location | Status |
|-------------|----------|--------|
| **Source Code** | `services/**/*.py` | ✅ Complete (12,450 lines) |
| **Infrastructure** | `docker-compose.yml`, `Makefile` | ✅ Complete |
| **Tests** | `tests/**/*.py` | ✅ 241 tests, 87% coverage |
| **Documentation** | `README.md`, `docs/api/` | ✅ Complete with examples |
| **API Docs** | `http://localhost:8000/docs` | ✅ OpenAPI/Swagger |
| **Requirements Intake** | `artifacts/requirements/intake.md` | ✅ Approved |
| **Implementation Plan** | `artifacts/plans/implementation-plan.md` | ✅ Executed |
| **Verification Checklist** | `artifacts/reports/verification-checklist.md` | ✅ All pass |

**Deployment Artifacts:**
- ✅ `.env.example` with all 23 required variables
- ✅ `docker-compose.prod.yml` for production
- ✅ Nginx configurations (TLS ready)
- ✅ Alembic migrations (6 migration files)

---

## Technology Stack (Implemented)

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12.4 | Runtime |
| FastAPI | 0.111.0 | REST API framework |
| Aiogram | 3.7.0 | Telegram bot framework |
| SQLAlchemy | 2.0.30 | PostgreSQL ORM |
| Motor | 3.4.0 | MongoDB async driver |
| RabbitMQ | 3.13 | Message broker |
| PostgreSQL | 16.3 | Relational database |
| MongoDB | 7.0 | Document database |
| Redis | 7.2 | Cache & sessions |
| Nginx | 1.25 | API Gateway |
| Stripe SDK | Latest | Payment processing |
| Twilio SDK | Latest | SMS (2FA) |

---

## Deployment Instructions

### 1. Prerequisites

```bash
# Install Docker & Docker Compose
docker --version  # >= 24.0
docker-compose --version  # >= 2.20

# Clone repository
git clone <repository-url>
cd p2p-lending
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your production values:
# - DATABASE_URL (PostgreSQL connection)
# - MONGO_URL (MongoDB connection)
# - STRIPE_SECRET_KEY (production key)
# - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
# - TELEGRAM_BOT_TOKEN
# - ONFIDO_API_TOKEN
# - SENDGRID_API_KEY
```

### 3. Deploy Stack

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
docker-compose ps
```

### 4. Run Migrations

```bash
# Apply database migrations
docker-compose exec db_postgres_service alembic upgrade head

# Verify migrations
docker-compose exec db_postgres_service alembic current
```

### 5. Verify Deployment

```bash
# Health checks
curl https://api.p2p-lending.com/health
# Expected: {"status":"ok"}

curl https://api.p2p-lending.com/api/v1/health
# Expected: {"status":"healthy","database":"connected"}

# Check all services
docker-compose ps
# All services should show "healthy"
```

### 6. Monitoring

**Dashboards:**
- Grafana: `https://grafana.p2p-lending.com`
- Prometheus: `https://prometheus.p2p-lending.com`
- Kibana: `https://kibana.p2p-lending.com`

**What to monitor in first 24h:**
- API error rates (should be < 1%)
- Database connection pool (should be < 80%)
- Payment processing success rate (should be > 95%)
- User registration funnel
- RabbitMQ queue depths

---

## Post-Deployment Checklist

- [ ] SSL certificates installed and valid
- [ ] Domain DNS configured correctly
- [ ] Production `.env` configured (all secrets set)
- [ ] Database backups scheduled (daily)
- [ ] Monitoring alerts configured
- [ ] Sentry error tracking active
- [ ] Stripe webhooks configured with production URL
- [ ] Rate limiting tested (100 req/min threshold)
- [ ] GDPR data export endpoint tested
- [ ] KYC provider (Onfido) production account active

---

## Known Limitations & Future Improvements

**Current Limitations (v1):**
- EUR only (no multi-currency)
- Single region (EU + UK only)
- No mobile apps (web-first)
- Basic admin panel

**Planned for v2:**
- Automated loan matching algorithm
- Mobile apps (iOS/Android)
- Multi-currency support
- Advanced analytics dashboard
- Secondary market for loan contracts

---

## Support & Contact

**Technical Documentation:**
- Architecture: `docs/architecture/`
- API Reference: `http://localhost:8000/docs`
- Troubleshooting: `docs/reference/troubleshooting.md`

**Incident Response:**
- Check logs: `docker-compose logs -f <service>`
- Rollback: `docker-compose down && git checkout <previous-commit> && docker-compose up -d`
- Database backup restore: `docs/operations/backup-restore.md`

---

**Sign-Off:**
- ✅ AI Agent: Claude (2025-10-01)
- ⏳ Reviewer: [Pending]
- ⏳ Stakeholder: [Pending]

---

**END OF QA REPORT**
```

### 👤 Взаимодействие с пользователем

**Момент диалога**: Финальная передача

**AI отправляет**:
```markdown
## 🎉 P2P Lending Platform: Ready for Deployment!

Проект завершен и готов к production deployment.

### 📊 Итоговая сводка:

**Реализовано за 6 недель:**
- 5 микросервисов (12,450 строк кода)
- 24 API endpoints
- 241 тест (87% coverage)
- Полная GDPR compliance
- Performance: 67ms p95 (< 200ms target ✅)

**Deliverables:**
- ✅ Полный исходный код (GitHub repo)
- ✅ Docker Compose конфигурации
- ✅ OpenAPI документация
- ✅ Deployment guide
- ✅ QA отчет (см. выше)

### 🚀 Следующие шаги:

1. **Review QA Report** - убедитесь что всё соответствует требованиям
2. **Test locally** - запустите `docker-compose up` для проверки
3. **Deploy to staging** - протестируйте в staging environment
4. **Production deployment** - следуйте инструкциям в QA Report секция "Deployment Instructions"

**Команды для быстрого старта:**
```bash
# Local testing
cp .env.example .env
docker-compose up -d
curl http://localhost:8000/docs  # OpenAPI UI

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

**Нужна помощь?**
- Troubleshooting: `docs/reference/troubleshooting.md`
- Architecture questions: `docs/guides/ARCHITECTURE_GUIDE.md`

---

✅ **Project Status:** READY FOR PRODUCTION
```

**Пользователь может**:
- Принять и начать deployment
- Запросить изменения/улучшения
- Задать вопросы по любой части реализации

### ⏱️ Длительность

- Создание QA отчета: ~5 минут
- Сбор deliverables: ~2 минуты

### ✅ Критерий завершения

QA отчет одобрен пользователем, все deliverables переданы.

---

## Примеры диалогов

### Пример 1: Полный успешный пайплайн

```
👤 USER: Хочу P2P lending платформу с автоматическими платежами через Stripe и Telegram уведомлениями.

🤖 AI: ⚠️ Prompt Validation: INCOMPLETE
      Нужны детали по аутентификации, масштабу, compliance...

👤 USER: JWT + 2FA, Stripe, 1K users, EU GDPR + UK FCA, 7 лет retention.

🤖 AI: ✅ Validation Complete → Stage 2
      [Generates Requirements Intake document]
      Пожалуйста, проверьте Requirements Intake. Одобрите или дайте feedback.

👤 USER: APPROVED. Но добавьте max 3 active loans per borrower.

🤖 AI: ✅ Requirements Updated → Stage 3
      [Generates Implementation Plan with 6 phases]
      План готов (6 недель). Одобрите для начала Phase 1?

👤 USER: START PHASE 1

🤖 AI: ✅ Phase 1 Started → Infrastructure Setup
      [Generates Docker, Makefiles, .env]
      ✅ Phase 1 Complete. All services healthy.
      ✅ Phase 2 Started → Data Layer...
      [... continues through all phases ...]
      ✅ Phase 4.6 Complete → All code generated
      → Stage 5: Quality Verification
      [Runs all checks]
      ✅ All checks passed (87% coverage, 0 errors)
      → Stage 6: QA Report
      [Generates QA Report]

🤖 AI: 🎉 Project Complete! Ready for production deployment.
      See QA Report above for deployment instructions.

👤 USER: Отлично! Начинаю deployment.
```

### Пример 2: Пайплайн с исправлениями

```
👤 USER: [Дает полный промпт для marketplace платформы]

🤖 AI: ✅ Validation Complete → Requirements Intake
      [Generates Requirements Intake]

👤 USER: APPROVED

🤖 AI: → Stage 3: Planning
      [Generates Implementation Plan]

👤 USER: Изменить: вместо MongoDB использовать только PostgreSQL для всего.

🤖 AI: ⚠️ Architecture Conflict Detected

      MongoDB используется для:
      1. Audit logs (immutable, append-only)
      2. Analytics (flexible schema)

      Improved Hybrid Approach рекомендует:
      - PostgreSQL для transactional data (ACID)
      - MongoDB для analytics, audit logs (flexible, high-write)

      Можем использовать только PostgreSQL, но:
      - Audit logs в отдельной таблице (performance impact при больших объемах)
      - Analytics будет менее гибким (JSON columns в PostgreSQL)

      Рекомендация: Оставить MongoDB для audit/analytics.

      Ваш выбор?

👤 USER: Хорошо, согласен с рекомендацией. Оставьте MongoDB.

🤖 AI: ✅ Plan Confirmed → Stage 4: Code Generation
      [Continues with original plan]
```

### Пример 3: Пайплайн с проблемами на тестировании

```
[... stages 0-4 complete ...]

🤖 AI: → Stage 5: Quality Verification
      Running checks...

      ❌ Type Checking Failed:
      services/api_service/src/domain/entities/loan.py:25:
      Argument 1 to "Decimal" has incompatible type "str"

      ❌ Coverage: 74% (target: ≥ 80%)

      Исправляю проблемы...

      [AI fixes type error]
      [AI adds missing tests]

      Re-running verification...
      ✅ Type checking: 0 errors
      ✅ Coverage: 84%

      All checks now passed! → Stage 6: QA Report

🤖 AI: [Generates QA Report with note about fixes made]
```

---

### Пример 3: Level 1 (PoC) — Минимальная генерация за ~5 минут

```
👤 USER: Хочу простой task manager API для командного проекта. Базовый CRUD для задач.

🤖 AI: 🔍 Prompt Validation: INCOMPLETE

      **Нужно выбрать уровень зрелости (Maturity Level)**:

      1. 🧪 **PoC** (~5 мин) — Только core (FastAPI + PostgreSQL + Docker)
      2. 🛠️ **Development** (~10 мин) — + Логирование, health checks
      3. 🚀 **Pre-Production** (~15 мин) — + Nginx, SSL, метрики
      4. 🏢 **Production** (~30 мин) — + OAuth, ELK, tracing, CI/CD

      **Ваш выбор (1-4)**: _____

👤 USER: Level 1 (PoC). Мне нужен только быстрый MVP для демо.

🤖 AI: ✅ Maturity Level: 1 - PoC (~5 мин)
      ✅ Validation Complete → Stage 2

      [Generates Requirements Intake]
      - Maturity Level: 1 - PoC
      - Optional Modules: None
      - Estimated Time: ~5 минут

      Одобрите Requirements Intake?

👤 USER: APPROVED

🤖 AI: → Stage 3: Planning
      [Generates Implementation Plan]

      ## Что будет включено (Level 1):
      ✅ FastAPI service (core endpoints)
      ✅ PostgreSQL data service
      ✅ Docker Compose (basic)
      ✅ Basic tests (coverage ≥ 60%)

      ## Что НЕ будет включено (доступно в Level 2+):
      ❌ Структурированное логирование (Level 2)
      ❌ Nginx API Gateway (Level 3)
      ❌ SSL/TLS (Level 3)
      ❌ Prometheus метрики (Level 3)
      ❌ OAuth/JWT (Level 4)
      ❌ ELK Stack (Level 4)

      💡 **Upgrade Path**: Позже можно добавить эти features, см. MATURITY_LEVELS.md

      Одобрить план?

👤 USER: START

🤖 AI: ✅ Stage 4: Code Generation (PoC mode)

      [4.1] Infrastructure (basic) ✅ (~1 min)
      - docker-compose.yml
      - .env.example
      - Makefile

      [4.2] Data Layer ✅ (~1.5 min)
      - PostgreSQL service: tasks model
      - HTTP API for data access

      [4.3] Business Logic (core only) ✅ (~1.5 min)
      - FastAPI service
      - CRUD endpoints для tasks
      - NO logging, NO metrics (PoC mode)

      [4.6] Testing (basic) ✅ (~1 min)
      - pytest setup
      - Unit tests для core
      - Coverage: 63% (Level 1 target: ≥ 60%) ✅

      ✅ Total time: ~5 минут

      → Stage 5: Verification
      [Runs checks]
      ✅ Ruff: 0 errors
      ✅ Mypy: 0 errors
      ✅ Bandit: 0 high severity
      ✅ Tests: 42 passed
      ✅ Coverage: 63% (≥ 60% для Level 1) ✅

      → Stage 6: QA Report

🤖 AI: 🎉 PoC Ready! (5 минут)

      **Что сделано**:
      - Task Manager API (CRUD)
      - 42 tests, 63% coverage
      - Docker Compose ready

      **Deployment (PoC)**:
      ```bash
      docker-compose up -d
      curl http://localhost:8000/api/v1/tasks
      ```

      **Upgrade to Level 2** (if needed):
      - + Structured logging
      - + Health checks
      - Time: ~5 доп. минут

👤 USER: Отлично! Запускаю demo.
```

---

### Пример 4: Level 2 (Development Ready) — С логированием за ~10 минут

```
👤 USER: Task manager API как в Примере 3, но с логированием для debugging в staging.

🤖 AI: 🔍 Рекомендую **Level 2 (Development Ready)**:
      - Включает всё из Level 1
      - + Структурированное логирование (JSON)
      - + Health checks
      - + Error tracking
      - Время: ~10 минут

      Согласны с Level 2?

👤 USER: Да, Level 2.

🤖 AI: ✅ Maturity Level: 2 - Development Ready
      → Stage 2-3: Requirements + Planning

      ## Что включено (Level 2):
      ✅ Всё из Level 1 (core)
      ✅ Структурированное логирование (structlog)
      ✅ Request ID propagation
      ✅ Health check endpoints
      ✅ Error tracking
      ✅ docker-compose.dev.yml (dev overrides)
      ✅ Coverage target: ≥ 75%

      Одобрить?

👤 USER: APPROVED

🤖 AI: → Stage 4: Code Generation (Development mode)

      [4.1] Infrastructure (basic) ✅
      [4.1b] + Dev Overrides ✅ (Level 2)
      - docker-compose.dev.yml
      - Healthcheck setup

      [4.2] Data Layer ✅

      [4.3] Business Logic (core) ✅
      [4.3b] + Structured Logging ✅ (Level 2)
      - Logger setup (structlog)
      - Request ID middleware
      - Error logging

      [4.6] Testing (basic) ✅
      [4.6b] + Integration Tests ✅ (Level 2)
      - Testcontainers
      - Coverage: 78% (≥ 75% target)

      ✅ Total time: ~10 минут

      → Stage 5: Verification
      ✅ All checks passed
      ✅ Coverage: 78% (≥ 75%) ✅

🤖 AI: 🎉 Development-Ready App! (10 минут)

      **Что добавлено vs Level 1**:
      - ✅ Структурированные логи (JSON)
      - ✅ Request ID во всех логах
      - ✅ Health checks: /health, /ready
      - ✅ Integration tests

      **Deployment (Dev)**:
      ```bash
      docker-compose -f docker-compose.dev.yml up -d
      curl http://localhost:8000/health  # {"status":"ok"}
      ```

      **Upgrade to Level 3** (if needed):
      - + Nginx API Gateway
      - + SSL/TLS
      - + Prometheus + Grafana
      - Time: ~5 доп. минут
```

---

### Пример 5: Level 3 (Pre-Production) — С Nginx и метриками за ~15 минут

```
👤 USER: Task manager для публичного запуска (beta). Нужен SSL и мониторинг.

🤖 AI: 🔍 Рекомендую **Level 3 (Pre-Production)**:
      - Всё из Level 2
      - + Nginx API Gateway (reverse proxy)
      - + SSL/TLS (Let's Encrypt ready)
      - + Prometheus + Grafana
      - + Rate limiting
      - Время: ~15 минут

      Level 3?

👤 USER: Да.

🤖 AI: ✅ Maturity Level: 3 - Pre-Production
      → Stage 2-3: Requirements + Planning

      ## Что включено (Level 3):
      ✅ Всё из Level 1 + 2
      ✅ Nginx (reverse proxy, load balancing)
      ✅ SSL/TLS setup (certbot ready)
      ✅ Prometheus metrics (/metrics)
      ✅ Grafana dashboards
      ✅ Rate limiting (Nginx)
      ✅ docker-compose.prod.yml
      ✅ Coverage target: ≥ 80%

      Одобрить?

👤 USER: START

🤖 AI: → Stage 4: Code Generation (Pre-Production mode)

      [4.1] Infrastructure (basic) ✅
      [4.1b] + Dev Overrides ✅
      [4.1c] + Nginx + SSL + Metrics ✅ (Level 3)
      - Nginx config (reverse proxy)
      - SSL setup (certbot-ready)
      - Prometheus + Grafana
      - docker-compose.prod.yml

      [4.2] Data Layer ✅

      [4.3] Business Logic (core) ✅
      [4.3b] + Structured Logging ✅
      [4.3c] + Prometheus Metrics ✅ (Level 3)
      - /metrics endpoint
      - Custom business metrics
      - Grafana dashboard

      [4.6] Testing (basic + integration) ✅
      [4.6c] + E2E Tests ✅ (Level 3)
      - End-to-end API tests
      - Coverage: 83% (≥ 80%)

      ✅ Total time: ~15 минут

      → Stage 5: Verification
      ✅ All checks passed
      ✅ Coverage: 83%
      ✅ Nginx config validated
      ✅ SSL ready

🤖 AI: 🎉 Pre-Production Ready! (15 минут)

      **Что добавлено vs Level 2**:
      - ✅ Nginx reverse proxy
      - ✅ SSL/TLS (certbot integration)
      - ✅ Prometheus metrics (/metrics)
      - ✅ Grafana dashboards
      - ✅ Rate limiting (100 req/min/IP)
      - ✅ E2E tests

      **Deployment (Production-like)**:
      ```bash
      docker-compose -f docker-compose.prod.yml up -d

      # Setup SSL (manual step):
      docker-compose exec nginx certbot --nginx -d yourdomain.com

      # Access
      https://yourdomain.com/api/v1/tasks  # via Nginx + SSL
      http://localhost:9090                 # Prometheus
      http://localhost:3000                 # Grafana
      ```

      **Upgrade to Level 4** (if needed):
      - + OAuth 2.0 / JWT
      - + ELK Stack (centralized logging)
      - + Distributed tracing
      - + CI/CD pipelines
      - Time: ~15 доп. минут
```

---

### Пример 6: Level 4 (Production) — Full Enterprise за ~30 минут

```
👤 USER: Task manager для enterprise клиента. Нужна аутентификация, compliance, CI/CD.

🤖 AI: 🔍 Рекомендую **Level 4 (Production)**:
      - Всё из Level 3
      - + OAuth 2.0 / JWT + RBAC
      - + ELK Stack (Elasticsearch + Logstash + Kibana)
      - + Distributed tracing (Jaeger)
      - + PostgreSQL replication + backups
      - + CI/CD pipelines (GitHub Actions)
      - Время: ~30 минут

      Level 4?

👤 USER: Да, нужен полный production.

🤖 AI: ✅ Maturity Level: 4 - Production
      → Stage 2-3: Requirements + Planning

      ## Что включено (Level 4):
      ✅ Всё из Level 1 + 2 + 3
      ✅ OAuth 2.0 / JWT authentication
      ✅ RBAC (Role-Based Access Control)
      ✅ ELK Stack (centralized logging)
      ✅ Distributed tracing (Jaeger)
      ✅ PostgreSQL replication (master-replica)
      ✅ Automated backups
      ✅ CI/CD pipelines (GitHub Actions)
      ✅ Security tests
      ✅ Coverage target: ≥ 85%

      Одобрить?

👤 USER: APPROVED

🤖 AI: → Stage 4: Code Generation (Production mode)

      [4.1] Infrastructure ✅
      [4.1b] + Dev Overrides ✅
      [4.1c] + Nginx + SSL + Metrics ✅
      [4.1d] + ELK + Replication ✅ (Level 4)
      - ELK Stack config
      - PostgreSQL replication
      - Backup scripts

      [4.2] Data Layer ✅

      [4.3] Business Logic (core) ✅
      [4.3b] + Structured Logging ✅
      [4.3c] + Prometheus Metrics ✅
      [4.3d] + OAuth/JWT + Tracing ✅ (Level 4)
      - OAuth 2.0 / JWT setup
      - RBAC middleware
      - Distributed tracing (Jaeger)

      [4.6] Testing ✅
      [4.6b] + Integration Tests ✅
      [4.6c] + E2E Tests ✅
      [4.6d] + Security Tests ✅ (Level 4)
      - Security test suite
      - Bandit config (strict)
      - Coverage: 87% (≥ 85%)

      [CI/CD] GitHub Actions pipelines ✅
      - Lint, test, build, deploy
      - Automated security scans

      ✅ Total time: ~30 минут

      → Stage 5: Verification
      ✅ All checks passed
      ✅ Coverage: 87%
      ✅ Security tests: passed
      ✅ OAuth functional

🤖 AI: 🎉 Production-Ready Enterprise App! (30 минут)

      **Что добавлено vs Level 3**:
      - ✅ OAuth 2.0 / JWT authentication
      - ✅ RBAC (admin, user roles)
      - ✅ ELK Stack (centralized logs)
      - ✅ Distributed tracing (Jaeger)
      - ✅ PostgreSQL replication
      - ✅ Automated backups (daily)
      - ✅ CI/CD pipelines
      - ✅ Security test suite

      **Deployment (Production)**:
      ```bash
      # Production deployment
      docker-compose -f docker-compose.prod.yml up -d

      # Verify all services
      docker-compose ps  # All healthy

      # Access
      https://api.yourdomain.com/auth/login    # OAuth login
      https://api.yourdomain.com/api/v1/tasks  # Authenticated API
      http://localhost:5601                     # Kibana (logs)
      http://localhost:16686                    # Jaeger (traces)
      ```

      **Compliance Ready**:
      - ✅ GDPR (audit logs in ELK)
      - ✅ SOC 2 (authentication, encryption, backups)
      - ✅ Security scans (automated in CI/CD)

👤 USER: Perfect! Запускаю в production.
```

---

## 📝 Резюме: Когда AI читает документы и спрашивает пользователя

| Этап | AI читает | AI спрашивает пользователя | Пользователь должен |
|------|-----------|----------------------------|---------------------|
| **0. Initialization** | CLAUDE.md, AGENT_CONTEXT_SUMMARY.md, MASTER_WORKFLOW.md | — | Ничего (AI загружается) |
| **1. Prompt Validation** | PROMPT_VALIDATION_GUIDE.md | ✅ ДА (если промпт неполный) | Дополнить промпт |
| **2. Requirements Intake** | ARCHITECTURE_GUIDE.md, tech_stack.md, atomic/architecture/* | ✅ ДА (если нужны уточнения) | Одобрить Requirements Intake |
| **3. Planning** | IMPLEMENTATION_PLAN_TEMPLATE.md, atomic/services/*, atomic/integrations/* | ✅ ДА (запрашивает approval плана) | Одобрить Implementation Plan |
| **4. Code Generation** | atomic/* (on-demand по фазам) | Опционально (прогресс-репорты) | Наблюдать или давать feedback |
| **5. Verification** | AGENT_VERIFICATION_CHECKLIST.md, troubleshooting.md | Только если проблемы | — (AI исправляет автоматически) |
| **6. QA Report** | QA_REPORT_TEMPLATE.md, DELIVERABLES_CATALOG.md | ✅ ДА (финальный handoff) | Принять deliverables |

---

## ✅ Проверка отсутствия противоречий

Я проверил все ключевые документы:

| Документ | Этапы | Совместимость |
|----------|-------|---------------|
| CLAUDE.md | 7 (0-6) | ✅ Согласуется |
| AI_CODE_GENERATION_MASTER_WORKFLOW.md | 7 (0-6) | ✅ Согласуется |
| AI_NAVIGATION_MATRIX.md | 7 (0-6) | ✅ Согласуется |

**Вывод**: ❌ **НЕТ ПРОТИВОРЕЧИЙ**. Все документы согласованы, AI имеет четкие инструкции на каждом этапе.

---

**Конец документа**
