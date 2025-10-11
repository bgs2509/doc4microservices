# Contributing to doc4microservices

> **PURPOSE**: Guidelines for contributing to the microservices framework and atomic documentation knowledge base.

## Table of Contents

- [Framework Development Model](#framework-development-model)
- [Atomic Documentation Contribution](#atomic-documentation-contribution)
- [Pull Request Process](#pull-request-process)
- [Code Contribution Guidelines](#code-contribution-guidelines)
- [Quality Standards](#quality-standards)

---

## Framework Development Model

### Framework-as-Submodule Architecture

This repository is designed to be used as a **Git submodule** in your projects:

```bash
# In your project
git submodule add <repo-url> .framework
```

**IMPORTANT**:
- **NEVER modify framework files** when used as a submodule in your application
- Framework contributions happen **in this repository**
- Application code stays **separate in the host project**

### Repository Structure

```
doc4microservices/
├── docs/                    # Framework documentation
│   ├── atomic/             # Atomic knowledge base
│   ├── guides/             # Implementation guides
│   ├── reference/          # Reference materials
│   └── INDEX.md            # Documentation catalog
├── prompts/                # AI agent prompts
├── scripts/                # Validation and automation scripts
├── CLAUDE.md               # AI agent entry point
└── README.md               # Project overview
```

---

## Atomic Documentation Contribution

### Creating New Atomic Documents

**MANDATORY**: Always use the universal template:

```bash
# 1. Copy template to appropriate category
cp docs/atomic/TEMPLATE.md docs/atomic/{category}/{your-topic}.md

# 2. Edit file and replace placeholders:
#    - {Topic Title} → Your specific topic name
#    - {Brief introduction} → 1-3 paragraphs explaining what, why, when
#    - Add code examples with CORRECT/INCORRECT patterns
#    - Link 2-3+ related documents

# 3. Remove reference sections:
#    - Delete "Category-Specific Section Guide"
#    - Delete "Validation Checklist"

# 4. Update indexes
#    - Add entry to docs/INDEX.md
#    - Add entry to docs/atomic/README.md if creating new category
```

### Updating Existing Documents

1. **Read current version** - Understand existing content
2. **Check template compliance** - Verify structure matches `docs/atomic/TEMPLATE.md`
3. **Update content** - Improve clarity, add examples, update versions
4. **Verify links** - Ensure all related document links work
5. **Test code examples** - Validate all Python code runs correctly

### Atomic Documentation Principles

| Principle | Description | Example |
|-----------|-------------|---------|
| **Single Responsibility** | One topic = one file | ✅ `redis-connection-management.md` <br> ❌ `redis-everything.md` |
| **Concise** | Keep focused, typically < 200 lines | Short, scannable documents |
| **Definitive** | Authoritative source for the topic | This is the SSOT |
| **Linked** | Reference related docs, don't duplicate | Use links instead of copying |
| **Practical** | Include working code examples | Real-world guidance |
| **Current** | Use latest versions (Python 3.12+) | No outdated patterns |

---

## Pull Request Process

### Before Submitting PR

**MANDATORY**: Run full documentation validation:

```bash
# 1. Validate all documentation
./scripts/audit_docs.sh --full

# 2. Check for critical issues
./scripts/audit_docs.sh --links
./scripts/audit_docs.sh --structure

# 3. Fix all CRITICAL and HIGH priority issues
```

### PR Checklist

Before submitting a pull request, ensure:

- [ ] All validation scripts pass (`./scripts/audit_docs.sh --full`)
- [ ] No broken internal links
- [ ] No TODO placeholders in final documents
- [ ] All code examples use Python 3.12+ with type hints
- [ ] Code examples follow CORRECT/INCORRECT pattern (when applicable)
- [ ] New atomic documents follow `docs/atomic/TEMPLATE.md` structure
- [ ] `docs/INDEX.md` updated if adding new documents
- [ ] `docs/atomic/README.md` updated if adding new category
- [ ] No sensitive data (passwords, tokens, real IPs)
- [ ] Follows `docs/STYLE_GUIDE.md` conventions

### PR Description Template

```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] Documentation improvement
- [ ] New atomic document
- [ ] Bug fix (broken link, typo, incorrect example)
- [ ] New feature (new template, guide, reference)
- [ ] Breaking change (structural reorganization)

## Testing
- [ ] Ran `./scripts/audit_docs.sh --full`
- [ ] Tested all code examples
- [ ] Verified all links

## Related Issues
Closes #XXX
```

### Review Process

1. **Automated checks** - CI runs validation scripts
2. **Peer review** - At least one documentation team member reviews
3. **Merge approval** - Maintainer approves and merges
4. **Submodule update** - Users run `git submodule update --remote` to get changes

---

## Code Contribution Guidelines

### Python Code Examples

**MANDATORY**: All Python code examples MUST:

- Use **Python 3.12+** syntax
- Include **type hints** (PEP 484)
- Follow **async/await** patterns for I/O operations
- Include **docstrings** for functions
- Follow **PEP 8** style guide

**Example**:

```python
# ✅ CORRECT: Full example with type hints, async, docstring
from typing import List
from pydantic import BaseModel

async def fetch_users(limit: int = 10) -> List[User]:
    """Fetch users from data service.

    Args:
        limit: Maximum number of users to return

    Returns:
        List of user instances

    Raises:
        HTTPError: If data service is unreachable
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://finance_user_api:8000/users",
            params={"limit": limit}
        )
        response.raise_for_status()
        return [User(**u) for u in response.json()]

# ❌ INCORRECT: No type hints, sync code, no docstring
def get_users(limit):
    response = requests.get(f"http://api:8000/users?limit={limit}")
    return response.json()
```

### Bash Script Examples

**MANDATORY**: All bash scripts MUST:

- Pass **shellcheck** validation
- Include **error handling** (`set -e`)
- Use **proper quoting** for variables
- Include **comments** explaining purpose

**Example**:

```bash
# ✅ CORRECT: Shellcheck-compliant, error handling
#!/bin/bash
set -euo pipefail

# Validate all markdown files for broken links
DOCS_DIR="${1:-docs}"

if [ ! -d "$DOCS_DIR" ]; then
    echo "Error: Directory $DOCS_DIR not found" >&2
    exit 1
fi

find "$DOCS_DIR" -name "*.md" -print0 | \
    xargs -0 -P 4 grep -Hn '\[.*\](.*\.md'
```

### Naming Conventions

**MANDATORY**: Follow project naming standards:

| Element | Convention | Example |
|---------|-----------|---------|
| **Documentation files** | kebab-case | `redis-connection-management.md` |
| **Python files** | snake_case | `finance_lending_api.py` |
| **Python variables** | snake_case | `user_data`, `loan_amount` |
| **Python classes** | PascalCase | `UserCreateDTO`, `LoanService` |
| **Service names** | {context}_{domain}_{type} | `finance_lending_api` |
| **Database tables** | snake_case | `user_accounts`, `loan_applications` |

See [Naming Conventions](docs/atomic/architecture/naming/README.md) for complete guide.

---

## Quality Standards

### Documentation Quality Gates

**CRITICAL** (must pass):
- Zero broken internal links
- All code examples syntactically valid
- `docs/INDEX.md` matches actual file structure
- No TODO placeholders in published docs

**HIGH** (should pass):
- All atomic documents follow TEMPLATE.md structure
- Code examples include CORRECT/INCORRECT patterns
- Related Documents section has 2-3+ links
- Python 3.12+ syntax in all examples

**MEDIUM** (nice to have):
- Readability score appropriate for technical audience
- Consistent terminology across documents
- No duplicate content

### Code Quality Gates

For any Python code contributed (templates, scripts, examples):

```bash
# Type checking
mypy --strict your_module.py

# Linting
ruff check your_module.py

# Formatting
ruff format your_module.py

# Testing
pytest tests/
```

### Validation Commands

**Before committing**:

```bash
# Quick validation
./scripts/audit_docs.sh --quick

# Full audit
./scripts/audit_docs.sh --full > audit_results.txt

# Check specific areas
./scripts/audit_docs.sh --links
./scripts/audit_docs.sh --structure
./scripts/audit_docs.sh --spelling
```

---

## Style Guidelines

### Documentation Style

**MANDATORY**: Follow `docs/STYLE_GUIDE.md` for:

- Header hierarchy (H1 for title, H2 for sections, etc.)
- Link format (use relative paths)
- Code block format (with language tags)
- Table format (with headers)
- Emphasis format (bold for important terms)

### Writing Tone

- **Concise**: Avoid unnecessary words
- **Precise**: Use specific technical terms
- **Imperative**: Use command form ("Use X" not "You should use X")
- **Professional**: Technical documentation, not marketing copy

**Example**:

```markdown
✅ GOOD:
Use Redis connection pooling to manage concurrent requests efficiently.

❌ BAD:
You might want to consider using Redis connection pooling because it's really
important for managing lots of concurrent requests in your amazing application!
```

---

## Common Mistakes to Avoid

1. **Creating documents without using TEMPLATE.md**
   - ❌ Result: Inconsistent structure, missing sections
   - ✅ Fix: Always `cp docs/atomic/TEMPLATE.md ...`

2. **Not updating INDEX.md**
   - ❌ Result: Documents not discoverable
   - ✅ Fix: Add entry to `docs/INDEX.md` when creating files

3. **Using outdated Python versions**
   - ❌ Result: Users copy old patterns
   - ✅ Fix: Always use Python 3.12+, latest library versions

4. **Including sensitive data**
   - ❌ Result: Security risk
   - ✅ Fix: Use placeholders (example: `your-api-key`, `your-database-password`)

5. **Duplicating content from other documents**
   - ❌ Result: Maintenance nightmare
   - ✅ Fix: Link to other docs instead of copying

6. **Not removing TEMPLATE.md reference sections**
   - ❌ Result: Published docs contain meta-instructions
   - ✅ Fix: Delete "Category-Specific Section Guide" and "Validation Checklist"

---

## Getting Help

### Documentation Questions

- **Template usage**: See `docs/atomic/TEMPLATE.md` instructions
- **Atomic documentation**: See `docs/atomic/README.md`
- **Style guide**: See `docs/STYLE_GUIDE.md`
- **Architecture**: See `docs/guides/architecture-guide.md`

### Technical Questions

- **Framework setup**: See `README.md`
- **AI agent workflow**: See `docs/guides/ai-code-generation-master-workflow.md`
- **Technology stack**: See `docs/reference/tech_stack.md`
- **Troubleshooting**: See `docs/reference/troubleshooting.md`

### Community

- **Issues**: Open an issue for bugs, feature requests, questions
- **Discussions**: Use GitHub Discussions for general questions
- **Pull Requests**: Submit PRs with clear description and checklist

---

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (see [LICENSE](LICENSE)).

---

## Recognition

Contributors are recognized in:
- Git commit history
- GitHub Contributors page
- Release notes (for significant contributions)

Thank you for contributing to doc4microservices! 🎉

---

**Last Updated**: 2025-10-11
**Maintainers**: Documentation Team
