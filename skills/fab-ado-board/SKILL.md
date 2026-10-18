---
name: fab-ado-board
description: Use this skill to read and write Azure DevOps work items (Epics, Features, User Stories, Tasks) for the project board. Covers reading item details, updating descriptions, adding comments, changing state, and querying items by WIQL.
---

# Fab ADO Board

## Use

Use this skill when the user wants to:

1. Read work item details (description, state, comments, children)
2. Update work item fields (description, state, assigned_to, etc.)
3. Add comments to a work item
4. Query work items by type, state, iteration, or custom WIQL
5. Document completed work (add implementation details to tasks)

Use `fab-notebook-dev` for the actual Fabric notebook work. Use this skill to track and document that work on the board.

## Configuration

Organization and project live in:

```
skills/fab-ado-board/fab-ado-board.config.json
```

```json
{
    "ado_organization": "<your-organization>",
    "ado_project": "<your-project>",
    "ado_pat": "",
    "ado_area_path": "",
    "output_path": "output/requirements"
}
```

The Personal Access Token comes from the `ADO_PAT` environment variable. Leave `ado_pat` empty and never write a token into this file or anywhere else in the repository. Read the file for organization and project before making API calls.

## Real Agent Runner

This skill has an executable agent runner in the repository:

```bash
python scripts/fab_ado_board_agent.py --help
```

Quick examples:

```bash
# Read one work item
python scripts/fab_ado_board_agent.py get --id 123

# Dry-run write (no API mutation)
python scripts/fab_ado_board_agent.py add-comment --id 123 --text-file /tmp/comment.html

# Execute write
python scripts/fab_ado_board_agent.py add-comment --id 123 --text-file /tmp/comment.html --execute
```

## Sprint Query Patterns

Use these WIQL patterns for sprint-level reporting automation.

### Current sprint stories + tasks

```sql
SELECT [System.Id]
FROM WorkItems
WHERE
    [System.TeamProject] = @project
    AND [System.IterationPath] = @CurrentIteration
    AND [System.WorkItemType] IN ('User Story', 'Task')
ORDER BY [System.WorkItemType], [System.Id]
```

### Current sprint bugs

```sql
SELECT [System.Id]
FROM WorkItems
WHERE
    [System.TeamProject] = @project
    AND [System.IterationPath] = @CurrentIteration
    AND [System.WorkItemType] = 'Bug'
ORDER BY [System.Id]
```

### Important WIQL constraint

- Do **not** use `CONTAINS` with `System.IterationPath` (ADO rejects it for path fields).
- Use `= @CurrentIteration` or `UNDER 'Project\\Iteration n'` instead.

## Release Notes Mapping Rule

When building release notes from board data:

- For **User Stories**, developer attribution must come from **Task assignees** under that story.
- For **Bugs**, use **Bug assignee** (or responsible implementer if reassigned through tasks).

Full usage guide:

- `docs/fab-ado-board-agent.md`

## API Base URL

```
https://dev.azure.com/{organization}/{project}/_apis
```

Authentication: `HTTPBasicAuth("", pat)` — empty username, PAT as password.

## Reading Work Items

### Get a single work item

```python
import requests
from requests.auth import HTTPBasicAuth

resp = requests.get(
    f"{base}/wit/workitems/{work_item_id}",
    auth=auth,
    params={"api-version": "7.1", "$expand": "all"},
    timeout=60
)
wi = resp.json()
# Key fields:
# wi["fields"]["System.Title"]
# wi["fields"]["System.State"]
# wi["fields"]["System.Description"]
# wi["fields"]["System.AssignedTo"]["displayName"]
# wi["fields"]["System.WorkItemType"]  (Epic, Feature, User Story, Task)
```

### Get comments on a work item

```python
resp = requests.get(
    f"{base}/wit/workitems/{work_item_id}/comments",
    auth=auth,
    params={"api-version": "7.1-preview.4"},
    timeout=60
)
comments = resp.json().get("comments", [])
for c in comments:
    print(f"{c['createdBy']['displayName']} ({c['createdDate'][:10]}): {c['text'][:100]}")
```

### Query work items with WIQL

