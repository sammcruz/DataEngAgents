# The knowledge layer (keep it private)

The five layers in [`architecture.md`](architecture.md) describe **reusable** context, so they can live in a public template. Real engagements also generate context that must never be public: customer and environment names, workspace maps, incident history, board conventions. This is a sixth layer, kept apart on purpose.

| Layer | Question it answers | Where it lives |
|---|---|---|
| **Knowledge** | What is true about *this* customer, repository or environment? | A **private** repository next to this one, laid out like [`templates/knowledge/`](templates/knowledge/) |

## Layout

```
knowledge/
├── clients/<ClientName>.md             environment naming, board and git conventions, editing discipline
├── repos/<RepoName>.md                 what the repository is, entry points, where its docs live
├── repos/<RepoName>.WorkspaceMap.md    which notebook or table lives where, by layer
├── repos/<RepoName>.WorkspaceLogic.md  why it works that way: conventions, recurring risk areas
├── decisions/LOG.md                    durable, dated, cross-project decisions
└── errors/LOG.md                       root causes of past incidents worth remembering
```

Empty templates for every file are in [`templates/knowledge/`](templates/knowledge/). Copy that folder into your private repository and fill it in.

## How agents use it

- The [`repo-orientation`](../skills/repo-orientation/SKILL.md) skill reads `knowledge/repos/<RepoName>.md` before exploring an unfamiliar repository.
- The workflow agents read `clients/` and `repos/` before an investigation, and `errors/LOG.md` before re-diagnosing a known failure.
- At the end of a task, agents are asked to append what they learned to the right file, so the next session does not rediscover it: a standing design fact goes to `repos/`, a specific incident to `errors/LOG.md`, a cross-project decision to `decisions/LOG.md`.

## Rules

1. **Never copy knowledge files into this public repository.** The generic lessons that survive anonymisation belong in [`gotchas.md`](gotchas.md) instead.
2. **No secrets even in the private repository.** Resolve ids by name each session instead of recording them. See [`standing-instructions.template.md`](standing-instructions.template.md) for a pre-commit secrets check.
3. **Record the reasoning, not only the rule.** A decision log entry that says why survives a change of mind.
