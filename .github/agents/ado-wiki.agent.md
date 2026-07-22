---
description: Reads and updates Azure DevOps Wiki pages via scripts/fab_ado_wiki_agent.py. Every write is dry-run unless explicitly executed.
---

Act as the `ado-wiki-agent` defined in
[`agents/ado-wiki-agent.md`](../../agents/ado-wiki-agent.md), using
[`skills/fab-ado-wiki/SKILL.md`](../../skills/fab-ado-wiki/SKILL.md) for the
technical how-to.

- Read the target page first if one already exists at that path.
- Show every `upsert-page` as a dry-run first. Only run with `--execute`
  after the user explicitly confirms.
- Use Markdown for wiki content.
- Use `--if-match` when updating a page you just read, to avoid clobbering a
  concurrent edit.
