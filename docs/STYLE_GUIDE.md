# Documentation Style Guide

> **PURPOSE**: Unified formatting standards for all project documentation to improve readability and navigation.

## Header Standards

### Header Format
```markdown
# Main Document Title
## Section Header
### Subsection
#### Detailed Subsection
```

## Link Standards

### Internal Links
```markdown
<!-- PREFERRED: Links through central table -->
See [Architecture Guide](LINKS_REFERENCE.md#core-documentation)

<!-- AVOID: Direct links with submodule variants -->
[Architecture Guide](guides/architecture-guide.md) *(or `.framework/docs/...` in submodule mode)*
```

### External Links
```markdown
<!-- Correct format -->
[GitHub Repository](https://github.com/user/repo)
```

## Emphasis and Quote Standards

### Important Blocks
```markdown
<!-- For architectural principles -->
> **ARCHITECTURAL FOUNDATION**: Principle description

<!-- For mandatory requirements -->
> **MANDATORY**: Mandatory requirement

<!-- For links to additional materials -->
> **DETAILS**: See [Link Standards](#link-standards) for detailed information
```

### Requirement Lists
```markdown
#### Mandatory Requirements (MANDATORY)
- **Requirement 1**: Description
- **Requirement 2**: Description

#### Prohibited Practices (PROHIBITED)
- **Practice 1**: Why prohibited
- **Practice 2**: Why prohibited
```

## Table Standards

### Navigation Tables
```markdown
| Task | Document |
|------|----------|
| **Quick start** | [Example Link](guides/architecture-guide.md) |
| **Understand architecture** | [Example Link](guides/architecture-guide.md) |
```

### Technical Specifications
```markdown
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| **Runtime** | Python | 3.12+ | Main platform |
| **Web Framework** | FastAPI | Latest | API services |
```

## Code Standards

### Code Examples
```markdown
```python
# CORRECT: Description of correct approach
async def good_example():
    return await some_async_operation()

# INCORRECT: Description of incorrect approach
def bad_example():
    return sync_operation()
```
```

## Document Structure

### Standard Document Template
```markdown
# Document Title

> **PURPOSE**: Brief description of document purpose

## Table of Contents
- [Header Standards](#header-standards)
- [Link Standards](#link-standards)

---

## Main Content

Main document content...

## Related Documents

- **Architecture**: [Link](LINKS_REFERENCE.md#core-documentation)
- **Implementation Guide**: [Link](LINKS_REFERENCE.md#developer-guides)

---

> **NAVIGATION**: To return to main guide see [AGENTS.md](LINKS_REFERENCE.md#core-documentation)
```

## Writing Principles

### Tone and Style
- **Conciseness**: Avoid unnecessary words
- **Precision**: Use specific terms
- **Structure**: Logical sequence of sections
- **Relevance**: Regularly update content

### Avoid Duplication
- Reference central links table instead of repeating paths
- Reference canonical sources instead of copying information
- Use brief overviews + links instead of full duplication

## Quality Control

### Pre-publication Checklist
- [ ] All internal links work
- [ ] Consistent header style used
- [ ] No duplication of information from other documents
- [ ] Links to related documents included
- [ ] Structure follows template

---

> **APPLICATION**: Use this guide when creating and editing all project documents to maintain style consistency.
