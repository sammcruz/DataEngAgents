# Single-Workspace Fabric Architecture

Use this reference when the team wants one Fabric workspace with one primary lakehouse and medallion-style layering inside it. This reference is intentionally narrower than a general Fabric architecture guide.

## Positioning

Microsoft Fabric guidance strongly supports medallion architecture, but many official examples isolate bronze, silver, and gold into separate workspaces or separate lakehouses for stronger security and operational boundaries. If the team is intentionally standardizing on one workspace and one lakehouse, apply the controls below to keep that pattern disciplined.

Treat this as:

- a valid constrained operating model for smaller teams or domain-owned workspaces
- not a reason to blur environment boundaries
- not a substitute for explicit security, deployment, and data-product contracts

## Recommended Baseline

### Core layout

- Use one primary lakehouse per workspace for analytical tables that follow the workspace's domain boundary.
- Enable and use lakehouse schemas to model `bronze`, `silver`, and `gold` explicitly.
- Keep workspace folders for code and runnable assets, not for replacing data-layer contracts.
- Use a dedicated orchestration folder for pipelines and triggers.
- Use a dedicated shared folder for utility notebooks, environment helpers, and reusable libraries.

### Stage intent

- `bronze`: land raw or near-raw data, preserve source fidelity, avoid consumer-facing logic.
- `silver`: clean, standardize, deduplicate, conform, and join data into reusable analytic tables.
- `gold`: publish business-ready, trusted tables or views intended for semantic models, reports, and downstream consumers.

### Suggested workspace folder split

The exact names belong in the naming-conventions skill. Architecturally, the workspace should separate at least:

- a bronze folder for ingestion notebooks and bronze-adjacent dataflows
- a silver folder for transformation notebooks
- a gold folder for publishing notebooks or SQL assets
- an orchestration folder for pipelines, schedules, and control tables
- a shared folder for utilities, test helpers, and framework code

If the workspace is large, add subfolders by source system or domain inside each stage rather than mixing stage and source directly at the root.

### Concrete single-workspace blueprint

Use a blueprint like this when the user wants something directly actionable:

```text
Workspace
|- Lakehouse
|  |- bronze schema
|  |- silver schema
|  |- gold schema
|- bronze
|  |- sap
|  |- salesforce
|- silver
|  |- customer
|  |- finance
|- gold
|  |- semantic-serving
|  |- operational-kpis
|- orchestration
|  |- pipelines
|  |- control
|- shared
|  |- utils
|  |- tests
|  |- config
```

Interpretation:

- `bronze/<source>` keeps landing logic close to each source system.
- `silver/<domain>` keeps reusable transformation logic aligned to business concepts.
- `gold/<product-or-serving-area>` keeps consumer-facing outputs grouped by purpose.
- `orchestration/` owns coordination across stages.
- `shared/` prevents utility code from polluting stage folders.

## What Else To Consider

### Keep medallion flow one-way

- Allow dependencies only from bronze to silver to gold.
- Prevent notebooks in bronze from reading gold as an input.
- Prevent reports or semantic models from binding straight to bronze except for controlled engineering diagnostics.
- Treat gold outputs as the serving contract.

### Keep bronze immutable where practical

- Prefer append-only or snapshot-style ingestion.
- Avoid applying business rules in bronze.
- Preserve source columns and metadata that help trace lineage and replay.
- Record ingestion timestamps, source system, and extraction identifiers early.

### Prefer shortcuts over unnecessary raw copies

- Use OneLake shortcuts when the source already exists in OneLake or supported external storage and a copy is not required for governance or performance reasons.
- Copy data into bronze only when you need isolation, history retention, performance shaping, or transformation control.
- Be deliberate about what is physically duplicated.

### Treat schemas as data contracts and folders as delivery structure

- Put tables and views into `bronze`, `silver`, and `gold` schemas.
- Put notebooks, pipelines, SQL scripts, and helper artifacts into folders that match their primary lifecycle stage.
- Do not rely on folders alone to indicate data quality or serving readiness.

### Keep serving assets on gold

