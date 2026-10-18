#!/usr/bin/env python3
"""Scan a tree for content that should never be published in a template repo.

Usage:
    python scripts/check_anonymized.py [PATH ...]        # default: repo root
    python scripts/check_anonymized.py --denylist my-terms.txt skills/

What it flags:
  * GUIDs / UUIDs (workspace, item, tenant, capacity ids)
  * e-mail addresses, IPv4 addresses
  * URLs whose host is not on the allowlist below (docs and public tooling)
  * Azure DevOps / Fabric / SharePoint tenant URLs
  * token-shaped strings (PATs, JWTs, private keys, password/secret assignments)
  * every term in an optional private deny-list (one term per line, `#` comments)
    -- put customer, employer and internal project names there. The default
    location is `.anonymize-denylist.txt`, which is git-ignored on purpose so the
    names themselves never reach the repository.

Exit code is 1 when anything is found, so it can run in CI or a pre-commit hook.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TEXT_SUFFIXES = {
    ".md", ".txt", ".json", ".yaml", ".yml", ".py", ".sh", ".ps1", ".toml", ".cfg",
    ".ini", ".csv", ".sql", ".ipynb", ".example", ".html", ".xml", ".env",
}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "output"}
# The deny-list holds the very names we must not publish; the scanner holds its own allowlist.
SKIP_FILES = {".anonymize-denylist.txt", "check_anonymized.py"}

# Hosts that are fine to reference in public docs.
ALLOWED_HOSTS = {
    "learn.microsoft.com", "docs.microsoft.com", "github.com", "raw.githubusercontent.com",
    "microsoft.github.io", "pypi.org", "docs.python.org", "json-schema.org", "json.schemastore.org",
    "schema.management.azure.com", "aka.ms", "api.fabric.microsoft.com", "api.powerbi.com",
    "onelake.dfs.fabric.microsoft.com", "login.microsoftonline.com", "management.azure.com",
    "app.fabric.microsoft.com", "app.powerbi.com", "analysis.windows.net", "dev.azure.com",
    "vssps.dev.azure.com", "www.microsoft.com", "code.visualstudio.com", "nodejs.org",
    "docs.databricks.com", "docs.github.com", "www.python.org", "example.com", "www.w3.org",
    "opensource.org", "choosealicense.com", "pypi.python.org", "conda.io", "brew.sh",
    "schemas.microsoft.com", "developer.microsoft.com", "powerbi.microsoft.com",
    "marketplace.visualstudio.com", "tabulareditor.github.io", "daxstudio.org",
    "www.sqlbi.com", "semantic-link-labs.readthedocs.io", "docs.pydantic.dev",
    "graph.microsoft.com", "storage.azure.com", "database.windows.net", "vault.azure.net",
    "docs.tabulareditor.com", "pbi.tools", "pypi.org", "learn.microsoft.com",
}
PLACEHOLDER_URL = re.compile(r"<[^>]+>|\{[^}]+\}|\$\{?\w+\}?|your[-_]|example|contoso|placeholder", re.I)

GUID = re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b")
ZERO_GUID = re.compile(r"^(0{8}-0{4}-0{4}-0{4}-0{12}|[0-9a-f])\b")
EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
IPV4 = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
URL = re.compile(r"https?://([A-Za-z0-9.-]+)([^\s)>\"'`]*)")
TENANT = re.compile(r"[\w-]+\.(?:onmicrosoft\.com|sharepoint\.com|visualstudio\.com|crm\d*\.dynamics\.com)", re.I)
SECRETS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}")),
    ("ADO PAT-like", re.compile(r"\b[a-z0-9]{52}\b")),
    ("secret assignment", re.compile(r"(?i)\b(password|passwd|client[_-]?secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*[\"']?[A-Za-z0-9/+_=-]{12,}")),
]
SAFE_GUIDS = {
    "00000000-0000-0000-0000-000000000000",
    "11111111-1111-1111-1111-111111111111",
    "12345678-1234-1234-1234-123456789012",
}


def iter_files(paths):
    for p in paths:
        p = Path(p)
        if p.is_file():
            if p.name not in SKIP_FILES:
                yield p
            continue
        for f in sorted(p.rglob("*")):
            if f.is_file() and f.name not in SKIP_FILES and not (set(f.parts) & SKIP_DIRS) and (f.suffix.lower() in TEXT_SUFFIXES or f.name in {"LICENSE", ".env.example"}):
                yield f


def load_denylist(path: Path | None):
    if not path or not path.exists():
        return []
    terms = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            terms.append(re.compile(re.escape(line), re.I))
    return terms


def scan_text(text: str, deny):
    findings = []
    for n, line in enumerate(text.splitlines(), 1):
        for m in GUID.finditer(line):
            if m.group(0).lower() not in SAFE_GUIDS:
                findings.append((n, "GUID", m.group(0), line))
        for m in EMAIL.finditer(line):
            if not m.group(0).lower().endswith(("@example.com", "@contoso.com")):
                findings.append((n, "e-mail", m.group(0), line))
        for m in IPV4.finditer(line):
            findings.append((n, "IPv4", m.group(0), line))
        for m in URL.finditer(line):
            host, rest = m.group(1).lower().rstrip("."), m.group(2)
            if PLACEHOLDER_URL.search(m.group(0)):
                continue
            if host == "dev.azure.com" and re.match(r"/[A-Za-z0-9._-]+", rest) and not PLACEHOLDER_URL.search(rest):
                findings.append((n, "ADO org URL", m.group(0), line))
            elif host not in ALLOWED_HOSTS and not any(host.endswith("." + h) for h in ALLOWED_HOSTS):
                findings.append((n, "URL host", m.group(0), line))
        for m in TENANT.finditer(line):
            if m.group(0).lower() not in ALLOWED_HOSTS:
                findings.append((n, "tenant host", m.group(0), line))
        for label, rx in SECRETS:
            for m in rx.finditer(line):
                findings.append((n, label, m.group(0)[:40] + "...", line))
        for rx in deny:
            for m in rx.finditer(line):
                findings.append((n, "deny-list", m.group(0), line))
    return findings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", default=["."])
    ap.add_argument("--denylist", type=Path, default=Path(".anonymize-denylist.txt"))
    ap.add_argument("--summary", action="store_true", help="only print counts per rule and per file")
    args = ap.parse_args()

    deny = load_denylist(args.denylist)
    if not deny:
        print(f"note: no deny-list loaded from {args.denylist}; customer and employer names are NOT checked", file=sys.stderr)

    total = 0
    by_rule: dict[str, int] = {}
    by_file: dict[str, int] = {}
    for f in iter_files(args.paths):
        try:
            text = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        hits = scan_text(text, deny)
        for n, rule, value, line in hits:
            total += 1
            by_rule[rule] = by_rule.get(rule, 0) + 1
            by_file[str(f)] = by_file.get(str(f), 0) + 1
            if not args.summary:
                print(f"{f}:{n}: [{rule}] {value}   | {line.strip()[:120]}")
    if args.summary:
        for r, c in sorted(by_rule.items(), key=lambda x: -x[1]):
            print(f"{c:5d}  {r}")
        for fn, c in sorted(by_file.items(), key=lambda x: -x[1])[:25]:
            print(f"{c:5d}  {fn}")
    print(f"\n{total} finding(s)" if total else "clean: no findings")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
