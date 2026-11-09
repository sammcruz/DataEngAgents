#!/usr/bin/env python3
"""Build an INDEX.md for the private knowledge base and report what needs review.

Agents read the index instead of the whole log: one line per entry with its
status, so a 150 KB error log costs a few hundred tokens to scan. The same pass
lists entries that are unverified, volatile and overdue, or missing a status,
and warns when a file outgrows its size budget.

Two layouts are understood, per directory (`errors/`, `decisions/`):

  * one shared log:     errors/LOG.md, entries start with `## YYYY-MM-DD — title`
  * one file per entry: errors/entries/*.md, with a small `key: value` header

An entry can carry these lines (anywhere in the entry for LOG.md, in the header
for per-entry files). All are optional; a missing Status counts as "unknown".

    Status: verified-live | from-docs | unverified
    Last checked: YYYY-MM-DD
    Volatile: tool-version | api | none

Usage:
    python scripts/build_knowledge_index.py KNOWLEDGE_DIR            # write INDEX.md files
    python scripts/build_knowledge_index.py KNOWLEDGE_DIR --check    # exit 1 if stale or over budget
    python scripts/build_knowledge_index.py KNOWLEDGE_DIR --review-days 60 --max-kb 25

Standard library only. Run it in your private knowledge repository, never in a
public one (the index lists your entry titles).
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

HEADING = re.compile(r"^##\s+(?:(\d{4}-\d{2}-\d{2})\s*[—–-]\s*)?(.+?)\s*$")
FIELD = re.compile(r"^\**(Status|Last checked|Volatile)\**\s*[:：]\**\s*(.+?)\s*$", re.I)
STATUSES = {"verified-live", "from-docs", "unverified"}


@dataclass
class Entry:
    day: str
    title: str
    status: str
    checked: str
    volatile: str
    link: str


def slug(heading: str) -> str:
    """GitHub's heading anchor: lowercase, drop punctuation, each space becomes a hyphen."""
    return re.sub(r"[^\w\- ]", "", heading.lower()).strip().replace(" ", "-")


def parse_fields(lines):
    out = {"status": "unknown", "checked": "", "volatile": "none"}
    for line in lines:
        m = FIELD.match(line.strip())
        if not m:
            continue
        key, val = m.group(1).lower(), m.group(2).strip().strip("`*").lower()
        if key == "status":
            out["status"] = val if val in STATUSES else "unknown"
        elif key == "last checked":
            out["checked"] = val
        elif key == "volatile":
            out["volatile"] = val
    return out


def parse_log(path: Path, rel: str):
    entries, cur, body = [], None, []

    def flush():
        if cur:
            f = parse_fields(body)
            heading = f"{cur[0]} — {cur[1]}" if cur[0] else cur[1]
            entries.append(Entry(cur[0], cur[1], f["status"], f["checked"], f["volatile"], f"{rel}#{slug(heading)}"))

    for line in path.read_text(encoding="utf-8").splitlines():
        m = HEADING.match(line)
        if m and line.startswith("## "):
            flush()
            cur, body = (m.group(1) or "", m.group(2)), []
        elif cur:
            body.append(line)
    flush()
    return entries


def parse_entry_file(path: Path, rel: str):
    lines = path.read_text(encoding="utf-8").splitlines()
    head = []
    if lines and lines[0].strip() == "---":
        for ln in lines[1:]:
            if ln.strip() == "---":
                break
            head.append(ln)
    meta = {k.strip().lower(): v.strip().strip("\"'") for k, v in (l.split(":", 1) for l in head if ":" in l)}
    title = meta.get("title") or next((l.lstrip("# ").strip() for l in lines if l.startswith("# ")), path.stem)
    day = meta.get("date") or (re.match(r"(\d{4}-\d{2}-\d{2})", path.name) or [None, ""])[1]
    f = parse_fields([f"{k}: {v}" for k, v in meta.items()] + lines)
    return Entry(day or "", title, f["status"], f["checked"], f["volatile"], rel)


def collect(kdir: Path, section: str):
    base = kdir / section
    entries = []
    log = base / "LOG.md"
    if log.exists():
        entries += parse_log(log, "LOG.md")
    for p in sorted((base / "entries").glob("*.md")) if (base / "entries").exists() else []:
        entries.append(parse_entry_file(p, f"entries/{p.name}"))
    return sorted(entries, key=lambda e: (e.day, e.title), reverse=True)