- Build business-facing semantic models from gold tables or views.
- If the workload is BI-heavy and SQL-serving semantics matter, consider whether a Warehouse or SQL endpoint layer belongs on top of gold even if the main persistence stays in one lakehouse.
- Use Direct Lake or SQL consumption against curated gold objects rather than raw ingestion tables.

### Make ownership explicit

- Assign each bronze source area an owning ingestion team or maintainer.
- Assign each silver domain area an owner responsible for conformance rules and reusable semantics.
- Assign each gold serving area a product owner or analytics owner.
- Make exceptions explicit when one notebook updates objects across multiple stages.

### Separate orchestration from transforms

- Put pipelines, schedules, and control logic in orchestration folders rather than mixing them into bronze, silver, or gold implementation folders.
- Keep stage notebooks focused on one responsibility: ingest, transform, or publish.
- Centralize shared functions in the shared folder so stage notebooks stay readable and replaceable.

### Design for deployment, not just for one workspace

- Keep dev, test, and prod as separate workspaces even if each workspace uses the same one-lakehouse pattern.
- Use Git integration and deployment pipelines for promotion rather than hand-editing production as the source of truth.
- Avoid environment-specific secrets or IDs inside notebooks; externalize configuration.

### Use secure identities and secret handling

- Prefer workspace identity, managed identities, service principals, or approved secret stores instead of embedded credentials.
- Restrict who can modify bronze ingestion and gold publishing paths.
- Remember that a single workspace reduces some isolation, so permissions need to be more deliberate.

### Monitor operational quality

- Track pipeline and notebook failures by stage.
- Use lineage views and metadata checks to confirm that gold objects derive from silver and bronze as intended.
- Add lightweight data quality checks before promotion into gold.
- Plan compaction or table-maintenance routines for large Delta tables where performance matters.

### Review exceptions deliberately

These can be acceptable, but only when documented:

- a small utility notebook stored in `shared` but used by all stages
- a source-specific quality check living under `bronze/<source>`
- a gold publication notebook that also materializes a final silver helper object during cutover
- a raw copy in bronze even though a shortcut exists, when replay, retention, or performance requires it

## Recommended Review Checklist

Use this checklist when assessing a workspace:

1. Is there exactly one primary analytical lakehouse for the workspace's domain?
2. Are bronze, silver, and gold represented as schemas rather than only as folders?
3. Are notebooks placed by lifecycle stage, with shared utilities separated?
4. Are pipelines concentrated in an orchestration area?
5. Are raw ingests landing in bronze with minimal transformation?
6. Are silver objects the main reusable transformation layer?
7. Are reports and semantic models reading from gold only?
8. Are shortcuts used intentionally instead of duplicating raw data by default?
9. Are secrets and identities handled without hard-coded credentials?
10. Is the workspace clearly one environment rather than a mix of dev, test, and prod?

## Common Anti-Patterns

- one lakehouse with medallion folder names but no actual schema boundaries
- notebooks for every stage mixed together at the workspace root
- pipelines stored beside individual notebooks instead of in an orchestration area
- direct report access to bronze or silver tables
- business rules embedded in bronze ingestion code
- raw copies proliferating even when shortcuts would satisfy the requirement
- one workspace acting as both engineering sandbox and production serving area

## Official Guidance To Keep In Mind

These Microsoft Learn sources informed this reference:

- Medallion architecture in Fabric: [Medallion architecture in Fabric](https://learn.microsoft.com/en-us/fabric/onelake/onelake-medallion-lakehouse-architecture)
- Lakehouse schemas and medallion examples: [Create and use schemas in lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-schemas)
- OneLake shortcuts and one-copy principles: [What are OneLake shortcuts?](https://learn.microsoft.com/en-us/fabric/onelake/onelake-shortcuts)
- Workspace identity and secure access patterns: [Workspace identity in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/security/workspace-identity)
- Deployment pipelines: [Deployment pipelines in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/intro-to-deployment-pipelines)
- Git integration and source control: [Source control in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration)
- Delta optimization and maintenance guidance: [Delta Lake table optimization and V-Order](https://learn.microsoft.com/en-us/fabric/data-engineering/delta-optimization-and-v-order)

Use the Microsoft sources above to explain the platform-preferred direction. Then explain clearly where the team's chosen single-workspace pattern is a pragmatic constraint rather than the default recommendation.
