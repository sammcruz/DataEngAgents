#!/usr/bin/env python3
"""
Render or execute a fab acl command from a JSON spec.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path


def build_command(spec: dict) -> list[str]:
    operation = spec["operation"]
    path = spec["path"]
    identity = spec.get("identity")
    role = spec.get("role")
    output_format = spec.get("outputFormat", "json")
    force = bool(spec.get("force", False))

    if operation not in {"dir", "get", "set", "del"}:
        raise ValueError("operation must be one of: dir, get, set, del")

    command = ["fab", "acl", operation, path, "--output_format", output_format]

    if identity:
        command.extend(["-I", identity])
    if role:
        command.extend(["-R", role])
    if force:
        command.append("-f")

    return command


def main() -> int:
    parser = argparse.ArgumentParser(description="Render or execute a fab acl command from a JSON spec.")
    parser.add_argument("spec", help="Path to a JSON ACL spec file.")
    parser.add_argument("--execute", action="store_true", help="Execute the rendered fab acl command.")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    command = build_command(spec)
    printable = " ".join(shlex.quote(part) for part in command)
    print(printable)

    if args.execute:
        result = subprocess.run(command, check=False)
        return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
