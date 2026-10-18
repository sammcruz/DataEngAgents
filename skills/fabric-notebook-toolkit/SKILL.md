---
name: fabric-notebook-toolkit
description: Use when iterating on, debugging, or verifying a Fabric notebook interactively with Microsoft's Fabric Notebook Toolkit (`fntk`) — running an existing notebook cell by cell in a live Spark session, running ad-hoc verification queries without creating a debug notebook, reading real cell output and tracebacks, editing one cell in place, or pulling Spark driver and cell logs. Prefer this over the fab-cli export → import → full `fab job start` loop whenever the goal is to iterate or inspect; keep `fab-notebook-dev` for bulk definition edits, new-item creation in folders, and the final full end-to-end run.
---

# Fabric Notebook Toolkit (`fntk`)

`fntk` (PyPI `fabric-notebook-toolkit`, Microsoft, **preview**) drives the same notebook workload API the Fabric web editor uses: interactive Jupyter/Livy sessions, per-cell edits, ad-hoc code execution with real outputs, Spark monitoring and logs. All output is JSON with `--json`. The CLI is young and changes quickly, so treat `fntk --help` and `fntk <domain> <cmd> --help` as the source of truth for flags.

What it changes compared with the plain `fab` CLI loop in `fab-notebook-dev`:

| Task | Old way (fab-cli) | With `fntk` |
|---|---|---|
| See a cell's real output or traceback | Not possible — `fab job run-status` only reports a generic failed-statements status | `code get-result` returns `data.outputs` / `data.error` |
| Check a hypothesis against data | Create a `debug_*` notebook → write JSON to `Files/_debug` → `fab cp` → delete the notebook | `code run --code "..."` in a session on the existing notebook; nothing is created in the workspace |
| Change one line in one cell | `fab export` → patch the `.ipynb` → `fab import -f` | `cell update --cell-index N --code "..."` |
| Iterate on a fix | Re-import and a full `fab job start` every time (cold start each run) | One warm session; re-run only the cell you changed |
| Final validation of the real writer | `fab job start` | **Still `fab job start`** (see Validation below) |

## Setup (one-time per machine)

```bash
pipx install fabric-notebook-toolkit --python python3.13   # check the supported Python range on PyPI
fntk --version
```

- It installs its own `ms-fabric-cli` inside its virtual environment. Keep the global `fab` on the same version so both share one `~/.config/fab` login.
- **Be careful with `fntk init`.** It scans the git root for folders holding Fabric `.platform` files and upserts a managed block into a `CLAUDE.md` there, and it registers plugin marketplaces. Inside a customer repository checkout that edits files you do not own. Run it only in a scratch folder, or skip it and use this skill instead. Its built-in guidance is still readable with `fntk skill get <id> --json` (for example `fabric-session-ids`, `spark-debug`, `notebookutils`).
- Remote telemetry to Microsoft is on by default. For customer engagements export `FNTK_TELEMETRY_DISABLED=1` (in your shell profile, or in the same command before every `fntk` call): it keeps local logs and drops remote sending.

## Auth (every session)

`fntk` needs **both** a Fabric CLI token and an Azure CLI token, for the **same account and tenant** as the target workspace:

```bash
fab auth login --tenant <TENANT_ID>     # interactive
az login --tenant <TENANT_ID>           # interactive
FNTK_TELEMETRY_DISABLED=1 fntk discover whoami --json --client-name <your-agent-name>
```

- Both are interactive browser logins: an agent should hand these commands to the human, not try to run them.
- When working on a customer tenant, sign in to that tenant with both CLIs, or `fntk` may get a token for the wrong directory.
- `FAB_AUTH_UNAVAILABLE` or "Fabric CLI could not supply a token without interaction" means the `fab` login has expired.

## Always pass

`--json --client-name <your-agent-name>` on every operational call. Read the envelope, not the exit code:

- Top-level `status: "success"` means **the query succeeded**, not that Spark is ready or your code worked.
- Session ready ⇔ `data.livy_session_state == "idle"`.
- Execution done ⇔ `data.status` is `completed` or `error`; then read `data.outputs` / `data.error`.
- Follow `next_actions[].retry_after` / `stop_condition` for polling; on error read `error.suggestion` first.
- On a flag error run `fntk <domain> <cmd> --help` once instead of guessing again. `code run` has **no file flag** — pass multi-line code as `--code "$(cat cell.py)"`.