```python
wiql = """
SELECT [System.Id], [System.Title], [System.State]
FROM workitems
WHERE [System.WorkItemType] = 'Task'
  AND [System.State] = 'Active'
    AND [System.IterationPath] UNDER 'your-project\\Sprint 26'
ORDER BY [System.Id]
"""

resp = requests.post(
    f"{base}/wit/wiql",
    auth=auth,
    json={"query": wiql},
    params={"api-version": "7.1"},
    timeout=60
)
ids = [wi["id"] for wi in resp.json().get("workItems", [])]
```

### Get multiple work items in batch

```python
id_str = ",".join(str(x) for x in ids[:200])  # max 200 per batch
resp = requests.get(
    f"{base}/wit/workitems",
    auth=auth,
    params={"ids": id_str, "$expand": "all", "api-version": "7.1"},
    timeout=60
)
items = resp.json().get("value", [])
```

## Writing / Updating Work Items

### Update fields (description, state, assignment, etc.)

Uses JSON Patch format (`application/json-patch+json`):

```python
patch_body = [
    {"op": "add", "path": "/fields/System.Description", "value": "<p>HTML description here</p>"},
    {"op": "add", "path": "/fields/System.State", "value": "Active"},
    {"op": "add", "path": "/fields/System.AssignedTo", "value": "user@example.com"},
]

resp = requests.patch(
    f"{base}/wit/workitems/{work_item_id}",
    auth=auth,
    headers={"Content-Type": "application/json-patch+json"},
    params={"api-version": "7.1"},
    json=patch_body,
    timeout=60
)
```

### Add a comment

```python
resp = requests.post(
    f"{base}/wit/workitems/{work_item_id}/comments",
    auth=auth,
    headers={"Content-Type": "application/json"},
    params={"api-version": "7.1-preview.4"},
    json={"text": "<p>Comment in HTML format</p>"},
    timeout=60
)
comment_id = resp.json().get("id")
```

### Create a new work item

```python
patch_body = [
    {"op": "add", "path": "/fields/System.Title", "value": "New Task Title"},
    {"op": "add", "path": "/fields/System.Description", "value": "<p>Description</p>"},
    {"op": "add", "path": "/fields/System.AssignedTo", "value": "user@example.com"},
    {"op": "add", "path": "/fields/System.IterationPath", "value": "your-project\\Sprint 26"},
    # Link to parent (e.g., User Story):
    {"op": "add", "path": "/relations/-", "value": {
        "rel": "System.LinkTypes.Hierarchy-Reverse",
        "url": f"https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{parent_id}"
    }}
]

resp = requests.post(
    f"{base}/wit/workitems/$Task",  # $Epic, $Feature, $User Story, $Task
    auth=auth,
    headers={"Content-Type": "application/json-patch+json"},
    params={"api-version": "7.1"},
    json=patch_body,
    timeout=60
)
new_id = resp.json()["id"]
```

## Pull Requests (ADO Git REST API, not the `wit/` endpoints)

Not covered by the `fab_ado_board_agent.py` runner's subcommands yet (no `pr-get`/`pr-update`) — done ad hoc by importing `_read_config`/`FabAdoBoardAgent` from the script and calling `agent._request(...)` directly, reusing the same safe PAT-loading path. **Key difference from work items: PR updates take a plain JSON body, not a JSON Patch array.**

### Find the repo id first

```python
repos = agent._request("GET", "git/repositories", params={"api-version": "7.1"})
repo_id = next(r["id"] for r in repos["value"] if r["name"].lower() == project.lower())
```

### Read a PR

```python
pr = agent._request(
    "GET",
    f"git/repositories/{repo_id}/pullrequests/{pr_id}",
    params={"api-version": "7.1"},
)
# pr["title"], pr["description"], pr["sourceRefName"], pr["targetRefName"], pr["status"]
```

### Update a PR's description

```python
agent._request(
    "PATCH",
    f"git/repositories/{repo_id}/pullrequests/{pr_id}",
    params={"api-version": "7.1"},
    headers={"Content-Type": "application/json"},
    json_body={"description": new_description},  # plain body -- NOT a JSON Patch array like work items
)
```

**Hard cap: 4000 characters.** Exceeding it returns a plain HTTP 400 `InvalidArgumentValueException` (no truncation) — check `len(current_description)` before drafting an addition.

### List commits on a branch (to verify a claimed commit before writing about it)

