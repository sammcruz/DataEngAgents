---
name: memory-review
description: Offline review of the private knowledge base: recheck volatile and unverified notes against ground truth, merge duplicates, fix links, and promote recurring lessons. Proposes changes as a diff or pull request.
---

# Memory Review

## Action

Reorganise and correct the knowledge layer with hindsight, away from any live task. This is the "dreaming" pass described in [`docs/memory-maintenance.md`](../docs/memory-maintenance.md). It improves existing notes; it does not add new incidents. Run by the [`governance-agent`](../agents/governance-agent.md).

## Input

- The path of the private knowledge directory.
- Optionally the user-level instruction file and the auto-memory index, to check their size.
- Optionally a review window in days for volatile entries (default 90).

## Workflow

1. **Measure.** Run `python scripts/build_knowledge_index.py <dir> --check --injected <files>`. Note stale indexes, files over budget and always-loaded files that are too long.
2. **Pick the work from the index,** not by reading everything: the "due for review" list first (no status, unverified, or volatile and overdue).
3. **Recheck each due entry against ground truth, read-only.**
   - Tool-version notes: run `--version` and `--help` on the current release and try the documented behaviour on a harmless command.
   - API notes: re-read the current documentation or make one read-only call.
   - Incident notes: confirm against the transcript or the live item that the cause and fix are what the note says.
   Never write to a customer workspace and never run anything destructive during a review.
4. **Correct in place.** Update the note, set `Status`, `Last checked`, and add one line stating what changed. If a note is obsolete, mark it so and say what replaced it. Do not delete the history of a decision, only its stale instructions.
5. **Merge duplicates and fix links.** Combine entries that describe the same root cause. Repair or remove links to pages that no longer exist.
6. **Promote and demote.**
   - A lesson that has recurred, or that applies to every customer, becomes a rule in a skill or an anonymised page such as `docs/gotchas.md`. Run the anonymisation check before anything goes to a public repository.
   - Detail that is only useful once stays in its own entry, linked from the index. Do not copy it into a summary.
   - Keep always-loaded files under their budget by moving detail down and leaving a link.
7. **Split anything over budget** into one file per entry or per topic, then regenerate the indexes.
8. **Propose.** Show a summary of what changed and why, then open a pull request (or leave a diff). Do not push directly.

## Guardrails

- Read-only against live systems. Fixes to notes only.
- No secrets, tokens or customer data copied into any note or summary.
- If a recheck cannot be done (no access, tool not installed), leave the entry as `unverified` and say why. Do not guess a status.
- Prefer fewer, truer notes over more notes.

## Success Criteria

- Every entry due for review has a status and a date, or an explicit reason it could not be checked.
- The indexes are current and no file exceeds its budget.
- Corrected facts were fixed in place, not contradicted by a newer entry.
- The change was proposed as a diff or pull request.
