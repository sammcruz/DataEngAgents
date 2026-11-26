# Error log

Root causes of past incidents worth remembering. Append dated entries, newest last. Private: keep customer-specific detail here. Lessons that survive anonymisation belong in the public [`docs/gotchas.md`](../../../gotchas.md).

Entry format:

```
## YYYY-MM-DD — <one-line symptom> (<customer>, <item>)

**Status:** verified-live | from-docs | unverified
**Last checked:** YYYY-MM-DD
**Volatile:** tool-version | api | none

**Symptom:** what was observed, with the exact error text.
**Root cause:** the confirmed cause and the evidence that confirmed it.
**Diagnostic:** the fastest check that would have found it.
**Fix:** what was changed, and in which environments.
**General lesson:** what to do next time.
```

Keep this single log until it passes about 25 KB, then move to one file per entry (see [`ENTRY.template.md`](ENTRY.template.md)). Generate `INDEX.md` with `scripts/build_knowledge_index.py`, and read the index before the log. See [`docs/memory-maintenance.md`](../../../memory-maintenance.md).
