# Prompt Templates

> **Purpose**: Provide reusable prompt snippets for human–agent interaction across the workflow. Always adapt placeholders to the specific context.

## Usage Guidelines

- Keep responses and generated documents aligned with `docs/STYLE_GUIDE.md`.
- Do not bypass architectural constraints; reference `docs/guides/architecture-guide.md` and `docs/architecture/*.mdc` when clarifying requirements.
- Use the templates below to fill gaps identified in `docs/guides/prompt-validation-guide.md`.

## Prompt Augmentation (Validation)

| Scenario | Prompt Body | Variables | Expected Agent Output | References |
|----------|-------------|-----------|-----------------------|------------|
| Missing business context | "Please provide the business problem we are solving, the target users, and the success metrics so I can confirm alignment with the framework." | None | Structured description of context | `docs/guides/prompt-validation-guide.md` |
| Missing maturity level | "Choose target maturity level:\n\n1. 🧪 **PoC** (Proof of Concept)\n   - Core functionality only (FastAPI + PostgreSQL)\n   - Time: ~5 min \| Use: MVP, demo, learning\n\n2. 🛠️ **Development** Ready\n   - + Structured logging, health checks, error tracking\n   - Time: ~10 min \| Use: Active development, staging\n\n3. 🚀 **Pre-Production**\n   - + Nginx, SSL, Prometheus metrics, rate limiting\n   - Time: ~15 min \| Use: Public beta, small production\n\n4. 🏢 **Production**\n   - + Security (OAuth, RBAC), ELK, tracing, CI/CD, HA\n   - Time: ~30 min \| Use: Enterprise, compliance\n\nYour choice (1-4): _____" | None | Selected level (1-4) | `docs/reference/maturity-levels.md` |
| Missing optional modules | "Optional modules (available at any maturity level):\n  [ ] Telegram Bot (Aiogram)\n  [ ] Background Workers (AsyncIO)\n  [ ] MongoDB (NoSQL database)\n  [ ] RabbitMQ (event messaging)\n  [ ] Redis (caching)\n  [ ] File Storage (S3/MinIO)\n  [ ] Real-Time (WebSockets)\n\nYour selection (comma-separated or 'none'): _____" | None | List of selected modules or "none" | `docs/reference/maturity-levels.md` |
| Missing functional requirements | "List the core features or user stories that the application must support. Prioritize them if possible." | None | Ordered feature list | `docs/guides/prompt-validation-guide.md` |
| Missing non-functional constraints | "Share performance, security, and compliance expectations. I need these to verify architecture and quality rules." | None | Non-functional requirements | `docs/guides/architecture-guide.md` |
| Missing dependencies | "Describe external systems, queues, or databases we must integrate with. Mention protocols or APIs if known." | None | Integration details | `docs/atomic/infrastructure/` |
| Missing scope boundaries | "Clarify what is explicitly out of scope so the plan does not include unnecessary features." | None | Out-of-scope list | `docs/guides/implementation-plan-template.md` |
| Missing deliverables/acceptance criteria | "Specify required deliverables (code, documentation, reports) and acceptance criteria such as tests or coverage targets." | None | Deliverables and acceptance list | `docs/reference/deliverables-catalog.md`, `docs/quality/agent-verification-checklist.md` |
| Missing scalability requirements | "Please clarify scalability expectations:\n\n**Traffic & Load**:\n- Expected requests per second (RPS): _____\n- Expected daily active users (DAU): _____\n- Peak load multiplier (e.g., 3x normal): _____\n\n**Scaling Strategy**:\n- [ ] Horizontal scaling (multiple service instances)\n- [ ] Vertical scaling (larger containers)\n- [ ] Database read replicas needed?\n- [ ] Caching strategy required?\n\n**Performance Targets**:\n- API response time (p95): _____ ms\n- Database query time (p95): _____ ms\n- Acceptable downtime per month: _____\n\nNote: Horizontal scaling and DB replication typically require Level 4 (Production)." | None | Scalability requirements (RPS, DAU, SLA targets, scaling strategy) | `docs/reference/maturity-levels.md`, `docs/atomic/infrastructure/databases/postgresql-replication.md` |
| Missing compliance requirements | "Please specify compliance and regulatory requirements:\n\n**Regulations** (check all that apply):\n- [ ] GDPR (EU General Data Protection Regulation)\n- [ ] HIPAA (US Healthcare data protection)\n- [ ] PCI-DSS (Payment Card Industry)\n- [ ] SOC 2 (Security & availability controls)\n- [ ] CCPA (California Consumer Privacy Act)\n- [ ] Other: _____\n\n**Data Protection**:\n- Data residency requirements (EU, US, Asia): _____\n- Data retention period: _____\n- Right to deletion (GDPR Article 17): Yes / No\n- Encryption at rest required: Yes / No\n- Encryption in transit required: Yes / No\n\n**Audit & Logging**:\n- Audit log retention: _____ years\n- Security event logging required: Yes / No\n- User consent tracking required: Yes / No\n\nNote: Full compliance features typically require Level 4 (Production) with audit logging, encryption, and access controls." | None | Compliance requirements (regulations, data protection, audit needs) | `docs/reference/maturity-levels.md`, `docs/atomic/security/authentication-authorization-guide.md`, `docs/atomic/observability/logging/sensitive-data-handling.md` |

## Planning & Confirmation

| Scenario | Prompt Body | Variables | Expected Agent Output | References |
|----------|-------------|-----------|-----------------------|------------|
| Confirm ready to plan | "I have validated the prompt. Summarize the requirements and confirm we can proceed to the implementation plan." | None | Intake summary + go/no-go | `docs/guides/requirements-intake-template.md` |
| Request plan approval | "Here is the proposed implementation plan: {{plan_link}}. Please review the stages, DoD, and risks. Confirm or provide adjustments." | `plan_link` | Plan approval or change requests | `docs/guides/implementation-plan-template.md` |
| Clarify risks | "Highlight any additional risks or dependencies we should track before coding begins." | None | Risk updates | Plan template |

## Coding & Execution

| Scenario | Prompt Body | Variables | Expected Agent Output | References |
|----------|-------------|-----------|-----------------------|------------|
| Kick off implementation | "Proceed with implementing the plan. Reference the architecture and service rules as you create code." | None | Execution acknowledgement | `docs/guides/ai-code-generation-master-workflow.md` Stage 4, `docs/atomic/services/*` |
| Request progress update | "Provide a status update for each stage in the implementation plan, including blockers." | None | Status report | Implementation plan |

## Verification & Release

| Scenario | Prompt Body | Variables | Expected Agent Output | References |
|----------|-------------|-----------|-----------------------|------------|
| Trigger verification | "Run the full verification checklist and report results for linting, typing, security, tests, and coverage." | None | Checklist results | `docs/quality/agent-verification-checklist.md` |
| Request QA report | "Compile the QA report summarizing checks, test evidence, and outstanding risks." | None | QA report draft | `docs/quality/qa-report-template.md` |
| Final hand-off | "Summarize deliverables, link to artefacts, and state whether acceptance criteria are met." | None | Final summary | `docs/reference/deliverables-catalog.md` |

## Anti-Patterns

- Avoid prompts asking the agent to ignore architecture or quality rules.
- Do not solicit direct database access or merged service processes (violates `docs/architecture/data-access-rules.mdc`).
- Never request code generation without validated requirements.

## Maintenance

- Update scenarios when new workflow steps are introduced.
- Keep references synchronized with `docs/INDEX.md` and `docs/reference/agent-context-summary.md`.
- Follow `docs/STYLE_GUIDE.md` when editing.
