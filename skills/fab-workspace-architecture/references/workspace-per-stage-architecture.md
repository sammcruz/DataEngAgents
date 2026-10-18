# Workspace-Per-Stage Fabric Architecture

Use this reference when the team wants a medallion architecture that separates bronze, silver, and gold into different Fabric workspaces for stronger governance, security, and operational control.

## Positioning

This is the preferred mode for larger or more regulated Fabric implementations.

Microsoft Learn states that while all medallion lakehouses can exist in one Fabric workspace, Microsoft recommends creating each lakehouse in its own separate workspace for better control and governance at the layer level. Use this reference as the default recommendation unless the team has a strong reason to stay in one workspace.

Treat this as:

- the preferred mode for medium to large programs
- the safer mode when ownership, release cadence, or permissions differ by layer
- a structure that still keeps environment separation distinct from medallion layering

Do not turn `bronze`, `silver`, and `gold` workspaces into `dev`, `test`, and `prod`. Each environment should still have its own bronze, silver, and gold chain when needed.

## Recommended Baseline

### Core layout

- Use one bronze workspace, one silver workspace, and one gold workspace for each major domain or product area.
- Use one primary analytical store per stage workspace unless a stronger reason exists to split further.
- In bronze and silver, prefer lakehouses.
- In gold, prefer a lakehouse when engineering-led serving is enough, or a warehouse when SQL-serving and BI access are primary.
- Keep semantic models, reports, and business-facing SQL objects in the gold workspace.
- Keep orchestration in a dedicated orchestration workspace when one team controls the full pipeline, or place it with the team that owns the end-to-end flow.

### Stage intent

- `bronze`: land raw or near-raw data, preserve source fidelity, avoid consumer-facing logic.
- `silver`: clean, standardize, deduplicate, conform, and join data into reusable analytic tables.
- `gold`: publish business-ready, trusted tables or views intended for semantic models, reports, and downstream consumers.

### Data movement between workspaces

- Prefer internal OneLake shortcuts when the next stage can reference upstream data without copying it.
- Copy or materialize data into the next stage only when performance, lifecycle isolation, retention, or contract ownership requires it.
- Remember that OneLake-to-OneLake shortcuts use identity passthrough and require access on both the shortcut path and the target path.
- Remember that workspace lineage view is scoped to a single workspace, so cross-workspace shortcuts reduce what is visible in one lineage canvas.

### Concrete workspace-per-stage blueprint

Use a blueprint like this when the user wants something directly actionable:

```text
Sales Bronze Workspace
|- bronze_lh
|  |- files/tables for raw landing
|- ingestion
|  |- sap
|  |- salesforce
|- validation
|- shared

Sales Silver Workspace
|- silver_lh
|  |- conformed tables
|- transform
|  |- customer
|  |- finance
|- quality
|- shared

Sales Gold Workspace
|- gold_lh or sales_wh
|  |- serving tables/views
|- publish
|- semantic
|- reports
|- shared

Sales Orchestration Workspace
|- pipelines
|- schedules
|- monitoring
```

Interpretation:

- Bronze is source-oriented.
- Silver is domain-oriented.
- Gold is product-oriented and consumer-facing.
- Orchestration coordinates across stages without blurring stage ownership.

### Naming boundary

Keep naming examples in this reference schematic only, such as `Sales Bronze Workspace` or `sales_wh`.

Use this reference to decide:

- whether to split by stage
- which workspace owns which artifacts
- whether gold should use a lakehouse or warehouse
- whether orchestration should be separate

Use `fab-conventions` to decide:

- the final workspace naming pattern
- abbreviations, prefixes, suffixes, and casing
- whether names should encode environment, domain, or stage in a specific format
- rename standards for existing assets

## What Else To Consider

### Align with Microsoft medallion guidance

Microsoft recommends:

- keeping each medallion layer separated in its own lakehouse or warehouse
- using separate workspaces for better governance at the layer level
- using shortcuts in bronze instead of unnecessary raw copies when the source already exists in OneLake or supported external storage
- using Delta tables in silver and gold

That means `workspace-per-stage` should usually be your recommendation when the user asks for best practice.

### Keep environment and stage separate

