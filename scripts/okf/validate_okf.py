#!/usr/bin/env python3
"""Validate an Open Knowledge Format bundle.

Checks the ESSENSYS OKF conventions used by this repository:
- non-reserved markdown files have YAML frontmatter and non-empty type;
- root index may declare okf_version frontmatter;
- log date headings use YYYY-MM-DD;
- local OKF links and local repository-relative citations resolve.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

RESERVED = {"index.md", "log.md"}
URL_RE = re.compile(r"^(?:https?://|mailto:|#)")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    root = root.resolve()
    repo = root.parent
    for p in sorted(root.rglob("*.md")):
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8")
        if p.name in RESERVED:
            if p.name == "index.md":
                body = text
                if rel == "index.md" and text.startswith("---\n"):
                    end = text.find("\n---\n", 4)
                    if end == -1:
                        errors.append(f"{rel}: unclosed root index frontmatter")
                    else:
                        if "okf_version:" not in text[4:end]:
                            errors.append(f"{rel}: root index frontmatter lacks okf_version")
                        body = text[end + 5 :]
                if not body.lstrip().startswith("#"):
                    errors.append(f"{rel}: index body should start with heading")
            if p.name == "log.md":
                if not text.lstrip().startswith("#"):
                    errors.append(f"{rel}: log should start with heading")
                for m in re.finditer(r"^##\s+(.+)$", text, flags=re.M):
                    if not re.match(r"\d{4}-\d{2}-\d{2}$", m.group(1).strip()):
                        errors.append(f"{rel}: non ISO date heading {m.group(1)!r}")
            continue

        if not text.startswith("---\n"):
            errors.append(f"{rel}: missing YAML frontmatter")
            continue
        end = text.find("\n---\n", 4)
        if end == -1:
            errors.append(f"{rel}: unclosed YAML frontmatter")
            continue
        fm = text[4:end]
        if not re.search(r"^type:\s*\S+", fm, flags=re.M):
            errors.append(f"{rel}: missing non-empty type")

        for m in LINK_RE.finditer(text):
            url = m.group(1).split("#", 1)[0]
            if not url or URL_RE.match(url):
                continue
            target = (root / url.lstrip("/")) if url.startswith("/") else (p.parent / url)
            if url.endswith("/"):
                target = target / "index.md"
            # permit repo-relative citations that climb outside okf but remain under repo
            try:
                target.resolve().relative_to(repo.resolve())
            except ValueError:
                errors.append(f"{rel}: local link escapes repository: {url}")
                continue
            if not target.exists():
                errors.append(f"{rel}: broken local link {url} -> {target}")
    return errors


def main(argv: list[str]) -> int:
    root = Path(argv[1] if len(argv) > 1 else "okf")
    errors = validate(root)
    if errors:
        print("OKF validation: FAIL")
        for e in errors:
            print(f"- {e}")
        return 1
    concept_count = sum(1 for p in root.rglob("*.md") if p.name not in RESERVED)
    print("OKF validation: PASS")
    print(f"Concept documents: {concept_count}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
