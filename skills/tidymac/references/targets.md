# Scan targets and specialist checks

Use built-in macOS commands for measurement and metadata. Use an ecosystem's own commands only when that tool is already installed.

## Scan progression

1. Record sealed System-volume and writable Data-volume context separately; use the filesystem containing `$HOME` for user-storage pressure.
2. Measure likely storage-bearing user roots one at a time. Never run `du` on `$HOME`, all of `$HOME`'s children, or a loop over every home child; never launch multiple deep scans in one shell call.
3. Rank non-overlapping results and aggregate smaller peers.
4. Drill into one selected consumer at a time. Wait for each recursive measurement and interpret it before starting another.
5. Inspect detected development, app-data, Xcode, container, VM, backup, cloud, local-AI, creative-media, game, browser, Trash, and package-manager areas where relevant.
6. Run native inventory or dry-run commands for material ecosystems.
7. Run a finer second pass. Continue until marginal investigation no longer changes the explanation or recommendations.

Keep commands bounded and observable: one recursive `du` root per invocation, no overlapping measurements, and progress interpretation between slow roots. When supported, give the selected command about 30 seconds of initial yield time. If the host returns a running-session handle, poll it to completion rather than treating the missing output as an empty result.

Treat every measurement as evidence, not a deletion plan.

## User-space coverage

| Area | Examples | Special treatment |
|---|---|---|
| App caches | `~/Library/Caches`, nested Chromium/Electron caches | Check running state; distinguish Code Cache and GPUCache from Service Workers, blob storage, and IndexedDB. |
| App state | Application Support, containers, saved state, HTTP storage | Broad app-data directories are context until investigated. |
| Logs | User and diagnostic logs | Preserve recent logs during active debugging; recommend old, owner-verified, isolated logs when material. |
| XDG and tool data | Hidden home directories and `~/.cache` | Identify the owner, current installation, and regeneration cost. |
| Xcode | DerivedData, DeviceSupport, simulators, archives | Archives are non-regenerable; use `simctl` for current simulator state. |
| Backups | MobileSync device backups | Confirm individually; never count as routine cleanup. |
| Trash | `~/.Trash` | Inventory immediate contents before discussing irreversible emptying. |

Keep Desktop, Documents, Downloads, Pictures, Movies, Music, cloud storage, and other personal-content roots as contextual totals unless the user explicitly asks to analyze their contents.

## File Provider and cloud storage

Detect installed providers and material local allocation before investigating. Common examples include iCloud Drive, OneDrive, Dropbox, and Google Drive, but do not emit a checklist for absent providers.

- Use provider metadata, Finder status, or the installed provider's native view to distinguish online-only, locally available, pinned/always available, pending, and conflicted content.
- Measure allocated local blocks, not only logical file sizes shown by Finder or cloud metadata.
- Verify synchronization before proposing local eviction. A pending or conflicted item is not a safe eviction candidate.
- Prefer Finder or provider actions such as Remove Download, Free up space, or Make online-only. Confirm the exact installed wording and behavior.
- Keep local eviction separate from deletion. Deletion may propagate through the cloud and other devices.
- Aggregate by provider and useful ownership category. Do not enumerate personal filenames without explicit content-review permission.
- Treat shared folders, external-provider caches, File Provider internals, and database-like metadata as owner-managed state, not direct-path cleanup.

## Local AI models and datasets

Detect local model ecosystems from installed applications, CLIs, configured storage locations, and material directories. Investigate Ollama, Hugging Face caches, LM Studio, and other detected model managers conditionally.

- Use the owning tool's inventory to identify model family, revision or quantization, size, and shared blobs when available.
- Respect configured model/cache locations; do not assume a default path is authoritative.
- Distinguish models, incomplete downloads, old revisions, shared content-addressed blobs, embeddings, datasets, application state, and user-created fine-tunes or adapters.
- Prefer native list, dry-run prune, and model removal. Never manually delete individual content-addressed blobs or identity keys.
- Treat downloaded public models as redownloadable only when their source and exact variant remain known. Fine-tunes, adapters, prompts, datasets, and local exports may be non-regenerable.
- Do not count every revision or shared blob independently. Use the native expected-recovery estimate when available.

