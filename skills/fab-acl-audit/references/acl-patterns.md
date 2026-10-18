# ACL Patterns

Use this reference when the user needs a repeatable way to inspect or modify ACLs with `fab`.

## Read-First Pattern

1. Run `fab acl dir <path>` or `fab acl get <path>`.
2. Summarize the current principals and roles.
3. Render the intended `set` or `del` command before executing it.
4. Re-read ACLs after any change.

## Workspace Roles

For workspaces, `fab acl set` accepts:
- `Admin`
- `Member`
- `Contributor`
- `Viewer`

Use:

```powershell
fab acl set "ws.Workspace" -I "<objectId>" -R Viewer -f
```

## Removal Pattern

Use:

```powershell
fab acl del "ws.Workspace" -I "<upn-or-objectId>" -f
```

## Helper Script

Render a request from JSON:

```powershell
python scripts/render_acl_spec.py .\acl-request.json
```

Execute only after review:

```powershell
python scripts/render_acl_spec.py .\acl-request.json --execute
```

## Notes

- Use `force` for non-interactive automation.
- Prefer principal-specific changes over broad role churn.
- In live testing, `fab acl dir "Test123.Workspace"` returned `admin@example.com` with role `Admin`.