## Resolve IDs by name, every session

Never hardcode GUIDs in skills, knowledge files or scripts. Resolve and echo them at the start of each session:

```bash
fntk discover list-workspaces --json --client-name <agent>                 # → workspace_id by display name
fntk discover list-notebooks -w <WS_ID> --json --client-name <agent>     # → artifact_id by display name
fntk discover list-lakehouses -w <WS_ID> --json --client-name <agent>
```

## Core loop: run an existing notebook cell by cell

```bash
W=<WS_ID>; A=<ART_ID>; F="--json --client-name <agent>"
export FNTK_TELEMETRY_DISABLED=1

fntk notebook list-sessions -w $W -a $A $F           # reuse an idle session if one exists
fntk notebook start-session -w $W -a $A $F           # → data.session_id; Livy cold start takes minutes
fntk notebook get-session  -w $W -a $A -s <SID> $F   # poll until data.livy_session_state == "idle"

fntk cell list -w $W -a $A $F                        # index, type, preview of every cell
fntk cell get  -w $W -a $A -i 3 $F                   # full source of cell 3

# run cells 0..5 in order in the live session, stopping at the first error:
python3 skills/fabric-notebook-toolkit/scripts/fntk_run_cells.py -w $W -a $A --cells 0-5

fntk notebook delete-session -w $W -a $A -s <SID> $F   # ALWAYS, when finished
```

How it actually works — keep this model in mind:

- There is **no "run saved cell N" command**. `code run --code` submits code to the session's kernel; the helper script reads the live notebook content and submits each code cell's source in order. Kernel state (variables, temp views, `%run` imports) persists between submissions exactly like the Fabric editor.
- The session uses the notebook's own default Lakehouse and Environment, so unqualified `spark.table(...)` resolves as it would in a real run.
- **Parameter cells:** to test with different parameters, submit an override instead of editing the notebook: `--override 1=/path/params_override.py` in the helper script, or run the cell, then `code run --code "param_name = 'value'"`.
- `%%configure` cells restart the session when run — the helper skips them unless `--include-configure`.
- `%run <helper_notebook>` cells are submitted as-is like in the editor. Confirm the behaviour the first time you rely on it in your environment.
- Fresh state without a cold start: `notebook restart-kernel -k <KERNEL_ID>`. A wedged cell: `code cancel --execution-id <EID>` or `notebook interrupt-kernel`.

## Ad-hoc verification queries (replaces the debug-notebook pattern)

Attach a session to an **existing** notebook whose default Lakehouse is the one you need (often the writer notebook itself) and run read-only code:

```bash
fntk code run -w $W -a $A --code "print(spark.table('gold.dbo.sales_summary').filter(\"name like '%[%'\").count())" $F
fntk code get-result -w $W -a $A --execution-id <EID> $F
```

- Nothing is created in the workspace: no `debug_*` notebook, no `Files/_debug` JSON, nothing left to clean up or to pollute the Git status of the workspace (stale debug notebooks otherwise keep showing up as pending changes).
- `code run` does **not** save code into the notebook. Only `cell *`, `notebook put-content` and `notebook set-lakehouse` change it.
- Do **not** `set-lakehouse` on a real notebook just to query another Lakehouse — that persists a metadata change on the live item. Use 3-part names (`silver.dbo.table`) instead; if you really need another binding, create a throwaway notebook (`notebook create`) and delete it afterwards.
- Prefer `print(...)` / `.collect()` / `toPandas().to_string()` over `display()` for agent-readable output.
- The JSON-to-OneLake pattern in `fab-notebook-dev` is still the fallback when `fntk` auth isn't available.

## Editing cells in place

```bash
fntk notebook get-content -w $W -a $A --output-file <scratch>/<nb>.before.ipynb --json   # snapshot first, always
fntk cell update -w $W -a $A -i 4 --code "$(cat <scratch>/cell4.py)" $F
fntk cell insert -w $W -a $A -i 5 --code "..." $F
fntk cell append -w $W -a $A --type markdown --code "..." $F
fntk cell get    -w $W -a $A -i 4 $F                                      # read back to confirm
```

