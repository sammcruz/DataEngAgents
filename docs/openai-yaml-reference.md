# `agents/openai.yaml` Reference

This repo follows the same `agents/openai.yaml` conventions as the Codex `skill-creator` skill.

## Example

```yaml
interface:
  display_name: "Optional user-facing name"
  short_description: "Optional user-facing description"
  icon_small: "./assets/small-400px.png"
  icon_large: "./assets/large-logo.svg"
  brand_color: "#3B82F6"
  default_prompt: "Use $skill-name to do the task."
```

## Rules

- Quote all string values.
- Keep keys unquoted.
- `interface.default_prompt` should be a short example prompt and must explicitly mention the skill as `$skill-name`.
- `interface.short_description` should stay between 25 and 64 characters.
- Only include optional fields when they are actually needed.

## Fields

- `interface.display_name`: Human-facing title used in skill lists and chips.
- `interface.short_description`: Short UI blurb for scanning.
- `interface.icon_small`: Relative path to a small icon asset.
- `interface.icon_large`: Relative path to a large icon asset.
- `interface.brand_color`: Hex color for UI accents.
- `interface.default_prompt`: Default prompt snippet inserted when invoking the skill.
