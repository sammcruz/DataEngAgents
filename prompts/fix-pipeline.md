---
name: fix-pipeline
description: Investigate and fix a failing Azure DevOps Pipeline run (a CI/CD deployment).
---

# Fix Pipeline

## Action

Read a failed pipeline run and its logs, diagnose the failure, present fix options and execute only on an explicit go-ahead. Run by the [`devops-pipeline-agent`](../agents/devops-pipeline-agent.md).

## Input

- A pipeline name or URL and a run id if known. If none is given, ask.

## Before starting

1. Read your private customer notes for the organization, project and the deployment pipeline's path, if they exist.
2. Check [`docs/gotchas.md`](../docs/gotchas.md) for a known root cause before re-diagnosing.
3. Confirm Azure DevOps access is actually available in this session before promising to execute anything.
4. **Read the actual deploy script and YAML once.** `fabric-cicd`-style pipelines typically deploy whatever is checked out of git, so they are blind to anything fixed only in a live workspace.

## Workflow

1. Get the failing run and its logs through the Azure DevOps REST API (a different surface from the board skill). Pattern: `_apis/pipelines/{id}/runs`, then `_apis/build/builds/{id}/timeline` (find the failed record's `log.url`), then `_apis/build/builds/{id}/logs/{logId}`.
2. Identify the exact failing step and error, not just "the pipeline failed".
3. Diagnose the root cause: known gotchas first. If it is novel, search for the exact error signature instead of guessing. For semantic-model import failures, trace the whole dependency chain (Direct Lake source tables, the notebook that fills them, the orchestration pipeline that runs it), because the cause is often one hop upstream.
4. Present the root cause and two or three concrete fix options with trade-offs. **Do not act yet.** Say which options are low blast radius (retry, transient) and which are structural.
5. On an explicit go-ahead:
   - **Retry the run:** safe, low blast radius.
   - **Fix the underlying artifact** (a model's roles, a notebook, a table): delegate to the matching skill.
   - **Edit the pipeline YAML or definition:** high blast radius for the whole team. Ask for a confirmation that names this action specifically.
6. Re-run to confirm. A successful retry after an artifact fix is the real proof. If the fix was applied live and the pipeline deploys from git, it must be committed before a retry can succeed. Say so.

## Success Criteria

- The failing step and exact error are identified.
- No pipeline definition was changed without a specific confirmation.
- The fix was proven by a re-run.
