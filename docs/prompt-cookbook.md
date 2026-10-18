# Prompt Cookbook

<p align="center">
  <strong>Copy-paste prompt recipes for real Fabric work.</strong><br>
  Built so teammates can scan, steal, and use a prompt in seconds.
</p>

<p align="center">
  <a href="#before-you-start"><strong>Before You Start</strong></a> ·
  <a href="#recipe-index"><strong>Recipe Index</strong></a> ·
  <a href="#setup"><strong>Setup</strong></a> ·
  <a href="#permissions"><strong>Permissions</strong></a>
</p>

---

## Before You Start

<table>
  <tr>
    <td width="33%" valign="top">
      <h3>Codex</h3>
      <p>Use <code>$skill-name</code>.</p>
      <p>Example: <code>$fab-job-ops</code></p>
    </td>
    <td width="33%" valign="top">
      <h3>GitHub Copilot</h3>
      <p>Use <code>/skill-name</code>.</p>
      <p>Example: <code>/fab-job-ops</code></p>
    </td>
    <td width="33%" valign="top">
      <h3>Always Replace</h3>
      <p>Swap in your own workspace names, item names, table names, and paths before running anything.</p>
    </td>
  </tr>
</table>

> A strong Fabric prompt usually names the skill, the exact path or workspace, the desired action, and any safety rule like "dry run first" or "do not execute yet."

---

## Recipe Index

<table>
  <tr>
    <td width="25%" valign="top"><a href="#setup"><strong>Setup</strong></a><br>Install, sign in, repair PATH</td>
    <td width="25%" valign="top"><a href="#discovery"><strong>Discovery</strong></a><br>Inspect workspaces and items</td>
    <td width="25%" valign="top"><a href="#semantic-models"><strong>Semantic Models</strong></a><br>Improve and document models</td>
    <td width="25%" valign="top"><a href="#deployments"><strong>Deployments</strong></a><br>Promote safely between environments</td>
  </tr>
  <tr>
    <td width="25%" valign="top"><a href="#jobs"><strong>Jobs</strong></a><br>Run, monitor, and explain failures</td>
    <td width="25%" valign="top"><a href="#onelake"><strong>OneLake</strong></a><br>Inspect files, tables, and paths</td>
    <td width="25%" valign="top"><a href="#architecture"><strong>Architecture</strong></a><br>Design and audit single-workspace or per-stage layouts</td>
    <td width="25%" valign="top"><a href="#apis"><strong>APIs</strong></a><br>Bridge into REST workflows</td>
    <td width="25%" valign="top"><a href="#permissions"><strong>Permissions</strong></a><br>Review ACLs before changing access</td>
  </tr>
</table>

---

## Setup

### Install Fabric CLI and sign in

Codex:

```text
Use $fab-bootstrap to install Fabric CLI, fix PATH if needed, and help me log in with user auth.
```

GitHub Copilot:

```text
Use the /fab-bootstrap skill to install Fabric CLI, fix PATH if needed, and help me log in with user auth.
```

### Repair PATH for an existing install

Codex:

```text
Use $fab-bootstrap to check my current fab installation and repair PATH only.
```

GitHub Copilot:

```text
Use the /fab-bootstrap skill to check my current fab installation and repair PATH only.
```

---

## Discovery

### Inspect a workspace

Codex:

```text
Use $fab-discovery to inspect Analytics Dev.Workspace and summarize the items I can work with.
```

GitHub Copilot:

```text
Use the /fab-discovery skill to inspect Analytics Dev.Workspace and summarize the items I can work with.
```

### Check which commands are relevant for an item

Codex:

```text
Use $fab-discovery to inspect Test123.Workspace/nb_silver_customers.Notebook and tell me which fab commands are relevant.
```

GitHub Copilot:

```text
Use the /fab-discovery skill to inspect Test123.Workspace/nb_silver_customers.Notebook and tell me which fab commands are relevant.
```

---

## Semantic Models

### Improve an open Power BI Desktop model end-to-end

Codex:

```text
Use $fab-semantic-model to connect to my open Power BI Desktop model through the Power BI Modeling MCP Server, improve the semantic model safely end-to-end, and return a Markdown documentation pack with rename mappings, hidden technical fields, measures created, hierarchy changes, and all skipped risky items.
```

GitHub Copilot:

```text
Use the /fab-semantic-model skill to connect to my open Power BI Desktop model through the Power BI Modeling MCP Server, improve the semantic model safely end-to-end, and return a Markdown documentation pack with rename mappings, hidden technical fields, measures created, hierarchy changes, and all skipped risky items.
```

### Review a Fabric semantic model before making changes

Codex:

```text
Use $fab-semantic-model to connect to the semantic model Sales Analytics in workspace Analytics Dev through the Power BI Modeling MCP Server, assess star schema quality, naming, measures, folders, and descriptions, and separate safe direct fixes from risky recommendations before changing anything.
```

GitHub Copilot:

```text
Use the /fab-semantic-model skill to connect to the semantic model Sales Analytics in workspace Analytics Dev through the Power BI Modeling MCP Server, assess star schema quality, naming, measures, folders, and descriptions, and separate safe direct fixes from risky recommendations before changing anything.
```

---

## Deployments

### Promote a notebook into Test

Codex:

