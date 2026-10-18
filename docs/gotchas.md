# Known gotchas

Root causes and workarounds for problems that cost real debugging time on Microsoft Fabric, the `fab` CLI, `fabric-cicd` and Azure DevOps. They were distilled from real incidents and generalised: every customer name, identifier, table name and work-item number has been removed.

Treat each entry as a lead to verify, not as gospel. Tool versions move quickly, so entries mention the version where it matters and are worth re-checking after an upgrade. Add your own findings in the same shape: **symptom → cause → what to do**.

## `fab` CLI

- **`-f` is required for non-interactive `get`, `export`, `cp` and `mv` (since 1.0).** They ask for confirmation that sensitivity labels are not included and wait on a prompt otherwise.
- **A Python version can silently pin an old CLI.** `ms-fabric-cli` 0.2 and later require Python below 3.14. A pipx environment built on 3.14 keeps resolving the old release, and `pipx install --force` reuses the same interpreter. Uninstall, then `pipx install ms-fabric-cli --python python3.13`. Log in again afterwards, because the auth file format changed in 1.0.
- **Folders and paths.** Older versions gave `InvalidPath` for workspace-folder paths. To create an item inside a folder, `POST workspaces/{id}/items` through `fab api` with a `folderId` and an inline base64 `definition`. `fab import -f` on an existing item keeps its folder. Newer releases added folder support to the file-system commands: verify on your version before relying on either behaviour.
- **`fab export` needs `-o`, and the output directory must already exist**, otherwise it fails with `InvalidPath`.
- **Downloading a file from a Lakehouse `Files` area uses `fab cp`,** not `fab get` (which reads item properties). There is no `fab cat`.
- **Binary downloads through `fab cp` were corrupted in old versions** (a text decode inserted replacement bytes), while JSON and text came through fine. For binaries, use the OneLake DFS endpoint with a storage token or read them from a notebook. Re-test on newer releases.
- **`fab get <item> -q lakehouse` can return nothing even when a Lakehouse is attached.** Check `metadata.dependencies.lakehouse` in the exported `notebook-content.ipynb` instead.
- **Long-running operations return `202` with an empty body** (for example `getDefinition` on a notebook, `updateDefinition`, item creation with a definition). Read the operation id from the response headers, poll `operations/<id>`, then read `operations/<id>/result`.
- **`fab job run --timeout` crashed client-side in old versions** after creating the job, with a comparison error between `int` and `str`. The job still runs. Poll it yourself with `fab job run-status --id <jobInstanceId>`. Newer versions return the instance id as a JSON field with `--output_format json`.
- **Strip carriage returns** (`tr -d '\r'`) from `fab` output before using it in shell loops or building ids. A hidden `\r` breaks matching and can end up inside a pipeline definition (see "Notebook ids" below).
- **Calls against real workspaces are slow** (minutes for `ls`, `cp`, `import`, `export`). Run slow calls in the background and poll with short ones, export several items in parallel, and prefer one notebook that reads many things over many separate `fab` calls.
- **Login from a non-interactive shell** can fail with "Input is not a terminal". When it gets further, macOS may show a keychain dialog asking for the login keychain password. The human types it, an agent never needs it. Holding two tenants at once through a `HOME` override does not work: log out and in sequentially. macOS has no `timeout` command.
- **Do not poll `run-status` to "confirm a fix".** It costs capacity for nothing. Verify offline by exporting the changed item, or with one short query. The REST job API never returns cell-level Spark errors, only a generic wrapper such as `System_Cancelled_Session_Statements_Failed`. To get the real traceback, use `fabric-notebook-toolkit`, ask the human to paste it from the portal's run snapshot, or wrap the risky statement in a `try/except` that writes `str(e)` somewhere readable.

## Notebooks and Spark

