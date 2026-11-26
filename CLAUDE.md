@AGENTS.md

## Claude Code notes

- Skills, agents and prompts load from `.claude/skills`, `.claude/agents` and
  `.claude/commands`, which are symlinks to `skills/`, `agents/` and
  `prompts/`. Edit the real folders, never the links.
- The same content is packaged as the `dataengagents` plugin
  (`.claude-plugin/plugin.json`). Keep the manifest in sync when you add a
  top-level component folder; individual skills, agents and prompts are picked
  up automatically.
- Slash commands from the plugin are namespaced, for example
  `/dataengagents:fix-bug`; inside this repo the bare names also work.
