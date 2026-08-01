<p align="center">
  <pre align="center">
  _____ _     _       __  __
 |_   _(_) __| |_   _|  \/  | __ _  ___
   | | | |/ _` | | | | |\/| |/ _` |/ __|
   | | | | (_| | |_| | |  | | (_| | (__
   |_| |_|\__,_|\__, |_|  |_|\__,_|\___|
                |___/
  </pre>
  <br/>
  <strong>Your Mac is hoarding. Let's find out why.</strong>
  <br/><br/>
  A judgment-driven macOS disk-space auditor for Claude Code and Codex.
</p>

---

TidyMac finds meaningful disk-space opportunities across macOS, explains the consequence of each one, and cleans only what you approve.

It is a skill rather than a conventional cleaner app because the hard part is not finding large directories. The hard part is deciding whether an unfamiliar directory is disposable, expensive to regenerate, useful historical state, or the only remaining copy of something important.

## Install

```bash
npx skills add azohra/tidymac
```

The installer can target Claude Code, Codex, or both. Invoke the installed skill with the syntax used by your host:

| Host | Invocation |
|---|---|
| Claude Code | `/tidymac` |
| Codex | `$tidymac` |

For example:

```text
$tidymac Audit my Mac and present a cleanup plan.
```

A bare invocation runs a read-only audit. TidyMac presents a cleanup plan before making any changes.

## What it inspects

- macOS and XDG caches
- Application Support, containers, logs, saved state, and HTTP storage
- Xcode DerivedData, DeviceSupport, simulators, and archives
- Docker Desktop, OrbStack, Podman, and Colima
- Package-manager caches and developer toolchains
- Old runtime versions
- Regenerable project artifacts such as `node_modules`, `target`, `.build`, `.next`, and virtual environments
- Evidence of app data whose owner is no longer obvious
- iOS device backups, Trash, installers, and other large contextual storage

The default pass starts with large user-space findings. It expands into slower or more specialized scans only when the results justify doing so.

## How decisions work

TidyMac keeps two questions separate:

1. **How certain are we about what this is?** Verified, likely, or unknown.
2. **What happens if it goes away?** Silent regeneration, redownload, rebuild, workflow reset, possible state loss, or non-regenerable loss.

That distinction prevents a common cleanup mistake: treating “cache” as synonymous with “free.” A dependency cache may be safe to remove but expensive to download again; an unmatched app directory may be an orphan, shared state, or a deliberately retained archive.

Findings are grouped by consequence so you can approve cheap cleanup without also agreeing to long rebuilds or loss of historical state.

## Safety model

- Auditing is the default. Nothing is silently cleaned.
- Every mutation is tied to an approved finding or command.
- Unknown findings are researched rather than guessed at.
- “Unmatched” app data is never automatically called orphaned.
- The current project and its ancestors are excluded from path cleanup.
- Broad roots, symlinks, system directories, and changed-since-scan paths are rejected.
- Direct path cleanup defaults to moving data to Trash.
- Trash is never presented as reclaimed disk space until it is reviewed and emptied.
- Container volumes, Xcode archives, iOS backups, and other stateful data receive individual treatment.
- Time Machine local snapshots are shown as context, not added to routine reclaimable totals; macOS normally manages their space automatically.

## Architecture

TidyMac deliberately splits deterministic work from subjective work:

```text
Read-only scanners → structured evidence → model judgment → approval → guarded execution
```

The bundled Python scanners handle pathname-safe inventory, allocated-size estimates, project-marker verification, installed-app evidence, and structured JSON output. The skill handles research, confidence, consequences, prioritization, and conversation with the user.

The guarded path executor creates a plan before acting. It records path identity and size, emits an approval token, and revalidates everything immediately before moving or deleting data. If a target changed in the meantime, it stops.

## Example requests

```text
/tidymac
$tidymac
Audit my Mac, but don't clean anything.
Focus on Xcode and old simulators.
Find stale build artifacts outside this project.
Investigate whether these large Application Support folders are leftovers.
Clean only the low-impact items I approve.
I need 20 GB quickly; prioritize things that won't require a rebuild.
```

## Requirements

- macOS
- Claude Code or Codex
- Python 3 from macOS developer tools or another local installation; bundled scripts use only the standard library
