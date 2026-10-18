---
name: fab-workspace-architecture
description: Use this skill to design, assess, and refine Microsoft Fabric workspace architecture with fab-cli, especially when choosing between a single-workspace medallion pattern and a workspace-per-stage pattern for bronze, silver, and gold with clear governance, security, and deployment boundaries.
---

# Fab Workspace Architecture

## Use

Use this skill when the task is about Fabric workspace architecture rather than naming. It is optimized for:

1. designing a new medallion-aligned workspace pattern
2. choosing between one workspace and separate bronze, silver, gold workspaces
3. auditing an existing setup against that pattern
4. planning safer remediation when structure, dependencies, or security boundaries are unclear

Use `fab-conventions` when the main problem is naming or naming standardization. Use `fab-workspace-organize` when the main problem is folder creation or cleanup. Use `fab-discovery` first when the current workspace shape is still unknown.

Read the relevant reference before making architecture recommendations:

- [references/single-workspace-architecture.md](references/single-workspace-architecture.md) for the compact, one-workspace pattern
- [references/workspace-per-stage-architecture.md](references/workspace-per-stage-architecture.md) for the larger, stage-isolated pattern that aligns more closely with Microsoft guidance

Keep `SKILL.md` focused on workflow and decision-making.

Do not use this skill as the primary skill when the user mainly wants:

- exact workspace, item, folder, schema, table, or column naming rules
- prefix, suffix, abbreviation, or casing standards
- rename planning or rename safety analysis

In those cases, hand off to `fab-conventions` after the architecture mode and target shape are clear.

## Mode Selection

Choose one of these two modes explicitly:

1. `single-workspace`
   Use when the project is small to medium, the team is compact, governance is light, and simplicity matters more than strict isolation.
2. `workspace-per-stage`
   Use when the project is growing, multiple teams or owners are involved, security boundaries matter, or the user wants the platform-preferred design for medallion governance.

Default to `workspace-per-stage` when the user asks for best practice without constraining the solution.

Default to `single-workspace` only when the user explicitly wants one workspace, the scope is intentionally small, or operational simplicity clearly outweighs stronger isolation.

## Workflow

1. Determine whether the task is design, assessment, or remediation.
2. Determine the architecture mode:
   - `single-workspace`
   - `workspace-per-stage`
3. Inventory the relevant workspace or workspaces with `fab dir`, `fab get`, `fab api`, and item-specific metadata where needed.
4. Apply the target pattern from the matching reference.
5. Separate findings into:
   - hard platform or operational risks
   - strong recommendations
   - optional preferences
6. Verify dependency flow:
   - sources or shortcuts into bronze
   - bronze into silver
   - silver into gold
   - gold into serving items such as semantic models or reports
7. Call out where the chosen pattern differs from Microsoft guidance and why that tradeoff may still be acceptable.
8. End with a concrete target structure, exceptions list, and next actions.

## Architecture Defaults

Use these defaults unless the user gives a better domain-specific variant:

- For `single-workspace`:
- one primary lakehouse for analytical persistence in the workspace
- `bronze`, `silver`, and `gold` schemas inside that lakehouse
- root-level workspace folders for stage assets, orchestration, and shared utilities

If the recommended design uses Lakehouse schemas such as `bronze`, `silver`, and `gold`, call out that the Lakehouse should be created with schema support enabled, for example `fab create "<workspace>/<lakehouse>.Lakehouse" -P enableSchemas=true`.
- For `workspace-per-stage`:
  - one primary bronze workspace, one primary silver workspace, and one primary gold workspace for the same domain or program
  - one primary analytical store per stage workspace unless a stronger reason exists to split further
  - shortcuts or controlled data movement between workspaces
  - serving assets, semantic models, and business-facing SQL objects anchored in gold
  - orchestration placed either in a dedicated orchestration workspace or in the stage that owns end-to-end control

When the user is also organizing by business domain, recommend domains first and then apply the chosen mode inside each domain. Do not mix unrelated domains into the same bronze, silver, gold chain unless the user explicitly accepts that coupling.

Describe naming patterns only at the placeholder level in this skill, such as:

- `<domain>-bronze-workspace`
- `<domain>-silver-workspace`
- `<domain>-gold-workspace`
- `<lakehouse>`
- `<warehouse>`

Do not invent or enforce the final prefix, suffix, abbreviation, or casing standard here. Send that follow-up work to `fab-conventions`.

## Preferred Target Shapes

Recommend a `single-workspace` shape like this:

```text
<workspace>
|- <lakehouse>
|  |- bronze schema
|  |- silver schema
|  |- gold schema
|- bronze/
|  |- <source-system>/
|- silver/
|  |- <domain-area>/
|- gold/
|  |- <data-product-or-serving-area>/
|- orchestration/
|  |- pipelines/
|  |- schedules/
|- shared/
|  |- utils/
|  |- tests/
|  |- config/
```

Recommend a `workspace-per-stage` shape like this:

```text
<domain>-bronze-workspace
|- <bronze-lakehouse>
|- ingestion/
|- validation/
|- shared/

<domain>-silver-workspace
|- <silver-lakehouse>
|- transform/
|- conformance/
|- shared/

<domain>-gold-workspace
|- <gold-lakehouse-or-warehouse>
|- publish/
|- semantic/
|- reports/
|- shared/

<domain>-orchestration-workspace (optional)
|- pipelines/
|- schedules/
|- monitoring/
```

If the team is small, keep only one layer of subfolders. If the implementation grows, prefer `stage -> source` in bronze, `stage -> domain` in silver, and `stage -> product` in gold rather than mixing patterns inconsistently.