- **A notebook without a default Lakehouse fails with a generic error** when it uses unqualified `saveAsTable`, `spark.table` or `spark.sql`. Attach `metadata.dependencies.lakehouse` before the first import.
- **`mssparkutils.notebook.run(child)` fails when the child's default Lakehouse differs from the caller's** (`checkNotebookDefaultLH`). Pass `{"useRootDefaultLakehouse": True}` in the parameters and use fully qualified table names in the child.
- **Rebinding a notebook's Lakehouse** reliably works as: `fab export`, patch the workspace and Lakehouse ids in the exported files, `fab import -f`, then verify the whole workspace.
- **Versioned migration notebooks hide bugs in the environment that is ahead.** A chain of `if check_migration(...)` blocks short-circuits in an environment that already applied a version, so a bug in that cell sits inert until an environment that is behind finally runs it. "It fails in TEST but DEV never complained" is information, not proof TEST is broken. Do not only diff notebook text: check which environment is behind, and re-read the next pending migration. Push the fix to **both** environments.
- **An `ADD COLUMN` migration needs a matching change in every writer of the table.** A writer using `overwriteSchema` silently drops the column. A `MERGE ... UPDATE SET *` writer **hard-fails** because every target column must exist in the source. Grep for every writer before shipping a migration. Any new column a semantic model references needs its own migration, because deployment order guarantees migrations but not data rebuilds.
- **`xxhash64(NULL)` returns 42, not NULL.** Add an explicit NULL check around hashed keys.
- **Rarely run notebooks rot.** Before running a one-off or migration-only notebook, compare its `f.col("...")` references with `fab table schema` for the tables it reads. A short script over the exported `.ipynb` finds mismatches in seconds.
- **The SQL analytics endpoint lags behind Spark writes** for minutes or hours, and no API exposes a "last synced" time. Validate a just-written fix through a notebook (Spark reads the Delta table directly) or `DESCRIBE HISTORY <table>`, not through the endpoint. If the endpoint looks stale, refresh it and re-query.
- **`TooManyRequestsForCapacity` (HTTP 430) on an unrelated notebook** means the capacity ran out, not that the notebook is wrong. Do not rerun the unrelated failed notebook. Run the pipeline's remaining steps on their own, passing the same run id. On small capacity SKUs, concurrency is the usual culprit.
- **A pipeline activity wired to a notebook id with a trailing carriage return** looks fine in `fab get`, but the item never shows as modified in Fabric Git status and later imports fail with `UnknownError`. After every pipeline import check that Git status lists the item and that every `notebookId` is a clean GUID.

## CI/CD (`fabric-cicd`, Azure DevOps)

- **A workspace-only fix does not make a pipeline succeed if the pipeline deploys from git.** The fix must be committed first. Say which of "fixed in the workspace", "committed" and "deployed" you have reached.
- **Live edits are lost on the next deployment** from a branch, in TEST as well as DEV, unless they were committed through Fabric Git integration. List any live patch as "uncommitted" in hand-offs.
- **Commit one item from a messy workspace with a selective commit.** Use the Git integration API's `commitToGit` with `"mode": "Selective"` and an explicit `items` array (`objectId` and `logicalId` from `git/status`). Afterwards `git/status` should show `workspaceHead == remoteCommitHash` and the other pending changes still pending: that is the proof only the intended items were pushed. See the `git-integration-operations-cli` skill from Microsoft's `skills-for-fabric`.
- **`parameter.yml` replacements are tied to the workspace a branch was synced from.** A `find_value` that matches nothing is not an error in `fabric-cicd`. If you point a deployment at a branch synced from another environment, count the matches first: zero matches means zero replacements and no warning.
- **Pin `fabric-cicd`.** An unpinned `pip install fabric-cicd --upgrade` can change a default (for example parallel publishing with several workers) with no commit in your repository, and a small capacity then throttles. Pin the version and set `FABRIC_CICD_PARALLEL_MAX_WORKERS` to match your capacity.
- **A deployment publishes the whole branch.** Production may carry a hotfix that exists in no branch, and the next deployment would remove it. Before deploying, export and compare every item in the chain between production, the source environment and the branch (normalise GUIDs). Commit endpoints need full 40-character ids. Compare version strings as tuples, not numbers (`0.9` sorts after `0.10` as a double).
- **Name-based lookups run as the deploying principal.** Items published by a pipeline are owned by its service principal, so a notebook calling `GET /v1/workspaces` only sees workspaces that principal has a role on. "Workspace X not found" is then a missing role, never a 403. Check the run's submitter against the target workspace's role assignments before suspecting code. Debugging as yourself will not reproduce it.

## Semantic models and Power BI

