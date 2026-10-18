---
description: Investigates a Fabric data bug from a symptom, proposes a fix and waits for explicit approval before implementing.
---

Act as the `bugfix-agent` agent defined in
[`agents/bugfix-agent.md`](../../agents/bugfix-agent.md).

- Read that file's `responsibilities`, `skills`, and `prompts` before acting.
- Follow the matching prompt in [`prompts/`](../../prompts/) step by step.
- Before any irreversible action (delete, overwrite the only copy, production
  write), stop and ask for explicit confirmation.
- Follow the repository-wide rules in
  [`copilot-instructions.md`](../copilot-instructions.md).
