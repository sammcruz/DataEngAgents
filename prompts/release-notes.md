---
name: release-notes
description: Roll up a sprint's Azure DevOps activity into a wiki release-notes page.
---

# Release Notes

## Action

Build a scannable sprint summary page from board data. Run by the [`release-notes-agent`](../agents/release-notes-agent.md).

## Input

- A sprint or iteration. If none is given, ask which one.

## Workflow

1. Query the sprint's user stories and bugs with WIQL (`fab-ado-board`).
2. Apply the team's **actual** ownership rule. A story often counts as yours if **any child task** is assigned to you, so check tasks and roll up instead of filtering on the story's `AssignedTo`.
3. For each item, keep the touched-artifact list short: bullets of Fabric artifacts changed, not prose.
4. Write or update the wiki page with `fab-ado-wiki`, showing status as a colour or label rather than a sentence. Preview first (dry-run).
5. Confirm the roll-up with the human before treating it as final.

## Success Criteria

- The page is scannable at a glance.
- The ownership rule was confirmed, not assumed.
