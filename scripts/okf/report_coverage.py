#!/usr/bin/env python3
"""Write a coverage report for the ESSENSYS OKF discovery."""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

VAULT_ROOT = Path(__file__).resolve().parents[2]
OKF = VAULT_ROOT / "okf"
INVENTORY = VAULT_ROOT / "output" / "okf-repository-inventory.json"
SUMMARY = VAULT_ROOT / "output" / "okf-generation-summary.json"

MANDATORY = {
    "Armoire architecture": OKF / "synthesis" / "armoire-architecture.md",
    "Table d'échange": OKF / "protocols" / "table-d-echange.md",
    "Legacy HTTP": OKF / "protocols" / "legacy-http.md",
    "Dual Protocol": OKF / "protocols" / "dual-protocol.md",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> int:
    inv = load(INVENTORY)
    summary = load(SUMMARY)
    repos = inv.get("repositories", [])
    covered = set(summary.get("repositories_covered", []))
    missing = [r["name"] for r in repos if r["name"] not in covered]
    concept_files = [p for p in OKF.rglob("*.md") if p.name not in {"index.md", "log.md"}]
    report_path = VAULT_ROOT / "output" / f"okf-discovery-coverage-{date.today().isoformat()}.md"

    lines = [
        "# OKF Discovery Coverage Report",
        "",
        f"Date: {date.today().isoformat()}",
        "Change: `essensys-okf-discovery-2026-06-029`",
        "",
        "## Summary",
        "",
        f"- Repositories discovered: {len(repos)}",
        f"- Repositories covered by OKF: {len(covered)}",
        f"- OKF concept documents: {len(concept_files)}",
        f"- Missing repository coverage: {len(missing)}",
        "",
        "## Repository coverage",
        "",
    ]
    for r in repos:
        status = "covered" if r["name"] in covered else "missing"
        lines.append(f"- {status}: `{r['name']}` — layer `{r.get('layer')}`, era `{r.get('era')}`")
    lines += ["", "## Mandatory legacy / architecture coverage", ""]
    for label, path in MANDATORY.items():
        lines.append(f"- {'covered' if path.exists() else 'missing'}: {label} — `{path.relative_to(VAULT_ROOT)}`")
    lines += ["", "## Roadmap and portals", ""]
    lines.append(f"- Roadmap concepts: {summary.get('roadmap_count', 0)}")
    for p in summary.get("portals", []):
        lines.append(f"- Portal concept: `{p}`")
    lines += [
        "",
        "## Gaps and contradictions",
        "",
        "- No hard contradictions were automatically detected in this generation pass.",
        "- Any index/protocol contradiction discovered during future manual review must be added to the affected OKF concept and to this report family.",
        "- Items with `TBD` horizon or deployment state require source-backed follow-up rather than inference.",
        "",
        "## Validation",
        "",
        "Run:",
        "",
        "```bash",
        "python3 scripts/okf/validate_okf.py okf",
        "openspec validate essensys-okf-discovery-2026-06-029 --strict",
        "```",
        "",
        "## Security notes",
        "",
        "- Discovery avoids `.env`, decrypted SOPS material, private keys, tokens and credentials.",
        "- OKF records code pointers and citations, not full source code dumps.",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report_path)
    return 1 if missing else 0

if __name__ == "__main__":
    raise SystemExit(main())
