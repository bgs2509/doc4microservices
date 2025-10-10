# Documentation File Naming Conventions

This guide covers naming patterns for documentation files in the doc4microservices framework. It implements a two-tier strategy distinguishing entry points from content files.

**Key Principle**: Use SCREAMING_SNAKE_CASE for entry points, kebab-case for content. This maximizes visibility of critical files while maintaining web-friendly URLs for content.

---

## Two-Tier Naming Strategy

Documentation files fall into two categories with different naming conventions:

| Category | Pattern | Example | Purpose |
|----------|---------|---------|---------|
| **Entry Points** | SCREAMING_SNAKE_CASE | `README.md`, `CLAUDE.md` | First files humans/AI read |
| **Content Files** | kebab-case | `naming-conventions.md` | Reference and guide documents |

### Decision Rule

Ask: **"Is this the FIRST file someone reads when discovering this project/directory?"**
- **YES** → Entry point → `SCREAMING_SNAKE_CASE.md`
- **NO** → Content → `kebab-case.md`

---

## Entry Point Files

### Standard Entry Points

```
README.md            # Project/directory main entry
CLAUDE.md           # AI agent instructions
LICENSE             # Legal terms
CONTRIBUTING.md     # Contribution guidelines
CHANGELOG.md        # Version history
SECURITY.md         # Security policies
CODE_OF_CONDUCT.md  # Community standards
```

### Why SCREAMING_SNAKE_CASE?

1. **Industry Convention**: GitHub, npm, PyPI expect README.md
2. **Maximum Visibility**: Stands out in file listings
3. **Special Treatment**: Tools recognize and prioritize these files
4. **Historical Standard**: Unix tradition (LICENSE, INSTALL, AUTHORS)

### Entry Point Hierarchy

```
project/
├── README.md              # Project entry point
├── CLAUDE.md             # AI entry point
├── LICENSE               # Legal entry point
├── docs/
│   ├── README.md         # Docs entry point
│   ├── atomic/
│   │   ├── README.md     # Atomic docs entry
│   │   └── architecture/
│   │       ├── README.md # Architecture entry
│   │       └── naming-guide.md  # Content file
```

---

## Content Files

### Content File Patterns

```
# Guides and references
naming-conventions.md
architecture-guide.md
python-style-guide.md
deployment-checklist.md

# Technical documentation
api-reference.md
database-schema.md
integration-guide.md

# Process documentation
code-review-process.md
release-notes-v1.md
migration-guide.md
```

### Why kebab-case?

1. **URL-Friendly**: Direct mapping to web URLs
2. **SEO-Optimized**: Search engines prefer hyphens
3. **GitHub Pages**: Clean URLs without encoding
4. **Readability**: Natural word separation
5. **Tool Compatibility**: Static site generators expect it

### kebab-case Rules

```
# Good examples
user-authentication-guide.md    ✅
api-v2-migration.md            ✅
2024-01-release-notes.md       ✅
faq.md                          ✅

# Bad examples
user_authentication_guide.md    ❌ (underscores)
userAuthenticationGuide.md      ❌ (camelCase)
USER-AUTHENTICATION-GUIDE.md    ❌ (unless entry point)
user-authentication-guide.MD    ❌ (uppercase extension)
```

---

## Special Cases

### Index Files

```
INDEX.md            # Directory index (entry point)
index.md            # Web root index (content)
```

### Configuration Documentation

```
.env.example        # Example config (dot file)
config-guide.md     # Config documentation
```

### Template Files

```
TEMPLATE_README.md           # Template entry point
template-service.md          # Template content
pull-request-template.md    # GitHub template
```

---

## Directory Organization

### Atomic Documentation Structure

```
docs/
├── README.md                    # Entry point
├── INDEX.md                     # Documentation index
├── atomic/
│   ├── README.md               # Atomic entry
│   ├── architecture/
│   │   ├── README.md           # Architecture entry
│   │   ├── naming/
│   │   │   ├── README.md       # Naming hub
│   │   │   ├── naming-services.md
│   │   │   └── naming-python.md
│   │   └── service-patterns.md
│   └── testing/
│       ├── README.md           # Testing entry
│       ├── unit-testing.md
│       └── integration-testing.md
```

### Content Grouping

Group related content with consistent naming:

```
docs/guides/
├── getting-started.md
├── quick-start.md
├── installation-guide.md
├── configuration-guide.md
├── deployment-guide.md
└── troubleshooting-guide.md

docs/reference/
├── api-reference.md
├── cli-reference.md
├── configuration-reference.md
└── error-reference.md
```

---

## File Extensions

### Markdown Files

Always use lowercase `.md`:

```
README.md     ✅
readme.MD     ❌
README.markdown  ❌
```

### Other Documentation Formats

```
architecture.puml    # PlantUML
schema.json         # JSON Schema
openapi.yaml        # OpenAPI spec
diagram.drawio      # Draw.io diagram
```

---

## Versioned Documentation

### Version in Filename

```
migration-guide-v2.md
api-reference-v1.md
changelog-2024.md
release-notes-1.0.0.md
```

### Version Directories

```
docs/
├── v1/
│   └── api-reference.md
├── v2/
│   └── api-reference.md
└── latest/
    └── api-reference.md
```

---

## Language-Specific Docs

Use ISO 639-1 codes:

```
README.md           # Default (English)
README.ru.md        # Russian
README.zh-cn.md     # Simplified Chinese
README.es.md        # Spanish
```

---

## Checklist

- [ ] Entry points use SCREAMING_SNAKE_CASE
- [ ] Content files use kebab-case
- [ ] File extensions are lowercase `.md`
- [ ] No spaces in filenames
- [ ] Version numbers follow pattern
- [ ] Language codes use ISO 639-1
- [ ] README.md exists at each major directory
- [ ] Consistent naming within directories

---

## Common Patterns Reference

| File Type | Example | Pattern |
|-----------|---------|---------|
| Project entry | `README.md` | SCREAMING |
| AI instructions | `CLAUDE.md` | SCREAMING |
| Legal | `LICENSE` | SCREAMING |
| Guide | `setup-guide.md` | kebab-case |
| Reference | `api-reference.md` | kebab-case |
| Checklist | `deployment-checklist.md` | kebab-case |
| Template | `template-service.md` | kebab-case |
| Notes | `release-notes-v1.md` | kebab-case |

---

## Related Documents

- `../README.md` — Main naming conventions hub
- `../../STYLE_GUIDE.md` — Documentation writing style
- `../../guides/DOCUMENTATION_GUIDE.md` — Documentation structure patterns