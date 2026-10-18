---
name: fab-bootstrap
description: Use this skill to bootstrap Fabric CLI for users who do not already have fab-cli installed, especially on Windows or macOS when the task includes pip install, persistent PATH setup, version verification, and interactive user-auth login.
---

# Fab Bootstrap

## Use

Use this skill for first-time `fab` setup on Windows and macOS in user-auth mode. It handles install or upgrade, persistent PATH updates, version verification, auth status checks, and interactive login handoff when `fab auth login` cannot run inside the current terminal host.

Read [references/install-auth.md](references/install-auth.md) for the setup flow and caveats. Use [scripts/bootstrap_fab.py](scripts/bootstrap_fab.py) to automate install, PATH setup, verification, and interactive login.
Use [scripts/repair_fab_path.py](scripts/repair_fab_path.py) when `fab` is already installed and the only issue is persistent PATH configuration.

## Workflow

1. Detect the OS and the user-level Python script directory.
2. Resolve every `fab` executable on `PATH` with `where.exe fab` on Windows before reinstalling or upgrading.
3. If multiple `fab` executables exist, identify which Python environment owns each one and remove stale `ms-fabric-cli` installs first.
4. Install or upgrade `ms-fabric-cli` with `pip --user`.
5. Add the user-level script directory to the user's persistent PATH automatically.
6. Verify `fab --version` and confirm `where.exe fab` resolves to the intended executable.
7. Check `fab auth status`.
8. If auth files are corrupt or status parsing fails, remove `~/.config/fab/auth.json` and `~/.config/fab/cache.bin`, then retry.
9. If requested and not already logged in, try `fab auth login`.
10. If interactive login cannot start in the current terminal host, tell the user to run the printed `fab auth login` command in a regular local terminal and then re-check `fab auth status`.

## Commands

Bootstrap everything, including login when the current terminal host supports it:

```powershell
python scripts/bootstrap_fab.py --login
```

Windows launcher fallback if `python` is not mapped:

```powershell
py -3 scripts/bootstrap_fab.py --login
```

Verify only:

```powershell
python scripts/bootstrap_fab.py --verify-only
```

Skip persistent PATH updates:

```powershell
python scripts/bootstrap_fab.py --no-path --login
```

Preview actions without applying changes:

```powershell
python scripts/bootstrap_fab.py --login --dry-run
```

Repair PATH only:

```powershell
python scripts/repair_fab_path.py
```

Detect duplicate `fab` executables on Windows:

```powershell
where.exe fab
```

Check which Python install owns the current package:

```powershell
python -m pip show ms-fabric-cli
py -3.12 -m pip show ms-fabric-cli
```

Clear corrupted auth cache before retrying login:

```powershell
cmd /c del /f /q %USERPROFILE%\.config\fab\auth.json
cmd /c del /f /q %USERPROFILE%\.config\fab\cache.bin
```

## Guardrails

- Prefer user-level install so admin rights are not required.
- Treat PATH updates as persistent user-environment changes and say so clearly.
- Expect `fab auth login` to require browser interaction even when the setup steps are automated.
- On Windows, be explicit that embedded terminals may fail to launch the interactive login flow cleanly. If that happens, direct the user to run the printed login command in a regular PowerShell, Windows Terminal, or `cmd.exe` session.
- If `fab auth status` shows encoding problems, retry with `PYTHONIOENCODING=utf-8` and `PYTHONUTF8=1`.
- If `fab auth status`, `fab dir`, or `fab pwd` fail with JSON parsing errors such as `Expecting value: line 1 column 1`, inspect `~/.config/fab/auth.json` for corruption and clear the auth cache files before reinstalling.
- Do not assume `python -m pip install --user ms-fabric-cli` updates the same Python environment that `fab` resolves from. On Windows Store Python setups, stale installs from another Python version may remain earlier on `PATH`.
- If `python -m pip` is unavailable, retry with the Windows launcher (`py -3`) or ensure Python is installed for the current user.
- Tell the user that a new shell may be needed before plain `fab` resolves everywhere.

## Output

- Show the detected script directory and whether it was added to PATH in a compact status view.
- Show the resolved `fab` executable and version.
- Report whether the user is already logged in, whether interactive login was launched, or whether login must be completed in a regular local terminal.
