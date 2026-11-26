# Memory maintenance

Appending lessons to a knowledge base is the easy half. Left alone, it grows until nobody can find anything, old notes go stale, and a wrong note is carried into every session. This page is the other half: keeping the knowledge layer small, indexed and true.

It follows the model in Anthropic's article [The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory): memory is written quickly during work, then **reorganised offline with hindsight** (the article calls this *dreaming*), and what is loaded into every session stays small.

## The layers, mapped to this repository

| Layer | What it is here | Rule |
|---|---|---|
| **Transcripts** | Your agent's session history | Ground truth. Use it to check a note, not as a place to look things up |
| **Memory notes** | Entries in the private `errors/` and `decisions/` logs, written at the end of a task | Written fast, with a status (below) |
| **Representations** | Per-customer and per-repository pages, and anonymised write-ups such as [`gotchas.md`](gotchas.md) | Built by the review pass, not by hand under time pressure |
| **Injected context** | The user-level instruction file and the auto-memory index | Always loaded. Keep it **under 200 lines and about 25 KB**, link to detail instead of copying it |

## What goes wrong without maintenance

- **The log outgrows its use.** A single log of 100 KB or more costs tokens every time an agent "checks the log" before diagnosing. An index lets it scan one line per entry and open only the match.
- **Old notes go stale.** Tool-version and API gotchas are true until the next release. A note that is wrong gets reused with full confidence.
- **Corrections pile up as new entries,** while the original wrong claim stays in place and keeps being found first.
- **Parallel agents overwrite each other** when they all append to one file. Several agents writing to one shared page lost 16 of 57 facts in the article's experiment, and giving each subject its own page kept all 57.
- **A summary that abstracts nothing is not a summary.** A wiki larger than its sources only adds a second place to be wrong.

## What to do

1. **Give every entry a status.** Three fields, all optional but worth always filling:

   ```text
   Status: verified-live | from-docs | unverified
   Last checked: YYYY-MM-DD
   Volatile: tool-version | api | none
   ```

   *verified-live* means someone reproduced it. *from-docs* means it was read, not run. *unverified* means a hypothesis. Mark anything tied to a tool release or an API as volatile.
2. **Keep an index.** Generate `errors/INDEX.md` and `decisions/INDEX.md` with [`scripts/build_knowledge_index.py`](../scripts/build_knowledge_index.py). Agents read the index first: one line per entry, newest first, with a "due for review" list on top.
3. **One file per entry once the log passes about 25 KB.** Put them in `errors/entries/YYYY-MM-DD-slug.md` using [`ENTRY.template.md`](templates/knowledge/errors/ENTRY.template.md). Per-entry files cannot clobber each other, and the index links straight to them. Customer and repository pages should likewise hold one subject each.
4. **Correct in place.** When a note turns out wrong, fix the note, set its status and date, and add one line saying what changed. Do not leave the wrong claim standing with a correction elsewhere.
5. **Run a review pass on a schedule** (weekly or monthly) with the [`memory-review`](../prompts/memory-review.md) prompt. It rechecks volatile and unverified entries against the real tool or API, merges duplicates, fixes broken links, and promotes lessons that keep recurring into a skill or an anonymised write-up.
6. **Check the budget.** `python scripts/build_knowledge_index.py <knowledge-dir> --check --injected <your-instruction-file>` fails when an index is stale, a file is over its size budget, or an always-loaded file is too long. Wire it into a pre-commit hook in the private repository.

## Guidance for the agent that writes notes

- Tell the agent **what memory is for** ("so the next session does not rediscover this") and let it judge what is worth saving. A rule such as "only record failures" costs more than it saves on capable models.
- Weaker or smaller models do better with explicit steps: read the index first, state a hypothesis, test it, then write down the rule together with the evidence.
- Record **evidence and warnings about traps**, not only the answer. Prefer the rule, the proof and what to check next time over the story of the incident.
- Do not store what is visible from the code or the current state. Store what took effort to find out.

## Evaluating it

Keep a handful of past incidents with known root causes. Replay them with the knowledge layer enabled and with it removed, and compare how many are solved and how many tool calls it takes. If the gap closes, the notes are not earning their size and the review pass should trim them.

## Safety

- The review pass **proposes** changes as a pull request or a diff. It does not push to a customer repository, and it never copies a secret.
- Anything promoted to a public repository goes through the anonymisation check ([`scripts/check_anonymized.py`](../scripts/check_anonymized.py)) first.
