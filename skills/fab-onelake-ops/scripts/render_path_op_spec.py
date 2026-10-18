#!/usr/bin/env python3
"""
Render or execute a fab path operation from a JSON spec.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path


VALID_OPS = {"dir", "exists", "copy", "move", "mkdir", "mklink", "del", "table-schema"}


def build_command(spec: dict) -> list[str]:
    operation = spec["operation"]
    output_format = spec.get("outputFormat", "json")
    force = bool(spec.get("force", False))
    recursive = bool(spec.get("recursive", False))

    if operation not in VALID_OPS:
        raise ValueError(f"operation must be one of: {', '.join(sorted(VALID_OPS))}")

    if operation == "dir":
        command = ["fab", "dir", spec["path"], "--output_format", output_format]
    elif operation == "exists":
        command = ["fab", "exists", spec["path"], "--output_format", output_format]
    elif operation == "copy":
        command = ["fab", "copy", spec["fromPath"], spec["toPath"], "--output_format", output_format]
        if recursive:
            command.append("-r")
        if bool(spec.get("blockOnPathCollision", False)):
            command.append("-bpc")
    elif operation == "move":
        command = ["fab", "move", spec["fromPath"], spec["toPath"], "--output_format", output_format]
        if recursive:
            command.append("-r")
    elif operation == "mkdir":
        command = ["fab", "mkdir", spec["path"], "--output_format", output_format]
        params = spec.get("params", {})
        if params:
            encoded = ",".join(f"{key}={value}" for key, value in params.items())
            command.extend(["-P", encoded])
    elif operation == "mklink":
        command = ["fab", "mklink", spec["path"], "--output_format", output_format]
        if spec.get("type"):
            command.extend(["--type", spec["type"]])
        if spec.get("target"):
            command.extend(["--target", spec["target"]])
        if spec.get("inputFile"):
            command.extend(["-i", spec["inputFile"]])
    elif operation == "del":
        command = ["fab", "del", spec["path"], "--output_format", output_format]
    else:
        command = ["fab", "table", "schema", spec["path"], "--output_format", output_format]

    if force and operation in {"copy", "move", "mklink", "del"}:
        command.append("-f")

    return command


def main() -> int:
    parser = argparse.ArgumentParser(description="Render or execute a fab path operation from a JSON spec.")
    parser.add_argument("spec", help="Path to a JSON path-op spec file.")
    parser.add_argument("--execute", action="store_true", help="Execute the rendered fab command.")
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
