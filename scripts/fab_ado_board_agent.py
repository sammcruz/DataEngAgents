#!/usr/bin/env python3
"""
Fab ADO Board Agent

A lightweight, real agent runner for the `fab-ado-board` skill that can:
- read work items
- read comments
- run WIQL queries
- batch-fetch work items
- add comments (dry-run by default)
- update work items via JSON patch (dry-run by default)
- execute multi-step plan files

Usage examples:
  python scripts/fab_ado_board_agent.py get --id 123
  python scripts/fab_ado_board_agent.py comments --id 123 --top 20
  python scripts/fab_ado_board_agent.py wiql --query-file /tmp/query.wiql --fetch-details
  python scripts/fab_ado_board_agent.py add-comment --id 123 --text-file /tmp/comment.html --execute
  python scripts/fab_ado_board_agent.py update --id 123 --patch-file /tmp/patch.json --execute
  python scripts/fab_ado_board_agent.py plan --plan-file /tmp/ado-plan.json --execute
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

import requests
from requests.auth import HTTPBasicAuth

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = REPO_ROOT / "skills" / "fab-ado-board" / "fab-ado-board.config.json"
DEFAULT_SKILL_PATH = REPO_ROOT / "skills" / "fab-ado-board" / "SKILL.md"
DEFAULT_RUN_LOG_DIR = REPO_ROOT / "output" / "agents" / "fab-ado-board" / "runs"

WORK_ITEM_API_VERSION = "7.1"
COMMENTS_API_VERSION = "7.1-preview.4"


class AgentError(RuntimeError):
    """Raised for expected operational errors."""


@dataclass
class AdoConfig:
    organization: str
    project: str
    pat: str

    @property
    def base_url(self) -> str:
        return f"https://dev.azure.com/{self.organization}/{self.project}/_apis"


class FabAdoBoardAgent:
    def __init__(
        self,
        config: AdoConfig,
        timeout_seconds: int = 60,
        skill_doc_path: Optional[Path] = None,
    ) -> None:
        self.config = config
        self.timeout_seconds = timeout_seconds
        self.skill_doc_path = skill_doc_path
        self._auth = HTTPBasicAuth("", self.config.pat)

    def get_skill_summary(self) -> Dict[str, Any]:
        """Load basic metadata from SKILL.md to prove skill-bound behavior."""
        if not self.skill_doc_path:
            return {"loaded": False}
        if not self.skill_doc_path.exists():
            return {"loaded": False, "path": str(self.skill_doc_path), "reason": "missing"}

        content = self.skill_doc_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        name = None
        description = None
        if lines and lines[0].strip() == "---":
            for line in lines[1:40]:
                if line.strip() == "---":
                    break
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip()
                if line.startswith("description:"):
                    description = line.split(":", 1)[1].strip()

        return {
            "loaded": True,
            "path": str(self.skill_doc_path),
            "name": name,
            "description": description,
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        url = f"{self.config.base_url}/{endpoint.lstrip('/')}"
        response = requests.request(
            method=method,
            url=url,
            auth=self._auth,
            params=params,
            json=json_body,
            headers=headers,
            timeout=self.timeout_seconds,
        )

        if not response.ok:
            body_preview = response.text[:2000]
            raise AgentError(
                f"ADO API {method} {url} failed: {response.status_code}\n{body_preview}"
            )

        if not response.text:
            return {}

        try:
            return response.json()
        except ValueError:
            return {"raw": response.text}

    def get_work_item(self, work_item_id: int, expand: str = "all") -> Dict[str, Any]:
        return self._request(
            "GET",
            f"wit/workitems/{work_item_id}",
            params={"api-version": WORK_ITEM_API_VERSION, "$expand": expand},
        )

    def get_comments(self, work_item_id: int, top: Optional[int] = None) -> Dict[str, Any]:
        params: Dict[str, Any] = {"api-version": COMMENTS_API_VERSION}
        if top is not None:
            params["$top"] = top
        return self._request(
            "GET",
            f"wit/workitems/{work_item_id}/comments",
            params=params,
        )

    def query_wiql(self, query_text: str) -> Dict[str, Any]:
        return self._request(
            "POST",
            "wit/wiql",
            params={"api-version": WORK_ITEM_API_VERSION},
            json_body={"query": query_text},
        )

    def batch_get_work_items(self, ids: Iterable[int], expand: str = "all") -> Dict[str, Any]:
        id_list = [int(x) for x in ids]
        if not id_list:
            return {"count": 0, "value": []}
        if len(id_list) > 200:
            raise AgentError("Batch get supports a maximum of 200 work item IDs per request.")

        id_csv = ",".join(str(x) for x in id_list)
        return self._request(
            "GET",
            "wit/workitems",
            params={
                "api-version": WORK_ITEM_API_VERSION,
                "ids": id_csv,
                "$expand": expand,
            },
        )

    def add_comment(self, work_item_id: int, html_text: str, execute: bool) -> Dict[str, Any]:
        payload = {"text": html_text}
        if not execute:
            return {
                "dry_run": True,
                "action": "add_comment",
                "work_item_id": work_item_id,
                "payload": payload,
            }

        return self._request(
            "POST",
            f"wit/workitems/{work_item_id}/comments",
            params={"api-version": COMMENTS_API_VERSION},
            headers={"Content-Type": "application/json"},
            json_body=payload,
        )

    def update_work_item(self, work_item_id: int, patch_ops: List[Dict[str, Any]], execute: bool) -> Dict[str, Any]:
        if not isinstance(patch_ops, list) or not patch_ops:
            raise AgentError("Patch body must be a non-empty JSON array of JSON Patch operations.")

        if not execute:
            return {
                "dry_run": True,
                "action": "update_work_item",
                "work_item_id": work_item_id,
                "payload": patch_ops,
            }

        return self._request(
            "PATCH",
            f"wit/workitems/{work_item_id}",
            params={"api-version": WORK_ITEM_API_VERSION},
            headers={"Content-Type": "application/json-patch+json"},
            json_body=patch_ops,
        )

    def get_repository_id(self, repository_name: Optional[str] = None) -> str:
        repos = self._request("GET", "git/repositories", params={"api-version": WORK_ITEM_API_VERSION})
        values = repos.get("value", [])
        if not values:
            raise AgentError("No git repositories found for this project.")
        target_name = (repository_name or self.config.project).lower()
        match = next((r for r in values if r["name"].lower() == target_name), None)
        return (match or values[0])["id"]

    def get_pull_request(self, pull_request_id: int, repository_id: Optional[str] = None) -> Dict[str, Any]:
        repo_id = repository_id or self.get_repository_id()
        return self._request(
            "GET",
            f"git/repositories/{repo_id}/pullrequests/{pull_request_id}",
            params={"api-version": WORK_ITEM_API_VERSION},
        )

    def update_pull_request(
        self,
        pull_request_id: int,
        fields: Dict[str, Any],
        execute: bool,
        repository_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not isinstance(fields, dict) or not fields:
            raise AgentError("PR update body must be a non-empty JSON object (plain fields, not a JSON Patch array).")

        if "description" in fields and len(fields["description"]) > 4000:
            raise AgentError(
                f"PR description is {len(fields['description'])} characters; ADO caps it at 4000."
            )

        if not execute:
            return {
                "dry_run": True,
                "action": "update_pull_request",
                "pull_request_id": pull_request_id,
                "payload": fields,
            }

        repo_id = repository_id or self.get_repository_id()
        return self._request(
            "PATCH",
            f"git/repositories/{repo_id}/pullrequests/{pull_request_id}",
            params={"api-version": WORK_ITEM_API_VERSION},
            headers={"Content-Type": "application/json"},
            json_body=fields,
        )

    def get_branch_commits(
        self,
        branch_name: str,
        top: int = 15,
        repository_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        repo_id = repository_id or self.get_repository_id()
        return self._request(
            "GET",
            f"git/repositories/{repo_id}/commits",
            params={
                "api-version": WORK_ITEM_API_VERSION,
                "searchCriteria.itemVersion.version": branch_name,
                "searchCriteria.itemVersion.versionType": "branch",
                "$top": top,
            },
        )

    def execute_plan(self, plan: Dict[str, Any], execute: bool, continue_on_error: bool = False) -> Dict[str, Any]:
        steps = plan.get("steps")
        if not isinstance(steps, list) or not steps:
            raise AgentError("Plan file must contain a non-empty 'steps' array.")

        results: List[Dict[str, Any]] = []
        for index, step in enumerate(steps, start=1):
            if not isinstance(step, dict):
                error = f"Step {index} is not an object."
                if continue_on_error:
                    results.append({"index": index, "ok": False, "error": error})
                    continue
                raise AgentError(error)

            action = str(step.get("action", "")).strip().lower()
            try:
                result = self._run_step(action, step, execute=execute)
                results.append({"index": index, "ok": True, "action": action, "result": result})
            except Exception as exc:  # noqa: BLE001
                if continue_on_error:
                    results.append(
                        {
                            "index": index,
                            "ok": False,
                            "action": action,
                            "error": str(exc),
                        }
                    )
                else:
                    raise

        return {
            "execute": execute,
            "continue_on_error": continue_on_error,
            "step_count": len(steps),
            "results": results,
        }

    def _run_step(self, action: str, step: Dict[str, Any], execute: bool) -> Dict[str, Any]:
        if action == "get_work_item":
            return self.get_work_item(int(step["id"]), expand=str(step.get("expand", "all")))

        if action == "get_comments":
            top = step.get("top")
            return self.get_comments(int(step["id"]), top=int(top) if top is not None else None)

        if action == "query_wiql":
            wiql_result = self.query_wiql(str(step["query"]))
            if step.get("fetch_details"):
                ids = [item["id"] for item in wiql_result.get("workItems", [])]
                expand = str(step.get("expand", "all"))
                return {
                    "wiql": wiql_result,
                    "details": self.batch_get_work_items(ids, expand=expand),
                }
            return wiql_result

        if action == "batch_get":
            ids = [int(x) for x in step["ids"]]
            return self.batch_get_work_items(ids, expand=str(step.get("expand", "all")))

        if action == "add_comment":
            return self.add_comment(int(step["id"]), str(step["text"]), execute=execute)

        if action == "update_work_item":
            patch_ops = step.get("patch")
            if not isinstance(patch_ops, list):
                raise AgentError("update_work_item step requires a list field named 'patch'.")
            return self.update_work_item(int(step["id"]), patch_ops, execute=execute)

        raise AgentError(f"Unsupported plan step action: {action}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Real agent runner for the fab-ado-board skill")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to fab-ado-board config JSON",
    )
    parser.add_argument(
        "--skill-doc",
        default=str(DEFAULT_SKILL_PATH),
        help="Path to skill markdown (for context/reporting)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="HTTP timeout in seconds",
    )
    parser.add_argument(
        "--log-dir",
        default=str(DEFAULT_RUN_LOG_DIR),
        help="Directory where run logs will be written",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_get = sub.add_parser("get", help="Get one work item")
    p_get.add_argument("--id", type=int, required=True, help="Work item ID")
    p_get.add_argument("--expand", default="all", help="$expand value")

    p_comments = sub.add_parser("comments", help="Get work item comments")
    p_comments.add_argument("--id", type=int, required=True, help="Work item ID")
    p_comments.add_argument("--top", type=int, help="Limit number of comments")

    p_wiql = sub.add_parser("wiql", help="Execute WIQL query")
    p_wiql.add_argument("--query", help="Inline WIQL query")
    p_wiql.add_argument("--query-file", help="Path to WIQL file")
    p_wiql.add_argument("--fetch-details", action="store_true", help="Fetch full details for returned IDs")
    p_wiql.add_argument("--expand", default="all", help="$expand value when --fetch-details is used")

    p_batch = sub.add_parser("batch", help="Batch get work items")
    p_batch.add_argument("--ids", help="Comma-separated IDs")
    p_batch.add_argument("--ids-file", help="Path to JSON array file with IDs")
    p_batch.add_argument("--expand", default="all", help="$expand value")

    p_add_comment = sub.add_parser("add-comment", help="Add a comment to a work item")
    p_add_comment.add_argument("--id", type=int, required=True, help="Work item ID")
    p_add_comment.add_argument("--text", help="Inline HTML comment text")
    p_add_comment.add_argument("--text-file", help="Path to HTML comment file")
    p_add_comment.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute write operation (default is dry-run)",
    )

    p_update = sub.add_parser("update", help="Update fields with JSON Patch")
    p_update.add_argument("--id", type=int, required=True, help="Work item ID")
    p_update.add_argument("--patch-file", required=True, help="Path to JSON patch array file")
    p_update.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute write operation (default is dry-run)",
    )

    p_pr_get = sub.add_parser("pr-get", help="Get one pull request")
    p_pr_get.add_argument("--id", type=int, required=True, help="Pull request ID")
    p_pr_get.add_argument("--repository", help="Repository name (defaults to the project name)")

    p_pr_update = sub.add_parser("pr-update", help="Update a pull request's fields (plain JSON body, not JSON Patch)")
    p_pr_update.add_argument("--id", type=int, required=True, help="Pull request ID")
    p_pr_update.add_argument("--fields-file", required=True, help="Path to a JSON object file, e.g. {\"description\": \"...\"}")
    p_pr_update.add_argument("--repository", help="Repository name (defaults to the project name)")
    p_pr_update.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute write operation (default is dry-run)",
    )

    p_commits = sub.add_parser("commits", help="List commits on a branch")
    p_commits.add_argument("--branch", required=True, help="Branch name, e.g. development")
    p_commits.add_argument("--top", type=int, default=15, help="Max commits to return")
    p_commits.add_argument("--repository", help="Repository name (defaults to the project name)")

    p_plan = sub.add_parser("plan", help="Execute a multi-step plan JSON")
    p_plan.add_argument("--plan-file", required=True, help="Path to plan JSON file")
    p_plan.add_argument(
        "--execute",
        action="store_true",
        help="Actually execute write operations (default is dry-run)",
    )
    p_plan.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue to next step when one step fails",
    )

    return parser.parse_args()


def _read_config(config_path: Path) -> AdoConfig:
    if not config_path.exists():
        raise AgentError(f"Config file not found: {config_path}")

    raw = json.loads(config_path.read_text(encoding="utf-8"))

    org = str(raw.get("ado_organization", "")).strip()
    project = str(raw.get("ado_project", "")).strip()

    # Allow environment variable override so PAT is not hard-bound to file storage.
    pat = os.environ.get("ADO_PAT", "").strip() or str(raw.get("ado_pat", "")).strip()

    if not org:
        raise AgentError("Missing 'ado_organization' in config.")
    if not project:
        raise AgentError("Missing 'ado_project' in config.")
    if not pat:
        raise AgentError("Missing ADO PAT. Set 'ado_pat' in config or provide ADO_PAT env var.")

    return AdoConfig(organization=org, project=project, pat=pat)


def _read_text_input(inline_value: Optional[str], file_path: Optional[str], label: str) -> str:
    if bool(inline_value) == bool(file_path):
        raise AgentError(f"Provide exactly one of --{label} or --{label}-file.")
    if inline_value:
        return inline_value
    return Path(file_path).read_text(encoding="utf-8")


def _read_ids(ids_inline: Optional[str], ids_file: Optional[str]) -> List[int]:
    if bool(ids_inline) == bool(ids_file):
        raise AgentError("Provide exactly one of --ids or --ids-file.")

    if ids_inline:
        raw_parts = [part.strip() for part in ids_inline.split(",") if part.strip()]
        return [int(x) for x in raw_parts]

    data = json.loads(Path(ids_file).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise AgentError("--ids-file must contain a JSON array.")
    return [int(x) for x in data]


def _write_run_log(log_dir: Path, payload: Dict[str, Any]) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = log_dir / f"run-{ts}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def _build_command_result(agent: FabAdoBoardAgent, args: argparse.Namespace) -> Dict[str, Any]:
    cmd = args.command

    if cmd == "get":
        return agent.get_work_item(args.id, expand=args.expand)

    if cmd == "comments":
        return agent.get_comments(args.id, top=args.top)

    if cmd == "wiql":
        query_text = _read_text_input(args.query, args.query_file, "query")
        wiql_result = agent.query_wiql(query_text)
        if args.fetch_details:
            ids = [item["id"] for item in wiql_result.get("workItems", [])]
            return {
                "wiql": wiql_result,
                "details": agent.batch_get_work_items(ids, expand=args.expand),
            }
        return wiql_result

    if cmd == "batch":
        ids = _read_ids(args.ids, args.ids_file)
        return agent.batch_get_work_items(ids, expand=args.expand)

    if cmd == "add-comment":
        text = _read_text_input(args.text, args.text_file, "text")
        return agent.add_comment(args.id, text, execute=args.execute)

    if cmd == "update":
        patch_ops = json.loads(Path(args.patch_file).read_text(encoding="utf-8"))
        return agent.update_work_item(args.id, patch_ops, execute=args.execute)

    if cmd == "pr-get":
        return agent.get_pull_request(args.id, repository_id=None if not args.repository else agent.get_repository_id(args.repository))

    if cmd == "pr-update":
        fields = json.loads(Path(args.fields_file).read_text(encoding="utf-8"))
        repo_id = agent.get_repository_id(args.repository) if args.repository else None
        return agent.update_pull_request(args.id, fields, execute=args.execute, repository_id=repo_id)

    if cmd == "commits":
        repo_id = agent.get_repository_id(args.repository) if args.repository else None
        return agent.get_branch_commits(args.branch, top=args.top, repository_id=repo_id)

    if cmd == "plan":
        plan_data = json.loads(Path(args.plan_file).read_text(encoding="utf-8"))
        return agent.execute_plan(plan_data, execute=args.execute, continue_on_error=args.continue_on_error)

    raise AgentError(f"Unsupported command: {cmd}")


def main() -> int:
    try:
        args = parse_args()
        config_path = Path(args.config).resolve()
        skill_path = Path(args.skill_doc).resolve()
        log_dir = Path(args.log_dir).resolve()

        config = _read_config(config_path)
        agent = FabAdoBoardAgent(config=config, timeout_seconds=args.timeout, skill_doc_path=skill_path)

        result = _build_command_result(agent, args)

        envelope = {
            "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
            "command": args.command,
            "config_path": str(config_path),
            "organization": config.organization,
            "project": config.project,
            "skill": agent.get_skill_summary(),
            "result": result,
        }

        log_path = _write_run_log(log_dir, envelope)
        print(json.dumps(envelope, indent=2, ensure_ascii=False))
        print(f"\nRun log: {log_path}")
        return 0

    except AgentError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2
    except requests.RequestException as exc:
        print(f"[ERROR] Network/API request failed: {exc}", file=sys.stderr)
        return 3
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] Unexpected failure: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
