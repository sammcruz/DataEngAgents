# Job Runbook

Use this reference when the user asks for a runbook-style workflow rather than a one-off command.

## Run Modes

- `fab job run <path>` is best when you want the CLI to run the job and wait.
- `fab job start <path>` is best when you want to trigger work and monitor separately.
- `fab job run-list <path>` is useful for finding recent execution IDs.
- `fab job run-status <path> --id <id>` is the main inspection command for a known run.

## Polling Helper

For longer waits, use:

```powershell
python scripts/poll_run.py "ws.Workspace/item.Notebook" "<run-id>"
```

Add `--schedule` when polling a scheduled run.

If the user does not know the run ID yet, use:

```powershell
python scripts/poll_latest_run.py "ws.Workspace/item.Notebook"
```

The helper:
- calls `fab job run-status ... --output_format json`
- prints each poll payload
- exits `0` on success
- exits `1` on terminal failure
- exits `2` on timeout
- exits `3` when the item has no runs yet

## Troubleshooting Sequence

1. Collect the latest runs with `fab job run-list`.
2. Inspect the specific run with `fab job run-status`.
3. Separate execution state from business logic failures in the summary.
4. If the user asks for a retry, make the retry explicit instead of silently rerunning.

## Recommended Summary

Include:
- item path
- run ID
- final state
- whether the run was interactive or scheduled
- notable errors or next action
