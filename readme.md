# DataEngAgents

A reusable, sanitized template for running AI coding agents against
**Microsoft Fabric** and **Azure DevOps** — read/write work items, read/update
wiki pages, and manage Fabric workspaces/notebooks, all with a dry-run-first
safety model.

No real organization names, credentials, or endpoints are included anywhere
in this repository — every example uses placeholders you fill in locally.

> Looking for agent-facing setup instructions (build/validate commands,
> non-negotiable rules)? See [`AGENTS.md`](AGENTS.md). This README is the
> human-facing overview.

## Why this structure

Agent context is split into five layers, each answering exactly one
question, so nothing gets duplicated or buried. See
[`docs/architecture.md`](docs/architecture.md) for the full model.

```
docs/          → what exists           (reference material, this architecture)
.github/       → what rules apply      (repo-wide + path-scoped instructions)
agents/        → who is responsible    (role definitions + trust boundaries)
skills/        → what they know        (technical how-to, reusable)
prompts/       → what action to run    (task templates)
scripts/       → the executable runners behind the agents
```

## What's included

- **Skills** (`skills/`) — technical how-to for:
  - `fab-ado-board` — Azure DevOps work item read/write
  - `fab-ado-wiki` — Azure DevOps wiki read/update
  - `fab-notebook-dev` — Fabric notebook export/edit/import/run cycle
  - `fab-table-query` — reading and validating Fabric Lakehouse table data
  - `fab-semantic-model` — Fabric/Power BI semantic model quality
  - `fab-workspace` — Fabric workspace architecture and organization
- **Agents** (`agents/`, `.github/agents/`) — role definitions with explicit
  trust boundaries: `data-engineer` (coordinator), `ado-board-agent`,
  `ado-wiki-agent`, `governance-agent`.
- **Prompts** (`prompts/`) — ready-to-run task templates that tie agents and
  skills together (`document-completed-work`, `sync-notebook-changes`,
  `audit-workspace`, `new-skill`).
- **Executable runners** (`scripts/`):
  - `fab_ado_board_agent.py`, `fab_ado_wiki_agent.py` — real API clients,
    dry-run by default.
  - `quick_validate.py` — validates a skill's `SKILL.md` structure.
  - `init_skill.py`, `generate_openai_yaml.py` — scaffold a new skill.

## Prerequisites

- Python 3.10+
- Network access to the Azure DevOps REST API
- An Azure DevOps Personal Access Token (PAT) with the scopes you need

## Setup

```bash
python -m pip install -r requirements.txt
cp .env.example .env
# edit .env and set ADO_PAT — never commit this file
export $(grep -v '^#' .env | xargs)   # or use your usual env-loading approach
```

Edit `skills/fab-ado-board/fab-ado-board.config.json`:

```json
{
  "ado_organization": "<your-organization>",
  "ado_project": "<your-project>",
  "ado_pat": "",
  "ado_area_path": "",
  "output_path": "output/requirements"
}
```

If `ADO_PAT` is set, it overrides `ado_pat` in the config — that's the
recommended path so no token ever touches a file in this repo.

## Quick start

```bash
# ADO board agent
python scripts/fab_ado_board_agent.py --help
python scripts/fab_ado_board_agent.py get --id 123
python scripts/fab_ado_board_agent.py add-comment --id 123 --text "<p>Hello</p>"
python scripts/fab_ado_board_agent.py add-comment --id 123 --text "<p>Hello</p>" --execute

# ADO wiki agent
python scripts/fab_ado_wiki_agent.py --help
python scripts/fab_ado_wiki_agent.py list-wikis
python scripts/fab_ado_wiki_agent.py get-page --wiki "<project>.wiki" --path "/" --include-content
python scripts/fab_ado_wiki_agent.py upsert-page --wiki "<project>.wiki" --path "/Automation/Test" --text "# Test"
```

## Validate the included skills

```bash
python scripts/quick_validate.py skills/fab-ado-board
python scripts/quick_validate.py skills/fab-ado-wiki
python scripts/quick_validate.py skills/fab-table-query
python scripts/quick_validate.py skills/fab-notebook-dev
python scripts/quick_validate.py skills/fab-semantic-model
python scripts/quick_validate.py skills/fab-workspace
```

## Adding your own skill

```bash
python scripts/init_skill.py <skill-name> --path skills
# fill in the SKILL.md TODOs, then:
python scripts/quick_validate.py skills/<skill-name>
```

See [`prompts/new-skill.md`](prompts/new-skill.md) for the full workflow.

## Safety notes

- Write operations in both runners are **dry-run by default**.
- Use `--execute` only when you're ready to persist changes.
- Do not commit real PAT values, organization names, or endpoints — keep
  tenant-specific values in config placeholders, never in skill docs or
  agent files.
- Every run writes a JSON log to `output/agents/<runner>/runs/` — that
  directory is gitignored on purpose.

## GitHub Copilot integration

This repo ships native Copilot custom agents under `.github/agents/`
(`data-engineer`, `ado-board`, `ado-wiki`) plus repo-wide instructions at
[`.github/copilot-instructions.md`](.github/copilot-instructions.md) and a
path-scoped example at
[`.github/instructions/python-scripts.instructions.md`](.github/instructions/python-scripts.instructions.md).
Open this repo in VS Code with Copilot enabled and the custom agents are
available immediately — no extra setup.

## License

[MIT](LICENSE) — use, fork, and adapt freely.
