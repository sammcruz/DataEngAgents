# Deploy Patterns

Use this reference when the task goes beyond a one-off import and needs a repeatable promotion pattern.

## Typical Promotion Flow

1. Inspect source and destination.
2. Create the local staging directory if it does not already exist.
3. Export to a local staging directory.
4. Import into the target path.
5. Verify the target exists and has the expected properties.

## Path Guidance

- Workspace paths usually look like `ws.Workspace/item.ItemType`.
- Prefer fully qualified item paths during promotion instead of relying on the current `fab cd` context.
- Keep staging directories outside the repo unless the user explicitly wants deployment artifacts checked in.

## Force Flags

- `fab export -f` can bypass confirmation prompts and may export without sensitivity labels.
- `fab import -f` should be used only when replacement behavior is intended, and it is usually required for non-interactive automation.
- If the user did not request overwrite semantics, check `fab exists` first and explain the current target state.

## Manifest Helper

If the user needs a repeatable list of commands for multiple items, use:

```powershell
python scripts/render_manifest.py .\deploy-manifest.json
```

There is a starter manifest at [../assets/deploy-manifest.sample.json](../assets/deploy-manifest.sample.json).

The manifest helper emits:
- `fab exists` for the destination
- `fab export` into a staging directory
- `fab import` into the destination
- `fab get` for post-import verification

In live testing, `fab get` can be less reliable than `fab dir`, `fab desc`, or `fab open` in some Windows terminal contexts. If verification via `get` is noisy, fall back to those commands.

## Recommended Summary

For each item, report:
- source path
- destination path
- staging directory
- whether import was forced
- verification result