- **`Dataset_Import_FailedToImportDataset` has several unrelated causes behind generic wording.** Check in this order:
  1. A Direct Lake table whose source Delta table is missing in the **target** environment. Diff `fab ls .../Lakehouse/Tables` between environments. It often means the change was built in one workspace and never committed.
  2. A relationship cycle, for example an `isActive: false` line accidentally dropped in a TMDL edit. Git edits bypass Desktop's cycle guard.
  3. A real RLS or OLS role conflict (skip if the model has no roles).
  4. Capacity throttling: the message names "compute capacity has exceeded its limits". Look at concurrency, not at the model.
  5. `Changing the StringIndexingBehavior property requires model compatibility level 1707` when rebinding a Direct Lake model. The compatibility level cannot be lowered, so raise it deliberately in the source environment.
- **A clean import is not proof a model works.** Splitting one large import into several small ones can make it pass while the Direct Lake data dependency is still missing. Browse or refresh the model, and run a real DAX query.
- **A correct data fix can break a relationship that relied on the old bug.** If a column was unique only because of a bug, implicit relationship cardinality breaks once the fix legitimately makes it non-unique. Declare cardinality and direction explicitly, and validate with a DAX query (`executeQueries`) on the exact keys involved. Direct Lake validates lazily, so a completed refresh proves little.
- **PBIR import fails on a bookmark property newer than the file's `$schema`.** Desktop writes it, the live workspace accepts it, and the stricter deployment-time import rejects it (`Report_Import_FailedToImportReport`). Remove the property from each named `.bookmark.json`. It recurs whenever someone edits a bookmark, so a sanitising step in CI is better than patching each report.

## Fabric data agents

- **Chat answers are capped at 25 rows and 25 columns.** An instruction cannot override that. A preview raises the cap to 1,000 rows. A data agent is for conversation, not export.
- **With no tables ticked, there is no query tool.** If the code interpreter (preview) is enabled, even a simple count is routed to it and fails with "code_interpreter cannot access data directly, invoke an analyze_* tool first". Tick the tables.
- **The Standard runtime supports up to 25 tables per data source,** and topics and schema descriptions are Preview-only. Choosing a runtime does not choose the base model. A published agent keeps the runtime it had at publish time until republished.
- **Monitoring:** the Monitor hub lists data agents, but there is no data-agent-specific view yet. For per-conversation detail use Purview DSPM auditing (prompts, responses and generated queries).

## Fabric Policies (preview)

- **The allow-list trap:** item creation defaults to *Allowed*. Switching to an advanced setting and adding one Allow rule blocks every item type no rule matches once the policy set is active (propagation can take about 15 minutes). Write a rule for every scenario that must keep working first.
- **There is no dry run.** An inactive policy set enforces nothing. Activate on a non-production capacity, wait, and test with real accounts.
- **Semantics differ by feature.** Item creation needs the tenant setting **and** the policy to allow. External data sharing is allowed by the tenant setting **or** a policy rule.
- **Not supported for capacities in some regions.** Check the capacity's region first.

## Azure DevOps

- **A personal access token in a git-tracked config file will be reused by agents.** An agent with file access treats a plaintext secret as fair game and may inline it into a raw `curl`, which lands it in logs and transcripts. Keep tokens in environment variables, gitignore any config that could hold one, ship an `.example` file, and rotate a token that was ever exposed.
- **Pull request descriptions are capped at 4,000 characters** (a plain HTTP 400, no truncation). `searchCriteria.top` is silently ignored on commits; use `$top`.
- **One active pull request per branch pair is a common policy.** A second fix on the same source branch joins the existing PR, so update its description instead of leaving the addition undocumented.
- **Wiki Mermaid shows "Unsupported markdown: list"** when a node or edge label starts with a number, a dot and a space (`"1. Commit"`). Rephrase the label.
- **Do not trust a "this is committed" claim, including your own.** Before writing it into a PR or work item, check the real commit log and `git/status`.

## Working with agents

- **Interactive Spark sessions cost capacity until deleted.** Delete them when done, and never leave one running between tasks.
- **Notebook toolkit edits have no confirmation and no concurrency check.** Snapshot first, and do not edit a notebook someone else may have open.
- **A permission classifier may block workspace writes transiently.** An identical retry can succeed after the human re-confirms. Surface the block once instead of looping.
- **When a human's observation conflicts with an agent's own validation, re-verify from a primary source** (query the real table, read the real log) before answering either way.
- **Keep scope tight on live data fixes.** Report adjacent findings separately instead of folding them into the fix.