def needs_review(e: Entry, today: date, review_days: int):
    reasons = []
    if e.status == "unknown":
        reasons.append("no status")
    if e.status == "unverified":
        reasons.append("unverified")
    if e.volatile not in ("none", ""):
        try:
            age = today - date.fromisoformat(e.checked)
            if age > timedelta(days=review_days):
                reasons.append(f"volatile ({e.volatile}), last checked {age.days} days ago")
        except ValueError:
            reasons.append(f"volatile ({e.volatile}), never checked")
    return reasons


def render(section: str, entries, today: date, review_days: int):
    counts = {s: sum(1 for e in entries if e.status == s) for s in sorted(STATUSES | {"unknown"})}
    due = [(e, r) for e in entries for r in [needs_review(e, today, review_days)] if r]
    out = [f"# {section.capitalize()} index", "",
           f"Generated by `scripts/build_knowledge_index.py` on {today.isoformat()}. Do not edit by hand.", "",
           f"**{len(entries)} entries.** " + ", ".join(f"{n} {s}" for s, n in counts.items() if n) + f". **{len(due)} due for review.**", ""]
    if due:
        out += ["## Due for review", ""] + [f"- [{e.title}]({e.link}): {'; '.join(r)}" for e, r in due] + [""]
    out += ["## All entries (newest first)", "", "| Date | Entry | Status | Volatile | Last checked |", "|---|---|---|---|---|"]
    out += [f"| {e.day} | [{e.title}]({e.link}) | {e.status} | {e.volatile} | {e.checked or '–'} |" for e in entries]
    return "\n".join(out) + "\n", len(due)


def budget_warnings(kdir: Path, max_kb: int, injected: list[str], max_lines: int):
    warns = []
    for p in sorted(kdir.rglob("*.md")):
        if p.name == "INDEX.md":
            continue
        kb = p.stat().st_size / 1024
        if kb > max_kb:
            warns.append(f"{p.relative_to(kdir)} is {kb:.0f} KB (budget {max_kb} KB): split it into one file per entry or per topic")
    for name in injected:
        p = Path(name)
        if p.exists():
            n = len(p.read_text(encoding="utf-8").splitlines())
            if n > max_lines or p.stat().st_size / 1024 > max_kb:
                warns.append(f"{name} loads into every session and has {n} lines ({p.stat().st_size/1024:.0f} KB): keep it under {max_lines} lines, move detail down and link to it")
    return warns


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("knowledge_dir", type=Path)
    ap.add_argument("--sections", nargs="*", default=["errors", "decisions"])
    ap.add_argument("--review-days", type=int, default=90, help="re-check volatile entries older than this")
    ap.add_argument("--max-kb", type=int, default=25, help="size budget per knowledge file")
    ap.add_argument("--injected", nargs="*", default=[], help="always-loaded files to size-check (for example CLAUDE.md MEMORY.md)")
    ap.add_argument("--max-lines", type=int, default=200)
    ap.add_argument("--check", action="store_true", help="do not write; exit 1 if an index is stale or a budget is exceeded")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for tests")
    a = ap.parse_args()

    if not a.knowledge_dir.is_dir():
        sys.exit(f"not a directory: {a.knowledge_dir}")
    today = date.fromisoformat(a.today) if a.today else date.today()
    problems, total_due = 0, 0
    for section in a.sections:
        if not (a.knowledge_dir / section).is_dir():
            continue
        entries = collect(a.knowledge_dir, section)
        text, due = render(section, entries, today, a.review_days)
        total_due += due
        target = a.knowledge_dir / section / "INDEX.md"
        current = target.read_text(encoding="utf-8") if target.exists() else ""
        strip = lambda t: re.sub(r"on \d{4}-\d{2}-\d{2}\.", "on DATE.", t)
        if a.check:
            if strip(current) != strip(text):
                print(f"STALE: {target} is out of date")
                problems += 1
        else:
            target.write_text(text, encoding="utf-8")
            print(f"wrote {target}: {len(entries)} entries, {due} due for review")
    for w in budget_warnings(a.knowledge_dir, a.max_kb, a.injected, a.max_lines):
        print("BUDGET:", w)
        problems += 1
    if a.check and total_due:
        print(f"note: {total_due} entries are due for review (run the memory-review prompt)")
    return 1 if (a.check and problems) else 0


if __name__ == "__main__":
    sys.exit(main())
