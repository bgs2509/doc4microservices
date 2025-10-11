# Naming Conventions

> **📦 CONTENT MOVED**: This document has been reorganized into specialized files for better maintainability.

The naming conventions content has been split into focused, atomic documents following the hub-and-spoke pattern. Each document covers a specific aspect of naming in depth.

---

## 📍 New Location: naming/ Directory

**Main Hub (start here):**
- **[naming/README.md](naming/README.md)** — Complete naming guide with Quick Reference Table and AI Decision Tree

**Specialized Guides:**
- **[naming/naming-services.md](naming/naming-services.md)** — Service naming patterns (3-part vs 4-part formula)
- **[naming/naming-4part-reasons.md](naming/naming-4part-reasons.md)** — 10 serious reasons for using 4-part naming
- **[naming/naming-python.md](naming/naming-python.md)** — Python classes, functions, variables, and file naming
- **[naming/naming-infrastructure.md](naming/naming-infrastructure.md)** — Docker Compose, Kubernetes, Nginx configuration
- **[naming/naming-databases.md](naming/naming-databases.md)** — PostgreSQL and MongoDB naming conventions
- **[naming/naming-documentation.md](naming/naming-documentation.md)** — Documentation file naming (SCREAMING vs kebab-case)
- **[naming/naming-conversion.md](naming/naming-conversion.md)** — Dev→Prod name transformation utilities

---

## Why This Change?

1. **Atomic Documentation**: Each file now has a single, clear purpose (<600 lines)
2. **Better Navigation**: Find exactly what you need without scrolling through 1830 lines
3. **Maintainability**: Easier to update specific sections without affecting others
4. **Hub-and-Spoke Pattern**: Central hub (naming/README.md) with links to all specialized content

---

## Backward Compatibility

This file remains as a redirect for existing links and documentation. All original content is preserved and enhanced in the new structure.

---

## Related Documents

- `docs/atomic/architecture/context-registry.md` — Authorized context names for services
- `docs/atomic/architecture/service-separation-principles.md` — Service boundary definitions
- `docs/atomic/architecture/improved-hybrid-overview.md` — Overall architecture approach
- `docs/guides/template-naming-guide.md` — Template service renaming instructions
- `docs/checklists/service-naming-checklist.md` — Quick service naming decisions
