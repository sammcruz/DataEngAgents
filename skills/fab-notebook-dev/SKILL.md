---
name: fab-notebook-dev
description: Use this skill to export, edit, import, run, and validate Microsoft Fabric notebooks with fab-cli, including safe iteration loops and debug-output collection.
---

# Fab Notebook Dev

## Use

Use this skill when the user needs notebook work end to end:

1. Inspect notebook code and metadata
2. Edit or create notebook content locally
3. Import notebooks back into a workspace
4. Run notebooks and diagnose failures
5. Collect validation output for reproducible checks

## Workflow

1. Confirm the target path with `fab ls` or `fab dir`.
2. Export existing notebooks before editing.
3. Edit `notebook-content.ipynb` and keep Fabric metadata intact.
4. Import with `fab import -f`.
5. Run with `fab job start` and check `fab job run-status`.
6. Iterate on failures and re-run until success.
7. Remove temporary debug assets when done.

## Commands

Export an existing notebook for safe edits:

```bash
fab export "<workspace>.Workspace/<notebook>.Notebook" -o /tmp/exports -f
```

Import updated notebook:

```bash
fab import "<workspace>.Workspace/<notebook>.Notebook" -i "/tmp/exports/<notebook>.Notebook" -f
```

Run notebook:

```bash
fab job start "<workspace>.Workspace/<notebook>.Notebook"
fab job run-status "<workspace>.Workspace/<notebook>.Notebook" --id "<run-id>"
```

Copy debug report output from OneLake Files:

```bash
fab cp "<workspace>.Workspace/<lakehouse>.Lakehouse/Files/_debug/<report>.json" "/tmp/<report>.json" -f
```

## Notebook Structure Notes

- Use standard Jupyter `.ipynb` format (`nbformat` 4).
- Preserve Fabric cell metadata (`microsoft.language` and `language_group`).
- Keep `.platform` file when importing a notebook directory.

## Guardrails

- Prefer `fab export` over `fab get` when you plan to re-import.
- Keep write operations behind explicit user intent.
- Do not leave debug notebooks in shared workspaces.
- Report run ID, status, and key failure reason for each execution.
