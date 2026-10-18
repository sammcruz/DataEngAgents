---
name: fab-notebook-dev
description: Use this skill to read, create, edit, import, run, and validate Fabric notebooks with fab-cli and the Fabric Notebook Toolkit (fntk), especially when the task requires inspecting existing notebook code, authoring new PySpark notebooks, deploying them to a workspace, running them cell by cell in a live Spark session or end to end as a job, editing a single cell, and checking real outputs, tracebacks or errors.
---

# Fab Notebook Dev

## Use

Use this skill when the user wants to work with Fabric notebook content end to end through `fab`. It covers:

1. Reading existing notebook code from a workspace
2. Creating new notebooks locally in Fabric-compatible format
3. Editing and updating existing notebooks
4. Importing (deploying) notebooks to a target workspace
5. Running notebooks and checking execution results
6. Iterating on failures until the notebook succeeds

### Cloud-Only Notebook Editing Policy (Mandatory)

- Never edit notebook files stored in local source repositories (for example `<customer-repo>/<workspace-folder>/**`).
- Treat repository notebook files as read-only reference material unless the user explicitly asks to change source control files.
- Perform edits only on temporary notebook exports from Fabric (for example under `/tmp/exports`).
- Apply notebook changes to Fabric via `fab import`, then validate by running in the workspace.

Use `fab-discovery` first when the workspace layout or item names are unknown. Use `fab-job-ops` for advanced scheduling, polling, or pipeline-triggered notebook runs. Use `fab-conventions` when naming the notebook or its output tables.

