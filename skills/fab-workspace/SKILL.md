---
name: fab-workspace
description: Use this skill to design and organize Fabric workspaces with fab-cli, combining architecture decisions and practical folder-structure execution.
---

# Fab Workspace

## Use

Use this merged workspace skill for both architecture and organization tasks:

1. Choose a target workspace pattern (single workspace or workspace-per-stage)
2. Inventory current workspace items and folders
3. Plan a practical folder structure
4. Execute safe reorganization in phases
5. Verify outcomes and call out manual follow-up

## Architecture Modes

1. `single-workspace`
   - Best for smaller teams and simpler operations
   - Use stage schemas/folders within one workspace
2. `workspace-per-stage`
   - Best for stricter governance and team separation
   - Keep bronze/silver/gold in separate workspaces

Default to `workspace-per-stage` when best-practice guidance is requested without constraints.

## Workflow

1. Inventory current state.
2. Pick architecture mode explicitly.
3. Define target structure.
4. Create folders first.
5. Move or recreate assets in controlled phases.
6. Verify each step with `fab exists`, `fab dir`, or `fab api`.
7. Remove obsolete assets only after replacement is validated.

## Commands

Inventory workspace:

```bash
fab config set folder_listing_enabled true
fab dir "<workspace>.Workspace" -l
fab get "<workspace>.Workspace"
```

Create folders:

```bash
fab mkdir "<workspace>.Workspace/10_Bronze.Folder"
fab mkdir "<workspace>.Workspace/20_Silver.Folder"
fab mkdir "<workspace>.Workspace/30_Gold.Folder"
fab mkdir "<workspace>.Workspace/40_Orchestration.Folder"
```

Validate state:

```bash
fab exists "<workspace>.Workspace/10_Bronze.Folder"
fab api "workspaces/<workspace-id>/items" -X get
fab api "workspaces/<workspace-id>/folders" -X get
```

## Guardrails

- Do not delete the only working copy of a notebook or pipeline.
- Prefer phased cutover over risky in-place refactors.
- Keep medallion boundaries explicit and documented.
- Report unsupported folder/move behavior clearly.
- Separate completed changes from recommended follow-up.
