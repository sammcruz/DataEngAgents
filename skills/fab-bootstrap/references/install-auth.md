# Install And Auth

Use this reference when the user needs first-time Fabric CLI setup on Windows or macOS in user-auth mode.

## What This Skill Covers

- install or upgrade `ms-fabric-cli` with `pip`
- add the user-level script directory to persistent PATH
- verify `fab --version`
- check `fab auth status`
- launch `fab auth login` for interactive user sign-in, or hand the user off to a regular terminal when the current host cannot run that flow

## Preferred Flow

Run:

```powershell
python scripts/bootstrap_fab.py --login
```

That flow:
1. installs or upgrades Fabric CLI for the current user
2. updates user PATH automatically
3. verifies the `fab` executable
4. launches interactive user auth if needed
5. prints a manual fallback command when interactive login cannot start in the current host

## PATH Behavior

- Windows: updates the current user's PATH in `HKCU\Environment`
- macOS: appends PATH exports to shell startup files for the current shell family

The current shell session may still need to be restarted before plain `fab` resolves on PATH everywhere.

## Interactive Login Caveat

Some embedded or hosted terminals on Windows cannot launch `fab auth login` cleanly. If the bootstrap script reports that interactive login could not start, open a regular local PowerShell, Windows Terminal, or `cmd.exe` window and run the printed login command there.

If `fab auth status` shows Unicode or `charmap` encoding errors, retry with:

```powershell
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'
fab auth status
```

## Verification

If the user wants a non-mutating check, run:

```powershell
python scripts/bootstrap_fab.py --verify-only
```

## PATH Repair Only

If `fab` is already installed but not recognized reliably, run:

```powershell
python scripts/repair_fab_path.py
```

To inspect the change without writing anything:

```powershell
python scripts/repair_fab_path.py --dry-run
```

## Notes

- This skill is intentionally optimized for user auth, not service principal automation.
- Browser interaction is still required during `fab auth login`.
- Installing with `--user` avoids requiring admin rights in the common case.
- Prefer reporting the exact terminal limitation and the next command the user should run, instead of treating a failed login launch as a hard bootstrap failure.
