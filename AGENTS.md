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
for d in skills/*/; do python scripts/quick_validate.py "$d"; done
```

## Check for leaked customer data before every commit

```bash
python scripts/check_anonymized.py
```

It flags GUIDs, e-mail addresses, tenant URLs, token-shaped strings and
unknown URL hosts. Put customer, employer and project names in a private,
git-ignored `.anonymize-denylist.txt` (one per line) and it flags those too.
Enable the bundled hook with `git config core.hooksPath .githooks`.

## Directory map

| Path | Layer | Answers |
|---|---|---|
| `docs/` | Docs | What exists? |
| `.github/copilot-instructions.md`, `.github/instructions/` | Instructions | What rules must never be broken? |
| `agents/`, `.github/agents/` | Agents | Who is responsible? |
| `skills/` | Skills | What specialized knowledge is needed? |
| `prompts/` | Prompts | What specific action to run? |
| `scripts/` | — | Executable runners backing the agents above |
| *(private repo)* | Knowledge | What is true about this customer? See `docs/knowledge-layer.md` |

`REPO_MAP.md` indexes every agent, prompt, skill and doc on one page.

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
5. **Stay anonymous.** No customer, employer, workspace, table or person
   names, no ids, no tenant URLs, in any file. Run
   `python scripts/check_anonymized.py` before committing. Customer-specific
   knowledge belongs in a private repository (`docs/knowledge-layer.md`).
6. **Never edit a customer repository's local checkout.** Author live in the
   Fabric workspace with `fab` or `fntk`.

## Quick start (read-only, safe to run without any config)

```bash
python scripts/fab_ado_board_agent.py --help
python scripts/fab_ado_wiki_agent.py --help
```
