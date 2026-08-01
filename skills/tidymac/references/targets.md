# Scan targets and specialist checks

Use built-in macOS commands for measurement and metadata. Use an ecosystem's own commands only when that tool is already installed.

## Scan progression

1. Record sealed System-volume and writable Data-volume context separately; use the filesystem containing `$HOME` for user-storage pressure.
2. Measure likely storage-bearing user roots one at a time. Never run `du` on `$HOME`, all of `$HOME`'s children, or a loop over every home child; never launch multiple deep scans in one shell call.
3. Rank non-overlapping results and aggregate smaller peers.
4. Drill into one selected consumer at a time. Wait for each recursive measurement and interpret it before starting another.
5. Inspect detected development, app-data, Xcode, container, VM, backup, Trash, and package-manager areas where relevant.
6. Run native inventory or dry-run commands for material ecosystems.
7. Run a finer second pass. Continue until marginal investigation no longer changes the explanation or recommendations.

Keep commands bounded and observable: one recursive `du` root per invocation, no overlapping measurements, and progress interpretation between slow roots. When supported, give the selected command about 30 seconds of initial yield time. If the host returns a running-session handle, poll it to completion rather than treating the missing output as an empty result.

Treat every measurement as evidence, not a deletion plan.

## User-space coverage

| Area | Examples | Special treatment |
|---|---|---|
| App caches | `~/Library/Caches`, nested Chromium/Electron caches | Check running state; distinguish Code Cache and GPUCache from Service Workers, blob storage, and IndexedDB. |
| App state | Application Support, containers, saved state, HTTP storage | Broad app-data directories are context until investigated. |
| Logs | User and diagnostic logs | Preserve recent logs during active debugging; prefer age-bounded proposals. |
| XDG and tool data | Hidden home directories and `~/.cache` | Identify the owner, current installation, and regeneration cost. |
| Xcode | DerivedData, DeviceSupport, simulators, archives | Archives are non-regenerable; use `simctl` for current simulator state. |
| Backups | MobileSync device backups | Confirm individually; never count as routine cleanup. |
| Trash | `~/.Trash` | Inventory immediate contents before discussing irreversible emptying. |

Keep Desktop, Documents, Downloads, Pictures, Movies, Music, cloud storage, and other personal-content roots as contextual totals unless the user explicitly asks to analyze their contents.

The absence of Time Machine local snapshots does not prove every allocated byte is ordinary live data; keep snapshot and APFS claims limited to what the command actually established.

## Development artifacts

Search detected development roots for candidate directory names such as `node_modules`, `target`, `.build`, `build`, `dist`, `.next`, `.nuxt`, `.venv`, `.tox`, `.terraform`, `Pods`, `.dart_tool`, and language caches. A matching name is not sufficient: verify the adjacent manifest or marker, canonicalize the current working directory, and exclude its entire tree.

For each meaningful candidate, check project manifests, lockfiles, Git activity, worktree state, and rebuild source. Never list archive members or inspect dataset contents to decide whether a project is regenerable. Never propose deleting an entire project merely because it looks inactive.

## Xcode and simulators

- Detect full Xcode before Xcode-specific work.
- Use `xcrun simctl list devices` and `xcrun simctl list runtimes` for current state.
- Show unavailable devices before proposing `xcrun simctl delete unavailable`.
- Treat DeviceSupport as a redownload or reconnect cost.
- Treat Xcode Archives as non-regenerable.
- Verify the installed command surface with `xcrun simctl help`.

## Containers and VMs

- Detect Docker Desktop, OrbStack, Podman, and Colima independently.
- If a runtime is already running, prefer its inventory over its opaque disk image.
- If a stopped runtime materially contributes space, measure its host-allocated backing storage and offer to start it temporarily for read-only native inventory, then restore it to stopped. Record the initial state and restore it even after a failed inventory command.
- Before approval, do not run client, context, list, or inventory commands that might auto-start or connect to the stopped runtime. Do not present the opaque backing image as the final finding when native interrogation is available with approval.
- Do not count a sparse VM disk's apparent maximum as reclaimable.
- Do not propose removing runtime data directories except as an explicitly requested factory reset or removal of an abandoned runtime.
- Inventory containers, images, build cache, networks, and volumes separately. Treat a Docker volume reported as active as referenced, not proof that its owning container is running.
- Describe a referenced volume as an attached stateful volume, identify the container or stack that references it when useful to the user, and keep it out of cache totals.
- Never include volumes in a general prune. Investigate each volume's name, labels, attachment, and likely contents. Delete one only after exact state-loss approval, or as part of a separately approved native factory reset that explicitly destroys all runtime data.
- Keep native internal reclaimability, host-allocated backing-store size, and observed host recovery as separate numbers.

## APFS and Time Machine

- Record `/`, `$HOME` or `/System/Volumes/Data`, and APFS container figures separately when available. The sealed System volume's `Used` figure is not whole-machine physical usage.
- Treat `du -sk` blocks as allocated-size estimates, not logical sizes or guaranteed physically unique savings.
- Do not infer clones, hardlinks, compression, sparse allocation, or snapshot effects solely because unrelated measurements differ.
- List local snapshots as context. macOS normally manages their available space.
- Investigate snapshots only after ordinary cleanup fails to relieve real pressure.

## System paths

Inspect `/Library/Caches` and `/Library/Logs` only for a requested deep or system audit. Skip unreadable paths. Never inspect or modify `/System/Library`, swap, or broad system roots. Do not use `sudo` during ordinary investigation.
