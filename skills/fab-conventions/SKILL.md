---
name: fab-conventions
description: Use this skill to define, assess, and safely apply Microsoft Fabric naming conventions and architecture standards with fab-cli, especially for workspace, folder, item, table, view, measure, and column-level governance.
---

# Fab Conventions

## Use

Use this skill when the task is to create or enforce conventions in Microsoft Fabric. It is optimized for three modes:

1. design conventions for new workspaces and items
2. assess an existing workspace and report convention drift
3. apply safer remediation steps for names or structure without ignoring downstream break risk

Read [references/conventions-matrix.md](references/conventions-matrix.md) when you need the actual naming and architecture standard. Keep `SKILL.md` focused on workflow and risk management.

Use `fab-discovery` first when the current workspace shape is still unknown. Use `fab-api-bridge` when first-class `fab` commands do not expose the metadata you need. Use `fab-workspace-organize` when the user mainly wants folder cleanup rather than conventions.

## Workflow

1. Determine whether the request is for design, assessment, or remediation.
2. Inventory the scope with `fab dir`, `fab get`, `fab desc`, `fab api`, and item-specific metadata sources.
3. Apply the reference standard from [references/conventions-matrix.md](references/conventions-matrix.md), but separate hard platform constraints from team preferences.
4. Report findings by level:
   - workspace and folder
   - item
   - data object such as schema, table, view, notebook, pipeline activity, measure
   - column
5. Before proposing any rename, map dependency risk and call out what can break.
6. Prefer phased remediation over big-bang renames for production assets.
7. Re-verify the resulting state and summarize accepted exceptions.

## Commands

Inventory a workspace and its items:

```powershell
fab dir
fab dir "Analytics Dev.Workspace" -l
fab get "Analytics Dev.Workspace"
fab api "workspaces" -X get
fab api "workspaces/<workspace-id>/items" -X get
fab api "workspaces/<workspace-id>/folders" -X get
```

Inspect a specific item before naming or structural changes:

```powershell
fab get "Analytics Dev.Workspace/wh_curated.Warehouse"
fab get "Analytics Dev.Workspace/lh_bronze.Lakehouse"
fab desc "Analytics Dev.Workspace/pl_main.DataPipeline"
```

Use fallback API access when the metadata surface is incomplete:

```powershell
fab api "workspaces/<workspace-id>/items/<item-id>" -X get
```

## Assessment Workflow

For audits, produce a short scorecard instead of only a raw inventory:

1. List the existing names and structure.
2. Classify findings as:
   - compliant
   - inconsistent but low risk
   - risky because rename can break dependencies
   - blocked because metadata is not accessible through the current path
3. Distinguish between:
   - platform violations such as unsupported characters or duplicate names
   - team convention drift such as mixed prefixes, mixed casing, or unclear medallion layering
4. End with a prioritized remediation plan:
   - fix now
   - fix during next deployment cycle
   - leave as exception and document it

## Rename Safety Checklist

Before renaming an existing workspace, item, table, view, measure, or column, check for these dependency classes:

- workspace name dependencies such as XMLA connections or external documentation
- pipeline references to notebooks, lakehouses, warehouses, or dataflows
- semantic model relationships, measures, report visuals, Q&A synonyms, or Copilot descriptions
- Dataflow Gen2 references, especially when they are absolute rather than relative
- warehouse source control and deployment pipeline behavior
- workspace identity coupling, because the identity name matches the workspace name
- OneLake shortcuts, notebooks, SQL scripts, CI/CD variables, and environment-specific configuration

Prefer this order for higher-risk renames:

1. inventory dependencies
2. create the target or replacement object if a phased cutover is possible
3. update dependent references
4. validate runtime behavior
5. retire the legacy name only after verification

## Guardrails

- Do not rename production assets only because a style rule says so.
- Treat workspace renames as low to medium risk, not zero risk, because XMLA connections can be affected.
- Treat item and object renames as potentially high risk when downstream items bind by name or ID.
- Keep platform limits, deployment tooling behavior, and source control limitations separate from aesthetic preferences.
- Prefer names that are clear to humans first; abbreviations are allowed only when they are standardized and low ambiguity.
- Document explicit exceptions instead of forcing a rename that creates more operational risk than value.

## Output

- For design requests, return a usable naming standard with examples.
- For audit requests, return a conventions scorecard and a prioritized findings list.
- For remediation requests, separate:
  - safe direct changes
  - changes that require phased rollout
  - changes that should stay manual or UI-assisted
- Always say which rules are hard requirements, strong recommendations, or optional preferences.
- Present audit and remediation output in a visually ordered format, preferably with tables and explicit severity markers.
