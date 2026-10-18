---
name: audit-workspace
description: Inventory a Fabric workspace and propose a reorganization plan without executing destructive changes.
---

# Audit Workspace

## Action

Produce a clear picture of a workspace's current structure and a phased,
reversible plan to bring it in line with the target architecture — without
deleting or moving anything until each phase is verified.

## Input

- The target workspace name.
- Optionally, a target architecture mode (`single-workspace` or
  `workspace-per-stage` — see `skills/fab-workspace-architecture`, and
  `skills/fab-workspace-organize` for the folder work).

## Workflow

1. Inventory current items and folders.
2. If no architecture mode was given, default to `workspace-per-stage` and
   say so explicitly.
3. Define the target folder structure.
4. Propose folder creation first — this step is additive and safe to run
   immediately.
5. Propose asset moves/recreation in phases, each one independently
   verifiable.
6. For each phase, state the verification command
   (`fab exists`, `fab dir`, `fab api`) before proposing the next phase.
7. Only propose removing obsolete assets after their replacement has been
   verified.

## Success Criteria

- No asset is ever in a state where only one broken copy exists.
- Every phase has an explicit verification step before the next one starts.
- Medallion boundaries (Bronze/Silver/Gold) stay explicit in the final
  structure.