```text
Use $fab-deploy to export Analytics Dev.Workspace/nb_silver_customers.Notebook and import it into Test123.Workspace with overwrite safety checks.
```

GitHub Copilot:

```text
Use the /fab-deploy skill to export Analytics Dev.Workspace/nb_silver_customers.Notebook and import it into Test123.Workspace with overwrite safety checks.
```

### Generate commands from a deployment manifest

Codex:

```text
Use $fab-deploy to turn this deployment manifest into fab commands and explain what each step does.
```

GitHub Copilot:

```text
Use the /fab-deploy skill to turn this deployment manifest into fab commands and explain what each step does.
```

---

## Jobs

### Inspect recent pipeline runs

Codex:

```text
Use $fab-job-ops to inspect the latest runs of Analytics Dev.Workspace/pl-main.DataPipeline and summarize failures or recent issues.
```

GitHub Copilot:

```text
Use the /fab-job-ops skill to inspect the latest runs of Analytics Dev.Workspace/pl-main.DataPipeline and summarize failures or recent issues.
```

### Start a notebook and watch it finish

Codex:

```text
Use $fab-job-ops to start Test123.Workspace/nb_silver_customers.Notebook, monitor the run, and tell me the final status.
```

GitHub Copilot:

```text
Use the /fab-job-ops skill to start Test123.Workspace/nb_silver_customers.Notebook, monitor the run, and tell me the final status.
```

---

## OneLake

### Check whether a set of paths exists

Codex:

```text
Use $fab-onelake-ops to check whether these Test123 lakehouse paths exist and summarize what is missing.
```

GitHub Copilot:

```text
Use the /fab-onelake-ops skill to check whether these Test123 lakehouse paths exist and summarize what is missing.
```

### Inspect files and tables in a lakehouse

Codex:

```text
Use $fab-onelake-ops to inspect Test123.Workspace/lakehouse.Lakehouse/Files and Test123.Workspace/lakehouse.Lakehouse/Tables and explain the current structure.
```

GitHub Copilot:

```text
Use the /fab-onelake-ops skill to inspect Test123.Workspace/lakehouse.Lakehouse/Files and Test123.Workspace/lakehouse.Lakehouse/Tables and explain the current structure.
```

---

## Architecture

### Design a single-workspace medallion layout

Codex:

```text
Use $fab-workspace-architecture to propose a single-workspace Fabric architecture with one lakehouse, bronze/silver/gold schemas, and clear folders for notebooks, pipelines, and shared assets.
```

GitHub Copilot:

```text
Use the /fab-workspace-architecture skill to propose a single-workspace Fabric architecture with one lakehouse, bronze/silver/gold schemas, and clear folders for notebooks, pipelines, and shared assets.
```

### Design a per-stage workspace layout

Codex:

```text
Use $fab-workspace-architecture to propose a Fabric architecture with separate Dev, Test, and Prod workspaces, explain what belongs in each stage, and show how notebooks, pipelines, lakehouses, and deployment flow should be organized.
```

GitHub Copilot:

```text
Use the /fab-workspace-architecture skill to propose a Fabric architecture with separate Dev, Test, and Prod workspaces, explain what belongs in each stage, and show how notebooks, pipelines, lakehouses, and deployment flow should be organized.
```

### Audit an existing workspace against the pattern

Codex:

```text
Use $fab-workspace-architecture to inspect Analytics Dev.Workspace and tell me where it violates a one-lakehouse bronze/silver/gold architecture.
```

GitHub Copilot:

```text
Use the /fab-workspace-architecture skill to inspect Analytics Dev.Workspace and tell me where it violates a one-lakehouse bronze/silver/gold architecture.
```

---

## APIs

### Inspect a Fabric API response safely

Codex:

```text
Use $fab-api-bridge to call the workspaces endpoint, inspect the response shape, and then suggest a good query for just the names and IDs.
```

GitHub Copilot:

```text
Use the /fab-api-bridge skill to call the workspaces endpoint, inspect the response shape, and then suggest a good query for just the names and IDs.
```

### Build a reusable API spec

Codex:

```text
Use $fab-api-bridge to create a JSON request spec for this Fabric API call and render the final fab api command before executing it.
```

GitHub Copilot:

```text
Use the /fab-api-bridge skill to create a JSON request spec for this Fabric API call and render the final fab api command before executing it.
```

---

## Permissions

### Inspect workspace access

Codex:

```text
Use $fab-acl-audit to inspect the ACLs on Test123.Workspace and summarize who has which role.
```

GitHub Copilot:

```text
Use the /fab-acl-audit skill to inspect the ACLs on Test123.Workspace and summarize who has which role.
```

### Prepare a safe permission change

Codex:

```text
Use $fab-acl-audit to inspect the current ACLs, then render the command I would use to grant Viewer access to a specific user without executing it yet.
```

GitHub Copilot:

```text
Use the /fab-acl-audit skill to inspect the current ACLs, then render the command I would use to grant Viewer access to a specific user without executing it yet.
```

---

## Simple Rules That Help

- Start with discovery if you are unsure about a path or item.
- Ask for a dry run before copy, move, delete, import, or ACL changes.
- For API work, inspect one raw response before writing a query.
- For job work, look at recent runs before restarting workloads.
