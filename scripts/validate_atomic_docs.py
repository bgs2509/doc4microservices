#!/usr/bin/env python3
"""Validate atomic documentation files against the standard.

This script checks atomic documents for compliance with the standard
defined in docs/atomic/TEMPLATE.md.

Usage:
    python scripts/validate_atomic_docs.py [file_path]
    python scripts/validate_atomic_docs.py docs/atomic/services/fastapi/basic-setup.md
    python scripts/validate_atomic_docs.py  # validates all atomic docs
"""

import sys
from pathlib import Path
from typing import List, Tuple


class DocumentValidator:
    """Validator for atomic documentation files."""

    def __init__(self, filepath: Path):
        """Initialize validator with document path.

        Args:
            filepath: Path to the document to validate
        """
        self.filepath = filepath
        self.content = filepath.read_text(encoding="utf-8")
        self.lines = self.content.split("\n")
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validation checks.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self._check_h1_title()
        self._check_introduction()
        self._check_related_documents()
        self._check_no_todo_placeholders()
        self._check_code_examples()
        self._check_reference_sections_removed()

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _check_h1_title(self) -> None:
        """Check that document starts with H1 title."""
        if not self.content.strip().startswith("# "):
            self.errors.append("Missing H1 title at document start")
            return

        first_line = self.lines[0]
        if "{" in first_line and "}" in first_line:
            self.errors.append(f"H1 title contains placeholder: {first_line}")

    def _check_introduction(self) -> None:
        """Check that document has introduction paragraphs."""
        # Skip H1 and empty lines
        content_start = 0
        for i, line in enumerate(self.lines):
            if line.startswith("# "):
                content_start = i + 1
                break

        # Find first ## header
        first_h2 = len(self.lines)
        for i in range(content_start, len(self.lines)):
            if self.lines[i].startswith("## "):
                first_h2 = i
                break

        # Count paragraphs between H1 and first H2
        intro_lines = self.lines[content_start:first_h2]
        intro_text = "\n".join(intro_lines).strip()

        # Skip instruction blocks
        intro_text = "\n".join(
            line
            for line in intro_text.split("\n")
            if not line.startswith(">")
        )

        if len(intro_text) < 50:  # Minimum introduction length
            self.warnings.append(
                "Introduction appears too short (< 50 chars). "
                "Add 1-3 paragraphs explaining what, why, when."
            )

    def _check_related_documents(self) -> None:
        """Check for Related Documents section."""
        if "## Related Documents" not in self.content:
            self.errors.append("Missing '## Related Documents' section")
            return

        # Count links in Related Documents section
        in_related_section = False
        link_count = 0

        for line in self.lines:
            if line.startswith("## Related Documents"):
                in_related_section = True
                continue
            if in_related_section and line.startswith("## "):
                break
            if in_related_section and line.strip().startswith("- "):
                link_count += 1

        if link_count < 2:
            self.warnings.append(
                f"Related Documents section has only {link_count} link(s). "
                "Add at least 2-3 related document links."
            )

    def _check_no_todo_placeholders(self) -> None:
        """Check for TODO placeholders."""
        if "TODO:" in self.content or "TODO " in self.content:
            # Check if it's a stub file
            if "TODO: Populate authoritative guidance" in self.content:
                self.errors.append(
                    "Document is a TODO stub. Fill in content using TEMPLATE.md"
                )
            else:
                self.warnings.append("Document contains TODO placeholders")

    def _check_code_examples(self) -> None:
        """Check code examples follow conventions."""
        if "```python" not in self.content:
            # Not all documents need code examples
            return

        # Check for CORRECT/INCORRECT pattern
        has_correct = "# CORRECT:" in self.content
        has_incorrect = "# INCORRECT:" in self.content

        if not has_correct and "```python" in self.content:
            self.warnings.append(
                "Python code examples should include '# CORRECT:' comments"
            )

        # Check for hyphens in code (common mistake)
        in_code_block = False
        for line in self.lines:
            if line.strip().startswith("```python"):
                in_code_block = True
                continue
            if in_code_block and line.strip().startswith("```"):
                in_code_block = False
                continue

            if in_code_block:
                # Check for hyphenated identifiers (bad practice)
                if "-" in line and "# " not in line:
                    # Simple heuristic: check if hyphen appears in identifier context
                    words = line.split()
                    for word in words:
                        if "-" in word and word.count("-") > 0:
                            # Skip comments and strings
                            if not (word.startswith("#") or word.startswith('"') or word.startswith("'")):
                                self.warnings.append(
                                    f"Possible hyphen in code identifier: {word}. "
                                    "Use snake_case (underscores) for Python code."
                                )

    def _check_reference_sections_removed(self) -> None:
        """Check that reference sections were removed."""
        if "Category-Specific Section Guide" in self.content:
            self.errors.append(
                "Reference section 'Category-Specific Section Guide' must be removed. "
                "This section is for TEMPLATE.md reference only."
            )

        if "Validation Checklist" in self.content:
            self.warnings.append(
                "Reference section 'Validation Checklist' should be removed "
                "after validation."
            )

        if "FOR REFERENCE ONLY" in self.content:
            self.errors.append(
                "Reference-only sections must be removed from published documents."
            )


def validate_file(filepath: Path) -> bool:
    """Validate a single file.

    Args:
        filepath: Path to file to validate

    Returns:
        True if valid, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Validating: {filepath}")
    print(f"{'='*60}")

    validator = DocumentValidator(filepath)
    is_valid, errors, warnings = validator.validate()

    if errors:
        print("\n❌ ERRORS:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("\n⚠️  WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")

    if is_valid and not warnings:
        print("\n✅ VALID: Document passes all checks")
    elif is_valid:
        print("\n✅ VALID: Document passes mandatory checks (warnings present)")
    else:
        print("\n❌ INVALID: Document has errors that must be fixed")

    return is_valid


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Validate specific file
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"Error: File not found: {filepath}")
            sys.exit(1)

        is_valid = validate_file(filepath)
        sys.exit(0 if is_valid else 1)
    else:
        # Validate all atomic docs
        atomic_dir = Path("docs/atomic")
        if not atomic_dir.exists():
            print(f"Error: Directory not found: {atomic_dir}")
            sys.exit(1)

        print("Validating all atomic documentation files...\n")

        files = list(atomic_dir.rglob("*.md"))
        # Exclude README.md, TEMPLATE.md, CHANGELOG.md
        files = [
            f
            for f in files
            if f.name not in ("README.md", "TEMPLATE.md", "CHANGELOG.md")
        ]

        valid_count = 0
        invalid_count = 0
        stub_count = 0

        for filepath in sorted(files):
            validator = DocumentValidator(filepath)
            is_valid, errors, warnings = validator.validate()

            # Check if it's a TODO stub
            if any("TODO stub" in error for error in errors):
                stub_count += 1
                continue

            if is_valid:
                valid_count += 1
                print(f"✅ {filepath.relative_to('docs/atomic')}")
            else:
                invalid_count += 1
                print(f"❌ {filepath.relative_to('docs/atomic')}")
                for error in errors:
                    print(f"   - {error}")

        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Total files:      {len(files)}")
        print(f"✅ Valid:         {valid_count}")
        print(f"❌ Invalid:       {invalid_count}")
        print(f"⚠️  TODO stubs:    {stub_count}")
        print(f"📊 Coverage:      {valid_count}/{len(files)} ({100*valid_count//len(files) if files else 0}%)")

        sys.exit(0 if invalid_count == 0 else 1)


if __name__ == "__main__":
    main()
