# DataEngAgents

A reusable, sanitized template for running AI coding agents against
**Microsoft Fabric** and **Azure DevOps**: read and write work items, read
and update wiki pages, manage Fabric workspaces and notebooks, investigate
and fix data bugs, and ship changes through CI/CD, all with a dry-run-first
safety model and explicit human approval gates.

No real organization names, credentials, workspace names, ids or endpoints
are included anywhere in this repository. Every example uses placeholders
you fill in locally, and a [scanner](#keeping-it-anonymous) enforces it.

> Looking for agent-facing setup instructions (build/validate commands,
> non-negotiable rules)? See [`AGENTS.md`](AGENTS.md). This README is the
> human-facing overview, and [`REPO_MAP.md`](REPO_MAP.md) is the one-page
> index of everything in the repository.

## Why this structure

Agent context is split into layers, each answering exactly one question, so
nothing gets duplicated or buried. See
[`docs/architecture.md`](docs/architecture.md) for the full model.

```
docs/          → what exists           (reference material, gotchas, architecture)
.github/       → what rules apply      (repo-wide + path-scoped instructions)
agents/        → who is responsible    (role definitions + trust boundaries)
skills/        → what they know        (technical how-to, reusable)
prompts/       → what action to run    (workflows and task templates)
scripts/       → the executable runners behind the agents
(private repo) → what is true here     (customers, environments, incidents)
```

The last layer is **deliberately not in this repository**. Real customer and
environment knowledge belongs in a private repo next to this one; see
[`docs/knowledge-layer.md`](docs/knowledge-layer.md) for the layout and empty
templates.

## What's included

### Skills (`skills/`): technical how-to

| Group | Skills |
|---|---|
| **Get started** | `fab-bootstrap` (install and sign in to `fab`), `fab-discovery` (explore workspaces and items), `fab-api-bridge` (direct Fabric REST through `fab api`) |
| **Notebooks and jobs** | `fab-notebook-dev` (read, edit, import, run), `fabric-notebook-toolkit` (interactive Spark sessions with Microsoft's `fntk`: cell-by-cell runs, single-cell edits, real tracebacks), `fab-job-ops` (run, schedule, poll, troubleshoot), `fab-table-query` (read and validate Lakehouse tables) |
| **Data and storage** | `fab-onelake-ops` (files and folders in OneLake) |
| **Release** | `fab-deploy` (promote items between environments) |
| **Modeling** | `fab-semantic-model` (quality, TMDL, documentation) |
| **Workspace design** | `fab-workspace-architecture` (single workspace versus workspace per stage), `fab-workspace-organize` (folders and clean-up), `fab-conventions` (naming standards), `fab-acl-audit` (access control lists) |
| **Azure DevOps** | `fab-ado-board` (work items, comments, WIQL, pull requests), `fab-ado-wiki` (wiki pages) |
| **Orientation** | `repo-orientation` (check private knowledge before exploring a repo) |

### Agents (`agents/`, `.github/agents/`): who is responsible

| Agent | Responsible for | Prompt |
|---|---|---|
| `data-engineer` | Coordinating the work and delegating | `audit-workspace`, `sync-notebook-changes` |
| `incident-agent` | A pipeline or notebook failing in one environment but not another | `fix-env-diff` |
| `bugfix-agent` | A data bug from a symptom: investigate, propose, **wait for approval**, implement, document | `fix-bug` |
| `delivery-agent` | One work item, end to end | `deliver-work-item` |
| `release-notes-agent` | Sprint roll-up into a wiki page | `release-notes` |
| `semantic-model-agent` | Semantic model changes with parent/child edit safety | `sm-safe-update` |
| `devops-pipeline-agent` | A failed Azure DevOps CI/CD run | `fix-pipeline` |
| `ado-board-agent`, `ado-wiki-agent` | Board and wiki access, dry-run first | `document-completed-work` |
| `governance-agent` | Validating skills and agent contracts | `new-skill` |

### Prompts (`prompts/`): what to run

Step-by-step workflows that tie agents and skills together: `fix-bug`,
`fix-env-diff`, `fix-pipeline`, `deliver-work-item`, `release-notes`,
`sm-safe-update`, `audit-workspace`, `document-completed-work`,
`sync-notebook-changes`, `new-skill`.

### Docs (`docs/`)

- [`gotchas.md`](docs/gotchas.md): anonymised root causes and workarounds
  for the `fab` CLI, notebooks, CI/CD with `fabric-cicd`, semantic models and
  Fabric data agents. Start here when something fails with a generic error.
- [`knowledge-layer.md`](docs/knowledge-layer.md) and
  [`templates/knowledge/`](docs/templates/knowledge/): the private knowledge
  layer and empty templates for it.
- [`standing-instructions.template.md`](docs/standing-instructions.template.md):
  a starting point for the user-level instruction file your agent loads
  every session.
- [`prompt-cookbook.md`](docs/prompt-cookbook.md): copy-paste prompts for the skills.
- [`architecture.md`](docs/architecture.md): the layering model.

### Executable runners (`scripts/`)

- `fab_ado_board_agent.py`, `fab_ado_wiki_agent.py`: real API clients,
  dry-run by default. The board runner also reads and updates pull requests
  and lists branch commits.
- `check_anonymized.py`: scans for leaked ids, e-mails, tenant URLs, tokens
  and (optionally) a private deny-list of names.
- `quick_validate.py`, `init_skill.py`, `generate_openai_yaml.py`: validate
  and scaffold skills.

### Related skill packs

This template focuses on day-to-day Fabric operations. Microsoft's
[`skills-for-fabric`](https://github.com/microsoft/skills-for-fabric) covers
workloads this repository does not (Eventhouse, Eventstream, deployment
pipelines, Git integration, Spark, SQL warehouse and more). Install it
alongside this one rather than duplicating it here. In particular, its
`git-integration-operations-cli` skill is the recommended way to commit a
single item from a busy workspace (see [`docs/gotchas.md`](docs/gotchas.md)).

## Prerequisites

- Python 3.10+ (3.10 to 3.13 if you also install `fab` and `fntk`)
- Network access to the Azure DevOps REST API
- An Azure DevOps Personal Access Token (PAT) with the scopes you need
- Optionally the Fabric CLI (`fab`), see `skills/fab-bootstrap`

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

`ADO_PAT` overrides `ado_pat` in the config. That is the recommended path, so
no token ever touches a file in this repository.

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
```

## Validate the skills

```bash
for d in skills/*/; do python scripts/quick_validate.py "$d"; done
```

## Keeping it anonymous

This is a public template, so a customer name or a workspace id slipping
into a skill is the failure mode to guard against.

```bash
python scripts/check_anonymized.py          # scan the whole repo
git config core.hooksPath .githooks         # block commits that fail the scan
```

The scanner flags GUIDs, e-mail addresses, tenant URLs, token-shaped
strings and URL hosts outside a short allowlist. To also catch **names**,
put customer, employer and project names (one per line) in a private
`.anonymize-denylist.txt`. It is git-ignored on purpose, so the names
themselves never reach the repository. A GitHub Action runs the same scan on
every pull request.

## Adding your own skill

```bash
python scripts/init_skill.py <skill-name> --path skills
# fill in the SKILL.md TODOs, then:
python scripts/quick_validate.py skills/<skill-name>
```

See [`prompts/new-skill.md`](prompts/new-skill.md) for the full workflow.

## Safety notes

- Write operations in both runners are **dry-run by default**. Use
  `--execute` only when you are ready to persist changes.
- Agents that change a live workspace follow the same pattern: investigate
  read-only, propose, **wait for explicit approval**, then implement.
- Production is read-only outside CI/CD.
- Author live in the Fabric workspace with `fab` or `fntk`. Never edit a
  customer repository's local git checkout.
- Do not commit real PAT values, organization names, workspace names or
  endpoints. Keep tenant-specific values in config placeholders, never in
  skill docs or agent files.
- Every run writes a JSON log to `output/agents/<runner>/runs/`. That
  directory is gitignored on purpose.

## GitHub Copilot integration

This repo ships native Copilot custom agents under `.github/agents/`
(`data-engineer`, `ado-board`, `ado-wiki`, `incident`, `bugfix`, `delivery`,
`release-notes`, `semantic-model`, `devops-pipeline`) plus repo-wide
instructions at
[`.github/copilot-instructions.md`](.github/copilot-instructions.md) and a
path-scoped example at
[`.github/instructions/python-scripts.instructions.md`](.github/instructions/python-scripts.instructions.md).
Open this repo in VS Code with Copilot enabled and the custom agents are
available immediately — no extra setup. Claude Code, Codex, Cursor and Gemini
CLI read [`AGENTS.md`](AGENTS.md).

## License

[MIT](LICENSE) — use, fork, and adapt freely.
