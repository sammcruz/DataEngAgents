---
name: fab-semantic-model
description: Use this skill to inspect, improve, create, and document Microsoft Fabric or Power BI semantic models, especially when creating a populated semantic model from Fabric first, exporting it with fab-cli, editing the model locally through the Power BI Modeling MCP Server, and then re-importing it with safe best practices for relationships, naming, measures, hierarchies, descriptions, and documentation.
---

# Fab Semantic Model

## Use

Use this skill when the task is to inspect, clean up, extend, or document a semantic model.

This skill is optimized for:

1. improving an existing model end-to-end with safe direct changes
2. reviewing a model and separating safe fixes from risky recommendations
3. building reusable semantic-model standards for a team
4. documenting a model in Markdown for handoff or governance

If the Power BI Modeling MCP Server is available, always use it for model inspection and changes. Do not edit TMDL files directly when that server is present. Use exported TMDL only for documentation or diff-friendly inspection when helpful.

Read [references/modeling-best-practices.md](references/modeling-best-practices.md) when choosing defaults, deciding whether a change is safe, or explaining why something was skipped.

When Tabular Editor guidance is relevant, use the merged Tabular Editor baseline in [references/modeling-best-practices.md](references/modeling-best-practices.md).

Use `fab-discovery` only when you first need to discover the Fabric workspace or semantic model identity. Use `fab-conventions` when semantic model item naming, folder naming, or cross-workspace naming governance matters in addition to model internals.

## Connection Order

Prefer this connection order:

1. open Power BI Desktop model on Windows when the user says the file is already open
2. local TMDL or PBIP semantic-model definition folder exported from Fabric with `fab`
3. Fabric semantic model in a workspace when the user gives workspace and model names and a live connection is truly needed

Use `connection_operations` to inspect available connections and connect through the correct path:

- `ListLocalInstances` for open Desktop models
- `ConnectFolder` for TMDL or PBIP semantic-model definition folders
- `ConnectFabric` for Fabric-hosted semantic models
- `GetLastUsed` or `SetLastUsed` when continuing an existing modeling session

When loading a PBIP project, connect only to the `.SemanticModel/definition` folder.

For Fabric-hosted work, strongly prefer `ConnectFolder` after a `fab export` because it avoids unnecessary live-session dependency and usually avoids interactive authentication prompts. Use `ConnectFabric` as the fallback or final-validation path when:

- the semantic model already exists and no local export/import loop is needed
- `fab export` does not produce a usable semantic-model definition
- you must validate or inspect the final live item directly

When `ConnectFabric` is used, expect that Fabric may open an interactive browser sign-in window. Treat this as normal rather than as a failure, but avoid this path when a local TMDL workflow is available because it is slower.

## Workflow

1. If the task is to create or rebuild a Fabric semantic model, create a populated semantic model in Fabric first rather than trying to create the item through the MCP server.
2. Prefer this creation order for new Direct Lake models:
   - create the semantic model with all intended source tables first, without modeling cleanup
   - prefer a `fab` path that creates a populated semantic model directly from the source item
   - if `fab` can only create an empty placeholder model in the current version, use Fabric UI to create the populated model, then return to the local export/import loop
3. For Fabric-hosted work, prefer this loop:
   - create a populated semantic model first
   - export the semantic model locally with `fab export`
   - connect the MCP server to the exported `.SemanticModel/definition` folder with `ConnectFolder`
   - model locally through the MCP server
   - re-import the semantic model with `fab import`
   - use `ConnectFabric` only if final live validation is needed
4. If the task is an existing live model cleanup with no export/import loop, connect to the target model with the Power BI Modeling MCP Server.
5. Inventory the current state with `model_operations`, `table_operations`, `column_operations`, `measure_operations`, `relationship_operations`, `user_hierarchy_operations`, `perspective_operations`, `security_role_operations`, `culture_operations`, `partition_operations`, `calendar_operations`, and `named_expression_operations` as needed.
6. Split findings into:
   - safe direct changes
   - ambiguous or risky items that should be skipped and documented
7. For multi-object edits, prefer a transaction or a tightly grouped sequence so partial updates are minimized.
8. Apply changes in this order unless the request calls for a narrower scope:
   - relationships and star-schema cleanup
   - safe naming cleanup
   - hide technical fields
   - field properties and data types
   - measures table and core measures
   - display folders
   - hierarchies
   - descriptions
   - Markdown documentation
