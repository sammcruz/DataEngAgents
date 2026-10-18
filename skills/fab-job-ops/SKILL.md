---
name: fab-job-ops
description: Use this skill for running, scheduling, monitoring, and troubleshooting Fabric jobs with fab-cli, especially for notebooks, pipelines, and Spark job definitions that need status checks, polling, or schedule updates.
---

# Fab Job Ops

## Use

Use this skill when the user wants Codex to operate Fabric jobs end to end with `fab job`. It covers synchronous runs, asynchronous starts, polling, schedule changes, cancellations, and concise run summaries.

Read [references/job-runbook.md](references/job-runbook.md) for runbook-style troubleshooting and scheduling work. Use [scripts/poll_run.py](scripts/poll_run.py) when the user needs repeated status polling with a timeout.

Use [scripts/poll_latest_run.py](scripts/poll_latest_run.py) when the user wants "watch the latest run" and does not have an ID ready.

## Workflow

1. Confirm the target item path and job mode: run now, start asynchronously, inspect, schedule, or cancel.
2. Use `fab job --help` and the relevant subcommand help if arguments are not obvious.
3. Trigger the run.
4. Poll with `fab job run-status` or `fab job run-list` when the task requires waiting or troubleshooting. Treat pipeline `NotStarted` as a possible queue state and keep polling before concluding the run is stuck.
5. If the user needs table-level validation, row counts, or business-quality checks after the run, switch to a notebook, SQL endpoint, or API-based validation step rather than trying to infer quality from pipeline status alone.
6. When the task is to verify notebook parameters passed by a pipeline, prefer an indirect proof if `run-status` does not expose resolved inputs: confirm the deployed pipeline definition contains the parameter mapping, confirm the pipeline created child notebook runs, and if needed run a direct negative test against the notebook with an invalid parameter value.
7. Summarize the final state, important timestamps, run IDs, and next action.

## Commands

Run a job synchronously:

```powershell
fab job run "ws.Workspace/item.Notebook"
```

Start without waiting:

```powershell
fab job start "ws.Workspace/item.Notebook"
```

Check recent runs:

```powershell
fab job run-list "ws.Workspace/item.Notebook"
```

Inspect one run in detail:

```powershell
fab job run-status "ws.Workspace/item.Notebook" --id "<run-id>"
```

Schedule a job:

```powershell
fab job run-sch "ws.Workspace/item.Notebook"
```

Poll until the run finishes:

```powershell
python scripts/poll_run.py "ws.Workspace/item.Notebook" "<run-id>"
```

Poll the latest run automatically:

```powershell
python scripts/poll_latest_run.py "ws.Workspace/item.Notebook"
```

## Troubleshooting Pattern

- If a job fails, gather `run-list` and `run-status` output before suggesting retries.
- Separate infrastructure failure, authentication failure, and notebook or pipeline logic failure when summarizing.
- Treat `fab job` as a run-control surface, not a data-validation surface. Successful job completion does not prove the loaded data has the right row counts, dates, or business realism.
- If a notebook run fails with schema errors such as `SCHEMA_NOT_FOUND`, do not treat successful `fab dir` or `fab exists` checks under `Lakehouse/Tables` as proof that the target Spark schema exists.
- For notebook jobs that write with `saveAsTable("<schema>.<table>")`, recommend verifying the schema from notebook or SQL endpoint perspective, or running a bootstrap step such as `CREATE SCHEMA IF NOT EXISTS bronze`, `silver`, and `gold`, before retrying the job.
- For long waits, report periodic status instead of staying silent.
- If cancellation is requested, use the specific run identifier and confirm that the target run changed state.
- Prefer `fab job run-status --id <run-id>` over `fab job run-list` whenever the run ID is known. In some environments `run-list` may return `No runs found` even though the run exists and `run-status` works.
- For pipeline runs, `NotStarted` can represent a queued state rather than a failure. Poll until it transitions or times out before concluding that the run is stuck.
- `fab job run-status` may not expose the resolved notebook input or parameter payload for a pipeline-created notebook run. Do not claim a runtime parameter value unless the tool output actually shows it.
- When verifying pipeline-to-notebook parameter wiring, combine deployment verification with execution verification: export or inspect the deployed pipeline definition for the parameter mapping, then confirm that the pipeline spawned the expected notebook child runs.
- If you need to prove that a notebook parameter is really bound and validated, run the notebook directly once with an intentionally invalid value and confirm it fails on the expected validation path.
- When the user asks whether the run produced good data, prefer a dedicated validation notebook that writes a compact report into the lakehouse over manual spot-checking from run logs.

## Output

- Include the exact job command.
- Report run ID, state, and whether the action completed or is still in progress in a compact status view.
- If scheduling changed, include the updated schedule details and what changed.
- If the run was validated with `run-status` because `run-list` was incomplete, say so explicitly.
- If parameter verification was indirect because `run-status` did not expose resolved inputs, say so explicitly and describe the evidence chain.
- If the likely blocker is a Spark schema mismatch rather than a path problem, say that explicitly so the user does not retry a job that is guaranteed to fail again.
- If additional data-quality validation is still needed after the job completes, say that explicitly instead of implying the run status answered it.
