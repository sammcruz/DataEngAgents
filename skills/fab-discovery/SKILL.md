---
name: fab-discovery
description: Use this skill to explore Fabric workspaces, items, paths, and supported commands with fab-cli, especially when the user is unfamiliar with a tenant layout, item type, command surface, or current location.
---

# Fab Discovery

## Use

Use this skill for exploration and orientation in Fabric with `fab`. It helps map the workspace or item tree, discover valid paths, inspect object properties, and find which commands are supported before taking action.

## Workflow

1. Start with `fab pwd` and `fab dir` to understand the current context.
2. If the task depends on browsing workspace folders, enable direct folder visibility first with `fab config set folder_listing_enabled true` unless the user explicitly wants to avoid config changes.
3. Resolve the exact workspace or item path from `fab dir` output before using `fab get` or deeper listing commands.
4. Use `fab desc` on a dot element or resolved path to discover supported commands.
5. Narrow output with `fab get <path> -q <jmespath>` when large property payloads are noisy.
6. If notebook code or SQL references `schema.table` names such as `saveAsTable("bronze.orders")`, treat that as a Spark schema question as well as a path question.
7. Do not treat `.../Lakehouse/Tables/<schema>` visibility as proof that Spark or the SQL endpoint recognizes `<schema>` as a usable schema.
8. If `fab get` is unstable in the current terminal host, fall back to `fab api` for item and workspace discovery.
9. Only move to mutating commands after the path and object type are clear.

## Commands

Show current location:

```powershell
fab pwd
```

List workspaces or child items:

```powershell
fab config set folder_listing_enabled true
fab dir
fab dir "Analytics Dev.Workspace" -l
```

Inspect properties:

```powershell
fab get "Analytics Dev.Workspace"
fab get "Analytics Dev.Workspace/nb_silver_projects.Notebook"
```

See supported commands:

```powershell
fab desc ".notebook"
fab desc "Analytics Dev.Workspace/nb_silver_projects.Notebook"
```

Query only the needed fields from a resolved object:

```powershell
fab get "Analytics Dev.Workspace/nb_silver_projects.Notebook" -q "{displayName: displayName, type: type}"
```

Fallback to the Fabric REST surface through `fab api`:

```powershell
fab api "workspaces" -X get
fab api "workspaces/<workspace-id>/items" -X get
fab api "workspaces/<workspace-id>/folders" -X get
```

## Path Resolution Tips

- Prefer the exact path token emitted by `fab dir`, including suffixes such as `.Workspace`, `.Notebook`, or `.Lakehouse`.
- If a shorthand path such as `ws.<name>` fails with `InvalidPath`, fall back to the literal value returned by `fab dir`.
- Path syntax can vary across `fab` versions, so treat `fab dir` output as the source of truth.
- For folder-heavy workspace inspection, `fab config set folder_listing_enabled true` makes `fab dir` and `fab ls` show folders directly and reduces the need to switch to `fab api`.
- If `fab get` fails with host-specific errors such as `No Windows console found. Are you running cmd.exe?`, treat it as an embedded-host compatibility issue first, not as proof that the path or auth state is wrong. The same command may still work in a normal local PowerShell, Windows Terminal, or `cmd.exe` session. Use `fab api` rather than assuming the path is wrong.
- Folder paths can resolve inconsistently across `fab` commands. Verify folder operations carefully before depending on folder-contained item discovery for a larger workflow.

Example:

```powershell
fab dir
fab get "Analytics Dev.Workspace"
fab dir "Analytics Dev.Workspace"
fab dir "Analytics Dev.Workspace" -l
```

## Guardrails

- Prefer discovery commands before mutating commands.
- Prefer exact paths copied from `fab dir` output over inferred path prefixes.
- Use `fab dir` for listing and `fab get -q` for filtering JSON properties.
- When the user needs to iterate through workspace folders repeatedly, prefer enabling `folder_listing_enabled` before falling back to `fab api`.
- When `fab get` or folder listing is unreliable, prefer `fab api "workspaces/<wsId>/items"` and `fab api "workspaces/<wsId>/folders"` as the fallback source of truth.
- If an object type is uncertain, use `desc` rather than guessing the command family.
- When a notebook depends on `schema.table` targets, explicitly call out the boundary between OneLake paths and Spark schemas.
- A visible folder under `Lakehouse/Tables` can still coexist with Spark failures such as `SCHEMA_NOT_FOUND`; recommend verification from a notebook or SQL endpoint perspective before declaring the lakehouse ready.
- If no schema-level check is available in `fab`, recommend a bootstrap step such as `CREATE SCHEMA IF NOT EXISTS bronze`, `silver`, and `gold` in the target lakehouse before retrying the pipeline.
- Keep summaries short and structured when the listing is large.
- For workspace overview requests, prefer a compact visual structure over a plain bullet-only inventory.

## Output

- Explain the discovered structure in a visually ordered format.
- Include the path or item type you resolved.
- When the user asks for a workspace overview, present the result in a more visual format such as:
  - a short type summary table with counts
  - a compact tree-like listing grouped by item type or layer
  - a short "shape of the workspace" section before the detailed inventory
- Use bullets as a fallback, not the default, for workspace overviews.
- Call out which command families appear relevant next.

## Workspace Overview

When the user asks what is inside a workspace, prefer this response shape:

1. A one-line summary of the workspace shape, such as "1 Lakehouse, 1 SQL Endpoint, 1 Pipeline, 9 Notebooks".
2. A compact visual grouping, such as a Markdown table or tree grouped by item type.
3. Optional short notes about naming patterns, layers, or likely data flow.
4. Suggested next inspection commands or areas only if helpful.

Example format:

```text
Workspace shape
1 Lakehouse | 1 SQL Endpoint | 1 Pipeline | 9 Notebooks

Items
Lakehouse
- lakehouse

DataPipeline
- pl-main

Notebook
- nb_bronze_load_api_endpoints
- nb_silver_customers
- nb_silver_projects
```
