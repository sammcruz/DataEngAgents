# API Patterns

Use this reference when the user needs repeatable `fab api` calls or help translating a REST request into CLI flags.

## Core Mapping

- endpoint -> `fab api <endpoint>`
- method -> `-X`
- audience -> `-A`
- params -> `-P "key=value,key2=value2"`
- headers -> `-H "key=value,key2=value2"`
- input file -> `-i`
- JMESPath filter -> `-q`

## When To Prefer `fab api`

- A first-class `fab` command does not exist.
- A first-class command exists but does not expose the needed option.
- The user already has a REST endpoint and request payload in mind.

## Safe Execution Pattern

1. Build the request spec first.
2. Render the final command without executing it.
3. Review method, endpoint, and mutation risk.
4. Execute only when the command matches the intended operation.

## Helper Script

Use:

```powershell
python scripts/run_api_spec.py .\api-request.json
```

This prints the final command without running it.

To execute the rendered command:

```powershell
python scripts/run_api_spec.py .\api-request.json --execute
```

## JMESPath Patterns

Start by inspecting the raw JSON shape once with no query. In live testing, `fab api` may wrap the REST payload, so confirm the structure before assuming a path.

Select a few fields:

```text
value[].{id:id,name:displayName}
```

Filter by a substring:

```text
value[?contains(displayName, 'Sales')]
```

Return names only:

```text
value[].displayName
```

## Notes

- Prefer request body files over large inline JSON.
- Keep params and headers flat in the request spec unless you know the endpoint accepts structured JSON in the body.
- Use `showHeaders` only when the response headers matter to the task.
- Treat bundled JMESPath examples as starting points. Verify against the actual response shape in the current tenant before hard-coding them.
