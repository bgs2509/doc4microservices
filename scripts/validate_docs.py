#!/usr/bin/env python3
"""Validate internal Markdown links and anchors."""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Iterable

MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ANCHOR_TAG_RE = re.compile(r"<a\s+id=\"([^\"]+)\"", re.IGNORECASE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def slugify(text: str) -> str:
    slug = text.strip().lower()
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"[^a-z0-9\-]+", "", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug


def collect_anchors(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    anchors: set[str] = set()
    for match in ANCHOR_TAG_RE.finditer(text):
        anchors.add(match.group(1))
    for match in HEADING_RE.finditer(text):
        anchors.add(slugify(match.group(2)))
    return anchors


def iter_links(path: Path) -> Iterable[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    original_text = text

    # Remove code blocks first (triple backticks)
    text = re.sub(r"```[\s\S]+?```", lambda m: " " * len(m.group()), text)

    # Remove inline code (single backticks)
    text = re.sub(r"`[^`\n]+`", lambda m: " " * len(m.group()), text)

    # Find links in the cleaned text
    for match in MARKDOWN_LINK_RE.finditer(text):
        link = match.group(2).strip()
        line = original_text.count("\n", 0, match.start()) + 1
        yield line, link


def validate_link(source: Path, line: int, link: str) -> list[str]:
    errors: list[str] = []

    if any(link.startswith(prefix) for prefix in ("http://", "https://", "mailto:", "tel:", "data:")):
        return errors

    # Remove optional title (e.g. url "some" )
    if link.endswith('"') and ' "' in link:
        link = link.split(' "', 1)[0]

    path_part, anchor = (link.split('#', 1) + [None])[:2] if '#' in link else (link, None)

    target_path = source if path_part in ("", None) else (source.parent / path_part)
    target_path = target_path.resolve()

    if not target_path.exists():
        errors.append(f"{source.relative_to(Path.cwd())}:{line}: missing target '{link}' (resolved to {target_path})")
        return errors

    if anchor:
        anchor_slug = anchor
        anchors = collect_anchors(target_path)
        if anchor_slug not in anchors and slugify(anchor_slug) not in anchors:
            errors.append(
                f"{source.relative_to(Path.cwd())}:{line}: missing anchor '#{anchor}' in {target_path.relative_to(Path.cwd())}"
            )
    return errors


def main() -> int:
    root = Path.cwd()
    markdown_files = sorted(root.rglob("*.md"))
    errors: list[str] = []

    for md_file in markdown_files:
        for line, link in iter_links(md_file):
            errors.extend(validate_link(md_file, line, link))

    if errors:
        print("Documentation link validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("All internal Markdown links look good.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
