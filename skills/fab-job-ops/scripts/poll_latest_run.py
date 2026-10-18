#!/usr/bin/env python3
"""
Find the latest Fabric job run ID from `fab job run-list` and poll it to completion.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import time


TERMINAL_STATES = {"completed", "failed", "cancelled", "canceled", "success", "error"}
ID_KEYS = ("id", "runId", "executionId", "jobInstanceId", "instanceId")
STATE_KEYS = ("status", "state", "executionState", "runStatus")
TIME_KEYS = ("startTime", "createdTime", "createdAt", "startDateTime", "queuedTime", "lastUpdatedTime")


def parse_json_output(args: list[str]) -> object:
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "fab command failed")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Could not parse JSON output: {exc}") from exc


def normalize_timestamp(value: str) -> float:
    raw = value.strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        return dt.datetime.fromisoformat(raw).timestamp()
    except ValueError:
        return 0.0


def collect_candidates(payload: object) -> list[dict]:
    found: list[dict] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            run_id = None
            for key in ID_KEYS:
                value = node.get(key)
                if isinstance(value, str) and value.strip():
                    run_id = value.strip()
                    break

            timestamp = 0.0
            for key in TIME_KEYS:
                value = node.get(key)
                if isinstance(value, str) and value.strip():
                    timestamp = normalize_timestamp(value)
                    if timestamp:
                        break

            if run_id:
                found.append({"id": run_id, "timestamp": timestamp, "payload": node})

            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(payload)
    deduped: dict[str, dict] = {}
    for item in found:
        existing = deduped.get(item["id"])
        if not existing or item["timestamp"] >= existing["timestamp"]:
            deduped[item["id"]] = item
    return list(deduped.values())


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
        for key in STATE_KEYS:
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


def poll_status(path: str, run_id: str, schedule: bool, interval: int, timeout: int) -> int:
    start = time.time()
    attempt = 0

    while True:
        attempt += 1
        command = ["fab", "job", "run-status", path, "--id", run_id, "--output_format", "json"]
        if schedule:
            command.append("--schedule")
        payload = parse_json_output(command)
        state = extract_state(payload).lower()
        print(json.dumps({"attempt": attempt, "runId": run_id, "state": state or "unknown", "payload": payload}, indent=2))

        if state in TERMINAL_STATES:
            return 0 if state in {"completed", "success"} else 1
        if time.time() - start >= timeout:
            print("Timed out waiting for terminal state.", file=sys.stderr)
            return 2
        time.sleep(interval)


def main() -> int:
    parser = argparse.ArgumentParser(description="Find the latest fab job run and poll it.")
    parser.add_argument("path", help="Fabric item path.")
    parser.add_argument("--schedule", action="store_true", help="Use schedule run-list and run-status.")
    parser.add_argument("--interval", type=int, default=15, help="Polling interval in seconds.")
    parser.add_argument("--timeout", type=int, default=1800, help="Timeout in seconds.")
    args = parser.parse_args()

    command = ["fab", "job", "run-list", args.path, "--output_format", "json"]
    if args.schedule:
        command.append("--schedule")
    payload = parse_json_output(command)
    candidates = collect_candidates(payload)
    if not candidates:
        print(json.dumps(payload, indent=2))
        print("No run IDs found in fab job run-list output.", file=sys.stderr)
        return 3

    latest = max(candidates, key=lambda item: item["timestamp"])
    print(f"Selected latest run ID: {latest['id']}", file=sys.stderr)
    return poll_status(args.path, latest["id"], args.schedule, args.interval, args.timeout)


if __name__ == "__main__":
    raise SystemExit(main())
