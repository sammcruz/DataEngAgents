#!/usr/bin/env python3
"""
Render a simple deployment manifest into ordered fab-cli commands.

Example manifest:
{
    "stagingRoot": "staging/fab-deploy",
  "items": [
    {
      "source": "dev.Workspace/nb1.Notebook",
      "destination": "test.Workspace/nb1.Notebook",
      "forceImport": true
    }
  ]
}
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def quote(value: str) -> str:
    return f'"{value}"'


def render_commands(manifest: dict) -> list[str]:
    staging_root = manifest.get("stagingRoot", "staging/fab-deploy")
    items = manifest.get("items", [])
    if not items:
        raise ValueError("Manifest must include at least one item in 'items'.")

    commands: list[str] = []
    for index, item in enumerate(items, start=1):
        source = item["source"]
        destination = item["destination"]
        force_export = item.get("forceExport", False)
        force_import = item.get("forceImport", False)
        artifact_dir = item.get("artifactDir")
        if not artifact_dir:
            leaf_name = destination.rsplit("/", 1)[-1]
            artifact_dir = str(Path(staging_root) / f"{index:02d}-{leaf_name}")

        commands.append(f"fab exists {quote(destination)}")
        export_command = f"fab export {quote(source)} -o {quote(artifact_dir)}"
        if force_export:
            export_command += " -f"
        commands.append(export_command)

        import_command = f"fab import {quote(destination)} -i {quote(artifact_dir)}"
        if force_import:
            import_command += " -f"
        commands.append(import_command)
        commands.append(f"fab get {quote(destination)}")

    return commands


def main() -> int:
    parser = argparse.ArgumentParser(description="Render fab deployment commands from a manifest.")
    parser.add_argument("manifest", help="Path to a JSON manifest file.")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for command in render_commands(manifest):
        print(command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
