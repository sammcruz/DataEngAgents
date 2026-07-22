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

Use this skill to track and document engineering work on your board.

## Configuration

The Azure DevOps credentials are stored in:

```
skills/fab-ado-board/fab-ado-board.config.json
```

```json
{
    "ado_organization": "your-organization",
    "ado_project": "your-project",
    "ado_pat": "<PAT>",
    "ado_area_path": "",
    "output_path": "./output/requirements"
}
```

Always read this file to get the PAT and org/project details before making API calls.

## Real Agent Runner

This skill has an executable agent runner in the repository:

```bash
python scripts/fab_ado_board_agent.py --help
```

Quick examples:

```bash
# Read one work item
python scripts/fab_ado_board_agent.py get --id 1858

# Dry-run write (no API mutation)
python scripts/fab_ado_board_agent.py add-comment --id 1858 --text-file /tmp/comment.html

# Execute write
python scripts/fab_ado_board_agent.py add-comment --id 1858 --text-file /tmp/comment.html --execute
```

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
    {"op": "add", "path": "/fields/System.AssignedTo", "value": "user@domain.com"},
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
    {"op": "add", "path": "/fields/System.AssignedTo", "value": "user@domain.com"},
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

## Common Fields Reference

| Field path | Type | Example |
|---|---|---|
| `System.Title` | string | "Ingest new fields from api for SCD" |
| `System.Description` | HTML string | `<p>...</p>` |
| `System.State` | string | New, Active, Resolved, Closed |
| `System.AssignedTo` | email or display name | "user@domain.com" |
| `System.IterationPath` | string | "your-project\\Sprint 26" |
| `System.AreaPath` | string | "your-project" |
| `System.Tags` | semicolon-separated | "bronze; crm; api" |
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
<code>nb_transform_orders</code>

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

## Optional Local Cache Pattern

If your team maintains a local cache of board snapshots, keep it under:

```
./output/requirements/
├── index.json
└── epics/
```

This cache is optional and repository-specific. The agent works directly against the Azure DevOps API without it.
