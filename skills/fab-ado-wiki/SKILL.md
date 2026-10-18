---
name: fab-ado-wiki
description: Use this skill to read and update Azure DevOps Wiki pages for your Azure DevOps project, reusing the same Azure DevOps credentials as fab-ado-board.
---

# Fab ADO Wiki

## Use

Use this skill when the user wants to:

1. List available Azure DevOps wikis in the project
2. Read wiki pages (metadata and content)
3. Create or update wiki pages
4. Automate wiki updates with a controlled runner (dry-run first)

This skill reuses the same Azure DevOps organization/project/PAT config used by `fab-ado-board`.

## Configuration

Shared config file:

```text
skills/fab-ado-board/fab-ado-board.config.json
```

Expected fields:

```json
{
  "ado_organization": "<your-organization>",
  "ado_project": "<your-project>",
  "ado_pat": "<PAT>"
}
```

## Real Agent Runner

Executable runner:

```bash
python scripts/fab_ado_wiki_agent.py --help
```

Quick examples:

```bash
# List wikis
python scripts/fab_ado_wiki_agent.py list-wikis

# Read a page with content
python scripts/fab_ado_wiki_agent.py get-page --wiki "Wiki" --path "/" --include-content --version main --version-type branch

# Dry-run update (safe)
python scripts/fab_ado_wiki_agent.py upsert-page --wiki "Wiki" --path "/Automation/Test" --text "# Test" --version main --version-type branch

# Execute update
python scripts/fab_ado_wiki_agent.py upsert-page --wiki "Wiki" --path "/Automation/Test" --text-file /tmp/page.md --version main --version-type branch --execute
```

## Code Wiki Note

This project uses a **code wiki**. For reliable reads/writes, always pass:

- `--version main`
- `--version-type branch`

The runner supports true upsert behavior: if a page already exists and `--if-match` is not provided, it automatically fetches ETag and retries as an update.

Full usage guide:

- `docs/fab-ado-wiki-agent.md`

## API Base URL

```text
https://dev.azure.com/{organization}/{project}/_apis
```

## Core Endpoints

- `GET /wiki/wikis` : list wikis
- `GET /wiki/wikis/{wikiIdentifier}/pages` : read wiki page
- `PUT /wiki/wikis/{wikiIdentifier}/pages` : create/update wiki page content

## Guardrails

- Write operations are dry-run by default.
- Use `--execute` only when ready to commit wiki changes.
- Never print PAT values in logs or output.
- Prefer page-level updates with explicit path and content source.
- For code wiki pages, prefer `--version main --version-type branch` for deterministic behavior.
- When manually passing `--if-match`, retrieve the latest ETag with `get-page` first.

## Output Expectations

For each run, report:

1. Command and target wiki/path
2. Whether run was dry-run or execute
3. API result summary (page ID, path, remote URL)
4. Path to saved local run log
