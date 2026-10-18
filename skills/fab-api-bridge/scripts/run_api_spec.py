#!/usr/bin/env python3
"""
Render or execute a fab api command from a JSON spec.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path


def format_key_values(values: dict[str, object]) -> str:
    parts: list[str] = []
    for key, value in values.items():
        parts.append(f"{key}={value}")
    return ",".join(parts)


def build_command(spec: dict) -> list[str]:
    endpoint = spec["endpoint"]
    method = spec.get("method", "get")
    audience = spec.get("audience")
    query = spec.get("query")
    params = spec.get("params", {})
    headers = spec.get("headers", {})
    input_file = spec.get("inputFile")
    show_headers = bool(spec.get("showHeaders", False))
    output_format = spec.get("outputFormat", "json")

    command = ["fab", "api", endpoint, "-X", method, "--output_format", output_format]

    if input_file:
        command.extend(["-i", input_file])
    if audience:
        command.extend(["-A", audience])
    if params:
        command.extend(["-P", format_key_values(params)])
    if headers:
        command.extend(["-H", format_key_values(headers)])
    if query:
        command.extend(["-q", query])
    if show_headers:
        command.append("--show_headers")

    return command


def main() -> int:
    parser = argparse.ArgumentParser(description="Render or execute a fab api command from a JSON spec.")
    parser.add_argument("spec", help="Path to a JSON API spec file.")
    parser.add_argument("--execute", action="store_true", help="Execute the rendered fab api command.")
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
