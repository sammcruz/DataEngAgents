---
name: fix-env-diff
description: Investigate and fix a Fabric pipeline or notebook that fails in one environment but not another.
---

# Fix Environment Difference

## Action

Diagnose why the same pipeline or notebook behaves differently across environments, fix it where the human is debugging, then replicate the fix to the sibling pre-production environment. Run by the [`incident-agent`](../agents/incident-agent.md).

## Input

- The pipeline or notebook name, the **failing** environment and the **working** environment.
- If any of the three is missing, ask. Do not guess which environment is which.

## Before starting

Read your private knowledge for the customer and repository if it exists, including known incidents. See [`docs/knowledge-layer.md`](../docs/knowledge-layer.md) and [`docs/gotchas.md`](../docs/gotchas.md).

## Workflow

1. **Read the actual failure**: run logs and error messages (`fab-job-ops`), not assumptions. If the REST API returns only a generic wrapper (for example `System_Cancelled_Session_Statements_Failed`), try `fabric-notebook-toolkit` first: list the notebook's Livy sessions, then `monitor list-apps`, then `logs get-driver --filename stderr`, or reproduce the failing cell in a DEV or TEST `fntk` session to read `data.error`. If that yields nothing, say so and ask the human to paste the traceback from the portal's run snapshot. Never open sessions in production without explicit approval.
2. **Compare environments.** Table schemas first (`fab table schema`, the fastest signal), then notebook logic (`fab export` plus diff) if schemas match. Use `fab-table-query` for data-level comparison. Do not stop at the failing item: trace one hop upstream. Does the data it needs exist in the target environment, and if not, does the notebook that would create it exist **and has it actually run there**? Check migration state and job history, not only that the notebook text matches.
3. **State a root-cause hypothesis before changing anything.** Confirm with the human for anything non-obvious or destructive. Hold it loosely: a first hypothesis that fixes nothing is a result, not a failed attempt.
4. **Implement live in the workspace** (`fab-notebook-dev`, or a targeted `fntk cell update` and cell-by-cell iteration), starting with the environment being debugged. Never edit a customer's local git checkout.
5. **Validate.** Rerun the affected item, confirm success and repeat the step-2 drift check. Do not poll run status to save cost: verify by exporting and inspecting content, or with one short `fntk code run` count or sample query. Delete any session when done.
6. **Replicate.** Ask whether to apply the same fix to the other pre-production environment so the next deployment does not overwrite it. Do it explicitly.
7. **Workspace fix versus pipeline fix.** A workspace-only fix proves the diagnosis. It does not make a CI/CD pipeline succeed if that pipeline deploys from git. Tell the human which of the two you reached before they retry.
8. Production stays read-only unless the human explicitly approves an emergency action. Delete any temporary production artifact and verify its removal.

## After finishing

Summarize root cause, items touched, environments changed and validation evidence. Record a specific incident in the error log. Record how the workspace is designed to work (a notebook's real purpose, a convention, a cross-notebook dependency) in the repository notes.

## Success Criteria

- The root cause is stated with evidence, not asserted.
- Both environments were compared before and after.
- The human knows whether the fix is workspace-only, in git, or deployed.
