---
name: sm-safe-update
description: Make a Power BI semantic model change in Fabric while respecting parent/child edit safety.
---

# Semantic Model Safe Update

## Action

Change a semantic model without risking one the team does not own. Run by the [`semantic-model-agent`](../agents/semantic-model-agent.md).

## Input

- The model name and what to change. Confirm which model is the **parent** (edit-restricted) and which is the **child or copy** (safe to iterate on) before touching anything. Check your private customer notes if unsure.

## Workflow

1. Classify the target: a parent the team does not own is read and query only, and changes need explicit sign-off. A child or copy is safe to iterate on.
2. Build and validate new logic in a DirectQuery child or copy first. Port validated DAX into a shared parent only on an explicit go-ahead.
3. Check the target's storage mode before proposing a DAX pattern. DirectQuery calculated columns have restrictions (for example `CONCATENATEX`), so keep a Power Query or measure-based fallback ready.
4. After any change, refresh and **query the model** to confirm the new column or measure returns the expected values on a few known examples.
5. For `Dataset_Import_FailedToImportDataset` or similar generic security or consistency errors on a Direct Lake model, check first that every Direct Lake source table exists in the target environment's Lakehouse (`fab ls .../Lakehouse/Tables`). A missing physical dependency produces the same generic wording. See [`docs/gotchas.md`](../docs/gotchas.md) for the full diagnostic order.

## After finishing

If a DAX or storage-mode constraint or an ownership boundary was not already known, record it in your private customer notes.

## Success Criteria

- No parent model was edited without sign-off.
- The change was verified by a query, not only by a clean import.
