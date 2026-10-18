---
name: fix-bug
description: Investigate a Fabric data bug from a symptom, verify the root cause against real data, propose a fix and wait for approval before touching the workspace. After approval, implement, validate and document on Azure DevOps.
---

# Fix Bug

## Action

Take a reported data bug from symptom to documented fix, with one hard stop: no change to the live workspace before the human approves the proposal. Run by the [`bugfix-agent`](../agents/bugfix-agent.md).

## Input

- A symptom description, or an existing Azure DevOps Bug id (read it first, including its comments; do not work from a paraphrase).
- If neither is given, ask before starting.

## Before starting

Read your private knowledge for the customer and repository if it exists (environment names, editing discipline, board conventions, workspace map and design notes, known incidents). See [`docs/knowledge-layer.md`](../docs/knowledge-layer.md).

## Workflow

### Phase 1: Investigate (read-only, live workspace)

1. Identify the notebooks actually involved. The notebook named in the symptom is often only the entry point. Follow its `%run <helper>` cells: the real logic, and the bug, frequently lives in a shared helper used by several writers.
2. Read notebook content live (`fntk cell list` / `cell get`, or `fab export`), never a local git checkout. The live workspace is the only source of truth for current behaviour.
3. Do not trust naming conventions from general knowledge over what the project's own helpers do. Check how its own table-loading helper qualifies names before writing a verification query.
4. Form a root-cause hypothesis, then **verify it against real data** before presenting it as fact. Preferred: read-only `fntk code run` queries in a session on the existing DEV notebook. Fallback: a disposable debug notebook using the JSON-to-OneLake pattern in `fab-notebook-dev`.
5. Measure the actual blast radius: how many rows are affected, broken down by pattern. The true scope can be narrower than one example suggests, or reveal a second, unrelated, larger issue next to the reported one. Flag adjacent findings separately and do not fold them into the fix without an explicit go-ahead.
6. When a field encodes something real-world (a country, a region, a code), verify against the source record instead of asserting an interpretation. An unconfirmed label in a fix proposal or work item is worse than no label.

### Phase 2: Propose (hard stop)

Present, before changing anything:

- The confirmed root cause with evidence (row counts, example records).
- The exact proposed change (the literal line or list being edited).
- The measured blast radius.
- Any adjacent findings, marked out of scope for this fix.

**Wait for explicit approval.** A well-evidenced diagnosis is still not permission.

### Phase 3: Implement and validate (after approval)

1. Snapshot the live notebook first (`fntk notebook get-content --output-file` or `fab export`). Apply the approved change with a targeted `fntk cell update`, or edit the export and `fab import -f` for larger edits. Never edit a customer's local git checkout. Iterate on the changed cell in one live `fntk` session, remembering that running a writer cell writes for real.
2. Delete the `fntk` session, then re-run the real writer notebook end to end with `fab job start`. A warm interactive kernel can hide state. Read what its default parameters mean before running (a mode flag that looks destructive may be its normal production behaviour).
3. Validate against both the specific example from the report and the aggregate count for the affected population.
4. Delete every `fntk` session you started and every debug notebook or `Files/_debug` path you created.
5. State plainly which environment now holds the fix. Never write to production directly, and never assume git or other environments picked it up. Ask.

### Phase 4: Document on Azure DevOps

Use `fab-ado-board` (never raw `curl` with an inlined token).

- **No Bug exists yet:** create one. Repro steps describe only the observed problem (symptom, example, rough scope) in plain language, explicitly not the fix. Link it under the given parent and set assignee and iteration per the team's convention.
- **A Bug exists:** do not rewrite its repro steps. Add the resolution as a new comment so problem and fix stay distinguishable in history.
- **Resolution comment:** plain language for a non-technical reader, naming the notebooks changed, with no run ids, job ids, work-item ids or pipeline jargon. Say which environments hold the fix and whether propagation is pending.

## After finishing

Summarize root cause, notebooks touched, environments changed, validation evidence and the work item created or updated. Then record anything durable in your private knowledge base: standing design facts in the repository notes, a specific incident in the error log, a cross-project decision in the decision log.

## Success Criteria

- The fix was proposed and approved before any live change.
- Validation covers the example **and** the full affected population.
- No scratch artifacts are left in the workspace and no sessions are left running.