```python
commits = agent._request(
    "GET",
    f"git/repositories/{repo_id}/commits",
    params={
        "api-version": "7.1",
        "searchCriteria.itemVersion.version": "development",
        "searchCriteria.itemVersion.versionType": "branch",
        "$top": 15,  # NOT "searchCriteria.top" -- that's silently ignored, returns everything
    },
)
```

Useful before updating a PR description or work-item comment to claim something is "committed" or "included" — don't take a user's or a prior agent's self-report at face value for something you're about to write into a shared artifact; check the actual commit log (and `workspaces/{id}/git/status` for the Fabric-side workspace/git sync state) first.

**One active PR per branch pair is a common ADO branch-policy setup** (check your own policy) — a second validated fix landing on the same source branch while a PR is still open doesn't need (or get) its own PR; it becomes part of the same PR automatically, and the existing description should be updated to document it (e.g. an "Also included in this PR: ..." section), not left undocumented.

## Common Fields Reference

| Field path | Type | Example |
|---|---|---|
| `System.Title` | string | "Ingest new fields from api for SCD" |
| `System.Description` | HTML string | `<p>...</p>` |
| `System.State` | string | New, Active, Resolved, Closed |
| `System.AssignedTo` | email or display name | "user@example.com" |
| `System.IterationPath` | string | "your-project\\Sprint 26" |
| `System.AreaPath` | string | "your-project" |
| `System.Tags` | semicolon-separated | "bronze; ingestion; api" |
| `Microsoft.VSTS.Common.Priority` | integer | 1, 2, 3, 4 |
| `Microsoft.VSTS.Scheduling.RemainingWork` | decimal | 4.0 |

## HTML Format for Description & Comments

Azure DevOps uses HTML in description and comment fields. Key patterns:

```html
<!-- Headings -->
<h3>Section Title</h3>

<!-- Lists -->
<ul>
<li>Item one</li>
<li>Item two</li>
</ul>

<!-- Code -->
<code>nb_bronze_schemas</code>

<!-- Tables -->
<table>
<tr><th>Column 1</th><th>Column 2</th></tr>
<tr><td>Value</td><td>Value</td></tr>
</table>

<!-- Bold -->
<strong>Important</strong>
```

## Documenting Completed Work (Pattern)

When a technical task is done, update it like this:

1. **Update description** — brief summary of what was done
2. **Add a comment** — detailed implementation info (fields changed, notebooks touched, validation results, run IDs)

```python
# 1. Brief description
description = """<h3>Summary</h3>
<p>Brief description of what was implemented.</p>
<h3>Changes</h3>
<ul>
<li>Change 1</li>
<li>Change 2</li>
</ul>"""

patch_body = [{"op": "add", "path": "/fields/System.Description", "value": description}]
requests.patch(f"{base}/wit/workitems/{id}", auth=auth,
    headers={"Content-Type": "application/json-patch+json"},
    params={"api-version": "7.1"}, json=patch_body, timeout=60)

# 2. Detailed comment
comment = """<h3>Implementation Details</h3>
<p>Detailed info: schemas, notebooks, validation, job IDs...</p>"""

requests.post(f"{base}/wit/workitems/{id}/comments", auth=auth,
    headers={"Content-Type": "application/json"},
    params={"api-version": "7.1-preview.4"},
    json={"text": comment}, timeout=60)
```

## Guardrails

- Always read the work item first before updating to understand current state.
- Use HTML format for descriptions and comments (ADO renders it).
- Max 200 IDs per batch GET request.
- Comments use API version `7.1-preview.4` (different from other endpoints).
- The PAT is in `skills/fab-ado-board/fab-ado-board.config.json` — never hardcode it in scripts.
- When documenting work, put the **brief summary in description** and **full details in comments** (comments have history/timestamps).
- Always verify the update succeeded (check HTTP 200 response).

## Reading Local Requirements Cache

The project maintains a local cache of all ADO work items at:

```
./output/requirements/
├── index.json                    # All epics summary
├── epics/
│   ├── EPIC-1356_*.json          # Epic summary
│   └── EPIC-1356_*/
│       ├── Feature-1330_*.json   # Each child item
│       └── ...
```

To refresh this cache, run your project-local extractor and write into `./output/requirements`.

Use the local JSON files for quick lookups without hitting the API.
