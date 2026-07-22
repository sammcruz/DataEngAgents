# Fab ADO Board Agent Runner

Executable runner for the `fab-ado-board` skill.

## Paths

- Script: `scripts/fab_ado_board_agent.py`
- Skill: `skills/fab-ado-board/SKILL.md`
- Config: `skills/fab-ado-board/fab-ado-board.config.json`

## Capabilities

- Read one work item
- Read work item comments
- Execute WIQL queries
- Batch read work items
- Add comments (dry-run by default)
- Update work items via JSON patch (dry-run by default)
- Execute multi-step plan files

## Command Examples

```bash
# Read
python scripts/fab_ado_board_agent.py get --id 123
python scripts/fab_ado_board_agent.py comments --id 123 --top 20
python scripts/fab_ado_board_agent.py wiql --query-file /tmp/query.wiql --fetch-details

# Dry-run writes
python scripts/fab_ado_board_agent.py add-comment --id 123 --text "<p>Status update</p>"
python scripts/fab_ado_board_agent.py update --id 123 --patch-file /tmp/patch.json

# Execute writes
python scripts/fab_ado_board_agent.py add-comment --id 123 --text "<p>Status update</p>" --execute
python scripts/fab_ado_board_agent.py update --id 123 --patch-file /tmp/patch.json --execute
```

## Plan Mode

Plan schema:

```json
{
  "steps": [
    {"action": "get_work_item", "id": 123},
    {"action": "get_comments", "id": 123, "top": 10},
    {"action": "add_comment", "id": 123, "text": "<p>Validation complete.</p>"},
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

Run dry-run plan:

```bash
python scripts/fab_ado_board_agent.py plan --plan-file /tmp/ado-plan.json
```

Run with writes enabled:

```bash
python scripts/fab_ado_board_agent.py plan --plan-file /tmp/ado-plan.json --execute
```

## Logging

Each run writes JSON output to:

- `output/agents/fab-ado-board/runs/run-<timestamp>.json`

## Credential Handling

- Preferred: set `ADO_PAT` as an environment variable.
- Alternative: store placeholder PAT in config and inject securely in runtime.
- Never commit real PAT values.
