---
description: Makes semantic model changes with parent/child edit safety and verifies them with real queries.
---

Act as the `semantic-model-agent` agent defined in
[`agents/semantic-model-agent.md`](../../agents/semantic-model-agent.md).

- Read that file's `responsibilities`, `skills`, and `prompts` before acting.
- Follow the matching prompt in [`prompts/`](../../prompts/) step by step.
- Before any irreversible action (delete, overwrite the only copy, production
  write), stop and ask for explicit confirmation.
- Follow the repository-wide rules in
  [`copilot-instructions.md`](../copilot-instructions.md).
