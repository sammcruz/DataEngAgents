#!/usr/bin/env python3
"""Run a range of an existing Fabric notebook's code cells, in order, in one live fntk session.

Reads the notebook's current content from the workspace (or a local .ipynb with --from-file),
submits each selected code cell with `fntk code run`, polls `fntk code get-result`, prints a
compact result per cell, and stops at the first error.

The session should already be idle (`fntk notebook start-session` + `get-session`); `code run`
auto-creates one otherwise, which costs a 2-5 min cold start. This script never deletes the
session -- run `fntk notebook delete-session` yourself when finished.

Examples:
  fntk_run_cells.py -w <WS_ID> -a <ART_ID> --cells 0-5
  fntk_run_cells.py -w <WS_ID> -a <ART_ID> --cells 0,2,4-6 --override 1=params.py
  fntk_run_cells.py -w <WS_ID> -a <ART_ID> --cells 0-3 --dry-run
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time

CLIENT = ["--client-name", os.environ.get("FNTK_CLIENT_NAME", "agent")]


def fntk(args):
    env = dict(os.environ)
    env.setdefault("FNTK_TELEMETRY_DISABLED", "1")
    proc = subprocess.run(["fntk"] + args + ["--json"] + CLIENT,
                          capture_output=True, text=True, env=env)
    try:
        return json.loads(proc.stdout)
    except ValueError:
        sys.exit("fntk returned non-JSON output (exit %d):\n%s\n%s"
                 % (proc.returncode, proc.stdout[-2000:], proc.stderr[-2000:]))


def parse_cells(spec, total):
    if not spec:
        return list(range(total))
    out = []
    for part in spec.split(","):
        part = part.strip()
        if "-" in part:
            lo, hi = part.split("-", 1)
            out.extend(range(int(lo), int(hi) + 1))
        elif part:
            out.append(int(part))
    bad = [i for i in out if i < 0 or i >= total]
    if bad:
        sys.exit("cell index out of range (notebook has %d cells): %s" % (total, bad))
    return out


def source_of(cell):
    src = cell.get("source", "")
    return "".join(src) if isinstance(src, list) else src


def load_notebook(ws, art, from_file):
    if from_file:
        with open(from_file) as f:
            return json.load(f)
    fd, path = tempfile.mkstemp(suffix=".ipynb")
    os.close(fd)
    try:
        res = fntk(["notebook", "get-content", "-w", ws, "-a", art, "--output-file", path])
        if res.get("status") == "error":
            sys.exit("get-content failed: %s" % json.dumps(res.get("error") or res, indent=1))
        with open(path) as f:
            return json.load(f)
    finally:
        os.remove(path)


def render_outputs(data, limit):
    lines = []
    for o in data.get("outputs") or []:
        if isinstance(o, str):
            lines.append(o)
            continue
        if o.get("text"):
            t = o["text"]
            lines.append("".join(t) if isinstance(t, list) else t)
        d = o.get("data") or {}
        if d.get("text/plain"):
            t = d["text/plain"]
            lines.append("".join(t) if isinstance(t, list) else t)
        if o.get("ename"):
            lines.append("%s: %s" % (o.get("ename"), o.get("evalue")))
        if not (o.get("text") or d.get("text/plain") or o.get("ename")):
            lines.append(json.dumps(o)[:500])
    text = "\n".join(l.rstrip("\n") for l in lines)
    return text if len(text) <= limit else text[:limit] + "\n... [truncated %d chars]" % (len(text) - limit)


def run_cell(ws, art, code, timeout, limit):
    res = fntk(["code", "run", "-w", ws, "-a", art, "--code", code])
    if res.get("status") == "error":
        return False, "code run failed: %s" % json.dumps(res.get("error"), indent=1)
    eid = (res.get("data") or {}).get("execution_id")
    if not eid:
        return False, "no execution_id in response: %s" % json.dumps(res)[:1000]
    print("  execution_id=%s" % eid)
    deadline = time.time() + timeout
    while True:
        r = fntk(["code", "get-result", "-w", ws, "-a", art, "--execution-id", eid])
        if r.get("status") == "error":
            return False, "get-result failed: %s" % json.dumps(r.get("error"), indent=1)
        data = r.get("data") or {}
        state = data.get("status")
        if state in ("completed", "error"):
            out = render_outputs(data, limit)
            if state == "error" or data.get("error"):
                err = data.get("error")
                err_text = json.dumps(err, indent=1) if not isinstance(err, str) else err
                return False, (out + "\n" if out else "") + "ERROR: " + (err_text or "")[:limit]
            return True, out
        if time.time() > deadline:
            return False, "timed out after %ds; execution %s still %s (poll it or `fntk code cancel`)" % (timeout, eid, state)
        wait = 5
        for a in r.get("next_actions") or []:
            if a.get("type") == "poll" and a.get("retry_after"):
                wait = a["retry_after"]
                break
        time.sleep(wait)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-w", "--workspace-id", required=True)
    p.add_argument("-a", "--artifact-id", required=True)
    p.add_argument("--cells", help="e.g. '0-5' or '0,2,4-6' (default: all)")
    p.add_argument("--from-file", help="use a local .ipynb instead of the live content")
    p.add_argument("--override", action="append", default=[], metavar="IDX=FILE",
                   help="submit FILE's code instead of cell IDX (e.g. a parameter override); repeatable")
    p.add_argument("--include-configure", action="store_true",
                   help="also run %%configure cells (they restart the session)")
    p.add_argument("--continue-on-error", action="store_true")
    p.add_argument("--timeout", type=int, default=1800, help="per-cell timeout in seconds")
    p.add_argument("--max-output", type=int, default=4000, help="max chars of output printed per cell")
    p.add_argument("--dry-run", action="store_true", help="print what would run, submit nothing")
    a = p.parse_args()

    overrides = {}
    for o in a.override:
        idx, path = o.split("=", 1)
        with open(path) as f:
            overrides[int(idx)] = f.read()

    nb = load_notebook(a.workspace_id, a.artifact_id, a.from_file)
    cells = nb.get("cells", [])
    selected = parse_cells(a.cells, len(cells))
    failures = 0

    for i in selected:
        cell = cells[i]
        if cell.get("cell_type") != "code":
            print("[%d] skip (%s)" % (i, cell.get("cell_type")))
            continue
        code = overrides.get(i, source_of(cell))
        if not code.strip():
            print("[%d] skip (empty)" % i)
            continue
        if code.lstrip().startswith("%%configure") and not a.include_configure:
            print("[%d] skip (%%%%configure restarts the session; use --include-configure)" % i)
            continue
        first = code.strip().splitlines()[0][:100]
        tag = " (override)" if i in overrides else ""
        print("[%d]%s %s" % (i, tag, first))
        if a.dry_run:
            continue
        ok, out = run_cell(a.workspace_id, a.artifact_id, code, a.timeout, a.max_output)
        print("  %s" % ("OK" if ok else "FAILED"))
        if out:
            print("\n".join("  | " + l for l in out.splitlines()))
        if not ok:
            failures += 1
            if not a.continue_on_error:
                print("Stopped at cell %d. Session is still alive -- fix and re-run from here, "
                      "or delete it with `fntk notebook delete-session`." % i)
                sys.exit(1)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
