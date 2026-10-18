---
name: fab-onelake-ops
description: Use this skill for file and folder work inside Fabric and OneLake with fab-cli, especially when navigating paths, copying or moving content, checking existence, and verifying tables or files before and after changes.
---

# Fab Onelake Ops

## Use

Use this skill when the user is working with Fabric paths like workspaces, items, folders, files, or lakehouse table areas through `fab`. It focuses on safe navigation and file operations in filesystem-style paths.

Read [references/path-patterns.md](references/path-patterns.md) when the task needs reusable path conventions or a safe sequence for file operations. Use [scripts/render_path_op_spec.py](scripts/render_path_op_spec.py) for dry-run command generation from JSON specs, and [scripts/check_paths.py](scripts/check_paths.py) for batch existence checks. Point users to [assets/path-op.sample.json](assets/path-op.sample.json) and [assets/paths.sample.json](assets/paths.sample.json) as starter templates.

## Workflow

1. Start with `fab dir`, `fab pwd`, `fab exists`, or `fab get` to confirm the current path and target.
2. If the target is a Lakehouse, list both `.../Files` and `.../Tables` before assuming where the useful content lives.
3. If the data is table-oriented, list schemas under `.../Tables`, then list tables inside the schema before using `fab table` subcommands.
4. If notebook code will write with `saveAsTable("<schema>.<table>")` or otherwise depends on Spark schemas, stop and note that `fab` path checks validate the OneLake layer, not Spark metastore registration.
5. Do not infer Spark readiness from `Lakehouse/Tables/<schema>` alone; recommend verification from notebook or SQL endpoint perspective, or a schema bootstrap step, before declaring the target ready.
6. If copying or moving data, inspect both source and destination first.
7. Perform `copy`, `move`, `mklink`, `mkdir`, or `del` only after confirming the exact path.
8. If Spark output lands as a folder with `_SUCCESS` plus `part-*.txt` or similar files, treat the folder as the output unit and then copy the exact part file you need rather than assuming a single flat file path.
9. Re-list or re-check existence to verify the result.

## Commands

List a path:

```powershell
fab dir "ws.Workspace/lh.Lakehouse/Files"
```

List the Lakehouse table area:

```powershell
fab dir "ws.Workspace/lh.Lakehouse/Tables"
fab dir "ws.Workspace/lh.Lakehouse/Tables/silver"
```

Check existence:

```powershell
fab exists "ws.Workspace/lh.Lakehouse/Files/raw/file.csv"
```

Copy content:

```powershell
fab copy "src-path" "dst-path"
```

Move content:

```powershell
fab move "src-path" "dst-path"
```

Inspect table schema when the task is table-oriented:

```powershell
fab table schema "ws.Workspace/lh.Lakehouse/Tables/silver/customers"
```

Inspect a Spark text output folder before copying the payload file:

```powershell
fab dir "ws.Workspace/lh.Lakehouse/Files/validation/result.json" -l
fab copy "ws.Workspace/lh.Lakehouse/Files/validation/result.json/part-00000-<id>.txt" ".\\result.txt" -f
```

Render a path operation from a JSON spec:

```powershell
python scripts/render_path_op_spec.py .\path-op.json
```

Batch-check a list of paths:

```powershell
python scripts/check_paths.py .\paths.json
```

## Guardrails

- Treat `del` and `move` as high-risk actions. Confirm the exact path first.
- If the path is ambiguous, use `fab dir` to discover it rather than inferring a suffix.
- Prefer `exists` before and after any write operation.
- Do not assume Lakehouse data lives under `Files`; many workflows store the useful data under schema folders in `Tables`.
- Separate file workflows from table workflows. Use `fab table` subcommands when the resource is a Delta table rather than a plain file path.
- Treat `Lakehouse/Tables/<schema>` as a directory-style signal only. It is not enough to prove that Spark can use `<schema>` in `saveAsTable` or SQL statements.
- If the user is troubleshooting notebook writes and sees `SCHEMA_NOT_FOUND`, recommend notebook-side or SQL-endpoint schema verification, or a bootstrap step such as `CREATE SCHEMA IF NOT EXISTS bronze`, `silver`, and `gold`.
- Spark text outputs written with `DataFrame.write.text(...)` usually appear as a folder containing `_SUCCESS` plus one or more `part-*.txt` files. Do not try to copy the folder as if it were a single text file.
- Prefer rendering commands before executing copy, move, mklink, or delete operations in automation.

## Output

- Show the resolved paths.
- Note whether the relevant content was found under `Files` or `Tables`.
- If the task also depends on Spark schemas, state clearly whether you verified only the path layer or also the Spark schema layer.
- If the useful payload lives inside a Spark output folder, say that explicitly and report which `part-*` file you used.
- State what existed before and after in a compact visual structure.
- If a file or folder operation failed, report the exact path and the command attempted.