9. Re-read the affected objects after each major change area.
10. For a newly created Direct Lake model, run the first model refresh before DAX validation because queries can fail until the model has been refreshed at least once.
11. Validate measure expressions with `measure_operations`, `function_operations`, and `dax_query_operations` when the logic changed materially.
12. End with a consolidated summary of changes, skips, assumptions, and follow-up advice.

## Practical Caveats

- Treat `fab mkdir <name>.SemanticModel` as potentially creating only an empty placeholder model. Do not assume the exported TMDL will contain usable Direct Lake bindings unless you verify that tables and partitions were created.
- For new Direct Lake work, prefer a populated-model-first flow over an empty-model-first flow.
- If the local terminal host causes `fab get` or similar commands to fail with errors such as `No Windows console found`, switch to `fab api` instead of assuming the path or authentication is wrong.
- `fab config set folder_listing_enabled true` helps discovery, but it does not enable same-workspace item moves between folders.
- Same-workspace item moves into folders may currently fail with `NotSupported`. Prefer creating the item in the correct folder first and report the limitation clearly if later placement is blocked.
- In Direct Lake models, setting `IsKey` explicitly on columns may be rejected. Prefer relationships, hiding, and `Do Not Summarize` over forcing key metadata.
- Some model-level properties, such as `DiscourageReportMeasures`, may not be supported at the current Fabric compatibility level. Apply them opportunistically and document unsupported settings instead of treating them as hard failures.
- When creating measures, avoid names that collide with existing column names. Validate this especially in fact tables where common KPI names often mirror raw numeric columns.
- Hierarchy inventory through the MCP tool is table-scoped. When validating created hierarchies, query each relevant table explicitly rather than assuming one list call will return the full model.

## Fabric Item Guidance

- Treat the Fabric item and the internal semantic model as related but distinct layers.
- Follow `fab-conventions` for the workspace-facing semantic model item name whenever a convention exists or the user cares about naming standards.
- Keep a clear distinction between Fabric item naming and internal semantic naming:
  - Fabric item name: should follow workspace and platform naming conventions
  - internal model, table, column, hierarchy, and measure names: should optimize for business readability unless a translation strategy says otherwise
- Use `fab` to create the semantic model item and to rename the workspace-facing display name.
- For new Direct Lake models, prefer creating the populated item first and only then exporting it for local modeling.
- Use the MCP server to model tables, columns, measures, hierarchies, relationships, and model metadata.
- Do not rely on MCP model rename operations alone to rename the Fabric item shown in the workspace.
- When the user wants a cleaner business-facing name, apply the final display-name rename with `fab set <path> -q displayName -i <new-name>`.
- If the workflow goal is speed, prefer local modeling through exported TMDL over live Fabric editing because live connections can trigger interactive sign-in windows.

## Modeling Rules

### 1. Star Schema

- Prefer fact-to-dimension relationships with dimensions on the `1` side and facts on the `*` side.
- Prefer single-direction filtering from dimension to fact.
- Prefer one active relationship path between two filter domains.
- Create a missing relationship only when the join looks clearly inferable from names, compatible data types, and likely uniqueness on the dimension side.
- Skip relationships that would introduce ambiguity, many-to-many risk, or uncertain business meaning.
- If a snowflake can be flattened safely into a simpler star, recommend it; do not force a large restructure unless the user asked for broader remodeling.

### 2. Naming

- Standardize tables, columns, measures, hierarchies, and folders toward short business-facing names.
- Favor consistency over cleverness.
- Prefer readable names with spaces over CamelCase for visible objects unless the model relies on translations that intentionally present user-friendly names separately.
- Prefer visible table and measure names that start with uppercase letters and avoid technical prefixes in user-facing names.
- Apply only safe renames that can be updated cleanly in dependent objects during the same session.
- When one relationship exists between two tables, prefer aligned key names on both sides. When multiple role-playing relationships exist, prefer fact-side names that clarify the role, such as `Order Date Key` and `Ship Date Key`.
- Re-check affected measures, hierarchies, sort-by settings, relationships, translations, and perspectives after renames.

### 3. Hidden Technical Fields

Hide fields that are primarily technical and not useful to report authors, such as:

- surrogate keys
- foreign keys
- `*ID`, `*Id`, `*Key`
- GUIDs
- row identifiers
- sort helper columns that should not be used directly

Keep business attributes visible when users may actually slice, filter, search, or reconcile by them.

### 4. Data Types and Field Properties

- Prefer whole numbers for integer keys, sequence numbers, and counts.
- Use `Date` or `DateTime` deliberately; do not keep timestamps when a date grain is the real semantic meaning.
- Avoid floating-point `Double` where fixed decimal or whole number is the better semantic type.
- Keep decimal types only where fractional precision is needed, such as currency, rates, percentages, ratios, or measurements.
- Default visible numeric columns to `Do Not Summarize`; prefer explicit measures for business aggregations instead of implicit column summarization.
- Set IDs and codes to `Do Not Summarize`.
- Assign format strings to visible numeric and date fields and to visible numeric measures.
- Avoid risky type changes that could break relationships, DAX logic, or source-query assumptions.

### 5. Measures Table and Core Measures

- Reuse an existing dedicated measures table when present; otherwise create one.
- Move explicit measures into that table when the user wants central organization.
- Hide any placeholder column used only to host the table.
- Detect the primary fact table or fact tables before creating measures.
- Detect the amount column, status column, and primary date table from the model rather than assuming names.
- If a valid date table or calendar is missing, create time-intelligence measures that return `BLANK()` and explain why.
- Use `DIVIDE` for percentage measures and other protected division patterns.
- Prefer fully qualified column references and unqualified measure references in DAX where expressions are touched.
- State assumptions for business definitions such as `Net Sales`.

### 6. Display Folders

- Keep folder names short, professional, and stable.
- Reuse a good existing structure rather than churning names.
- Group measures by business area or calculation family, not by every tiny variation.
- Normalize casing and separator style when the current folders are inconsistent.
- When a table has many visible columns, hierarchies, or measures, organize them into display folders for usability.

### 7. Hierarchies

Create or repair only natural drill paths that actually exist in the data, for example:

- Date: `Year > Quarter > Month > Day`
- Geography: `Country > Region/State > City`
- Product: `Category > Subcategory > Product`

Do not create redundant hierarchies or duplicate what a calendar object already handles well.

### 8. Descriptions

Add clear descriptions to tables, columns, measures, and hierarchies.

Use these description rules:

- tables: business purpose and grain
- columns: meaning, business unit where relevant, and notable usage notes
- technical keys: short technical purpose only
- measures: plain-language definition and a brief logic summary
- hierarchies: intended drill path and level meaning

When cultures exist, prefer translated names, descriptions, hierarchy level names, and display folders instead of leaving only the base-language metadata.

### 9. Documentation

When asked to generate semantic-model documentation, produce Markdown that includes:

- overview and intended usage
- table-by-table data dictionary
- measures with DAX and business explanation
- relationship summary
- role or row-filter summary when roles exist
- high-level Power Query source summary when it can be derived safely
- Mermaid ER diagram
- display-folder layout
- assumptions, exceptions, and skipped risky changes

## Safety Rules

- Default to safe, non-breaking changes.
- Prefer metadata and organizational cleanup before structural remodeling.
- Do not create ambiguous relationships.
- Do not convert data types when relationship or logic breakage is likely.
- Do not assume a date table is valid just because a table is named `Date` or `Calendar`; verify it.
- If auto date/time tables exist, prefer a proper shared date table and treat auto date/time as technical debt.
- Prefer active single-path filtering over bidirectional fixes.
- If a required business rule is unclear, implement the safest neutral version and document the assumption.
- Do not delete unused hidden columns or measures automatically unless dependencies have been checked carefully; report them as cleanup candidates by default.
- Do not force perspective or translation work unless the model already uses perspectives or cultures, or the user explicitly wants multilingual or persona-specific design.
- When the model is large or the change is broad, checkpoint progress with concise summaries between phases.

## Output

For end-to-end improvement requests, return:

- connection path used
- summary of safe changes applied
- skipped items with reason
- rename mapping
- hidden fields by table
- property and data type changes
- created or moved measures
- final folder structure
- created or updated hierarchies
- description coverage stats
- complete Markdown model documentation when requested

Always state whether the Power BI Modeling MCP Server was used and whether any direct changes were intentionally deferred for safety.