## Commands

Inventory a single workspace:

```powershell
fab dir "Analytics Dev.Workspace" -l
fab get "Analytics Dev.Workspace"
fab api "workspaces/<workspace-id>/items" -X get
fab api "workspaces/<workspace-id>/folders" -X get
```

Inventory multiple stage workspaces:

```powershell
fab dir "Sales Bronze.Workspace" -l
fab dir "Sales Silver.Workspace" -l
fab dir "Sales Gold.Workspace" -l
fab api "workspaces/<bronze-workspace-id>/items" -X get
fab api "workspaces/<silver-workspace-id>/items" -X get
fab api "workspaces/<gold-workspace-id>/items" -X get
```

Inspect a lakehouse, warehouse, notebook, or pipeline before making architecture recommendations:

```powershell
fab get "Analytics Dev.Workspace/lh_core.Lakehouse"
fab get "Analytics Gold.Workspace/wh_serving.Warehouse"
fab get "Analytics Dev.Workspace/nb_bronze_ingest_sales.Notebook"
fab desc "Analytics Dev.Workspace/pl_ingest_sales.DataPipeline"
```

Inspect underlying metadata when the first-class surface is incomplete:

```powershell
fab api "workspaces/<workspace-id>/items/<item-id>" -X get
```

## Assessment Focus

For an architecture audit, check at least these dimensions:

- architecture mode fit, including whether the current mode is still appropriate
- lakehouse or warehouse strategy, including whether stage stores are being used consistently
- schema strategy for bronze, silver, and gold where a single workspace or single lakehouse is used
- workspace split strategy for notebooks, pipelines, semantic models, and shared assets
- ingestion pattern, including shortcuts versus copied raw data
- dependency direction and whether gold depends on raw assets directly
- serving pattern, especially whether reports or semantic models bypass gold
- security and identity handling
- deployment readiness, including whether a workspace is trying to represent multiple environments at once
- cross-workspace access controls and lineage visibility limitations when stage workspaces are used

## Guardrails

- Treat bronze, silver, and gold as contract boundaries, not just folder labels.
- If those stage boundaries live as Lakehouse schemas in one Lakehouse, require schema-enabled Lakehouse creation rather than assuming schema support is implicit.
- Do not expose bronze directly to business-facing semantic models or reports.
- Do not expose silver directly to business-facing semantic models or reports unless the user intentionally accepts that it is a semicurated consumer layer.
- Do not mix shared utility notebooks into bronze, silver, or gold stage folders; keep them in a dedicated shared area.
- Do not put orchestration notebooks and pipelines inside stage folders when they coordinate multiple stages.
- Prefer phased remediation when changing item placement or dependencies for active workloads.
- Be explicit when the `single-workspace` choice trades away security, lineage isolation, or operational control that separate workspaces would provide.
- Be explicit when the `workspace-per-stage` choice adds operational overhead, access-management work, and more cross-workspace dependency handling.
- Keep environment separation distinct from medallion layering; a single workspace should not become dev, test, and prod at the same time.

## Decision Heuristics

Use these defaults when the user has not specified the structure in detail:

- Put ingestion notebooks, landing dataflows, and source-specific validation in `bronze`.
- Put standardization, conformance, deduplication, and reusable joins in `silver`.
- Put serving tables, publishing notebooks, and semantic-model-facing SQL artifacts in `gold`.
- Put multi-stage pipelines, triggers, restart logic, and control metadata in `orchestration`.
- Put helper modules, environment bootstrapping, test fixtures, and notebook templates in `shared`.

Prefer `workspace-per-stage` when any of the following is true:

- different teams own bronze, silver, and gold
- the user wants clearer workspace-level permissions and approvals by layer
- deployment and release cadence differ by stage
- gold must be tightly controlled for BI consumers
- the project is large enough that root-level clutter or broad contributor access is becoming a problem

Prefer `single-workspace` when all of the following are mostly true:

- one team owns most artifacts end to end
- the project is still evolving quickly
- security boundaries between stages are light
- operational simplicity matters more than stronger workspace isolation
- the user is intentionally optimizing for speed and low ceremony

When an item fits multiple categories, place it where its primary responsibility lives and call out any cross-stage coupling explicitly.

## Naming Boundary

Keep this skill focused on structural decisions:

- how many workspaces to use
- which artifacts belong in bronze, silver, gold, orchestration, or shared areas
- whether a domain should stay together or split by stage
- where semantic models, reports, lakehouses, and warehouses should live

Keep `fab-conventions` focused on naming decisions:

- exact workspace and item names
- prefixes and suffixes
- abbreviations
- casing and separators
- rename standards and remediation

When the user needs both, do them in this order:

1. Use `fab-workspace-architecture` to choose the mode and target shape.
2. Use `fab-conventions` to turn that shape into concrete names and rename rules.

## Output

- For design requests, return the chosen mode, target architecture, rationale, and exceptions.
- For audit requests, return a short scorecard plus prioritized findings.
- For remediation requests, separate:
  - safe structural changes
  - changes that need dependency validation
  - changes that should stay manual or happen during deployment windows
- Always distinguish official-platform guidance from team-specific constraints or choices.
- When the user wants a recommendation, say plainly that Microsoft guidance prefers stronger layer isolation through separate workspaces, while a single workspace remains a pragmatic option for smaller implementations.
- If naming examples help, keep them schematic and explicitly say that `fab-conventions` owns the final naming standard.
- Present the main recommendation and audit output in a visually ordered format, preferably with a scorecard, comparison table, or simple diagram when helpful.
