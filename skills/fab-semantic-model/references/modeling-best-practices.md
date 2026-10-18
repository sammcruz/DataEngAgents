# Semantic Modeling Best Practices

Use this reference when you need a source-backed default for semantic-model cleanup decisions.

## Core Defaults

- Prefer a star schema with fact tables on the many side and dimension tables on the one side.
- Prefer one-to-many relationships and single-direction filtering unless a special scenario clearly requires more.
- Treat bidirectional filtering, many-to-many relationships, and ambiguous filter paths as exceptions that need justification.
- Use a real date table for time intelligence.
- Hide technical join columns and helper fields from report authors.
- Default visible numeric columns to `Do Not Summarize` and prefer explicit measures for aggregation.
- Keep model names and descriptions business-friendly and consistent.

## Safe Heuristics

### Distilled Microsoft Learn Baseline

- Model for analytics with a star schema whenever practical:
  - fact tables store events or transactions at a defined grain
  - dimension tables store descriptive attributes used for filtering and grouping
- Keep table grain explicit. Do not mix multiple incompatible grains in the same fact table unless the model is intentionally designed for that.
- Prefer denormalized dimensions over overly snowflaked dimensions unless normalization is required for governance or reuse.
- Treat many-to-many relationships as exceptions. Prefer bridge-table patterns or redesigned dimensions when that yields a clearer model.
- Treat bi-directional filtering as an exception, not a default. Use it only when a well-understood scenario truly requires it.
- Prefer one active relationship path between tables involved in a filter flow. Avoid ambiguous filter propagation.
- For role-playing dimensions, especially dates, prefer one active relationship plus inactive alternates with explicit DAX where needed, unless duplicating the dimension is the clearer user experience.
- Align relationship keys by semantic meaning and compatible data type before creating or changing a relationship.
- Use a dedicated date table for time intelligence and reporting consistency. It should cover the required date range and have unique daily dates.
- Disable reliance on auto date/time in favor of an explicit date table.
- Prefer measures for business calculations instead of leaving important behavior to implicit aggregations.
- Use display folders and descriptions to improve authoring usability, but do not churn metadata if the model is already clean and stable.
- Favor low-cardinality dimension attributes and hide technical columns that are not intended for report authors.
- Document exceptions when the ideal star-schema pattern is not possible because of source constraints, semantic ambiguity, or backward-compatibility risk.

### Relationships

- A relationship is usually safe to add only when the likely dimension key is unique, the fact-side values match the same semantic domain, and the filter direction is obvious.
- Prefer keeping one active relationship between a fact table and a date table. Additional date joins may need inactive relationships and explicit DAX instead of more active paths.
- If a fact table joins to the same dimension in multiple roles, prefer either inactive alternate relationships or duplicated role-playing dimensions based on what is clearer and safer for report authors.
- For fact tables at higher grains, avoid pretending a lower-grain relationship is exact when it is not. Keep the model honest about granularity.
- If the model already relies on a snowflake, avoid aggressive flattening unless the user asked for broader redesign.

### Date Tables

- Verify that the model has a real date column with unique daily granularity before treating it as the primary date table.
- Mark the date table appropriately when the model supports it.
- Ensure the date table supports the required reporting span and common calendar attributes such as year, quarter, month, and sortable month labels where needed.
- If no valid date table exists, do not fake time-intelligence correctness. Create guarded measures that return `BLANK()` and document the blocker.

### Measures and Organization

- Prefer explicit measures over relying on implicit aggregation for important business metrics.
- A dedicated measures table is useful when it improves discoverability and keeps fact tables cleaner, but avoid churn if the existing structure is already clean and the user did not ask to move measures.
- Use display folders to group calculation families such as Revenue, Margin, Time Intelligence, and Status.
- Prefer visible objects to use readable names instead of CamelCase-heavy technical names.
- Prefer format strings on visible numeric columns and measures.
- When editing DAX, prefer `DIVIDE()` over the `/` operator when the denominator is not a constant.
- When editing DAX, prefer fully qualified column references and unqualified measure references.

### Performance and Metadata

- Favor integer data types for keys and counts.
- Avoid floating-point `Double` when fixed decimal or integer is semantically correct.
- Avoid high-cardinality text columns unless they are genuinely needed for analysis.
- Hide technical columns that only support relationships, sorting, or ETL lineage.
- Add descriptions because they improve maintainability and downstream author experience.
- If the model uses cultures, keep translated names, descriptions, hierarchy levels, and display folders aligned.
- If the model uses perspectives, ensure visible objects appear in the relevant perspectives.
- Prefer a proper shared date table over auto date/time.
- Treat unused hidden columns or hidden measures as cleanup candidates, but do not auto-delete them without checking dependency risk.