- Every `cell update/insert/append/delete`, `put-content`, `set-lakehouse`, `set-parameter`, `set-language`, `notebook delete` **saves to the live item immediately, and `fntk` asks for no confirmation**. Your own approval gate (for example a "propose, wait for approval, then edit" step in the agent definition) is the only gate.
- It does a GET plus a full PUT of the notebook and **does not enforce an ETag**: if someone has the notebook open with unsaved changes in the browser, one side's changes are lost. Ask before editing a notebook someone may have open.
- Content-only edits keep cell metadata and the notebook's Lakehouse binding. Keep the binding workspace-local (never bind to a Lakehouse in another workspace) when using `set-lakehouse` or `put-content`.
- Prefer `cell update` for targeted changes. For a large rewrite (five or more cells restructured) use `get-content --output-file` → edit → `put-content --input-file`, then `cell list` to verify — or the `fab export` / `fab import` flow.
- Live edits stay live-only until committed through Fabric Git integration, and a later deployment from git can revert them. Nothing about that changes.

## Validation

Cell-by-cell runs prove each step works on real data; they do **not** replace one clean end-to-end run, because a warm interactive kernel can hide state a scheduled run wouldn't have (a variable defined by an earlier ad-hoc submission, a temp view, a different parameter value). After iterating:

1. `fntk notebook delete-session …`
2. One full run of the real writer with `fab job start` (or its pipeline), per `fab-notebook-dev` and `fab-job-ops`.
3. Verify the result with an `fntk code run` query (count or sample), in a new short session.

## Diagnosing a failure

- Interactive run failed: `code get-result` → `data.error` has the exception and traceback. Start there.
- Slow, out of memory or skewed: `notebook get-session` (→ `livy_id`) → `monitor list-apps --livy-id` (→ `app_id`) → `monitor get-diagnostic / get-advice / get-progress --app-id`; per cell: `monitor get-replmaps` (→ `job_group_id`) → `logs get-cell`.
- Driver log: `logs get-driver --livy-id <LID> --app-id <APP> --filename stderr` (Python tracebacks land in `stderr`; `stdout` for prints).
- A failed **scheduled or pipeline** run: `notebook list-livy-sessions` lists the notebook's Livy history (including job runs) → take its `livy_id` → `monitor list-apps` / `logs get-driver`. This is the route to the real traceback that the REST job API does not return. Verify it on your first real incident.
- 404s on `monitor` and `logs` are almost always the wrong ID type: `activity_id ≠ livy_id`. Load `fntk skill get fabric-session-ids --json`.

## Hard rules

- **PROD:** no `fntk` sessions, `code run`, or cell edits against production workspaces by default. Running code in a session executes it for real in that workspace; it is not a read-only operation like `fab job run-status`. A read-only diagnostic session in production needs explicit human approval for that specific query.
- **Running a writer cell executes the write.** `saveAsTable`, `MERGE`, migrations and `%run` of a writer all run for real in DEV and TEST. Read what a cell does before submitting it; for investigation, run only the read cells and replace the write cell with a `print` or count.
- **Cost:** a live session holds Spark capacity until it is deleted or times out (the local daemon drops its own connection after about 30 minutes idle; stopping the daemon does not stop the remote session). Always `notebook delete-session` when done, and never leave one running between tasks.
- Don't re-POST `code run` or `start-session` after a failure — poll the ID you already have.
- Never put real IDs, tokens or customer data from outputs into skill or knowledge files.
- In an agent's auto or unattended mode, `fntk` writes (`cell update`, `code run` on a writer, `notebook delete`) may be blocked the same way `fab import` and `fab job start` are. Hand the human the exact command rather than retrying.

## Known gaps (preview)

- Confirm on your own capacity: `%run` helper cells, `list-livy-sessions` for job runs, and the exact `cell list` JSON shape. Update this file with what you find.
- `fntk` has no folder support (like `fab`), no pipeline or item-definition operations, and no scheduling — those stay with the `fab-*` skills.
