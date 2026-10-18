---
name: repo-orientation
description: Use when starting non-trivial work in a project repository for the first time in a session, or when the repository's purpose and structure aren't obvious from context. Checks your private knowledge base for an existing orientation summary before exploring from scratch.
---

# Repo Orientation

Before spending exploration budget re-deriving a project repository's purpose and structure, check whether `knowledge/repos/<RepoName>.md` already has a short summary. The file is named after the repository's directory name.

If a summary exists: read it first, then explore further only for what the task actually needs.

If no summary exists and the repository turns out to be a real, recurring project (not a one-off scratch task): after finishing the task, suggest creating a short summary in `knowledge/repos/<RepoName>.md` so future sessions don't re-derive the same context. Keep it short: what the repository is, its key entry points, and where its own docs live. Do not write exhaustive documentation.

When the work is tied to a specific customer engagement, also check `knowledge/clients/<ClientName>.md` for environment naming conventions and tooling context.

## Keep the knowledge base private

`knowledge/` holds real customer names, environment names and incident history, so it belongs in a **private** repository next to this one, never in this public template. See [`docs/knowledge-layer.md`](../../docs/knowledge-layer.md) for the layout and empty templates.
