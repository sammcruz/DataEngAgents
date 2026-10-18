#!/usr/bin/env python3
"""
Poll a Fabric job run until it reaches a terminal state.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time


TERMINAL_STATES = {"completed", "failed", "cancelled", "canceled", "success", "error"}


def run_status(path: str, run_id: str, schedule: bool) -> dict:
    command = ["fab", "job", "run-status", path, "--id", run_id, "--output_format", "json"]
    if schedule:
        command.append("--schedule")

    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "fab job run-status failed")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse JSON from fab job run-status: {exc}") from exc


def extract_state(payload: object) -> str:
    if isinstance(payload, dict):
        result = payload.get("result")
        if result is not None:
            nested = extract_state(result)
            if nested:
                return nested
        data = payload.get("data")
        if data is not None:
            nested = extract_state(data)
            if nested:
                return nested
        for key in ("status", "state", "executionState", "runStatus"):
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        for value in payload.values():
            nested = extract_state(value)
            if nested:
                return nested
    elif isinstance(payload, list):
        for value in payload:
            nested = extract_state(value)
            if nested:
                return nested
    return ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Poll a fab job run until it reaches a terminal state.")
    parser.add_argument("path", help="Fabric item path.")
    parser.add_argument("run_id", help="Execution ID or schedule run ID.")
    parser.add_argument("--schedule", action="store_true", help="Poll a scheduled run.")
    parser.add_argument("--interval", type=int, default=15, help="Polling interval in seconds.")
    parser.add_argument("--timeout", type=int, default=1800, help="Timeout in seconds.")
    args = parser.parse_args()

    start = time.time()
    attempt = 0

    while True:
        attempt += 1
        payload = run_status(args.path, args.run_id, args.schedule)
        state = extract_state(payload).lower()
        print(json.dumps({"attempt": attempt, "state": state or "unknown", "payload": payload}, indent=2))

        if state in TERMINAL_STATES:
            return 0 if state in {"completed", "success"} else 1

        if time.time() - start >= args.timeout:
            print("Timed out waiting for terminal state.", file=sys.stderr)
            return 2

        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
