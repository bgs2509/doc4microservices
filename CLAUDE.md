# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this microservices framework.

> **CONTEXT**: This framework can be used in two ways:
> - **Direct**: Working in this repository directly (use paths like `docs/`)
> - **Submodule**: Added as `.framework/` submodule to your project (use paths like `.framework/docs/`)
>
> The paths below assume **direct usage**. When used as submodule, prefix all paths with `.framework/`.

## AI Agent Reading Order (MANDATORY)

**When starting work, AI agents MUST read documents in this exact order:**

### **Stage 0: Initialization** (Before receiving user prompt)

1. **CLAUDE.md** (this file) — Entry point, navigation, framework overview
2. **docs/reference/agent-context-summary.md** — Critical rules snapshot, mandatory constraints
3. **docs/guides/ai-code-generation-master-workflow.md** — Complete 7-stage process with detailed instructions
4. **docs/reference/maturity-levels.md** — 4 maturity levels from PoC to Production

**Purpose**: Load context about framework architecture (Improved Hybrid Approach), mandatory constraints (HTTP-only data access, service separation), available documentation, and maturity level options.

**Expected outcome**: AI understands:
- Framework-as-submodule model
- Improved Hybrid Approach architecture
- Mandatory constraints (HTTP-only data access, service separation, etc.)
- **Maturity levels** (PoC ~5 min, Development ~10 min, Pre-Production ~15 min, Production ~30 min)
  - **Core Principle**: Maturity Level = Scope Selector (how many features), NOT Quality Selector (how complete)
  - Level 1: min(features) × 100% completion | Level 4: all(features) × 100% completion
  - All levels require complete, production-quality code; only infrastructure features and coverage thresholds vary
- Where to find specific information during workflow execution

### **Stage 1-6: Dynamic Reading** (During workflow execution)

After initialization, AI reads documents **on-demand** based on the current workflow stage.

**Navigation Guide**: See [AI Navigation Matrix](docs/reference/ai-navigation-matrix.md) for exact document mapping per stage. This matrix shows:
- Which documents to read at each stage
- What outputs AI should generate
- Which tools/templates to use
- Success criteria for each stage

**Key Principle**: Don't read everything upfront. Read what's needed for the current stage to minimize context usage and maximize efficiency.

---

## Documentation Hierarchy

> **NAVIGATION GUIDE**: Each document has a single purpose. Use the references below instead of duplicating content.

### Primary Documentation (Essential Reading)

