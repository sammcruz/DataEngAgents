---
name: sync-notebook-changes
description: Take a Fabric notebook through a safe export, edit, import, run, validate cycle.
---

# Sync Notebook Changes

## Action

Move a change to a Fabric notebook from "idea" to "validated in the
workspace" without leaving the workspace in a half-edited state.

## Input

- The workspace/notebook path to change.
- A description of the intended change.

## Workflow

1. Confirm the target path exists (`fab ls` / `fab dir`).
2. Export the current notebook before touching anything.
3. Apply the edit locally, keeping Fabric cell metadata intact.
4. Import the updated notebook.
5. Run it and check status.
6. If it fails, iterate on the export/edit/import/run loop — don't patch the
   workspace copy directly.
7. If the change needs data-level proof (not just "job succeeded"), follow
   up with the table-query skill's read-only validation report pattern.
8. Remove any temporary debug notebooks or files created along the way.

## Success Criteria

- The workspace never holds a notebook mid-edit — every import is a
  complete, working version.
- Run ID and final status are reported.
- Temporary/debug artifacts are cleaned up.

## Skills Used

`fab-notebook-dev` for the edit cycle, `fab-table-query` if data-level
validation is required.