**Interactive iteration uses `fntk`** (Microsoft's Fabric Notebook Toolkit, see [Interactive iteration with fntk](#interactive-iteration-with-fntk-preferred-for-iterate--inspect)): running an existing notebook cell by cell in a live Spark session, reading real cell output and tracebacks, ad-hoc verification queries without a debug notebook, and single-cell edits. Keep `fab` for new items, bulk/structural edits, and the final full `fab job start` run. The `fabric-notebook-toolkit` skill in this repository has the full playbook and a cell-range runner script.

Requires `fab` ≥ 1.0 (tested on 1.7.0). Since 1.0.0, `fab get` / `fab export` / `fab cp` ask for confirmation that sensitivity labels aren't included: **always pass `-f` in non-interactive use**, or the command waits on a prompt.

## Workflow

0. Before any import/run, implement or verify a notebook safety gate that blocks non-production execution for write paths.
1. Identify the target workspace and confirm it exists with `fab ls`.
2. If editing an existing notebook, read it first: `fntk cell list` / `cell get` for a quick look, or `fab export -f` when you'll edit and re-import (never `fab get` for edit+reimport).
3. Small change (one or a few cells): snapshot with `fntk notebook get-content --output-file`, then `fntk cell update`. Larger change: edit a temporary `fab export` folder outside local repositories and `fab import -f`.
4. Iterate in one live `fntk` session: run the changed cells (or a cell range), read `data.outputs` / `data.error`, fix, re-run just that cell. No re-import and no cold start per attempt.
5. Delete the `fntk` session, then do one full validation run with `fab job start` (sleep 120s for cold sessions, 60s for warm before checking `fab job run-status`).
6. If the full run failed, get the real error (re-run the failing cell in an `fntk` session, or `fntk` Livy logs), fix, and re-run.
7. Check the outcome (row counts, sample data) with a short `fntk code run` query. Fallback when `fntk` isn't available: the JSON-to-OneLake-Files pattern + `fab cp`.
8. Clean up: `fntk notebook delete-session`, and `fab rm` any debug notebook you created.
9. Summarize the final state: success, outputs, or remaining blockers.

## Interactive iteration with fntk (preferred for iterate / inspect)

`fntk` (PyPI `fabric-notebook-toolkit`, **preview**) talks to the same notebook API as the Fabric web editor.

**Install and auth:**

```bash
pipx install fabric-notebook-toolkit --python python3.13   # Python 3.10–3.13 only
fab auth login --tenant <TENANT_ID>   # interactive
az login --tenant <TENANT_ID>         # interactive; must be the SAME account and tenant as fab
fntk discover whoami --json --client-name claude-code
```

- **Never run `fntk init`.** It writes a `CLAUDE.md` block into any git-root folder holding Fabric `.platform` files (i.e. client repo checkouts) and re-registers the `fabric-collection` plugin marketplace from GitHub.
- For client work, set `FNTK_TELEMETRY_DISABLED=1` (remote telemetry to Microsoft is on by default).
- `fntk` needs GUIDs: resolve them by name each session with `fntk discover list-workspaces` / `list-notebooks` / `list-lakehouses`. Don't hardcode them.

**Session → run → inspect → clean up:**

```bash
W=<WS_ID>; A=<ART_ID>; F="--json --client-name claude-code"
fntk notebook list-sessions -w $W -a $A $F                 # reuse an idle one if present
fntk notebook start-session -w $W -a $A $F                 # → data.session_id (cold start 2–5 min)
fntk notebook get-session -w $W -a $A -s <SID> $F          # poll until data.livy_session_state == "idle"
fntk cell list -w $W -a $A $F                              # index / type / preview
fntk cell get  -w $W -a $A -i 3 $F                         # one cell's full source
fntk code run  -w $W -a $A --code "$(cat cell3.py)" $F     # → data.execution_id (no --file flag)
fntk code get-result -w $W -a $A --execution-id <EID> $F   # poll until data.status is completed|error
fntk notebook delete-session -w $W -a $A -s <SID> $F       # ALWAYS when done (holds capacity)
```

- There is no "run saved cell N": cell-by-cell means submitting each cell's source in order to the same session. Kernel state persists between submissions, like in the editor. `%%configure` restarts the session.
- Top-level `status: "success"` only means the query worked. Read `data.livy_session_state`, `data.status`, `data.outputs`, `data.error`, and follow `next_actions[].retry_after`.
- Ad-hoc checks: `code run` against a session on an existing notebook (it uses that notebook's default Lakehouse). Nothing is saved into the notebook, and no debug item is created.
- `cell update/insert/append/delete`, `put-content`, `set-lakehouse`, `notebook delete` save to the live item **immediately, with no confirmation and no ETag check**. Snapshot first, and don't edit a notebook someone has open with unsaved changes. Never `set-lakehouse` a real notebook just to query another Lakehouse; use 3-part names instead.
- Running a writer cell writes for real. Never open `fntk` sessions against PROD without explicit approval.
- Failures: `data.error` holds the traceback. Spark-level: `notebook get-session` → `livy_id` → `monitor list-apps` → `monitor get-diagnostic` / `logs get-driver --filename stderr`. ID confusion (404s): `fntk skill get fabric-session-ids --json`.
- Cell-by-cell runs don't replace one full `fab job start`: a warm kernel can hide state that a scheduled run wouldn't have.

## Environment Safety Gate (Mandatory)

For notebooks that write/update definitions, rebind reports, or trigger refreshes, enforce execution only from PROD environment unless the user explicitly requests otherwise.

Use this pattern at the top of the notebook:

```python
def get_workspace_env_name(workspace_name):
    return workspace_name.split("-")[-1].lower()

current_ws = notebookutils.runtime.context.get("currentWorkspaceName")
env = get_workspace_env_name(current_ws)

if env != "prod":
    raise RuntimeError(
        f"Execution blocked: notebook updates are allowed only from PROD. Current workspace: {current_ws}"
    )
```

Guidance:
- If run from DEV/TEST, notebook must not perform update operations.
- Validate this gate before running via `fab job start`/`fab job run`.
- Keep `ALLOW_WRITE` style switches for explicit operator intent.

## Reading Notebook Content

Quickest look at an existing notebook's cells (no files):

```bash
fntk cell list -w <WS_ID> -a <ART_ID> --json --client-name claude-code
fntk cell get  -w <WS_ID> -a <ART_ID> -i <INDEX> --json --client-name claude-code
```

Or with `fab` (note `-f`, required since fab 1.0):

```bash
fab get "<workspace>.Workspace/<notebook>.Notebook" -q "definition.parts[0].payload" -f > /tmp/<notebook>.json
```

`fab export ... --format py` (fab ≥ 1.4) exports the notebook as a `.py` source file instead of `.ipynb`, which is easier to read and diff. Use the default `.ipynb` format when you'll re-import it.

Inspect cell structure with Python (faster than reading raw JSON):

```bash
python3 -c "
import json
with open('/tmp/<notebook>.json') as f: nb = json.load(f)
print(f'Total cells: {len(nb[\"cells\"])}')
for i, c in enumerate(nb['cells']):
    src = ''.join(c.get('source', []))
    print(f'--- Cell {i} [{c[\"cell_type\"]}] ---')
    print(src[:600])
    print()
"
```

Get notebook metadata (connections, schedules):

```bash
fab get "<workspace>.Workspace/<notebook>.Notebook" -q "connections"
fab get "<workspace>.Workspace/<notebook>.Notebook" -q "schedules"
```

## Editing Existing Notebooks (Preferred Workflow)

**Always prefer `fab export` over `fab get` when you intend to modify and re-import a notebook.** Export preserves all metadata (lakehouse bindings, kernel info, dependencies) that `fab get` strips.

```bash
# Step 1: Export the existing notebook directory
mkdir -p /tmp/exports
fab export "<workspace>.Workspace/<notebook>.Notebook" -o /tmp/exports -f

# Step 2: Edit the .ipynb file with Python (append/modify/replace cells)
python3 << 'EOF'
import json, os

src_path = "/tmp/exports/<notebook>.Notebook/notebook-content.ipynb"
with open(src_path) as f:
    nb = json.load(f)

# Append a new cell
nb["cells"].append({
    "cell_type": "code",
    "metadata": {"microsoft": {"language": "python", "language_group": "synapse_pyspark"}},
    "source": ["print('new cell')"],
    "outputs": [],
    "execution_count": None
})

# Replace a cell (e.g., the last one)
# nb["cells"][-1] = { ... }

# Write to a clean import directory
out_dir = "/tmp/<notebook>.Notebook"
os.makedirs(out_dir, exist_ok=True)
with open(f"{out_dir}/notebook-content.ipynb", "w") as f:
    json.dump(nb, f, indent=2)

# Always include .platform alongside notebook-content.ipynb
with open(f"{out_dir}/.platform", "w") as f:
    json.dump({
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {"type": "Notebook", "displayName": "<notebook>"},
        "config": {"version": "2.0", "logicalId": "00000000-0000-0000-0000-000000000000"}
    }, f, indent=2)
EOF

# Step 3: Re-import with -f
fab import "<workspace>.Workspace/<notebook>.Notebook" -i /tmp/<notebook>.Notebook -f
```

### Why export and not get?

- `fab export` produces a ready-to-reimport directory (`notebook-content.ipynb` + folder structure).
- `fab get` returns only the payload JSON — missing platform metadata.
- Editing the exported `.ipynb` preserves `metadata.dependencies.lakehouse`, kernel info, and microsoft language metadata — losing these causes runtime failures.

## Notebook Directory Format

Fabric notebooks are imported as a directory containing two files:

```
<notebook-name>.Notebook/
├── notebook-content.ipynb    # Standard Jupyter notebook (nbformat 4)
└── .platform                 # Fabric platform metadata
```

### `.platform` file structure:

```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
  "metadata": {
    "type": "Notebook",
    "displayName": "<notebook-name>"
  },
  "config": {
    "version": "2.0",
    "logicalId": "00000000-0000-0000-0000-000000000000"
  }
}
```

### `notebook-content.ipynb` structure:

Standard Jupyter `.ipynb` format with Fabric-specific metadata on each code cell:

```json
{
  "nbformat": 4,
  "nbformat_minor": 5,
  "metadata": {
    "kernel_info": {"name": "synapse_pyspark"},
    "kernelspec": {"name": "synapse_pyspark", "display_name": "Synapse PySpark"},
    "language_info": {"name": "python"},
    "microsoft": {"language": "python", "language_group": "synapse_pyspark"}
  },
  "cells": [
    {
      "cell_type": "code",
      "metadata": {
        "microsoft": {"language": "python", "language_group": "synapse_pyspark"}
      },
      "source": ["# code lines as array of strings\n", "print('hello')"],
      "outputs": [],
      "execution_count": null
    }
  ]
}
```

### Cell source format:

- Each line is a separate string in the `source` array
- Lines must end with `\n` except the last line
- Use `"cell_type": "markdown"` for documentation cells
- Use `"cell_type": "code"` for executable cells

## Creating a Notebook Locally

Use Python to generate the `.ipynb` file programmatically:

```bash
python3 << 'EOF'
import json, os

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": ["# My Notebook\n", "Description here."]
    },
    {
        "cell_type": "code",
        "metadata": {"microsoft": {"language": "python", "language_group": "synapse_pyspark"}},
        "source": ["from pyspark.sql import SparkSession\n", "spark = SparkSession.builder.getOrCreate()\n", "print('ready')"],
        "outputs": [],
        "execution_count": None
    }
]

notebook = {
    "nbformat": 4, "nbformat_minor": 5,
    "metadata": {
        "kernel_info": {"name": "synapse_pyspark"},
        "kernelspec": {"name": "synapse_pyspark", "display_name": "Synapse PySpark"},
        "language_info": {"name": "python"},
        "microsoft": {"language": "python", "language_group": "synapse_pyspark"}
    },
    "cells": cells
}

out_dir = "/tmp/my_notebook.Notebook"
os.makedirs(out_dir, exist_ok=True)

with open(f"{out_dir}/notebook-content.ipynb", "w") as f:
    json.dump(notebook, f, indent=2)

platform = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
    "metadata": {"type": "Notebook", "displayName": "my_notebook"},
    "config": {"version": "2.0", "logicalId": "00000000-0000-0000-0000-000000000000"}
}

with open(f"{out_dir}/.platform", "w") as f:
    json.dump(platform, f, indent=2)

print("Done")
EOF
```

## Importing (Deploying) a Notebook

Import a new notebook:

```bash
fab import "<workspace>.Workspace/<notebook>.Notebook" -i /tmp/<notebook>.Notebook
```

Overwrite an existing notebook (force):

```bash
fab import "<workspace>.Workspace/<notebook>.Notebook" -i /tmp/<notebook>.Notebook -f
```

Key notes:
- The `-i` path must point to the **directory** (not the `.ipynb` file directly)
- Use `-f` to skip confirmation when overwriting
- The directory name must match `<name>.Notebook`
- If the notebook already exists, `fab import` will prompt for overwrite (use `-f` to auto-confirm)

## Running and Checking Results

Start a notebook job (async):

```bash
fab job start "<workspace>.Workspace/<notebook>.Notebook"
```

Check run status:

```bash
fab job run-status "<workspace>.Workspace/<notebook>.Notebook" --id "<run-id>"
```

Poll until complete (with sleep):

```bash
sleep 90 && fab job run-status "<workspace>.Workspace/<notebook>.Notebook" --id "<run-id>"
```

### Realistic timing

| Scenario | Recommended initial sleep |
|----------|---------------------------|
| Small notebook, warm session | 60s |
| First run after import (cold Spark session) | 120s |
| Schema-migration / multi-table create | 120s |

If status is still `NotStarted` or `InProgress` after the first poll, `sleep 60` and re-check rather than spamming the API.

### Common status values:

| Status | Meaning |
|--------|---------|
| InProgress | Spark session starting or cells executing |
| Completed | All cells ran successfully |
| Failed | One or more cells threw an exception |

### Common failure codes:

| Error Code | Meaning | Action |
|------------|---------|--------|
| `System_Cancelled_Session_Statements_Failed` | A cell raised an unhandled exception | Fix the code and re-import |
| `SparkSessionNotFound` | Spark pool was unavailable | Retry |
| `UserError` | Logic error in notebook code | Read error details, fix, re-deploy |

## Iterating on Failures

**Preferred:** reproduce and fix in a live `fntk` session (see [Interactive iteration with fntk](#interactive-iteration-with-fntk-preferred-for-iterate--inspect)). Run the cells up to the failing one, read `data.error` for the real traceback, `fntk cell update` the fix, and re-run only that cell. Then do one full `fab job start`. The import/re-run loop below is the fallback when `fntk` isn't available.

When a notebook fails:

1. The `fab job run-status` output shows `failureReason`, often only a generic wrapper like `System_Cancelled_Session_Statements_Failed`. `fntk` gives you the actual exception.
2. Fix the code locally
3. Re-generate the `.ipynb` file
4. Re-import with `-f`
5. Re-run with `fab job start`
6. Check status again

Typical iteration loop:

```bash
# Fix code, regenerate notebook
python3 generate_notebook.py

# Re-import
fab import "Dev.Workspace/my_nb.Notebook" -i /tmp/my_nb.Notebook -f

# Re-run
fab job start "Dev.Workspace/my_nb.Notebook"

# Wait and check
sleep 120 && fab job run-status "Dev.Workspace/my_nb.Notebook" --id "<new-run-id>"
```

## Verifying Notebook Output

`fab job run-status` only shows pass/fail — it does **not** return cell stdout or DataFrame content.

**Preferred:** query directly in an `fntk` session on an existing notebook. Nothing is created in the workspace, so there's nothing to clean up and no stray `debug_*` item in Git status:

```bash
fntk code run -w <WS_ID> -a <ART_ID> --code "print(spark.table('bronze.<table_name>').count())" --json --client-name claude-code
fntk code get-result -w <WS_ID> -a <ART_ID> --execution-id <EID> --json --client-name claude-code
```

**Fallback** (no `fntk`): to inspect actual output (row counts, sample data), use this pattern:

### Write a JSON report to OneLake Files

Create a small debug notebook that queries the target table and writes results as JSON:

```python
# Inside the debug notebook cell
from pyspark.sql import functions as F
import json, os

df = spark.table("bronze.<table_name>")
cnt = df.count()
ts = df.select(F.max('meta_ingestion_timestamp').cast('string').alias('m')).collect()[0]['m']
sample = [r.asDict(True) for r in df.limit(5).collect()]

report = {'row_count': cnt, 'max_ingestion_timestamp': ts, 'sample_rows': sample}

out_path = '/lakehouse/default/Files/_debug/<table_name>_report.json'
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(report, f, indent=2, default=str)
```

### Download and read it locally

```bash
fab cp "<workspace>.Workspace/<lakehouse>.Lakehouse/Files/_debug/<table_name>_report.json" /tmp/<table_name>_report.json -f
cat /tmp/<table_name>_report.json
```

### Confirm table existence (no notebook needed)

```bash
fab ls "<workspace>.Workspace/<lakehouse>.Lakehouse/Tables" | grep "<table_name>"
```

### Check table schema (no notebook needed)

```bash
fab table schema "<workspace>.Workspace/<lakehouse>.Lakehouse/Tables/<table_name>"
```

### Clean up after verification

Always remove debug notebooks and files after you're done:

```bash
fab rm "<workspace>.Workspace/debug_<name>.Notebook" -f
```

### Key limitations

- **`fab table`** supports only: `load`, `optimize`, `schema`, `vacuum` — no SELECT/query.
- **`fab cp` for parquet files** downloads fine but may not be readable locally due to pyarrow version mismatches. Always write debug output as **JSON or text**, never parquet.
- **No SQL query command exists** in fab-cli. To query data, use `fntk code run` in a session, or run a notebook.

## Fabric PySpark Patterns

### Lakehouse Binding (REQUIRED for `spark.sql` and `saveAsTable`)

A notebook that uses `saveAsTable("<table>")`, `spark.table("<table>")`, or `spark.sql("SELECT ... FROM <table>")` **without a fully qualified path** must have a default lakehouse bound in its metadata. Without it, the cell will fail with `System_Cancelled_Session_Statements_Failed` and no obvious error reason.

**How to find a lakehouse ID** — copy from any existing notebook in the same workspace:

```bash
fab get "<workspace>.Workspace/<existing_notebook>.Notebook" -q "definition.parts[0].payload" -f \
  | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin)['metadata'].get('dependencies', {}), indent=2))"
```

**How to attach the lakehouse** before importing:

```python
nb["metadata"]["dependencies"] = {
    "lakehouse": {
        "known_lakehouses": [{"id": "<lakehouse-guid>"}],
        "default_lakehouse": "<lakehouse-guid>",
        "default_lakehouse_name": "<lakehouse_name>",
        "default_lakehouse_workspace_id": "<workspace-guid>"
    }
}
```

> When creating a brand new notebook that writes to a Lakehouse, always attach this metadata before the first import — don't wait for the first run to fail.

### Authentication with Workspace Identity:

```python
token = mssparkutils.credentials.getToken("https://graph.microsoft.com")
```

### Reading from Lakehouse tables:

```python
df = spark.read.format("delta").load(
    "abfss://<workspace>@onelake.dfs.fabric.microsoft.com/<lakehouse>.Lakehouse/Tables/<schema>/<table>"
)
# Or using the SQL endpoint:
df = spark.sql("SELECT * FROM <lakehouse>.<schema>.<table>")
```

### Writing to Lakehouse tables (overwrite for daily refresh):

```python
df.write.mode("overwrite") \
    .format("delta") \
    .option("overwriteSchema", "true") \
    .save("abfss://<workspace>@onelake.dfs.fabric.microsoft.com/<lakehouse>.Lakehouse/Tables/<schema>/<table>")
```

### Cross-lakehouse references in same workspace:

```python
# Use the SQL analytics endpoint name directly
df = spark.sql("SELECT * FROM silver.dbo.my_table")
df = spark.sql("SELECT * FROM gold.dbo.my_table")
```

## Guardrails

- Always read existing notebook content before overwriting to avoid data loss.
- **Never run `fntk init`**, and never open `fntk` sessions against PROD without explicit approval. Always `fntk notebook delete-session` when finished, since a live session holds capacity.
- Pass `-f` to `fab get` / `fab export` / `fab cp` in scripts (fab ≥ 1.0 asks for a sensitivity-label confirmation otherwise).
- **Always use `fab export` (not `fab get`) when you plan to re-import.** Editing the exported `.ipynb` keeps lakehouse bindings and kernel metadata intact.
- **Never edit local repository notebook files for runtime fixes.** Use cloud export/edit/import workflow only.
- **Always attach `metadata.dependencies.lakehouse` before importing** any notebook that uses unqualified `saveAsTable`, `spark.table`, or `spark.sql`. Missing this is the #1 cause of `System_Cancelled_Session_Statements_Failed`.
- Use `-f` (force) only when you are certain the new content is correct.
- Never import to PROD directly — always work in DEV or TEST first.
- Validate that Spark pool is available before assuming code errors (check for `SparkSessionNotFound`).
- When a notebook fails, the error may be permissions (e.g., workspace identity, missing lakehouse binding) rather than code — check the error message carefully.
- Keep notebook cells small and focused; large monolithic cells are harder to debug remotely.
- Always include error handling in cells that make external API calls.
- Do not create tables in exploratory/POC notebooks — print output instead until the approach is validated.

## Multi-Notebook Coordinated Changes

A common task pattern: **add a new bronze/silver/gold table that some other notebook will populate**. Follow this exact order:

1. **Read** the existing schema-definition notebook (`nb_<layer>_schemas`) and migrations notebook (`nb_<layer>_schema_migrations`) via `fab export`.
2. **Append** the new `StructType` schema(s) to `nb_<layer>_schemas` (raw + history pair if applicable). Keep original column names; add metadata columns:
   - `meta_ingestion_timestamp` on raw tables
   - `meta_historization_timestamp` (and any project-standard meta_* columns) on history tables — typically defined as `StructType(<RAW>.fields + [extra meta fields])`
3. **Append** a new migration block to `nb_<layer>_schema_migrations` with the next sequential version (e.g., if last was `0.15`, use `0.16`) calling `create_table(...)` for each new schema.
4. **Import & run the migrations notebook first** — verify `Completed` before touching writers.
5. **Update the writer notebook** to add `meta_ingestion_timestamp` (typically `F.current_timestamp()`) and write to the new table (`df.write.format("delta").mode("overwrite").saveAsTable("<table>")`).
6. **Ensure the writer notebook has the lakehouse binding** in its metadata (see Fabric PySpark Patterns).
7. **Import & run the writer notebook**; confirm `Completed`.

This order guarantees the target table exists before any write attempts it, and avoids ad-hoc table creation outside the migration system.

## Efficient Deploy-Run-Verify Pattern

Combine import + start + wait + status-check in a single chain to minimize round-trips:

```bash
# Import and immediately start
fab import "<workspace>.Workspace/<notebook>.Notebook" -i /tmp/<notebook>.Notebook -f && \
fab job start "<workspace>.Workspace/<notebook>.Notebook"

# Capture run ID for polling. fab >= 1.7 returns the job instance ID as a structured
# field with --output_format json (read the field from the JSON); grep is the fallback:
RUN_ID=$(fab job start "<workspace>.Workspace/<notebook>.Notebook" 2>&1 | grep -oE "'[a-f0-9-]{36}'" | head -1 | tr -d "'")
sleep 120
fab job run-status "<workspace>.Workspace/<notebook>.Notebook" --id "$RUN_ID"
```

## Parametrized Writer Notebooks

When a writer notebook uses parameters (e.g., `entity = "orders"` at the top to control which entity is fetched), and you need to test a new entity:

1. Export the notebook
2. **Only change the parameter cell** — don't restructure or rewrite logic
3. Import and run
4. After testing, **restore the original parameter** unless this notebook will now permanently target the new entity (usually it's pipeline-driven via parameters)

> Notebooks in Fabric pipelines typically receive parameters at runtime. The default value in Cell 1 is just for manual/debug runs.

## fab-cli Available Commands Reference

| Command | Use for |
|---------|---------|
| `fab ls` | List workspaces, items, files, tables |
| `fab get` | Read item properties (payload, connections) |
| `fab export` | Download full item directory (preferred for edit+reimport) |
| `fab import` | Upload/update an item |
| `fab cp` | Copy a single file from/to OneLake |
| `fab rm` | Delete items or files |
| `fab job start` | Start notebook/pipeline async |
| `fab job run-status` | Check job status (pass/fail only) |
| `fab table schema` | Show Delta table schema |
| `fab table load` | Load data into table |
| `fab api` | Make authenticated REST calls |
| `fab find` | Search the OneLake catalog across workspaces (fab ≥ 1.6) |
| `fab bulk-export` | Export all items of a workspace or folder (fab ≥ 1.7) |
| `fab export --format py` | Export a notebook as `.py` instead of `.ipynb` (fab ≥ 1.4) |
| `fab job start/run -P name:type=value` | Pass notebook parameters to a run |

**Not available in fab:** SQL queries, cell stdout, direct parquet reads. Cell stdout, tracebacks and ad-hoc queries are available through `fntk` (see the next table).

| `fntk` command | Use for |
|---------|---------|
| `fntk notebook start-session / get-session / delete-session` | Live Spark session on a notebook |
| `fntk code run / get-result / cancel` | Run code in the session, read outputs and errors |
| `fntk cell list / get / update / insert / append / delete` | Read and edit single cells in the live item |
| `fntk notebook get-content / put-content` | Whole-notebook `.ipynb` read and write |
| `fntk monitor ...` / `fntk logs ...` | Spark diagnostics, driver and cell logs |

## Naming Conventions

Follow the project's established patterns. If it has none, start from `fab-conventions`:

| Type | Pattern | Example |
|------|---------|---------|
| Layer notebooks | `nb_<layer>_<verb>_<subject>` | `nb_silver_standardize_customer` |
| Shared helper notebooks | `nb_helper_<topic>` | `nb_helper_logging` |
| Schema notebooks | `nb_<layer>_schemas` | `nb_gold_schemas` |
| Debug/test notebooks | `debug_<topic>` | `debug_notebook` |
