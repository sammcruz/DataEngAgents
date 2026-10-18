# Fabric Conventions Matrix

This reference is a practical standard for Fabric naming and architecture work. It blends Microsoft platform constraints with team-level conventions that are reasonable to automate.

Treat each rule as one of:

- `Required`: platform limit or strong interoperability rule
- `Recommended`: default team standard
- `Optional`: local preference if the team already uses another consistent pattern

## Design Goals

- Make names understandable to humans before tools.
- Keep names sortable and portable across dev, test, and prod.
- Separate business meaning from environment and lifecycle state.
- Use architecture to express intent: domain, layer, and ownership.
- Prefer stability for published and shared objects.

## Workspace Level

### Guidance

- `Required`: Workspace names must avoid characters that cause XMLA friction or are unsupported by downstream tools. Microsoft notes that certain special characters are not supported in workspace names when using XMLA endpoints.
- `Recommended`: Omit redundant words such as `workspace`, `Fabric`, or the company name unless they add real clarity.
- `Recommended`: Keep names short enough to avoid UI truncation.
- `Recommended`: Use workspace names to express domain and purpose, not implementation detail.
- `Recommended`: Keep environment as a short suffix when separate workspaces exist per environment.

### Pattern

`<domain>-<purpose>-<env>`

Examples:

- `sales-analytics-dev`
- `finance-planning-prod`
- `customer360-shared`

### Notes

- Renaming a workspace is often safe, but Microsoft guidance notes XMLA connections can be affected because they use the workspace name.
- Workspace identity uses the same name as the workspace, so renames should include identity-aware validation.

## Folder Level

### Guidance

- `Required`: Follow Fabric folder restrictions. Microsoft documents unsupported characters, reserved names, and no leading or trailing spaces.
- `Recommended`: Use folders for stable navigation, not to encode every metadata attribute.
- `Recommended`: Keep folder names business-readable and sortable.
- `Optional`: Use numeric sort prefixes only when teams rely on ordered navigation.

### Pattern

`<nn>_<group>`

Examples:

- `10_bronze`
- `20_silver`
- `30_gold`
- `40_orchestration`

## Item Level

### General Guidance

- `Required`: An item name should clearly communicate purpose.
- `Recommended`: Keep type hints only when they reduce ambiguity or improve scanning.
- `Recommended`: Put environment in the workspace name first, not every item name.
- `Recommended`: Standardize abbreviations. Do not mix `cust`, `customer`, and `cst`.
- `Recommended`: Use lowercase with hyphens for workspace and folder names, and snake_case or PascalCase consistently for item and data object names depending on the object family.

### Suggested Item Prefixes

These are team conventions, not Fabric platform requirements:

