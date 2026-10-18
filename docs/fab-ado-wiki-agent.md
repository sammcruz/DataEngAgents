# Fab ADO Wiki Agent Runner

Real runner for the `fab-ado-wiki` skill.

## Paths

- Script: `scripts/fab_ado_wiki_agent.py`
- Skill: `skills/fab-ado-wiki/SKILL.md`
- Shared config: `skills/fab-ado-board/fab-ado-board.config.json`

## Commands

```bash
# List all project wikis
python scripts/fab_ado_wiki_agent.py list-wikis

# Read root page content
python scripts/fab_ado_wiki_agent.py get-page --wiki "Wiki" --path "/" --include-content --version main --version-type branch

# Dry-run wiki update
python scripts/fab_ado_wiki_agent.py upsert-page --wiki "Wiki" --path "/Automation/Test" --text "# Test" --version main --version-type branch

# Execute wiki update
python scripts/fab_ado_wiki_agent.py upsert-page --wiki "Wiki" --path "/Automation/Test" --text-file /tmp/page.md --version main --version-type branch --execute

# Explicit ETag update (optional advanced mode)
python scripts/fab_ado_wiki_agent.py upsert-page --wiki "Wiki" --path "/Automation/Test" --text-file /tmp/page.md --version main --version-type branch --if-match '"<etag>"' --execute
```

## Safety

- Write operations are dry-run unless `--execute` is provided.
- PAT is never printed by the runner.
- In code wiki mode, pass `--version main --version-type branch`.
- Upsert auto-retries existing-page updates by resolving ETag when `--if-match` is omitted.

## Logs

Runs are logged to:

- `output/agents/fab-ado-wiki/runs/run-<timestamp>.json`
