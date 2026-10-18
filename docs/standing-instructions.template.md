# Standing instructions (template)

A starting point for the user-level instruction file your agent loads in every session (for example `~/.claude/CLAUDE.md`, or the equivalent in your tool). Copy it, replace the placeholders and keep your own version private.

```markdown
# Standing instructions

## Who you're working with

<Name> is a <role> working across several customer engagements. Reusable knowledge applies across all of them.

## Where knowledge lives

- **Repository map:** `REPO_MAP.md` in the agents repository is a one-page index of every agent, prompt, skill and doc. Read it before searching.
- **Skills:** installed from the agents repository and from Microsoft's `skills-for-fabric`. They surface when relevant.
- **Repository orientation:** before non-trivial work in an unfamiliar repository, check `knowledge/repos/<RepoName>.md` in the private knowledge repository.
- **Customer context:** environment naming and board conventions live in `knowledge/clients/<ClientName>.md`.
- **Past decisions and known gotchas:** `knowledge/decisions/LOG.md` and `knowledge/errors/LOG.md`. Check them before re-deciding or re-diagnosing.

## Working style

- Prefer editing an existing skill or agent over writing a one-off instruction when the knowledge is reusable.
- At the end of any task that produced a new, non-obvious learning (a mistake corrected, a root cause, a gotcha, a durable decision), update the right knowledge file yourself, then mention it briefly in the wrap-up. Do not wait to be asked.

## Never touch a customer repository's local checkout

For any customer repository, never edit, commit or push against the local git checkout. Author live in the Fabric workspace with `fab` or `fntk`, and sync to git through Fabric Git integration. Do not run tools that write into customer checkouts (for example `fntk init`).

## Secrets check before every commit

Before committing, review the staged diff (`git diff --staged`) for anything that looks like a live credential: personal access tokens, connection strings, private keys (`-----BEGIN`), passwords, JWTs, client secrets, or a bare secret-shaped string in a config or knowledge file. If anything looks live, do not commit. Report what you found and where, and let the human decide.

For repositories meant to be public, also run the anonymisation check:

    python scripts/check_anonymized.py

## Auto-commit (private knowledge repository only)

In the private knowledge repository, edits may be committed and pushed without asking each time, after the secrets check above. This never applies to customer repositories.
```
