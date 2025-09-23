# Documentation Style Guide

> **📋 PURPOSE**: Unified formatting standards for all project documentation to improve readability and navigation.

## Header Standards

### Header Format
```markdown
# Main Document Title
## 🔧 Section with Emoji (for important sections)
## Section without Emoji (for regular sections)
### Subsection
#### Detailed Subsection
```

### Recommended Section Emojis
- 🏗️ **Architecture** - architectural sections
- 📋 **Commands/Lists** - commands, lists, instructions
- 🔧 **Technical** - technical details, configurations
- 💻 **Examples** - code examples and implementations
- 🎯 **Goals/Objectives** - goals, objectives
- ⚠️ **Important/Mandatory** - important requirements, constraints
- 📖 **References** - links, additional materials
- 🐛 **Troubleshooting** - problem solving
- 🚀 **Getting Started** - quick start, introduction

## Link Standards

### Internal Links
```markdown
<!-- PREFERRED: Links through central table -->
See [Architecture Guide](LINKS_REFERENCE.md#core-documentation)

<!-- AVOID: Direct links with submodule variants -->
[docs/guides/ARCHITECTURE_GUIDE.md](docs/guides/ARCHITECTURE_GUIDE.md) *(or [.framework/...])*
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
> **🏗️ ARCHITECTURAL FOUNDATION**: Principle description

<!-- For mandatory requirements -->
> **⚠️ MANDATORY**: Mandatory requirement

<!-- For links to additional materials -->
> **📖 DETAILS**: See [document](link) for detailed information
```

### Requirement Lists
```markdown
#### Mandatory Requirements (MANDATORY)
- **Requirement 1**: Description
- **Requirement 2**: Description

#### Prohibited Practices (PROHIBITED)
- ❌ **Practice 1**: Why prohibited
- ❌ **Practice 2**: Why prohibited
```

## Table Standards

### Navigation Tables
```markdown
| Task | Document |
|------|----------|
| 🏁 **Quick start** | [Link](path) |
| 🏗️ **Understand architecture** | [Link](path) |
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
# ✅ CORRECT: Description of correct approach
async def good_example():
    return await some_async_operation()

# ❌ INCORRECT: Description of incorrect approach
def bad_example():
    return sync_operation()
```
```

## Document Structure

### Standard Document Template
```markdown
# Document Title

> **📋 PURPOSE**: Brief description of document purpose

## Table of Contents
- [Section 1](#section-1)
- [Section 2](#section-2)

---

## 🎯 Main Content

Main document content...

## 📖 Related Documents

- **Architecture**: [Link](LINKS_REFERENCE.md#core-documentation)
- **Examples**: [Link](LINKS_REFERENCE.md#examples-and-templates)

---

> **📖 NAVIGATION**: To return to main guide see [CLAUDE.md](../CLAUDE.md)
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
- [ ] Standard emojis applied for sections
- [ ] No duplication of information from other documents
- [ ] Links to related documents included
- [ ] Structure follows template

---

> **📖 APPLICATION**: Use this guide when creating and editing all project documents to maintain style consistency.