---
name: deliver-work-item
description: Implement and close a single Azure DevOps work item end-to-end in Fabric.
---

# Deliver Work Item

## Action

Read a work item, plan, implement in the Fabric workspace, validate with evidence and document the resolution back on the item. Run by the [`delivery-agent`](../agents/delivery-agent.md).

## Input

- A work item id or URL. If none is given, ask before starting.

## Workflow

1. Read the work item with `fab-ado-board`: title, description, acceptance criteria and existing comments. Do not work from the user's paraphrase alone.
2. Plan which notebooks, pipelines and tables change. Share the plan before implementing anything non-trivial.
3. Implement **live in the Fabric workspace**, in DEV unless told otherwise: `fab-notebook-dev` for new items and bulk edits, `fabric-notebook-toolkit` for single-cell edits and cell-by-cell iteration. Never edit a customer's local git checkout.
4. Before any `fab import`, check the notebook's Lakehouse binding: the exported default Lakehouse workspace id must match the target workspace, and every known Lakehouse must resolve in that same workspace.
5. Validate with one full `fab job start` run of the real notebook, then `fab-table-query` or an `fntk code run` query. Get concrete evidence (row counts, sample values), not just "ran without error". Delete any `fntk` session.
6. Document back on the item with `fab-ado-board`: a plain-language comment for a non-technical reader (which notebooks and tables changed and what the fix does), then transition the state (for example to Resolved) in the same update.

## After finishing

Confirm which environments hold the change and whether the other pre-production environment still needs it before the next deployment overwrites it. Record new board conventions or branch and pull-request policies in your private customer notes, and new facts about how the workspace works in the repository notes.

## Success Criteria

- The item has a plain-language resolution comment and the right state.
- Validation evidence exists and is quoted.
- No sessions or debug artifacts are left behind.