| Item type | Recommended pattern | Example |
| --- | --- | --- |
| Lakehouse | `lh_<domain>_<layer>` | `lh_sales_bronze` |
| SQL endpoint | `sqle_<subject>` or paired with lakehouse name | `sqle_sales_bronze` |
| Warehouse | `wh_<domain>_<layer>` | `wh_sales_gold` |
| SQL database | `sql_<domain>_<purpose>` | `sql_sales_serving` |
| Mirrored database | `md_<source>_<domain>` | `md_d365_finance` |
| Notebook | `nb_<layer>_<verb>_<subject>` | `nb_silver_standardize_customer` |
| Spark job definition | `sj_<verb>_<subject>` | `sj_refresh_customer_features` |
| Environment | `env_<runtime-purpose>` | `env_pyspark_standard` |
| Pipeline | `pl_<verb>_<subject>` | `pl_load_sales_gold` |
| Dataflow Gen2 | `df_<verb>_<subject>` | `df_ingest_sales_customer` |
| Copy job | `cj_<verb>_<subject>` | `cj_copy_erp_orders` |
| Mounted Data Factory | `mdf_<source>_<purpose>` | `mdf_adls_landing` |
| Variable library | `vl_<scope>_<purpose>` | `vl_sales_deployment` |
| Semantic model | `sm_<subject>` or business-friendly name | `sm_sales_performance` |
| Report | business-friendly title | `Sales Performance` |
| Paginated report | `rpt_<subject>_<shape>` or business-friendly title | `rpt_order_statement` |
| Dashboard | business-friendly title | `Executive Sales Dashboard` |
| Scorecard | business-friendly title | `Sales KPI Scorecard` |
| App | business-friendly title | `Sales Analytics App` |
| Lakehouse shortcut | `sc_<source>_<subject>` | `sc_finance_gl` |
| User data function | `udf_<verb>_<subject>` | `udf_resolve_customer_tier` |
| Eventstream | `es_<source>_<purpose>` | `es_iot_ingestion` |
| Eventhouse | `eh_<domain>_<purpose>` | `eh_ops_monitoring` |
| KQL database | `kql_<domain>_<purpose>` | `kql_ops_logs` |
| KQL queryset | `kqs_<subject>` | `kqs_ops_health` |
| KQL dashboard | `kd_<subject>` | `kd_ops_observability` |
| GraphQL API | `gql_<domain>_<purpose>` | `gql_customer_api` |
| Data agent | `da_<domain>_<purpose>` or business-friendly name | `da_sales_analyst` |
| Reflex / Activator | `rx_<trigger>_<action>` | `rx_pipeline_failure_alert` |
| Digital twin builder | `dtb_<domain>_<purpose>` | `dtb_factory_layout` |
| Digital twin builder flow | `dtf_<verb>_<subject>` | `dtf_sync_sensor_state` |
| ML experiment | `mlxp_<subject>` | `mlxp_churn_prediction` |
| ML model | `mlm_<subject>` | `mlm_churn_v1` |

### Item Naming Rules

- `Recommended`: Use verb plus subject for runnable assets such as notebooks, pipelines, and dataflows.
- `Recommended`: Use subject plus layer for storage assets such as lakehouses and warehouses.
- `Recommended`: Do not encode owner initials in permanent object names.
- `Recommended`: Avoid dates in durable item names unless the item is truly temporary or versioned by design.
- `Optional`: Use prefixes for engineering-heavy workspaces; use friendlier names for business-facing reports and apps.

### Prefix Notes

- `Recommended`: Treat this table as a starter set, not an exhaustive canonical list, because Fabric item families continue to expand.
- `Recommended`: Keep business-facing Power BI artifacts friendlier than engineering artifacts. For reports, dashboards, scorecards, and apps, readable titles are usually better than rigid prefixes.
- `Recommended`: Use paired names where items are tightly related, for example `lh_sales_bronze` with `sqle_sales_bronze`.
- `Optional`: If a team prefers fewer prefixes, retain them for engineering or operational items first, such as notebooks, pipelines, environments, eventstreams, and variable libraries.

## Data Object Level

This section covers schemas, tables, views, shortcuts, measures, and semantic model objects.

### Architecture Guidance

- `Recommended`: Favor domain-oriented workspaces and clear medallion layers where they help ownership and lifecycle separation.
- `Recommended`: Use dimensional modeling for curated warehouse layers that feed semantic models.
- `Recommended`: Build semantic models as star schemas where possible.
- `Recommended`: Keep facts and dimensions distinct. Avoid mixed-grain tables.
- `Recommended`: Prefer active relationships whenever possible. Duplicate role-playing dimensions rather than relying on many inactive relationships when concurrent filtering is needed.

### Schema Naming

- `Recommended`: Use schemas to separate lifecycle or semantic purpose, not random team habits.
- `Recommended`: Common warehouse schema set:
  - `bronze`
  - `silver`
  - `gold`
  - `ref`
  - `audit`
  - `stg`

### Table Naming

- `Required`: Respect engine-specific naming constraints. For example, Fabric Load to Delta documents that table names for that flow allow alphanumeric characters and underscores only.
- `Recommended`: Use singular nouns for dimensions and reference entities when the team favors Kimball-style naming.
- `Recommended`: Use one naming family consistently:
  - `dim_customer`, `fact_sales`, `bridge_customer_account`
  - or `Customer`, `Sales`, `CustomerAccountBridge`
