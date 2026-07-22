# Architecture

This repository separates agent context into five layers. Each layer answers
exactly one question. When a piece of content could arguably live in two
layers, it's in the wrong one.

| Layer | Question it answers | Where it lives |
|---|---|---|
| **Docs** | What exists? | `docs/` |
| **Instructions** | What rules must never be broken? | `.github/copilot-instructions.md`, `.github/instructions/` |
| **Agents** | Who is responsible? | `agents/`, `.github/agents/` |
| **Skills** | What specialized knowledge is needed? | `skills/` |
| **Prompts** | What specific action to run? | `prompts/` |

## Why split it this way

A single giant instructions file grows until nobody trusts it: agent-specific
detail buries the global rules, and technology-specific how-to buries both.
Splitting by *question answered* keeps each file skimmable and keeps the
right content loaded for the right task — an agent working on the wiki
doesn't need Fabric workspace architecture in its context window, and a rule
that applies to the whole repo shouldn't be duplicated across every skill.

## How a request flows through the layers

```
 request
    │
    ▼
 agent            (agents/*.md — decides which skill(s) apply)
    │
    ▼
 prompt           (prompts/*.md — the specific action to take)
    │
    ├──▶ skill    (skills/*/SKILL.md — the technical how-to)
    └──▶ docs     (docs/*.md — the specs / reference it needs)
    │
    ▼
 instructions     (.github/copilot-instructions.md — always applied)
    │
    ▼
 final context assembled for the model
```

## Layer definitions

### Docs — what exists

Reference material and specs: what a runner does, what an API returns, how a
config file is shaped. Docs describe **what**, never **how** — the how
belongs in a skill.

### Instructions — what rules must never be broken

Global policy that applies across the whole repository: the dry-run-by-default
rule, credential handling, coding conventions. If it only applies to one
skill or one agent, it doesn't belong here — see
[`.github/copilot-instructions.md`](../.github/copilot-instructions.md).

### Agents — who is responsible

Role definitions: scope, escalation path, which skills and prompts an agent
is allowed to reach for. An agent coordinates; it doesn't teach — technical
detail here is a sign it should move to a skill.

### Skills — what specialized knowledge is needed

Reusable, technology-specific expertise: API shapes, CLI commands, patterns
and guardrails. A skill should serve many prompts. If a piece of knowledge
only makes sense for one narrow task, it's a prompt, not a skill.

### Prompts — what action to run

Task templates: input expected, workflow steps, success criteria. A prompt
describes an **action**, not a technology — "document completed work", not
"use HTML `<h3>` tags in Azure DevOps descriptions" (that belongs in the
skill the prompt references).

## Anti-patterns

| Symptom | Fix |
|---|---|
| A skill name-checks a specific work item ID or wiki path | Move the specific case into a prompt; keep the skill general |
| An agent file explains an API request shape | Move it to the relevant skill |
| A global instruction only makes sense for one skill | Move it into that skill's `SKILL.md` |
| A doc tells the agent *how* to do something, not *what exists* | Move the how-to into a skill |

## Applying this to a new integration

1. Does the *rule* apply everywhere? → `.github/copilot-instructions.md` (or
   `.github/instructions/*.instructions.md` if it's scoped to a path).
2. Does the *knowledge* serve many future tasks? → a new skill under
   `skills/`.
3. Does someone need to be *responsible* for it, with a defined trust
   boundary for writes? → a new agent under `agents/` (and optionally
   `.github/agents/*.agent.md` so it's selectable in GitHub Copilot).
4. Is it a *specific, repeatable action*? → a new prompt under `prompts/`.
5. Is it *reference material* someone would look up, not follow step by
   step? → a new doc under `docs/`.
