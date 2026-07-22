# AGENTS.md

Instructions for AI coding agents (GitHub Copilot, Claude Code, Codex,
Cursor, Gemini CLI, and compatible tools) working in this repository. For
the reasoning behind the structure below, see
[`docs/architecture.md`](docs/architecture.md).

## What this repository is

A template for running AI agents against Microsoft Fabric and Azure DevOps:
executable runners with a dry-run-first safety model, skills describing the
technical how-to, and role definitions describing who's responsible for
what. It ships with no real credentials, endpoints, or tenant data — every
example uses placeholders.

## Setup

```bash
python -m pip install -r requirements.txt
cp .env.example .env   # then fill in ADO_PAT, do not commit .env
```

Edit `skills/fab-ado-board/fab-ado-board.config.json` with your
organization/project (never a real PAT — that comes from `ADO_PAT`).

## Validate before you trust a skill

```bash
python scripts/quick_validate.py skills/fab-ado-board
python scripts/quick_validate.py skills/fab-ado-wiki
python scripts/quick_validate.py skills/fab-notebook-dev
python scripts/quick_validate.py skills/fab-semantic-model
python scripts/quick_validate.py skills/fab-table-query
python scripts/quick_validate.py skills/fab-workspace
```

## Directory map

| Path | Layer | Answers |
|---|---|---|
| `docs/` | Docs | What exists? |
| `.github/copilot-instructions.md`, `.github/instructions/` | Instructions | What rules must never be broken? |
| `agents/`, `.github/agents/` | Agents | Who is responsible? |
| `skills/` | Skills | What specialized knowledge is needed? |
| `prompts/` | Prompts | What specific action to run? |
| `scripts/` | — | Executable runners backing the agents above |

## Non-negotiable rules

1. **Dry-run by default.** Both runners (`fab_ado_board_agent.py`,
   `fab_ado_wiki_agent.py`) only mutate Azure DevOps when called with
   `--execute`. Never add that flag on a user's behalf without them
   explicitly asking for it.
2. **No real credentials, ever.** PAT values come from the `ADO_PAT`
   environment variable. Config files and skill docs use placeholders like
   `<your-organization>`. If you're about to write a real token, endpoint,
   or tenant name into a file in this repo, stop.
3. **Keep the five layers separate.** Technical how-to goes in `skills/`,
   not `agents/`. Global rules go in `.github/copilot-instructions.md`, not
   scattered across skills. See `docs/architecture.md` before adding new
   content.
4. **New skills get validated.** Run `quick_validate.py` against any new or
   edited skill before referencing it from an agent or prompt.

## Quick start (read-only, safe to run without any config)

```bash
python scripts/fab_ado_board_agent.py --help
python scripts/fab_ado_wiki_agent.py --help
```
