# Path Patterns

Use this reference when the user needs repeatable filesystem-style Fabric operations.

## Common Shapes

- Workspace item: `ws.Workspace/item.Notebook`
- Lakehouse files root: `ws.Workspace/lh.Lakehouse/Files`
- Lakehouse tables root: `ws.Workspace/lh.Lakehouse/Tables`
- Lakehouse schema path: `ws.Workspace/lh.Lakehouse/Tables/silver`
- Lakehouse Delta table path: `ws.Workspace/lh.Lakehouse/Tables/silver/customers`
- Warehouse table path: `wh.Warehouse/Tables/dbo/table_name`

## Safe File Workflow

1. `fab dir` the source and destination.
2. `fab exists` the exact path before changing it.
3. Render the copy or move command first.
4. Re-run `exists` or `dir` after the change.

## Helper Scripts

Render a single operation:

```powershell
python scripts/render_path_op_spec.py .\path-op.json
```

Execute the rendered operation:

```powershell
python scripts/render_path_op_spec.py .\path-op.json --execute
```

Batch-check a list of paths:

```powershell
python scripts/check_paths.py .\paths.json
```

## Notes

- Use `copy` when you want safer testing.
- Treat `move` and `del` as destructive.
- Check both `/Files` and `/Tables` when discovering a Lakehouse; empty `Files` does not mean the Lakehouse is empty.
- For tables, prefer `fab table schema` over generic file inspection.
- `mkdir` supports Lakehouse directories under `/Files`.
