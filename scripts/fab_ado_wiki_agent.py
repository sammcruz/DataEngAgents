#!/usr/bin/env python3
"""
Fab ADO Wiki Agent

A real agent runner for Azure DevOps Wiki operations using the same credentials as fab-ado-board.

Examples:
  python scripts/fab_ado_wiki_agent.py list-wikis
    python scripts/fab_ado_wiki_agent.py get-page --wiki "<project>.wiki" --path "/" --include-content
    python scripts/fab_ado_wiki_agent.py upsert-page --wiki "<project>.wiki" --path "/Automation/Test" --text "# Test"
    python scripts/fab_ado_wiki_agent.py upsert-page --wiki "<project>.wiki" --path "/Automation/Test" --text-file /tmp/page.md --execute
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from requests.auth import HTTPBasicAuth

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = REPO_ROOT / "skills" / "fab-ado-board" / "fab-ado-board.config.json"
DEFAULT_SKILL_PATH = REPO_ROOT / "skills" / "fab-ado-wiki" / "SKILL.md"
DEFAULT_RUN_LOG_DIR = REPO_ROOT / "output" / "agents" / "fab-ado-wiki" / "runs"

API_VERSION = "7.1"


class AgentError(RuntimeError):
    """Raised for expected operational failures."""


@dataclass
class AdoConfig:
    organization: str
    project: str
    pat: str

    @property
    def base_url(self) -> str:
        return f"https://dev.azure.com/{self.organization}/{self.project}/_apis"


class FabAdoWikiAgent:
    def __init__(self, config: AdoConfig, timeout_seconds: int = 60, skill_doc_path: Optional[Path] = None) -> None:
        self.config = config
        self.timeout_seconds = timeout_seconds
        self.skill_doc_path = skill_doc_path
        self._auth = HTTPBasicAuth("", self.config.pat)

    def get_skill_summary(self) -> Dict[str, Any]:
        if not self.skill_doc_path or not self.skill_doc_path.exists():
            return {"loaded": False}

        lines = self.skill_doc_path.read_text(encoding="utf-8").splitlines()
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
            preview = response.text[:2000]
            raise AgentError(f"ADO Wiki API {method} {url} failed: {response.status_code}\\n{preview}")

        if not response.text:
            return {}

        try:
            data = response.json()
        except ValueError:
            data = {"raw": response.text}

        etag = response.headers.get("ETag")
        if etag:
            data.setdefault("_meta", {})["etag"] = etag
        return data

    def list_wikis(self) -> Dict[str, Any]:
        return self._request(
            "GET",
            "wiki/wikis",
            params={"api-version": API_VERSION},
        )

    def get_page(
        self,
        wiki_identifier: str,
        path: str,
        include_content: bool = False,
        recursion_level: str = "none",
    ) -> Dict[str, Any]:
        params = {
            "api-version": API_VERSION,
            "path": path,
            "includeContent": str(bool(include_content)).lower(),
            "recursionLevel": recursion_level,
        }
        return self._request(
            "GET",
            f"wiki/wikis/{wiki_identifier}/pages",
            params=params,
        )

    def upsert_page(
        self,
        wiki_identifier: str,
        path: str,
        content: str,
        execute: bool,
        comment: Optional[str] = None,
        if_match: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = {"content": content}
        params: Dict[str, Any] = {
            "api-version": API_VERSION,
            "path": path,
        }
        if comment:
            params["comment"] = comment

        headers = {"Content-Type": "application/json"}
        if if_match:
            headers["If-Match"] = if_match

        if not execute:
            return {
                "dry_run": True,
                "action": "upsert_page",
                "wiki": wiki_identifier,
                "path": path,
                "params": params,
                "headers": {k: v for k, v in headers.items() if k.lower() != "authorization"},
                "payload_preview": {"content_length": len(content)},
            }

        return self._request(
            "PUT",
            f"wiki/wikis/{wiki_identifier}/pages",
            params=params,
            headers=headers,
            json_body=payload,
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Real agent runner for the fab-ado-wiki skill")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG_PATH), help="Path to shared ADO config JSON")
    parser.add_argument("--skill-doc", default=str(DEFAULT_SKILL_PATH), help="Path to skill markdown")
    parser.add_argument("--timeout", type=int, default=60, help="HTTP timeout in seconds")
    parser.add_argument("--log-dir", default=str(DEFAULT_RUN_LOG_DIR), help="Run log directory")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-wikis", help="List available project wikis")

    p_get = sub.add_parser("get-page", help="Read a wiki page")
    p_get.add_argument("--wiki", required=True, help="Wiki identifier (name or id)")
    p_get.add_argument("--path", required=True, help="Wiki page path, e.g. / or /My/Page")
    p_get.add_argument("--include-content", action="store_true", help="Include page content body")
    p_get.add_argument("--recursion-level", default="none", help="none|oneLevel|full")

    p_put = sub.add_parser("upsert-page", help="Create or update wiki page content")
    p_put.add_argument("--wiki", required=True, help="Wiki identifier (name or id)")
    p_put.add_argument("--path", required=True, help="Wiki page path")
    p_put.add_argument("--text", help="Inline markdown/html content")
    p_put.add_argument("--text-file", help="Path to content file")
    p_put.add_argument("--comment", help="Change comment")
    p_put.add_argument("--if-match", help="ETag for update concurrency control")
    p_put.add_argument("--execute", action="store_true", help="Actually execute write operation")

    return parser.parse_args()


def _read_config(config_path: Path) -> AdoConfig:
    if not config_path.exists():
        raise AgentError(f"Config file not found: {config_path}")

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    org = str(raw.get("ado_organization", "")).strip()
    project = str(raw.get("ado_project", "")).strip()
    pat = os.environ.get("ADO_PAT", "").strip() or str(raw.get("ado_pat", "")).strip()

    if not org:
        raise AgentError("Missing 'ado_organization' in config")
    if not project:
        raise AgentError("Missing 'ado_project' in config")
    if not pat:
        raise AgentError("Missing PAT; set ADO_PAT env var or add ado_pat placeholder value in config")

    return AdoConfig(organization=org, project=project, pat=pat)


def _read_text(inline_value: Optional[str], file_path: Optional[str]) -> str:
    if bool(inline_value) == bool(file_path):
        raise AgentError("Provide exactly one of --text or --text-file")
    if inline_value is not None:
        return inline_value
    return Path(file_path).read_text(encoding="utf-8")


def _write_run_log(log_dir: Path, payload: Dict[str, Any]) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = dt.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    out = log_dir / f"run-{ts}.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return out


def _run(agent: FabAdoWikiAgent, args: argparse.Namespace) -> Dict[str, Any]:
    if args.command == "list-wikis":
        return agent.list_wikis()

    if args.command == "get-page":
        return agent.get_page(
            wiki_identifier=args.wiki,
            path=args.path,
            include_content=args.include_content,
            recursion_level=args.recursion_level,
        )

    if args.command == "upsert-page":
        text = _read_text(args.text, args.text_file)
        return agent.upsert_page(
            wiki_identifier=args.wiki,
            path=args.path,
            content=text,
            execute=args.execute,
            comment=args.comment,
            if_match=args.if_match,
        )

    raise AgentError(f"Unsupported command: {args.command}")


def main() -> int:
    try:
        args = parse_args()
        config_path = Path(args.config).resolve()
        skill_path = Path(args.skill_doc).resolve()
        log_dir = Path(args.log_dir).resolve()

        config = _read_config(config_path)
        agent = FabAdoWikiAgent(config=config, timeout_seconds=args.timeout, skill_doc_path=skill_path)

        result = _run(agent, args)
        envelope = {
            "timestamp_utc": dt.datetime.utcnow().isoformat() + "Z",
            "command": args.command,
            "organization": config.organization,
            "project": config.project,
            "config_path": str(config_path),
            "skill": agent.get_skill_summary(),
            "result": result,
        }

        run_log = _write_run_log(log_dir, envelope)
        print(json.dumps(envelope, indent=2, ensure_ascii=False))
        print(f"\\nRun log: {run_log}")
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