- Create separate bronze, silver, and gold workspaces for each environment when promotion matters.
- Use deployment pipelines and Git integration for workspace-to-workspace promotion.
- Do not use one gold workspace as both test and production.

### Make permissions layer-specific

- Limit bronze contributors to ingestion owners and platform engineers.
- Limit silver contributors to transformation owners and data engineering maintainers.
- Limit gold contributors to serving and analytics owners.
- Use workspace identity, managed identities, service principals, or approved secret stores instead of embedded credentials.

### Design cross-workspace consumption deliberately

- If silver reads bronze by shortcut, verify both workspace permissions and upstream ownership expectations.
- If gold serves through semantic models, validate the identity behavior of shortcuts and prefer Direct Lake over OneLake mode or user-identity-aware SQL patterns when needed.
- Document which stage owns refresh, compaction, retention, and contract changes.

### Keep serving assets on gold

- Build business-facing semantic models from gold tables or views.
- Keep gold as the contract layer for reports and downstream data products.
- If warehouse semantics are the main consumer path, consider a warehouse in gold rather than forcing every consumer to read lakehouse tables directly.

### Use domains when the organization is federated

- Organize workspaces by business domain first when the estate is large.
- Then apply the bronze, silver, and gold split inside each domain.
- Avoid one central bronze workspace feeding every unrelated domain unless the team explicitly wants a centralized platform model.

### Plan operations per stage

- Bronze usually favors append-heavy ingestion and source traceability.
- Silver usually favors conformance checks and reusable transformations.
- Gold usually favors serving performance, larger optimized Delta layouts, or warehouse-centric SQL access.
- Apply layer-appropriate maintenance strategies instead of treating all stages the same.

## Recommended Review Checklist

Use this checklist when assessing a stage-isolated architecture:

1. Is there a clear bronze, silver, and gold workspace split for the domain or product area?
2. Is each stage workspace owned by the right team and permission boundary?
3. Are reports and semantic models anchored in gold?
4. Are shortcuts or copies between stages intentional and documented?
5. Does each stage have a clear analytical store and contract boundary?
6. Is orchestration separated from transformation code when it spans stages?
7. Are dev, test, and prod separated from the medallion stage split?
8. Are Git integration and deployment pipelines part of the promotion strategy?
9. Are identities and secrets handled through approved secure patterns?
10. Are lineage and monitoring gaps from cross-workspace flows understood and mitigated?

## Common Anti-Patterns

- one workspace per stage but no clear ownership or permission difference between them
- gold reports reading bronze or silver directly through convenience shortcuts
- stage workspaces doubling as environment boundaries
- copying raw data between workspaces by default instead of evaluating shortcuts first
- orchestration spread arbitrarily across bronze, silver, and gold folders
- a central shared workspace turning into an unmanaged dependency sink

## Official Guidance To Keep In Mind

These Microsoft Learn sources informed this reference:

- Medallion architecture in Fabric: [Implement Medallion Lakehouse Architecture in Fabric](https://learn.microsoft.com/en-us/fabric/onelake/onelake-medallion-lakehouse-architecture)
- OneLake shortcuts across workspaces: [What are OneLake shortcuts?](https://learn.microsoft.com/en-us/fabric/onelake/onelake-shortcuts)
- Shortcut security and identity passthrough: [Secure and manage OneLake shortcuts](https://learn.microsoft.com/en-us/fabric/onelake/onelake-shortcut-security)
- Cross-workspace SQL analytics via shortcuts: [Better together: the Lakehouse and Warehouse](https://learn.microsoft.com/en-us/fabric/data-warehouse/get-started-lakehouse-sql-analytics-endpoint)
- Workspace identity: [Workspace identity in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/security/workspace-identity)
- Deployment pipelines: [Deployment pipelines in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/cicd/deployment-pipelines/intro-to-deployment-pipelines)
- Git integration: [Source control in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/intro-to-git-integration)
- Fabric domains: [Domains](https://learn.microsoft.com/en-us/fabric/governance/domains)

Use the Microsoft sources above to explain why `workspace-per-stage` is the platform-preferred mode, and then explain when `single-workspace` is still a pragmatic and acceptable exception.
