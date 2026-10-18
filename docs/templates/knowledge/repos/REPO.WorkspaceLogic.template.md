# <RepoName> workspace logic

> Private. Standing design facts: how the workspace is meant to work, not one-off incidents (those go in `errors/LOG.md`). Agents append discoveries here.

## Conventions

- Naming patterns for notebooks, tables, columns and migrations.
- Metadata columns every table carries and how they are populated.

## Historisation and loading

- How history is kept (SCD pattern), how deletes are handled, how full versus incremental loads are chosen.

## Schema migrations

- How migrations are versioned and ordered, what a new table or column must touch.

## Recurring risk areas

- Places where bugs have repeatedly appeared (mappings, whitelists, joins) and what to check first.