- **[README.md](docs/LINKS_REFERENCE.md#core-documentation)** — intro, quick start, value proposition.
- **[Technical Specifications](docs/LINKS_REFERENCE.md#core-documentation)** — technology versions and configurations.
- **[Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation)** — mandatory architecture principles and communication patterns.
- **[Development Commands](docs/LINKS_REFERENCE.md#developer-guides)** — canonical command catalog for local/dev/CI operations.
- **[Agent Workflow](docs/INDEX.md#documentation-pillars)** — end-to-end process for AI agents.

### Reference Materials

- **[Agent Context Summary](docs/INDEX.md#reference-materials)** — fastest orientation for agents; links to critical rules.
- **[Agent Toolbox](docs/INDEX.md#reference-materials)** — machine-friendly command lookup.
- **[Deliverables Catalog](docs/INDEX.md#reference-materials)** — required artefacts and storage locations.
- **[Prompt Templates](docs/INDEX.md#reference-materials)** — reusable prompts for clarification and reporting.
- **[Project Structure](docs/LINKS_REFERENCE.md#developer-guides)** — canonical repository layout when the framework is a submodule.
- **[Troubleshooting](docs/LINKS_REFERENCE.md#developer-guides)** — symptom-based diagnostics and recovery playbook.

### Agent Templates & Checklists

- **[Prompt Validation Guide](docs/INDEX.md#agent-templates-checklists)** — ensure user prompt completeness before any work.
- **[Requirements Intake Template](docs/INDEX.md#agent-templates-checklists)** — structured capture of inputs.
- **[Implementation Plan Template](docs/INDEX.md#agent-templates-checklists)** — planning artefact for approval.
- **[Agent Verification Checklist](docs/INDEX.md#agent-templates-checklists)** — mandatory quality gates.
- **[QA Report Template](docs/INDEX.md#agent-templates-checklists)** — final summary for stakeholders.
- **[Architecture Decision Log Template](docs/INDEX.md#reference-materials)** — standardized ADR format when major decisions arise.

### IDE Rules & Patterns

- See `docs/LINKS_REFERENCE.md#ide-rules-and-patterns` for machine-readable rules covering architecture, services, infrastructure, observability, and quality.

### Quick Navigation

| Need | Go To |
|------|-------|
| Validate a new prompt | [Prompt Validation Guide](docs/INDEX.md#agent-templates-checklists) |
| Prepare requirements | [Requirements Intake Template](docs/INDEX.md#agent-templates-checklists) |
| Build a plan | [Implementation Plan Template](docs/INDEX.md#agent-templates-checklists) |
| Execute tasks | [Agent Workflow](docs/INDEX.md#documentation-pillars) + [Agent Toolbox](docs/INDEX.md#reference-materials) |
| Verify quality | [Agent Verification Checklist](docs/INDEX.md#agent-templates-checklists) |
| Report results | [QA Report Template](docs/INDEX.md#agent-templates-checklists) |

## Framework Overview

This framework implements the **Improved Hybrid Approach** with FastAPI, Aiogram, and AsyncIO services, strict HTTP-only data access, and RabbitMQ eventing.

> **COMPLETE ARCHITECTURE DETAILS**: See [Architecture Guide](docs/LINKS_REFERENCE.md#core-documentation) for detailed principles, constraints, service types, and implementation guidelines.

## Template Service Naming

**IMPORTANT**: Framework templates use the `template_` context prefix to indicate placeholder names that must be replaced when generating real applications.

**Template Service Names**:
- `template_business_api` — FastAPI business logic service
- `template_business_bot` — Aiogram Telegram bot service
- `template_business_worker` — AsyncIO background worker service
- `template_data_postgres_api` — PostgreSQL HTTP data access service
- `template_data_mongo_api` — MongoDB HTTP data access service

**When Generating Code**: Replace with actual `{context}_{domain}_{type}` names:
- P2P Lending: `template_business_api` → `finance_lending_api`
- Telemedicine: `template_business_api` → `healthcare_telemedicine_api`
- Construction Bot: `template_business_bot` → `construction_house_bot`

**See**: [Template Naming Guide](docs/guides/template-naming-guide.md) for complete renaming instructions and examples.

**Why `template_` prefix?**:
- Clearly signals these are placeholders, not production service names
- Follows mandatory `{context}_{domain}_{type}` naming pattern ([Naming Conventions](docs/atomic/architecture/naming/README.md))
- Prevents confusion about whether templates represent real business services

**Service Naming Philosophy**:
- **DEFAULT TO 3-PART** (`{context}_{domain}_{type}`) — 80-90% of services
- Use 4-part ONLY when domain is ambiguous (burden of proof required)
- See [Service Naming Checklist](docs/checklists/service-naming-checklist.md) for quick decision
- See [10 Serious Reasons for 4-Part Naming](docs/atomic/architecture/naming/naming-4part-reasons.md) for detailed criteria

## Agent Workflow (High-Level)

For the **complete 7-stage AI code generation process** with detailed instructions, examples, and navigation matrix, see:

**→ [AI Code Generation Master Workflow](docs/guides/ai-code-generation-master-workflow.md)**

This unified workflow document includes:
- **Part 1**: AI Reading Order (what to read when)
- **Part 2**: 7-Stage Process (Init → Validation → Intake → Planning → Generation → Verification → Handoff)
- **Part 3**: Navigation Matrix (exact documents per stage)
- **Part 4**: Example Walkthrough (complete P2P lending example)
- **Part 5**: Common Issues & Recovery

**Quick stage summary**:
1. **Stage 0**: AI Initialization (load framework context)
2. **Stage 1**: Prompt Validation (ensure completeness)
3. **Stage 2**: Requirements Clarification & Intake (structured capture)
4. **Stage 3**: Architecture Mapping & Planning (detailed plan)
5. **Stage 4**: Code Generation (phase-by-phase implementation)
6. **Stage 5**: Quality Verification (all checks pass)
7. **Stage 6**: QA Report & Handoff (stakeholder sign-off)

## Important Notes

- Never modify framework files when used as submodule; generate application code under the host project ([README.md](README.md)).
- Maintain `.env` files, Docker configurations, and shared components per [Shared Components Guide](docs/guides/shared-components.md).
- Use ADR template for significant decisions impacting architecture or infrastructure.
- Reference [Technical Specifications](docs/reference/tech_stack.md) when selecting technologies or versions.
- Update documentation and changelog (when available) in tandem with code changes.

## Framework Management

- See [Project Structure Guide](docs/LINKS_REFERENCE.md#developer-guides) for complete submodule operations and development workflow.
- Keep documentation synchronized: update `docs/INDEX.md` and `docs/reference/agent-context-summary.md` when new files are added.
- Follow [Style Guide](docs/STYLE_GUIDE.md) for formatting and wording.
