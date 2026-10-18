#!/usr/bin/env python3
"""
Install, verify, and bootstrap Fabric CLI for user-auth workflows.
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import site
import subprocess
import sys
import sysconfig
from pathlib import Path


WINDOWS_PATH_SCOPE = "User"
PATH_BLOCK_START = "# Added by fab-bootstrap"
PATH_BLOCK_END = "# End fab-bootstrap"


def child_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    env.setdefault("PYTHONIOENCODING", "utf-8")
    return env


def run(command: list[str], dry_run: bool = False, check: bool = True) -> subprocess.CompletedProcess[str] | None:
    printable = " ".join(command)
    print(f"$ {printable}")
    if dry_run:
        return None
    return subprocess.run(command, text=True, check=check, env=child_env())


def user_script_dir() -> Path:
    scheme = "nt_user" if platform.system() == "Windows" else "posix_user"
    scripts_path = sysconfig.get_path("scripts", scheme=scheme)
    if scripts_path:
        return Path(scripts_path)

    user_base = Path(site.getuserbase())
    if platform.system() == "Windows":
        return user_base / "Scripts"
    return user_base / "bin"


def fab_executable() -> Path:
    script_dir = user_script_dir()
    executable = "fab.exe" if platform.system() == "Windows" else "fab"
    return script_dir / executable


def resolve_fab_path(script_dir: Path) -> Path:
    direct = fab_executable()
    if direct.exists():
        return direct

    resolved = shutil.which("fab")
    if resolved:
        return Path(resolved)

    raise FileNotFoundError(f"Could not find Fabric CLI executable in {script_dir} or on PATH")


def ensure_installed(python_executable: str, dry_run: bool) -> None:
    run([python_executable, "-m", "pip", "install", "--user", "--upgrade", "ms-fabric-cli"], dry_run=dry_run)


def path_contains(target: Path) -> bool:
    normalized_target = str(target).lower()
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if entry and entry.lower() == normalized_target:
            return True
    return False


def ensure_windows_user_path(script_dir: Path, dry_run: bool) -> None:
    import winreg

    current_path = os.environ.get("PATH", "")
    if path_contains(script_dir):
        print(f"PATH already includes {script_dir}")
        return

    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ | winreg.KEY_SET_VALUE)
    try:
        try:
            existing_value, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            existing_value = ""

        entries = [entry for entry in existing_value.split(";") if entry]
        if str(script_dir) not in entries:
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
    shell = Path(os.environ.get("SHELL", "")).name
    if shell == "bash":
        return [home / ".bash_profile", home / ".bashrc"]
    return [home / ".zprofile", home / ".zshrc"]


def ensure_unix_user_path(script_dir: Path, dry_run: bool) -> None:
    export_line = f'export PATH="{script_dir}:$PATH"'
    block = f"{PATH_BLOCK_START}\n{export_line}\n{PATH_BLOCK_END}\n"
    updated_any = False

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
                handle.write(block)
        updated_any = True

    if not updated_any:
        print(f"PATH already appears configured for {script_dir}")
    os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + str(script_dir)


def ensure_path(script_dir: Path, dry_run: bool) -> None:
    if platform.system() == "Windows":
        ensure_windows_user_path(script_dir, dry_run)
    else:
        ensure_unix_user_path(script_dir, dry_run)


def verify_fab(script_dir: Path) -> Path:
    fab_path = resolve_fab_path(script_dir)
    print(f"Found Fabric CLI at {fab_path}")

    resolved = shutil.which("fab")
    if resolved:
        print(f"`fab` resolves on PATH: {resolved}")
    else:
        print("`fab` is not yet visible on the current PATH. A new shell may be required.")

    result = subprocess.run([str(fab_path), "--version"], capture_output=True, text=True, check=True, env=child_env())
    print(result.stdout.strip())
    return fab_path


def check_auth_status(fab_path: Path) -> bool:
    result = subprocess.run(
        [str(fab_path), "auth", "status"],
        capture_output=True,
        text=True,
        check=False,
        env=child_env(),
    )
    output = (result.stdout or result.stderr or "").strip()
    print(output)
    normalized = output.lower()
    return "logged in to app.fabric.microsoft.com" in normalized and "not logged in" not in normalized


def run_user_login(fab_path: Path, dry_run: bool) -> None:
    if check_auth_status(fab_path):
        print("User auth already active.")
        return
    print("Launching interactive user login...")
    try:
        run([str(fab_path), "auth", "login"], dry_run=dry_run)
    except subprocess.CalledProcessError as exc:
        if platform.system() == "Windows":
            print("Interactive login could not start in this terminal.")
            print("Open a regular Windows terminal and run:")
            print(f"  {fab_path} auth login")
            print("If auth status output is garbled there too, set:")
            print("  $env:PYTHONIOENCODING='utf-8'")
            print("  $env:PYTHONUTF8='1'")
            raise SystemExit(exc.returncode)
        raise
    if not dry_run:
        check_auth_status(fab_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Install and bootstrap Fabric CLI for user-auth workflows.")
    parser.add_argument("--python", default=sys.executable, help="Python executable to use for pip installation.")
    parser.add_argument("--verify-only", action="store_true", help="Skip install and PATH updates, only verify current setup.")
    parser.add_argument("--no-path", action="store_true", help="Do not update persistent user PATH.")
    parser.add_argument("--login", action="store_true", help="Run fab auth login if the user is not already logged in.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing them.")
    args = parser.parse_args()

    script_dir = user_script_dir()
    print(f"Detected OS: {platform.system()}")
    print(f"User script directory: {script_dir}")

    if not args.verify_only:
        ensure_installed(args.python, args.dry_run)
        if not args.no_path:
            ensure_path(script_dir, args.dry_run)

    fab_path = verify_fab(script_dir)

    if args.login:
        run_user_login(fab_path, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
