---
name: fab-api-bridge
description: Use this skill when a Fabric task needs direct REST API access through fab-cli, especially for endpoints or filters not covered well by first-class fab commands, or when you need JMESPath queries, headers, params, or audience selection.
---

# Fab Api Bridge

## Use

Use this skill as the escape hatch for advanced Fabric workflows through `fab api`. It is best when the user wants direct endpoint access while still benefiting from `fab` authentication, output formatting, and JMESPath filtering.

Read [references/api-patterns.md](references/api-patterns.md) when the request needs a reusable API shape or translation from REST concepts into `fab api` flags. Use [scripts/run_api_spec.py](scripts/run_api_spec.py) when the user wants a dry-run command generated from a JSON spec. Point users to [assets/api-request.sample.json](assets/api-request.sample.json) as a starter template.

## Workflow

1. Prefer a first-class `fab` command when it exists and is adequate.
2. Switch to `fab api` only when the CLI command surface is missing or too limited.
3. Use `fab api` deliberately when the task needs REST-only item metadata, folder metadata, or other fields that the first-class command surface does not expose reliably in the current host.
4. Build the endpoint, method, params, headers, audience, and body explicitly.
5. Inspect one raw response before locking in a `-q` expression, because `fab api` may wrap the payload.
6. Summarize the request and the relevant response fields rather than dumping raw JSON unless the user asked for it.

## Response Shape Tip

`fab api` often wraps the actual API payload in an envelope like:

```json
{
  "status_code": 200,
  "text": {
    "value": []
  }
}
```

That means JMESPath filters often need to start from `text`, for example `text.value[]`, rather than `value[]`.

## Commands

Simple GET:

```powershell
fab api workspaces -X get
```

GET with params and filtering:

```powershell
fab api "workspaces" -X get -P "continuationToken=abc" -q "text.value[].{id:id,name:displayName}"
```

Inspect workspace items when `fab get` or folder-aware discovery is flaky in the current terminal host:

```powershell
fab api "workspaces/<workspace-id>/items" -X get -q "text.value[].{id:id,name:displayName,type:type}"
```

POST with a JSON body:

```powershell
fab api "some/endpoint" -X post -i ".\\request.json"
```

Audience override:

```powershell
fab api "storage/endpoint" -X get -A storage
```

Render a `fab api` call from a JSON spec:

```powershell
python scripts/run_api_spec.py .\api-request.json
```

Execute the rendered command only when the request is confirmed:

```powershell
python scripts/run_api_spec.py .\api-request.json --execute
```

## Guardrails

- Be explicit about method and audience.
- If request payload size or quoting is awkward, prefer a file path for `-i` over inline JSON.
- Use `--show_headers` only when headers matter to the task.
- If the endpoint mutates data, state that clearly before executing.
- Prefer the spec helper for repeated or complex calls so the request is reviewable before execution.
- When a JMESPath query unexpectedly returns `None`, retry against the wrapped payload shape, usually `text.value[...]`.
- Do not treat `fab api` as a substitute for querying Delta table contents. It is best for Fabric item and workspace metadata, not for direct business-data validation inside Lakehouse tables.
- If the user needs row counts, lane timing, or data-quality checks from loaded tables, prefer a notebook or SQL-based validation step over forcing `fab api` into that role.

## Output

- Show the final `fab api` command with method, endpoint, and notable options.
- Summarize the response shape and key fields in a compact visual structure.
- If a first-class `fab` command would be better, say so and prefer it.
- If `fab api` is still not the right surface for the requested validation, say so explicitly and recommend the better validation surface.
