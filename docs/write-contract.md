# The write contract

Before an agent writes to **any** table or notebook, agree a short *write contract* with the human. It takes a minute and prevents the two expensive mistakes: a rerun that duplicates or destroys data, and a schema change nobody expected.

State it per table (or per notebook that writes), in the plan or the fix proposal:

| Element | Question | Options |
|---|---|---|
| **Permission** | May the agent write at all? | Read-only, or write |
| **Safety pattern** | Where does the first write land? | Iterate **in place in DEV**; work on a **candidate copy** and promote it; or stop at a **staging table** and let a human promote it |
| **Rerun behaviour** | What does a second run do? | **Fail if populated**; **idempotent** on a named key; **append**; **overwrite** |
| **Schema behaviour** | What may change in the schema? | **Locked**; **new columns allowed**; **widening only** |

## Template

```text
Table:        <schema.table>
Permission:   write
Safety:       candidate copy (<table>__candidate) in DEV, promoted in the final full run
Rerun:        idempotent on <business key>
Schema:       new columns allowed, existing columns locked
Evidence:     literal count() and sample output from the session
```

## Rules that go with it

- **Candidate and staging tables are scratch.** Drop them afterwards. A new *permanent* table still goes through your schema and migration notebooks, never an ad-hoc `saveAsTable`.
- **Quote evidence literally.** Paste the `count()` or query output as returned. A paraphrase is how a wrong number reaches a hand-off.
- **The default Lakehouse is not a boundary.** A session can reach any Lakehouse the signed-in user can, so name every target with a 3-part name and check it against your workspace-local binding rule.
- **Production is read-only outside CI/CD.** The contract describes development and test environments.
- The contract is guidance for the agent, not enforcement. Fabric permissions are the real boundary.

Used by [`bugfix-agent`](../agents/bugfix-agent.md) (the proposal phase) and [`delivery-agent`](../agents/delivery-agent.md) (the plan). See also [`fabric-notebook-toolkit`](../skills/fabric-notebook-toolkit/SKILL.md).
