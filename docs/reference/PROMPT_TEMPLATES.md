# Prompt Templates

> **Purpose**: Provide reusable prompt snippets for human–agent interaction across the workflow. Always adapt placeholders to the specific context.

## Usage Guidelines

- Keep responses and generated documents aligned with `docs/STYLE_GUIDE.md`.
- Do not bypass architectural constraints; reference `docs/guides/ARCHITECTURE_GUIDE.md` and `docs/architecture/*.mdc` when clarifying requirements.
- Use the templates below to fill gaps identified in `docs/guides/PROMPT_VALIDATION_GUIDE.md`.

## Prompt Augmentation (Validation)

| Scenario | Prompt Body | Variables | Expected Agent Output | References |
|----------|-------------|-----------|-----------------------|------------|
| Missing business context | "Please provide the business problem we are solving, the target users, and the success metrics so I can confirm alignment with the framework." | None | Structured description of context | `docs/guides/PROMPT_VALIDATION_GUIDE.md` |
| Missing maturity level | "Choose target maturity level:\n\n1. 🧪 **PoC** (Proof of Concept)\n   - Core functionality only (FastAPI + PostgreSQL)\n   - Time: ~5 min \| Use: MVP, demo, learning\n\n2. 🛠️ **Development** Ready\n   - + Structured logging, health checks, error tracking\n   - Time: ~10 min \| Use: Active development, staging\n\n3. 🚀 **Pre-Production**\n   - + Nginx, SSL, Prometheus metrics, rate limiting\n   - Time: ~15 min \| Use: Public beta, small production\n\n4. 🏢 **Production**\n   - + Security (OAuth, RBAC), ELK, tracing, CI/CD, HA\n   - Time: ~30 min \| Use: Enterprise, compliance\n\nYour choice (1-4): _____" | None | Selected level (1-4) | `docs/reference/MATURITY_LEVELS.md` |
| Missing optional modules | "Optional modules (available at any maturity level):\n  [ ] Telegram Bot (Aiogram)\n  [ ] Background Workers (AsyncIO)\n  [ ] MongoDB (NoSQL database)\n  [ ] RabbitMQ (event messaging)\n  [ ] Redis (caching)\n  [ ] File Storage (S3/MinIO)\n  [ ] Real-Time (WebSockets)\n\nYour selection (comma-separated or 'none'): _____" | None | List of selected modules or "none" | `docs/reference/MATURITY_LEVELS.md` |
| Missing functional requirements | "List the core features or user stories that the application must support. Prioritize them if possible." | None | Ordered feature list | `docs/guides/PROMPT_VALIDATION_GUIDE.md` |
| Missing non-functional constraints | "Share performance, security, and compliance expectations. I need these to verify architecture and quality rules." | None | Non-functional requirements | `docs/guides/ARCHITECTURE_GUIDE.md` |
| Missing dependencies | "Describe external systems, queues, or databases we must integrate with. Mention protocols or APIs if known." | None | Integration details | `docs/atomic/infrastructure/` |
| Missing scope boundaries | "Clarify what is explicitly out of scope so the plan does not include unnecessary features." | None | Out-of-scope list | `docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md` |
| Missing deliverables/acceptance criteria | "Specify required deliverables (code, documentation, reports) and acceptance criteria such as tests or coverage targets." | None | Deliverables and acceptance list | `docs/reference/DELIVERABLES_CATALOG.md`, `docs/quality/AGENT_VERIFICATION_CHECKLIST.md` |

## Planning & Confirmation

| Scenario | Prompt Body | Variables | Expected Agent Output | References |
|----------|-------------|-----------|-----------------------|------------|
| Confirm ready to plan | "I have validated the prompt. Summarize the requirements and confirm we can proceed to the implementation plan." | None | Intake summary + go/no-go | `docs/guides/REQUIREMENTS_INTAKE_TEMPLATE.md` |
| Request plan approval | "Here is the proposed implementation plan: {{plan_link}}. Please review the stages, DoD, and risks. Confirm or provide adjustments." | `plan_link` | Plan approval or change requests | `docs/guides/IMPLEMENTATION_PLAN_TEMPLATE.md` |
| Clarify risks | "Highlight any additional risks or dependencies we should track before coding begins." | None | Risk updates | Plan template |

## Coding & Execution

| Scenario | Prompt Body | Variables | Expected Agent Output | References |
|----------|-------------|-----------|-----------------------|------------|
| Kick off implementation | "Proceed with implementing the plan. Reference the architecture and service rules as you create code." | None | Execution acknowledgement | `docs/guides/AI_CODE_GENERATION_MASTER_WORKFLOW.md` Stage 4, `docs/atomic/services/*` |
| Request progress update | "Provide a status update for each stage in the implementation plan, including blockers." | None | Status report | Implementation plan |

## Verification & Release

| Scenario | Prompt Body | Variables | Expected Agent Output | References |
|----------|-------------|-----------|-----------------------|------------|
| Trigger verification | "Run the full verification checklist and report results for linting, typing, security, tests, and coverage." | None | Checklist results | `docs/quality/AGENT_VERIFICATION_CHECKLIST.md` |
| Request QA report | "Compile the QA report summarizing checks, test evidence, and outstanding risks." | None | QA report draft | `docs/quality/QA_REPORT_TEMPLATE.md` |
| Final hand-off | "Summarize deliverables, link to artefacts, and state whether acceptance criteria are met." | None | Final summary | `docs/reference/DELIVERABLES_CATALOG.md` |

## Anti-Patterns

- Avoid prompts asking the agent to ignore architecture or quality rules.
- Do not solicit direct database access or merged service processes (violates `docs/architecture/data-access-rules.mdc`).
- Never request code generation without validated requirements.

## Maintenance

- Update scenarios when new workflow steps are introduced.
- Keep references synchronized with `docs/INDEX.md` and `docs/reference/AGENT_CONTEXT_SUMMARY.md`.
- Follow `docs/STYLE_GUIDE.md` when editing.
