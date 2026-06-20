#!/usr/bin/env python3
"""Quick wiki lint: broken wikilinks, index gaps, orphans."""
import os
import re
import glob
from collections import defaultdict

VAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = os.path.join(VAULT, "wiki")

SKIP = {"index.md", "log.md"}


def title_from_file(path: str) -> str:
    with open(path) as f:
        for line in f:
            if line.startswith("# "):
                return line[2:].strip()
    return os.path.basename(path).replace(".md", "").replace("-", " ").title()


def build_title_map():
    titles = {}
    for path in glob.glob(os.path.join(WIKI, "**", "*.md"), recursive=True):
        if os.path.basename(path) in SKIP:
            continue
        title = title_from_file(path)
        titles[title.lower()] = path
    # Aliases
    titles["roadmap openspec"] = os.path.join(WIKI, "roadmap", "index.md")
    titles["index"] = os.path.join(WIKI, "index.md")
    return titles


def main():
    titles = build_title_map()
    all_titles = {title_from_file(p) for p in glob.glob(os.path.join(WIKI, "**", "*.md"), recursive=True) if os.path.basename(p) not in SKIP}
    all_titles.add("Roadmap OpenSpec")

    errors, warnings, info = [], [], []
    inbound = defaultdict(set)
    broken = []

    for path in glob.glob(os.path.join(WIKI, "**", "*.md"), recursive=True):
        if os.path.basename(path) in SKIP:
            continue
        with open(path) as f:
            content = f.read()
        for m in re.finditer(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", content):
            link = m.group(1).strip()
            if link.lower() not in titles and link not in all_titles:
                broken.append((path, link))
            else:
                inbound[link].add(path)

    for path, link in broken:
        errors.append(f"Broken wikilink [[{link}]] in {os.path.relpath(path, VAULT)}")

    # Index consistency
    index_path = os.path.join(WIKI, "index.md")
    with open(index_path) as f:
        index_content = f.read()
    indexed = set(re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", index_content))

    for sub in ("entities", "concepts", "synthesis", "sources"):
        subdir = os.path.join(WIKI, sub)
        if not os.path.isdir(subdir):
            continue
        for path in glob.glob(os.path.join(subdir, "*.md")):
            title = title_from_file(path)
            if title not in indexed and f"[[{title}]]" not in index_content:
                warnings.append(f"Missing index entry for [[{title}]] ({os.path.relpath(path, VAULT)})")

    # Orphans (no inbound, not in index as main entry)
    for path in glob.glob(os.path.join(WIKI, "**", "*.md"), recursive=True):
        base = os.path.basename(path)
        if base in SKIP or "timeline" in path or "roadmap/changes" in path:
            continue
        title = title_from_file(path)
        if title in ("Roadmap OpenSpec",):
            continue
        if not inbound.get(title) and f"[[{title}]]" not in index_content:
            if path.startswith(os.path.join(WIKI, "entities")):
                info.append(f"Orphan entity (index only): [[{title}]]")

    print(f"=== LINT REPORT ===")
    print(f"Errors: {len(errors)} | Warnings: {len(warnings)} | Info: {len(info)}")
    for e in errors[:30]:
        print(f"  ERROR: {e}")
    for w in warnings[:20]:
        print(f"  WARN: {w}")
    for i in info[:10]:
        print(f"  INFO: {i}")
    if len(errors) > 30:
        print(f"  ... and {len(errors)-30} more errors")

    # Write stub pages for common broken links
    stubs_created = []
    stub_map = {
        "Essensys Cloud Backend Consolidation": ("roadmap/changes", "essensys-cloud-backend-consolidation"),
        "Essensys Remote User Interface": ("roadmap/changes", "essensys-remote-user-interface"),
        "Essensys Gateway Dual Nic": ("roadmap/changes", "essensys-gateway-dual-nic"),
        "Essensys Gateway Nixos": ("roadmap/changes", "essensys-gateway-nixos"),
        "Essensys Second Brain": ("roadmap/changes", "essensys-second-brain"),
    }
    for link, (subdir, slug) in stub_map.items():
        if any(link == b[1] for b in broken):
            target = os.path.join(WIKI, subdir, f"{slug}.md")
            if os.path.isfile(target):
                continue  # title mismatch fix instead
            # fix: roadmap pages exist but title might differ - check
            rp = os.path.join(WIKI, "roadmap", "changes", f"{slug}.md")
            if os.path.isfile(rp):
                with open(rp) as f:
                    actual = title_from_file(rp)
                if actual != link:
                    info.append(f"Title alias needed: [[{link}]] → actual [[{actual}]]")

    return len(errors), len(warnings), len(info)


if __name__ == "__main__":
    main()
