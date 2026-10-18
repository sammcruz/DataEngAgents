# Fab ADO Board Agent Runner

This repository now includes a real, executable agent runner for the `fab-ado-board` skill:

- Script: `scripts/fab_ado_board_agent.py`
- Skill doc: `skills/fab-ado-board/SKILL.md`
- Config: `skills/fab-ado-board/fab-ado-board.config.json`

## What makes it a real agent

- Loads skill context from `SKILL.md` for run metadata
- Loads ADO org/project/PAT from skill-local config
- Executes tool actions against Azure DevOps REST APIs
- Supports multi-step plans with per-step results
- Uses dry-run by default for write actions
- Writes run logs to `output/agents/fab-ado-board/runs`

## Commands

Read operations:

```bash
python scripts/fab_ado_board_agent.py get --id 123
python scripts/fab_ado_board_agent.py comments --id 123 --top 20
python scripts/fab_ado_board_agent.py wiql --query-file /tmp/query.wiql
python scripts/fab_ado_board_agent.py batch --ids "123,124,125"
```

Current sprint reporting examples:

```sql
-- /tmp/current-sprint-stories-tasks.wiql
SELECT [System.Id]
FROM WorkItems
WHERE
  [System.TeamProject] = @project
  AND [System.IterationPath] = @CurrentIteration
  AND [System.WorkItemType] IN ('User Story', 'Task')
ORDER BY [System.WorkItemType], [System.Id]
```

```sql
-- /tmp/current-sprint-bugs.wiql
SELECT [System.Id]
FROM WorkItems
WHERE
  [System.TeamProject] = @project
  AND [System.IterationPath] = @CurrentIteration
  AND [System.WorkItemType] = 'Bug'
ORDER BY [System.Id]
```

```bash
python scripts/fab_ado_board_agent.py wiql --query-file /tmp/current-sprint-stories-tasks.wiql --fetch-details --expand all
python scripts/fab_ado_board_agent.py wiql --query-file /tmp/current-sprint-bugs.wiql --fetch-details --expand all
```

Note: `System.IterationPath` does not support `CONTAINS` in WIQL.

Write operations (dry-run by default):

```bash
python scripts/fab_ado_board_agent.py add-comment --id 123 --text-file /tmp/comment.html
python scripts/fab_ado_board_agent.py update --id 123 --patch-file /tmp/patch.json
```

Actually execute writes:

```bash
python scripts/fab_ado_board_agent.py add-comment --id 123 --text-file /tmp/comment.html --execute
python scripts/fab_ado_board_agent.py update --id 123 --patch-file /tmp/patch.json --execute
```

## Plan mode

Plan file format:

```json
{
  "steps": [
    {"action": "get_work_item", "id": 123},
    {"action": "get_comments", "id": 123, "top": 10},
    {
      "action": "add_comment",
      "id": 123,
      "text": "<p>Validation completed in DEV.</p>"
    },
    {
      "action": "update_work_item",
      "id": 123,
      "patch": [
        {"op": "add", "path": "/fields/System.State", "value": "Resolved"}
      ]
    }
  ]
}
```

Run plan dry-run:

```bash
python scripts/fab_ado_board_agent.py plan --plan-file /tmp/ado-plan.json
```

Run plan with writes enabled:

```bash
python scripts/fab_ado_board_agent.py plan --plan-file /tmp/ado-plan.json --execute
```

## PAT handling

Default source:

- `skills/fab-ado-board/fab-ado-board.config.json` -> `ado_pat`

Optional override:

- Set `ADO_PAT` environment variable to override config value.

## Run logs

Each execution stores a JSON log under:

- `output/agents/fab-ado-board/runs/run-<timestamp>.json`

The log includes:

- command
- org/project
- skill metadata loaded
- API result or dry-run payload
