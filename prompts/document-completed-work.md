---
name: document-completed-work
description: Close the loop on a finished task by updating its Azure DevOps work item and, if relevant, the team wiki.
---

# Document Completed Work

## Action

Given a work item that has been completed, produce two things and propose
them as dry-run previews before anything is written:

1. A short **description update** — what was implemented, in 2-4 sentences.
2. A detailed **comment** — implementation specifics: what changed, what was
   validated, and how (counts, run IDs, links).

If the work also changed something a reader would need to find later
(a new pattern, a config, a gotcha), also propose a wiki page update.

## Input

- A work item ID.
- A summary of what was done (from the conversation, a diff, or a run log).

## Workflow

1. Read the current work item (`ado-board-agent`, `get`) so the update is
   additive, not a guess.
2. Draft the description and comment (HTML, per
   `skills/fab-ado-board/SKILL.md`).
3. Show both as dry-run output for review.
4. On confirmation, execute the board update.
5. If a wiki page is warranted, repeat the same dry-run-then-confirm pattern
   with `ado-wiki-agent`.

## Success Criteria

- Description stays brief; details live in the comment (comments carry
  timestamp/author history, descriptions don't).
- Every write was shown as a dry-run and explicitly confirmed before
  `--execute`.
- No PAT, tenant name, or other placeholder-only value leaks into the
  published text.
