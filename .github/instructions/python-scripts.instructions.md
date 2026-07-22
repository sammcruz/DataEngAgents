---
applyTo: "scripts/**/*.py"
---

# Python Scripts

Scoped conventions for files under `scripts/`, in addition to the repo-wide
rules in [`copilot-instructions.md`](../copilot-instructions.md).

- Every write-capable command must accept an `--execute` flag and default to
  dry-run (see `fab_ado_board_agent.py` / `fab_ado_wiki_agent.py` for the
  pattern).
- Read credentials via `os.environ` first, config file second — never
  require a real value to be present in the repo for the script to import.
- Raise a repo-local `AgentError` (or equivalent) for expected operational
  failures; let unexpected exceptions propagate with a clear `[ERROR]`
  prefix, so a caller can distinguish "bad input" from "something broke".
- Write run output as JSON to `output/agents/<name>/runs/run-<timestamp>.json`
  and print the log path — every run should be reproducible after the fact.
