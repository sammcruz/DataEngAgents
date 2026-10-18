#!/usr/bin/env python3
"""
Batch-check OneLake or Fabric paths with `fab exists`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def check_path(path: str) -> dict[str, object]:
    result = subprocess.run(["fab", "exists", path], capture_output=True, text=True, check=False)
    raw = (result.stdout or result.stderr).strip()
    exists = raw.lower() == "true"
    return {"path": path, "exists": exists, "raw": raw, "returncode": result.returncode}


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch-check paths with fab exists.")
    parser.add_argument("input_file", help="Path to a JSON file containing a list of paths.")
    args = parser.parse_args()

    input_path = Path(args.input_file)
    paths = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(paths, list):
        raise ValueError("Input file must contain a JSON list of paths.")

    results = [check_path(path) for path in paths]
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