- `Recommended`: If using prefixes, use semantic ones such as `dim_`, `fact_`, `bridge_`, `xref_`, `snap_`.
- `Recommended`: Keep table grain obvious from the name.

Examples:

- `dim_customer`
- `dim_product`
- `fact_sales_order_line`
- `fact_inventory_snapshot_daily`
- `xref_product_category`

### View Naming

- `Recommended`: Use views to communicate consumption intent.
- `Recommended`: Prefix or suffix consistently, for example:
  - `vw_customer_current`
  - `vw_sales_mtd`
  - `customer_current_v`

### Notebook and Pipeline Object Naming

- `Recommended`: Notebook names should state the layer, action, and subject.
- `Recommended`: Pipeline names should state orchestration purpose, not implementation details like trigger timing.
- `Recommended`: Activity names inside pipelines should be explicit and sequence-friendly.

Examples:

- `nb_bronze_ingest_erp_orders`
- `nb_silver_conform_customer`
- `pl_refresh_sales_gold`
- `Copy ERP Orders`
- `Run Customer Conformance Notebook`

### Semantic Model Object Naming

- `Recommended`: Use business-friendly names for tables, columns, and measures.
- `Recommended`: Prefer explicit measures over implicit aggregation for important business metrics.
- `Recommended`: Add descriptions to tables, columns, and measures.
- `Recommended`: Create logical hierarchies.
- `Recommended`: Hide surrogate keys and technical join columns from report authors when not needed.

Tables:

- `Sales`
- `Customer`
- `Date`

Measures:

- `Total Sales`
- `Gross Margin %`
- `Orders Shipped`

Avoid:

- `TR_AMT`
- `M01`
- `Calc2`

## Column Level

### Guidance

- `Required`: Respect engine-specific restrictions. Fabric SQL database preview documentation lists unsupported characters for column names, and Load to Delta validates column names during ingestion.
- `Recommended`: Use full words and business meaning.
- `Recommended`: Use one casing style per platform surface:
  - snake_case for engineering tables
  - spaced business names for semantic model fields if user-facing
- `Recommended`: Keep key columns obvious:
  - `customer_key`
  - `customer_id`
  - `order_date`
- `Recommended`: Differentiate business keys from surrogate keys.
- `Recommended`: For role-playing dimensions, rename columns so labels are self-describing, such as `Ship Year` instead of generic `Year`.
- `Recommended`: Avoid overloaded short names such as `amt`, `val`, `desc`, `txt`, `dt`.
- `Recommended`: Do not rename published columns casually because reports, DAX, SQL, notebooks, and APIs may bind to them directly.

### Preferred Families

| Purpose | Example |
| --- | --- |
| Surrogate key | `customer_key` |
| Natural key | `customer_id` |
| Foreign key | `order_date_key`, `product_key` |
| Audit | `created_utc`, `updated_utc`, `is_current` |
| Type 2 SCD | `effective_from_utc`, `effective_to_utc`, `is_current` |
| Boolean | `is_active`, `has_discount` |
| Amount | `net_amount`, `gross_amount` |
| Rate | `discount_rate`, `tax_rate` |

## Assessment Criteria

When auditing an existing workspace, score at least these dimensions:

| Area | Questions |
| --- | --- |
| Workspace naming | Is the name concise, environment-aware, and domain-oriented? |
| Folder structure | Are folders consistent, sortable, and meaningful? |
| Item naming | Do prefixes, verbs, and subjects follow one standard? |
| Layering | Are bronze, silver, gold, curated, and serving layers distinguishable? |
| Modeling | Are facts, dimensions, keys, and relationships clear? |
| Semantic usability | Are names business-friendly, measures explicit, and descriptions present? |
| Rename risk | Would changing the name break references, CI/CD, XMLA, or dependent items? |

## Safe Remediation Rules

