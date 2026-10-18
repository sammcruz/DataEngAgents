# <ClientName>

> Private. Copy this file to your own knowledge repository. Never publish a filled-in copy.

## Engagement

- Purpose and scope in one or two sentences.
- Main contacts and their roles (names live here, never in a public repository).

## Environments

| Environment | Workspace naming pattern | Notes |
|---|---|---|
| Development | `<pattern>` | |
| Test | `<pattern>` | |
| Production | `<pattern>` | Read-only outside CI/CD |

Resolve workspace and item ids by name each session. Do not record them.

## Azure DevOps

- Organization and project: `<organization>` / `<project>`
- Area and iteration path format: `<format>`
- Who work items are assigned to, and how "mine" is defined (often through child tasks).
- Comment style: plain language for non-technical readers, no ids or jargon.

## Git and deployment mechanics

- Which branches map to which environments, and how items reach them.
- Whether the deployment pipeline deploys from git (so live-only fixes are lost).
- Pull request rules: one active PR per branch pair, description length limit, required reviewers.
- How to commit a single item from a busy workspace (selective commit).

## Editing discipline

- Author live in the workspace with `fab` or `fntk`. Never edit the local checkout of this customer's repository.
- Anything not allowed in production, and what needs explicit approval.

## Known constraints

- Shared or parent semantic models this team does not own (edit-restricted).
- Capacity size and region, concurrency limits, anything that has throttled before.
