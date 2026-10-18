#!/usr/bin/env python3
"""
Repair persistent PATH entries for an existing fab executable.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
from pathlib import Path


def path_contains(target: Path) -> bool:
    normalized_target = str(target).lower()
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if entry and entry.lower() == normalized_target:
            return True
    return False


def ensure_windows_user_path(script_dir: Path, dry_run: bool) -> None:
    import winreg

    current_path = os.environ.get("PATH", "")
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_SET_VALUE)
    try:
        try:
            existing_value, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            existing_value = ""

        entries = [entry for entry in existing_value.split(";") if entry]
        if str(script_dir) in entries:
            print(f"Windows user PATH already includes {script_dir}")
            return

        entries.append(str(script_dir))
        new_value = ";".join(entries)
        print(f"Adding {script_dir} to Windows user PATH")
        if not dry_run:
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_value)
            os.environ["PATH"] = current_path + os.pathsep + str(script_dir)
    finally:
        winreg.CloseKey(key)


def shell_rc_files() -> list[Path]:
    home = Path.home()
    shell_name = Path(os.environ.get("SHELL", "")).name
    if shell_name == "bash":
        return [home / ".bash_profile", home / ".bashrc"]
    return [home / ".zprofile", home / ".zshrc"]


def ensure_unix_user_path(script_dir: Path, dry_run: bool) -> None:
    export_line = f'export PATH="{script_dir}:$PATH"'
    changed = False
    for rc_file in shell_rc_files():
        existing = rc_file.read_text(encoding="utf-8") if rc_file.exists() else ""
        if export_line in existing or str(script_dir) in existing:
            print(f"{rc_file} already references {script_dir}")
            continue
        print(f"Adding {script_dir} to {rc_file}")
        if not dry_run:
            with rc_file.open("a", encoding="utf-8") as handle:
                if existing and not existing.endswith("\n"):
                    handle.write("\n")
                handle.write(f"\n# Added by fab-bootstrap\n{export_line}\n")
        changed = True
    if not changed:
        print(f"PATH already appears configured for {script_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Repair persistent PATH entries for an existing fab executable.")
    parser.add_argument("--fab-path", help="Explicit path to fab or fab.exe. Defaults to resolving from PATH.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing them.")
    args = parser.parse_args()

    fab_path = Path(args.fab_path) if args.fab_path else Path(shutil.which("fab") or "")
    if not fab_path or not fab_path.exists():
        raise FileNotFoundError("Could not resolve an existing fab executable. Pass --fab-path explicitly.")

    script_dir = fab_path.parent
    print(f"Resolved fab executable: {fab_path}")
    print(f"Script directory to add: {script_dir}")

    if path_contains(script_dir):
        print("Current session PATH already includes the script directory.")
    else:
        print("Current session PATH does not include the script directory.")

    if platform.system() == "Windows":
        ensure_windows_user_path(script_dir, args.dry_run)
    else:
        ensure_unix_user_path(script_dir, args.dry_run)

    print("A new shell may be required before PATH changes are visible everywhere.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
