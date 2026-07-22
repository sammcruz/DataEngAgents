# Fab ADO Wiki Agent Runner

Executable runner for the `fab-ado-wiki` skill.

## Paths

- Script: `scripts/fab_ado_wiki_agent.py`
- Skill: `skills/fab-ado-wiki/SKILL.md`
- Shared config: `skills/fab-ado-board/fab-ado-board.config.json`

## Capabilities

- List project wikis
- Read wiki page metadata/content
- Create or update wiki pages (dry-run by default)

## Command Examples

```bash
# List wikis
python scripts/fab_ado_wiki_agent.py list-wikis

# Read root page
python scripts/fab_ado_wiki_agent.py get-page --wiki "<project>.wiki" --path "/" --include-content

# Dry-run update
python scripts/fab_ado_wiki_agent.py upsert-page --wiki "<project>.wiki" --path "/Automation/Test" --text "# Test"

# Execute update
python scripts/fab_ado_wiki_agent.py upsert-page --wiki "<project>.wiki" --path "/Automation/Test" --text-file /tmp/page.md --execute
```

## Logging

Each run writes JSON output to:

- `output/agents/fab-ado-wiki/runs/run-<timestamp>.json`

## Safety

- Writes are dry-run unless `--execute` is passed.
- Keep PAT values out of logs and committed files.
