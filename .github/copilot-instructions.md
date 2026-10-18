# Repository Instructions

These rules apply to every request in this repository, regardless of which
agent, skill, or prompt is in play. For the full model behind this file, see
[`docs/architecture.md`](../docs/architecture.md).

## Safety

- **Writes are dry-run by default.** Every write operation (Azure DevOps
  board updates, wiki updates) must be shown as a preview before it runs.
  Only proceed to `--execute` after explicit human confirmation.
- **Never commit, print, or log a real credential.** Personal Access Tokens
  are read from the `ADO_PAT` environment variable or a config placeholder —
  never hardcoded in a script, prompt, commit, or run log.
- **Never invent tenant-specific values.** Organization names, project
  names, workspace names, and endpoints are configuration, not content —
  keep them as placeholders (`<your-organization>`, `<workspace>`, etc.) in
  anything meant to be reused.
- **Stay anonymous.** This repository is a public template. Never write a
  real customer, employer, workspace, table or person name, an id or a tenant
  URL into any file. Run `python scripts/check_anonymized.py` before
  committing; customer-specific knowledge belongs in a private repository
  (see `docs/knowledge-layer.md`).
- **Never edit a customer repository's local checkout.** Author live in the
  Fabric workspace with `fab` or `fntk`.
- Read before you write. Fetch current state before proposing an update.

## Conventions

- Python 3.10+, type hints on public functions, `pathlib.Path` over string
  paths.
- Azure DevOps descriptions and comments use HTML, not Markdown (see
  `skills/fab-ado-board/SKILL.md`).
- Wiki pages use Markdown.
- Every runner script logs its run to `output/agents/<runner>/runs/` as
  JSON. That directory is gitignored — it's a local audit trail, not
  something to commit.

## Where to look

- `agents/` — who is responsible for what, and their trust boundaries.
- `skills/` — technical how-to for Fabric and Azure DevOps operations.
- `prompts/` — ready-to-run task templates.
- `docs/` — reference material, this repository's architecture and
  `docs/gotchas.md` (known root causes and workarounds).
- `REPO_MAP.md` — one-page index of everything above.

## Adding to this repository

Before adding a new skill, agent, or prompt, read
[`docs/architecture.md`](../docs/architecture.md) so new content lands in
the right layer. Validate new skills with
`python scripts/quick_validate.py skills/<skill-name>` before relying on
them in a workflow.