## Creative and media ecosystems

Detect the owning applications before scanning application-specific locations. Relevant categories include Final Cut generated/proxy/optimized media, Adobe media caches, Logic/MainStage sound libraries, render caches, waveform caches, and other owner-identified generated media.

- Separate originals, projects, libraries, exports, recordings, and purchased content from generated or downloadable media.
- Prefer the application's native generated-media deletion, cache management, optional-content removal, or library-relocation workflow.
- Treat relocation as a valid recovery action when the data is useful but need not remain on the internal disk.
- Confirm external destination capacity and whether the application requires that volume for future work.
- Never infer that a directory named cache is safe when it sits inside a project or media library; establish the owner's documented regeneration semantics.

## Games and virtual machines

- Detect Steam and other installed game libraries, including libraries on external volumes. Treat installed games, saves, mods, workshop data, and shader/download caches separately.
- Prefer uninstall, move-library, or verify/cleanup operations in the owning launcher. Never remove a game library directory as generic cache.
- Detect Parallels, VMware Fusion, UTM, and other VM owners from installed apps and bundles. Keep VM bundles, snapshots, suspend state, shared folders, and reclaimable guest free space separate.
- Prefer a supported compact, reclaim, move, or delete workflow. A sparse VM's maximum or Finder logical size is not host-reclaimable space.
- Confirm whether a VM is stopped before any operation that requires it; starting it is a state change requiring approval.

## Apple-managed app data

- **Device backups:** Use Finder's backup management where available. Identify device and date with minimal disclosure; archived backups may be uniquely valuable.
- **Messages:** Aggregate attachments without reading conversations. Native deletion can propagate through Messages in iCloud and may enter Recently Deleted.
- **Mail:** Prefer Mail's native attachment/message controls. Establish account type and server behavior before claiming a deletion is local-only.
- **Photos:** Distinguish optimized local storage, downloaded originals, edited libraries, and exports. Never manipulate a Photos library internally.
- **Music creation:** Treat optional downloadable sound libraries as removable or relocatable only through the owning application.

## Browsers and web applications

Separate ephemeral browser cache from cookies, site data, profiles, passwords, extensions, Service Workers, IndexedDB, offline content, and downloads. Check whether the browser is running. Prefer native clear-data controls scoped to verified cache categories; never remove an entire profile to recover cache space. State that clearing cookies or site data can sign the user out or erase offline workflow state.

## Optional personal-content review

Only after explicit permission, inspect personal roots for aggregated large media, installers, disk images, archives, downloads, duplicates, and attachments. Use stable finding IDs and reveal the minimum filename needed for a user decision.

Duplicate detection requires separate content-reading permission because strong verification may hash file bytes. Account for hard links and possible APFS clones, and never present identical logical files as guaranteed physically unique savings. Similar-image detection is optional and outside the default audit.

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
- When available, record snapshot identifiers and native size fields as context, but do not automatically delete snapshots or count them as routine recovery.

## Reconciliation and access gaps

- Compare the non-overlapping path census with Data-volume and APFS context without pretending they share one accounting basis.
- Track inaccessible roots, other users, mounted external volumes, provider-managed data, VM/runtime backing stores, documented purgeable context, and residual unexplained space separately.
- Do not request Full Disk Access or `sudo` merely to make the ledger look complete. Explain the exact missing scope and what additional evidence it would unlock.
- When external volumes are in scope, report their capacity, allocation, provider/runtime ownership, and Trash separately from the internal Data volume.
- Do not call the residual gap hidden junk. It is an unresolved storage-accounting difference until evidence identifies it.

## System paths

Inspect `/Library/Caches` and `/Library/Logs` only for a requested deep or system audit. Skip unreadable paths. Never inspect or modify `/System/Library`, swap, or broad system roots. Do not use `sudo` during ordinary investigation.
