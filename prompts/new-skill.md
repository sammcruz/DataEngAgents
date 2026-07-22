---
name: new-skill
description: Scaffold and validate a new skill so it follows the same contract as the skills already in this repository.
---

# New Skill

## Action

Add a new skill to `skills/` that pulls its weight across many future
prompts — not a one-off task dressed up as a skill.

## Input

- A skill name (hyphen-case).
- A one- or two-sentence description of when the skill applies.

## Workflow

1. Ask: does this knowledge serve **many** future prompts? If it only
   applies to one narrow task, write a prompt instead (see
   `prompts/`) — not a skill.
2. Scaffold it:

   ```bash
   python scripts/init_skill.py <skill-name> --path skills
   ```

3. Fill in the `SKILL.md` TODOs: when to use it, the workflow, concrete
   commands/examples, and guardrails.
4. Keep tenant-specific values (org names, endpoints, credentials) out of
   the skill doc — put them in a config file with placeholder values, the
   way `skills/fab-ado-board/fab-ado-board.config.json` does.
5. Validate:

   ```bash
   python scripts/quick_validate.py skills/<skill-name>
   ```

6. Hand off to [`governance-agent`](../agents/governance-agent.md) for a
   final review against `docs/architecture.md`.

## Success Criteria

- `quick_validate.py` passes.
- No technical HOW leaked into an agent file, and no role/responsibility
  language leaked into the skill file.
- No secret, PAT, or tenant-specific literal value anywhere in the skill.
