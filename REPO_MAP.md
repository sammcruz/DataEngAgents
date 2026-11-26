# Repository map

One-page index of everything in this repository. Read this first in a new session, then open only the file you need. Keep it current: update the relevant line whenever an agent, prompt, skill or doc is added, renamed or removed.

## Agents (`agents/`, Copilot pointers in `.github/agents/`)

| Agent | Responsible for | Run with prompt |
|---|---|---|
| `data-engineer` | Coordinating Fabric work; delegating to the agents below | `audit-workspace`, `sync-notebook-changes` |
| `incident-agent` | A pipeline or notebook that fails in one environment but not another | `fix-env-diff` |
| `bugfix-agent` | A data bug from a symptom: investigate, propose, **wait for approval**, implement, document | `fix-bug` |
| `delivery-agent` | One Azure DevOps work item, end to end | `deliver-work-item` |
| `release-notes-agent` | Sprint roll-up into a wiki release-notes page | `release-notes` |
| `semantic-model-agent` | Semantic model changes with parent/child edit safety | `sm-safe-update` |
| `devops-pipeline-agent` | A failed Azure DevOps CI/CD pipeline run | `fix-pipeline` |
| `ado-board-agent` / `ado-wiki-agent` | Board and wiki reads and (dry-run first) writes | `document-completed-work` |
| `governance-agent` | Validating skills and agent contracts; keeping the knowledge base small and true | `new-skill`, `memory-review` |

## Skills (`skills/`)

| Skill | Use for |
|---|---|
| `fab-bootstrap` | Installing and authenticating `fab` |
| `fab-discovery` | Exploring workspaces, items and paths |
| `fab-api-bridge` | Direct Fabric REST calls through `fab api` |
| `fab-notebook-dev` | Reading, creating, editing, importing and running notebooks |
| `fabric-notebook-toolkit` | Interactive Spark sessions, cell-by-cell runs, single-cell edits (`fntk`) |
| `fab-job-ops` | Running, scheduling, polling and troubleshooting jobs |
| `fab-table-query` | Reading and validating Lakehouse table data |
| `fab-onelake-ops` | Files and folders in OneLake |
| `fab-deploy` | Promoting items between environments |
| `fab-semantic-model` | Semantic model quality, TMDL and documentation |
| `fab-workspace-architecture` | Single-workspace versus workspace-per-stage design |
| `fab-workspace-organize` | Folders, grouping and clean-up |
| `fab-conventions` | Naming and architecture standards |
| `fab-acl-audit` | Inspecting and changing access control lists |
| `fab-ado-board` / `fab-ado-wiki` | Azure DevOps work items, pull requests and wiki |
| `repo-orientation` | Checking private knowledge before exploring a repository |

## Tool wiring

| Path | Tool | What it does |
|---|---|---|
| `AGENTS.md` | Codex, Cursor, Gemini CLI, Copilot | Repo-wide instructions |
| `CLAUDE.md` | Claude Code | Imports `AGENTS.md` and adds Claude Code notes |
| `.claude/skills`, `.claude/agents`, `.claude/commands` | Claude Code | Symlinks to `skills/`, `agents/`, `prompts/` so a clone works with no install |
| `.claude-plugin/plugin.json`, `marketplace.json` | Claude Code | Packages the same folders as the `dataengagents` plugin |
| `.github/agents/`, `.github/copilot-instructions.md` | GitHub Copilot | Custom agents and rules |
| `skills/*/agents/openai.yaml` | Codex | Skill display metadata |

## Prompts (`prompts/`)

`fix-bug`, `fix-env-diff`, `fix-pipeline`, `deliver-work-item`, `release-notes`, `sm-safe-update`, `audit-workspace`, `document-completed-work`, `sync-notebook-changes`, `new-skill`, `memory-review`.

## Docs (`docs/`)

| File | Contents |
|---|---|
| `architecture.md` | The layered model and why it is split this way |
| `knowledge-layer.md` | The private knowledge layer and how agents use it |
| `gotchas.md` | Anonymised root causes and workarounds (fab CLI, notebooks, data loading and deletes, pipelines, CI/CD, semantic models, data agents) |
| `memory-maintenance.md` | Status fields, generated index, size budgets and the periodic review pass for the knowledge layer |
| `write-contract.md` | The permission / safety pattern / rerun / schema agreement made before any write |
| `standing-instructions.template.md` | A starting point for a user-level instruction file |
| `templates/knowledge/` | Empty templates for the private knowledge repository |
| `prompt-cookbook.md` | Example prompts for the skills, for Codex, GitHub Copilot and Claude Code |

## Scripts (`scripts/`)

- `fab_ado_board_agent.py`, `fab_ado_wiki_agent.py`: Azure DevOps runners, dry-run by default.
- `build_knowledge_index.py`: generates `INDEX.md` for a private knowledge repo and flags entries due for review and files over budget.
- `check_anonymized.py`: scans for ids, e-mails, tenant URLs, tokens and (optionally) a private deny-list of names.
- `quick_validate.py`, `init_skill.py`, `generate_openai_yaml.py`: validate and scaffold skills.
