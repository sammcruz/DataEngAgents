---
name: fab-semantic-model
description: Use this skill to inspect, improve, and document Fabric or Power BI semantic models with safe, incremental changes to relationships, measures, naming, and metadata.
---

# Fab Semantic Model

## Use

Use this skill when the user asks to:

1. Review semantic model quality
2. Improve relationships and naming
3. Organize measures and display folders
4. Add model documentation and descriptions
5. Apply safe cleanup without breaking reports

## Workflow

1. Connect to the model through your preferred path (Fabric, Desktop, or local definition folder).
2. Inventory model objects: tables, columns, measures, relationships, roles, cultures.
3. Separate changes into safe-now vs risky-needs-confirmation.
4. Apply improvements in this order:
   - relationship cleanup
   - naming and visibility cleanup
   - measure organization
   - hierarchy and description updates
5. Re-check dependent objects and validate key DAX logic.
6. Summarize applied changes, skipped risks, and next actions.

## Recommended Priorities

- Prefer star-schema relationships and clear filter direction.
- Hide technical keys and helper fields from report authors.
- Keep business names short, clear, and consistent.
- Centralize explicit measures in a dedicated measures table.
- Add descriptions for tables, columns, and measures.

## Guardrails

- Default to non-breaking changes.
- Avoid ambiguous relationships.
- Avoid risky type changes without user approval.
- Document assumptions when business logic is unclear.
- Validate DAX after materially changing measure logic.
