# Notebook Development Patterns

## Directory Structure for Import

Fabric CLI expects notebooks in this exact directory layout:

```
<name>.Notebook/
├── notebook-content.ipynb
└── .platform
```

## Key Differences from Standard Jupyter

1. **Cell metadata**: Every code cell needs `"microsoft": {"language": "python", "language_group": "synapse_pyspark"}`
2. **No kernel state**: When running via `fab job start`, all cells execute top-to-bottom in a fresh session
3. **mssparkutils available**: Token acquisition, secrets, and notebook orchestration utilities are pre-loaded
4. **SparkSession pre-initialized**: `spark` is typically available but explicitly creating it is safer for portability
5. **Cross-lakehouse SQL**: Tables from other lakehouses in the same workspace are accessible via their SQL endpoint name

## Authentication Patterns

## Environment Safety Pattern (write notebooks)

Use a hard guard before any update/rebind/refresh operation:

```python
current_ws = notebookutils.runtime.context.get("currentWorkspaceName")
env = current_ws.split("-")[-1].lower()

if env != "prod":
    raise RuntimeError(
        f"Execution blocked: write operations are allowed only from PROD workspace. Current: {current_ws}"
    )
```

### Workspace Identity (recommended for automation)
```python
token = mssparkutils.credentials.getToken("https://graph.microsoft.com")
token = mssparkutils.credentials.getToken("https://storage.azure.com")
```

### Key Vault Secrets
```python
secret = mssparkutils.credentials.getSecret("https://my-kv.vault.azure.net/", "secret-name")
```

## Table Write Patterns

### Overwrite (daily refresh)
```python
df.write.mode("overwrite").format("delta").option("overwriteSchema", "true").save(path)
```

### Append (incremental)
```python
df.write.mode("append").format("delta").save(path)
```

### Merge/Upsert (SCD)
```python
from delta.tables import DeltaTable
delta_table = DeltaTable.forPath(spark, path)
delta_table.alias("target").merge(
    df.alias("source"), "target.id = source.id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| `InvalidInput` on import | Wrong directory structure or missing `.platform` | Ensure directory is `<name>.Notebook/` with both files |
| `System_Cancelled_Session_Statements_Failed` | Unhandled exception in a cell | Add try/except or fix the logic |
| Token returns 403 | Missing API permissions on workspace identity | Grant permissions in Entra ID |
| `InvalidPath` on import | Notebook path doesn't match existing item | Use `fab ls` to verify exact name |
| Cells run but no output visible | Running via `fab job start` doesn't capture display output | Use `fab job run-status` for pass/fail; open in browser for cell outputs |
