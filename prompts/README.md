# Project Prompts

This directory contains **shared prompt templates** for the entire team. These prompts are versioned in git and accessible to all project contributors.

## Purpose

Reusable prompt templates for:
- Documentation audits
- Code reviews
- Architecture validation
- Quality checks
- AI-assisted development workflows

## Usage

### In Claude Code

Reference prompts using `@` mentions:

```
@prompts/documentation_audit.md run full audit
```

### In Scripts

Reference prompts from scripts:

```bash
# Read prompt template
cat prompts/documentation_audit.md

# Use with AI agent
claude-code "$(cat prompts/documentation_audit.md)"
```

## Available Prompts

| Prompt | Purpose | When to Use |
|--------|---------|-------------|
| `documentation_audit.md` | Comprehensive documentation audit with purpose-alignment focus | Monthly audits, before releases, when docs change |

## Adding New Prompts

When creating a new prompt template:

1. **Location**: Save in `prompts/` directory (not `.claude/prompts/`)
2. **Naming**: Use descriptive names: `{action}_{target}.md`
   - Examples: `review_architecture.md`, `validate_security.md`
3. **Format**: Follow structure:
   ```markdown
   # {Prompt Name}

   ## Purpose
   Clear description of what this prompt does

   ## Usage
   How to use this prompt

   ## Full Prompt
   ```
   The actual prompt content here
   ```
   ```
4. **Documentation**: Update this README with new prompt in table above

## Personal vs Shared Prompts

```
📁 prompts/                   ← Shared (in git, accessible via @)
├── documentation_audit.md
├── code_review.md
└── README.md

📁 .claude/prompts/           ← Personal (gitignored, private)
├── my_shortcuts.md
└── custom_templates.md
```

**Use `prompts/`** for:
- Team-wide standards
- Project-specific workflows
- Documentation that everyone needs

**Use `.claude/prompts/`** for:
- Personal shortcuts
- Experimental prompts
- Private configurations

## Versioning

All prompts in this directory are versioned with git. When updating:

1. Make changes to prompt file
2. Test the prompt
3. Commit with descriptive message:
   ```bash
   git add prompts/documentation_audit.md
   git commit -m "docs: enhance documentation audit with purpose alignment"
   ```

## Maintenance

- **Review**: Quarterly review of all prompts
- **Update**: Keep prompts aligned with project evolution
- **Deprecate**: Move outdated prompts to `prompts/deprecated/`