## Tabular Editor Rule Coverage

Use this merged Tabular Editor baseline for the skill.

### Precedence

1. Start with the Tabular Editor 3 built-in BPA rules as the base set.
2. Add only non-overlapping or materially stronger rules from the older Tabular Editor 2 and GitHub `BestPracticeRules` set.
3. Keep destructive, environment-specific, or ambiguous rules as review-only findings unless the user explicitly asks to enforce them.
4. When actual model state and rule heuristics disagree, trust verified model metadata and safe modeling judgment over blind rule enforcement.

### Merged Baseline

Baseline from TE3:

- invalid characters in names
- invalid characters in descriptions
- calculated objects must have expressions
- imported columns must have sources
- relationship data types must match
- avoid provider partitions with structured data sources
- many-to-many relationships should prefer single-direction filtering
- hide foreign keys
- set numeric columns to `Do Not Summarize`
- remove auto date tables in favor of an explicit shared date table
- remove unused data sources
- add format strings to measures
- add format strings to visible numeric and date columns
- add descriptions to visible objects
- trim accidental whitespace in names
- ensure a proper date table exists
- calculation groups should contain items
- perspectives should contain relevant visible objects when perspectives are used
- prefer the latest supported Power BI compatibility level

Additional useful TE2 and GitHub rules:

- DAX expression style:
  - use `DIVIDE()` instead of `/` when the denominator is not a constant
  - fully qualify column references
  - keep measure references unqualified
  - flag `TODO` markers in DAX expressions
- model usability:
  - organize large sets of visible columns and hierarchies into display folders
  - organize large sets of visible measures into display folders
- translations:
  - translate visible names when cultures exist
  - translate descriptions when cultures exist
  - translate hierarchy level names when cultures exist
  - translate display folders when cultures exist
- naming consistency:
  - prefer aligned key names across simple relationships
  - prefer role-specific fact-side key names when multiple relationships exist between the same two tables
- cleanup candidates:
  - identify unused hidden columns
  - identify unused hidden measures
- metadata precision:
  - avoid floating-point `Double` where whole number or fixed decimal is the correct semantic type

### Review-Only Rules

Keep these as review findings unless the user explicitly asks for aggressive enforcement:

- deleting unused columns or measures
- provider and connection-string enforcement rules
- partition naming enforcement
- attribute hierarchy disabling for hidden columns
- broad rename rules that could break downstream reports or external tools
- compatibility-level upgrades without checking deployment and environment readiness
- any translation or perspective backfill in models that are not intentionally multilingual or persona-scoped

## Official Guidance

- Microsoft Learn: [Understand star schema and the importance for Power BI](https://learn.microsoft.com/power-bi/guidance/star-schema)
- Microsoft Learn: [Create and manage relationships in Power BI Desktop](https://learn.microsoft.com/power-bi/transform-model/desktop-create-and-manage-relationships)
- Microsoft Learn: [Bi-directional relationship guidance for Power BI Desktop](https://learn.microsoft.com/power-bi/guidance/relationships-bidirectional-filtering)
- Microsoft Learn: [Active vs inactive relationship guidance](https://learn.microsoft.com/power-bi/guidance/relationships-active-inactive)
- Microsoft Learn: [Set and use date tables in Power BI Desktop](https://learn.microsoft.com/power-bi/transform-model/desktop-date-tables)
- Microsoft Learn: [Create and use display folders in Power BI Desktop](https://learn.microsoft.com/power-bi/transform-model/desktop-display-folders)
- Microsoft Learn: [Create measures for data analysis in Power BI Desktop](https://learn.microsoft.com/power-bi/transform-model/desktop-measures)
- Tabular Editor docs: [Built-in BPA Rules](https://docs.tabulareditor.com/en/features/built-in-bpa-rules.html)
- Tabular Editor docs: [Best Practice Analyzer overview](https://docs.tabulareditor.com/en/getting-started/bpa.html)
- Tabular Editor: [BestPracticeRules repository](https://github.com/TabularEditor/BestPracticeRules)

## Power BI Modeling MCP Server Note

If the Power BI Modeling MCP Server is available in the current environment, use it as the primary control plane for connecting to Fabric semantic models, open Power BI Desktop models, and TMDL folders. Do not hand-edit TMDL in that case.
