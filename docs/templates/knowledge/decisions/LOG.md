# Decision log

Durable, cross-project decisions worth remembering the reasoning behind. Append dated entries, newest last. Private: keep it in your own knowledge repository.

Entry format:

```
## YYYY-MM-DD — <decision in one line>

**Context:** what forced the decision.
**Decision:** what was chosen.
**Why:** the reasoning, and what was rejected.
**Consequences:** what this changes from now on.
```

---

## Examples (generic, safe to delete)

## 2026-01-01 — Workspace-first editing for customer repositories

**Context:** agents repeatedly edited a customer's local git checkout, which mixes the fix with unrelated uncommitted drift from the workspace.
**Decision:** author live in the Fabric workspace with `fab` or `fntk`, validate there, and sync to git through Fabric Git integration with a selective commit. Never edit the local checkout.
**Why:** the workspace is the source of truth, and a selective commit proves only the intended items shipped.
**Consequences:** every agent definition carries the rule as a hard rule.

## 2026-01-01 — A workspace fix does not fix a pipeline that deploys from git

**Context:** a validated live fix did not make the CI/CD pipeline succeed on retry.
**Decision:** agents state explicitly whether a fix is workspace-only, committed or deployed, and never invite a retry before the fix is in git.
**Why:** the pipeline deploys whatever is checked out of the branch.
**Consequences:** the pipeline agent reads the deploy script once per engagement and records where it deploys from.

## 2026-01-01 — Re-verify from a primary source when observations conflict

**Context:** a human saw bad data after an agent had reported a clean validation.
**Decision:** when a human's observation conflicts with an agent's self-reported validation, re-check against the real table or log before answering either side.
**Why:** both were true at the time (the SQL endpoint had not yet synced), and trusting either blindly wasted a cycle.
**Consequences:** validation after a recent write goes through Spark, not the SQL analytics endpoint.
