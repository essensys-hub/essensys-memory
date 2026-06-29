#!/usr/bin/env python3
"""Discover local ESSENSYS repositories for OKF generation.

Security: this script deliberately avoids reading .env, decrypted secrets,
private key material, SOPS payloads, and arbitrary source files. It only
captures repository names, selected public manifests, README/docs pointers,
OpenSpec metadata, and protocol/code pointer paths.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, timezone

VAULT_ROOT = Path(__file__).resolve().parents[2]
ESSENSYS_ROOT = Path(os.environ.get("ESSENSYS_ROOT", VAULT_ROOT.parent))
OUTPUT = VAULT_ROOT / "output" / "okf-repository-inventory.json"

DENY_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
DENY_PARTS = {".git", "node_modules", "vendor", "dist", "build", ".next", ".venv", "venv", "secrets"}
MANIFESTS = [
    "README.md", "package.json", "go.mod", "pyproject.toml", "Cargo.toml",
    "Dockerfile", "docker-compose.yml", "compose.yml", "openspec/changes",
]
PROTOCOL_HINTS = [
    "TableEchange.h", "IHM_ECHANGES.INC", "constants.go", "order_expansion.go",
    "action_service.go", "serverinfos", "mystatus", "myactions", "done",
]


def classify(name: str) -> tuple[str, str]:
    n = name.lower()
    if "board" in n or n == "client-essensys-legacy":
        return "firmware", "legacy"
    if "web-legacy" in n:
        return "legacy", "legacy"
    if any(k in n for k in ["ansible", "traefik", "nginx", "redis", "mosquitto", "base", "prometheus"]):
        return "infra", "modern"
    if any(k in n for k in ["user-portal", "support-site"]):
        return "cloud", "modern"
    if any(k in n for k in ["server-backend", "server-frontend", "control-plane", "raspberry", "gateway"]):
        return "gateway-lan", "modern"
    if any(k in n for k in ["doc", "memory", "feature-lifecycle"]):
        return "documentation", "modern"
    if any(k in n for k in ["mcp", "utils", "gcc", "n8n", "homeassitant", "phone-apps"]):
        return "tooling", "modern"
    return "system", "modern"


def safe_relative_files(repo: Path, max_hits: int = 30) -> list[str]:
    hits: list[str] = []
    for rel in MANIFESTS:
        p = repo / rel
        if p.exists():
            hits.append(rel)
    # Known protocol/code pointers by filename/string, path-only; do not read secrets.
    for root, dirs, files in os.walk(repo):
        parts = set(Path(root).parts)
        dirs[:] = [d for d in dirs if d not in DENY_PARTS and d not in {"__pycache__", ".pytest_cache"}]
        if parts & DENY_PARTS:
            continue
        for fn in files:
            if fn in DENY_NAMES or fn.endswith((".age", ".key", ".pem")):
                continue
            rel = str((Path(root) / fn).relative_to(repo))
            if any(h.lower() in fn.lower() or h.lower() in rel.lower() for h in PROTOCOL_HINTS):
                hits.append(rel)
                if len(hits) >= max_hits:
                    return sorted(dict.fromkeys(hits))
    return sorted(dict.fromkeys(hits))


def main() -> int:
    repos = []
    for p in sorted(ESSENSYS_ROOT.iterdir()):
        if not p.is_dir() or not (p / ".git").exists():
            continue
        layer, era = classify(p.name)
        repos.append({
            "name": p.name,
            "path": str(p),
            "layer": layer,
            "era": era,
            "remote": None,
            "pointers": safe_relative_files(p),
        })
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "essensys_root": str(ESSENSYS_ROOT),
        "repository_count": len(repos),
        "repositories": repos,
        "security_rules": [
            "Do not read or print .env files, decrypted SOPS material, private keys, tokens, or credentials.",
            "Use path-level code pointers and wiki citations instead of copying full source code.",
        ],
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT} ({len(repos)} repositories)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
