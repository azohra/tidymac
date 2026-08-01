# Scan targets and specialist checks

Use the bundled scanner for repeatable filesystem inventory. Add native inspection only for detected tools and user-relevant categories.

## Scan progression

1. Run a quick user-space scan at a 100 MB threshold.
2. Present the largest non-overlapping findings.
3. Run a targeted deep scan only where it can change the recommendation: development roots, orphan evidence, Xcode, containers, or system paths.
4. Lower the threshold when the disk is critically constrained or the user asks for exhaustive results.

Examples, resolving `<skill-dir>` to the directory containing `SKILL.md`:

```bash
python3 <skill-dir>/scripts/scan.py --scope quick --min-size-mb 100 --output /tmp/tidymac-quick.json
python3 <skill-dir>/scripts/scan.py --scope dev --dev-root ~/Development --min-size-mb 100 --output /tmp/tidymac-dev.json
python3 <skill-dir>/scripts/scan_orphans.py --min-size-mb 50 --use-spotlight --output /tmp/tidymac-orphans.json
```

Treat all scanner output as evidence, not a deletion plan.

## User-space coverage

| Area | Examples | Special treatment |
|---|---|---|
| App caches | `~/Library/Caches`, nested Chromium/Electron caches | Check whether the app is running; distinguish sessions and IndexedDB from disposable code/GPU cache. |
| App state | Application Support, containers, saved state, HTTP storage | Treat parent app-data directories as context until inspected. |
| Logs | User and diagnostic logs | Preserve recent logs during active debugging; prefer age-bounded cleanup. |
| XDG caches | `~/.cache` | Identify the owning tool and redownload cost. |
| Xcode | DerivedData, DeviceSupport, simulators, archives | Keep archives non-regenerable; use `simctl` for simulator state. |
| Backups | MobileSync device backups | Confirm individually; never count as routine cleanup. |
| Trash | `~/.Trash` | Inventory contents before offering to empty it. |

## Development artifacts

Use `scan.py --scope dev`. It verifies artifact names against project markers and excludes the canonical current working directory tree. Typical verified pairs include:

| Artifact | Marker |
|---|---|
| `node_modules`, `.next`, `.nuxt`, `.parcel-cache` | `package.json` or framework config |
| `target` | `Cargo.toml` |
| `.build` | `Package.swift` |
| `.venv`, `venv` | `pyvenv.cfg` |
| `.terraform` | Terraform files |
| `Pods` | `Podfile` |
| `.dart_tool` | `pubspec.yaml` |
| `vendor` | `go.mod`, `composer.json`, or `Gemfile` |

Do not delete an entire project because it appears inactive. Offer only verified regenerable subdirectories unless the user explicitly asks to archive or remove projects.

## Xcode and simulators

- Detect full Xcode before scanning Xcode-specific locations.
- Use `xcrun simctl list devices` and `xcrun simctl list runtimes` for current state.
- Offer `xcrun simctl delete unavailable` only after showing the unavailable devices.
- Treat DeviceSupport as a redownload/reconnect cost, not silent regeneration.
- Treat Xcode Archives as non-regenerable.
- Verify current removal commands with `xcrun simctl help` before execution; command surfaces vary with Xcode.

## Containers and VMs

- Detect Docker Desktop, OrbStack, Podman, and Colima independently.
- When a runtime is running, prefer its inventory (`docker system df -v`, container lists, image lists, volume lists) over measuring its opaque VM image.
- Ask before starting a stopped runtime. Starting an app is a state change.
- Do not count a VM disk's apparent maximum size as reclaimable.
- Do not delete a runtime data directory unless the user explicitly requests a factory reset or removal of a replaced runtime and understands the consequence.
- Never include volumes in a general prune proposal. Inspect names, labels, attachment state, and likely database contents individually.

## APFS and Time Machine

- Record both filesystem and APFS container figures when available.
- Treat `du` output as allocated-size estimates, not guaranteed physical savings.
- List Time Machine local snapshots as context only. macOS counts their storage as available and normally reclaims it automatically when space is needed.
- Investigate snapshots only after ordinary cleanup fails to relieve real storage pressure.

## System paths

Scan `/Library/Caches` and `/Library/Logs` only when the user asks for a deep or system scan. Skip unreadable paths cleanly. Never inspect or modify `/System/Library`, swap files, or broad system roots. Request approval before any `sudo` command and show the exact command first.