- Rename only when clarity gains outweigh break risk.
- Prefer remediation windows tied to deployment cycles.
- For high-dependency assets, use a compatibility period when possible.
- Update documentation, descriptions, and environment mappings at the same time as the rename.
- Preserve stable business-facing names even if engineering names behind them stay technical.

## Additional Considerations

These often matter as much as the naming itself:

- ownership model and domain boundaries
- environment strategy: separate workspaces versus shared workspace with suffixes
- CI/CD portability, especially relative references and variable libraries
- source control and deployment pipeline limitations for warehouses
- security labels, item tags, and descriptions as part of discoverability
- AI readiness: descriptive names, descriptions, and explicit measures improve Copilot and data agent results
- exception handling: define who can approve deviations and where they are documented

## Source Notes

This reference is based mainly on Microsoft Learn guidance and platform docs, including:

- Workspaces in Microsoft Fabric: [https://learn.microsoft.com/en-us/fabric/get-started/workspaces](https://learn.microsoft.com/en-us/fabric/get-started/workspaces)
- Tenant-level workspace planning: [https://learn.microsoft.com/en-us/power-bi/guidance/powerbi-implementation-planning-workspaces-tenant-level-planning](https://learn.microsoft.com/en-us/power-bi/guidance/powerbi-implementation-planning-workspaces-tenant-level-planning)
- Workspace folders: [https://learn.microsoft.com/en-us/fabric/fundamentals/workspaces-folders](https://learn.microsoft.com/en-us/fabric/fundamentals/workspaces-folders)
- Create items in workspaces: [https://learn.microsoft.com/en-us/fabric/fundamentals/create-items-in-workspaces](https://learn.microsoft.com/en-us/fabric/fundamentals/create-items-in-workspaces)
- Workspace identity: [https://learn.microsoft.com/en-us/fabric/security/workspace-identity](https://learn.microsoft.com/en-us/fabric/security/workspace-identity)
- Dimensional modeling in Fabric Warehouse: [https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-overview](https://learn.microsoft.com/en-us/fabric/data-warehouse/dimensional-modeling-overview)
- What is Fabric Data Warehouse: [https://learn.microsoft.com/en-us/fabric/data-warehouse/data-warehousing](https://learn.microsoft.com/en-us/fabric/data-warehouse/data-warehousing)
- Star schema guidance: [https://learn.microsoft.com/en-us/power-bi/guidance/star-schema](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema)
- Active versus inactive relationship guidance: [https://learn.microsoft.com/en-us/power-bi/guidance/relationships-active-inactive](https://learn.microsoft.com/en-us/power-bi/guidance/relationships-active-inactive)
- Optimize your semantic model for Copilot: [https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data](https://learn.microsoft.com/en-us/power-bi/create-reports/copilot-evaluate-data)
- Semantic model best practices for data agent: [https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices](https://learn.microsoft.com/en-us/fabric/data-science/semantic-model-best-practices)
- Copilot in Fabric Data Warehouse: [https://learn.microsoft.com/en-us/fabric/data-warehouse/copilot](https://learn.microsoft.com/en-us/fabric/data-warehouse/copilot)
- Relative references in Dataflow Gen2: [https://learn.microsoft.com/en-us/fabric/data-factory/dataflow-gen2-relative-references](https://learn.microsoft.com/en-us/fabric/data-factory/dataflow-gen2-relative-references)
- Source control with Fabric Data Warehouse: [https://learn.microsoft.com/en-us/fabric/data-warehouse/source-control](https://learn.microsoft.com/en-us/fabric/data-warehouse/source-control)
- Load to Delta Lake tables: [https://learn.microsoft.com/en-us/fabric/data-engineering/load-to-tables](https://learn.microsoft.com/en-us/fabric/data-engineering/load-to-tables)
- DAX column and measure references: [https://learn.microsoft.com/en-us/dax/best-practices/dax-column-measure-references](https://learn.microsoft.com/en-us/dax/best-practices/dax-column-measure-references)
