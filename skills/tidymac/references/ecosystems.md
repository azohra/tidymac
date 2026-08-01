# Ecosystem checks

Investigate only ecosystems detected on this Mac that materially affect the result. Prefer installed help and native inventory over assumed paths or stale command syntax.

## User-space data

| Area | Distinction to establish |
|---|---|
| App caches | Ephemeral cache versus Service Workers, IndexedDB, offline content, or workflow state |
| Application Support and containers | Cache, settings, shared state, user content, or unknown ownership |
| Logs | Old isolated diagnostics versus current debugging evidence or secret-bearing content |
| XDG and hidden tool roots | Current owner, native cleanup, regeneration cost |
| Trash | Reviewed contents and size; staged space is not reclaimed space |
| Device backups | Device, date, archive status, and whether another usable backup exists |

Keep Desktop, Documents, Downloads, Pictures, Movies, Music, and cloud content as aggregate context unless the user requests deeper review.

## App ownership and leftovers

Treat leftover detection as ownership work, not name matching.

Correlate unknown app data with:

- bundles in system and user application folders, Spotlight results, bundle IDs, team IDs, and app groups
- vendor uninstallers, nested bundles, login/background items, LaunchAgents, extensions, plugins, and open processes
- package receipts, Homebrew casks, version managers, manifests, and product-specific structure
- timestamps and current primary documentation for an exact path or identifier

Use these labels:

- **Verified owner:** direct native, bundle, manifest, receipt, entitlement, or process evidence
- **Likely owner:** several consistent indirect signals
- **Likely leftover:** identified product, no remaining component, removal-aligned timestamps, product-specific contents
- **Unknown:** ownership or value remains ambiguous

Reserve **verified leftover** for authoritative uninstall evidence or direct user knowledge. App-group data, cloud state, shared model blobs, creative libraries, plugins, and game saves may outlive one app while serving another. Prefer a vendor uninstaller before investigating residual paths separately.

Even a verified leftover may contain projects, databases, exports, recordings, models, licenses, credentials, backups, archives, VM disks, or container volumes. Establish data value before proposing removal.

## Development and Xcode

Search detected development roots for candidates such as `node_modules`, `target`, `.build`, `build`, `dist`, `.next`, `.nuxt`, `.venv`, `.tox`, `.terraform`, `Pods`, and `.dart_tool`. A name is only a lead: verify the adjacent manifest, rebuild source, Git/worktree activity, and current-project exclusion.

For version managers, list installed and active versions plus references from `.tool-versions`, `.mise.toml`, language version files, toolchain manifests, and CI configuration.

For Xcode:

- use `xcrun simctl` inventory and installed help
- show unavailable devices before proposing their native removal
- treat DeviceSupport as a reconnect or redownload cost
- treat archives as non-regenerable

For package managers, establish the configured cache/store path, native inventory or dry-run, and whether cleanup means redownload, rebuild, uninstall, or rollback loss.

## Containers and VMs

Detect Docker Desktop, OrbStack, Podman, Colima, Parallels, VMware Fusion, UTM, and other owners independently.

- Prefer native inventory to an opaque backing image when the runtime is running.
- For a stopped material runtime, measure host allocation and ask before one bounded start/inventory/restore cycle.
- Before approval, avoid client, context, list, or inspect commands that may auto-start or connect the runtime.
- Inventory containers, images, build cache, networks, and volumes separately.
- A referenced volume is stateful and attached; it does not prove its workload is running.
- Never include volumes in a general prune. Establish labels, references, and likely data value individually.
- Keep internal reclaimability, host-allocated backing size, sparse maximum, guest free space, and observed host recovery distinct.
- Treat factory reset, individual-volume deletion, VM deletion, runtime uninstall, and compaction as separate scopes.

## Cloud and File Provider storage

Detect iCloud Drive, OneDrive, Dropbox, Google Drive, and other installed providers from local evidence.

- distinguish online-only, local, pinned, pending, and conflicted items
- measure local allocation, not only logical or cloud size
- verify completed synchronization before calling local eviction safe
- keep Remove Download, Free up space, or Make online-only separate from synced deletion
- aggregate personal content by provider or category; do not enumerate filenames by default
- treat provider databases and internals as owner-managed state

## Local AI

Detect configured stores and native inventories for Ollama, Hugging Face, LM Studio, and other installed model managers.

- distinguish models, revisions, quantizations, incomplete downloads, datasets, embeddings, app state, and shared blobs
- use native expected recovery when content-addressed data overlaps
- confirm the exact source and variant before calling a model redownloadable
- treat fine-tunes, adapters, prompts, datasets, exports, and custom models as potentially non-regenerable
- never remove individual shared blobs or identity keys manually

## Creative media and games

Separate originals, projects, saves, recordings, exports, mods, and purchased content from generated or downloadable derivatives.

- use Final Cut generated-media controls for render, optimized, and proxy media
- use Adobe’s owning-app media-cache controls
- use Logic or MainStage relocation and optional-library controls
- use game-launcher uninstall or move-library workflows; keep saves, mods, workshop data, and sync state separate
- confirm destination capacity and attachment requirements before relocation

Never infer that a directory named cache is safe when it sits inside a project or media library.

## Apple apps and browsers

- **Finder backups:** identify device, date, and archive status; manage them through Finder
- **Messages:** aggregate attachments without reading conversations; deletion may sync and may enter Recently Deleted
- **Mail:** establish account/server behavior before calling removal local-only
- **Photos:** distinguish optimized local storage, downloaded originals, edited libraries, and exports; never manipulate a library internally
- **Browsers:** separate ephemeral cache from cookies, profiles, passwords, extensions, Service Workers, IndexedDB, and offline data; use native controls and state sign-out consequences

## Personal review and duplicates

With explicit permission, review personal roots for large media, installers, disk images, archives, downloads, attachments, and duplicates. Reveal only the minimum filename needed for a decision.

Strong duplicate verification may hash content and therefore needs content-reading permission. Account for hard links and possible APFS clones; identical logical files do not guarantee unique physical recovery. Similar-image detection is outside the default audit.

## APFS, snapshots, external volumes, and system scope

- List Time Machine snapshots as context; do not count or remove them routinely.
- Investigate snapshots only after ordinary cleanup fails to relieve real pressure.
- Track inaccessible scope, other users, mounted volumes, external Trash, provider storage, and runtime disks separately.
- Do not request Full Disk Access or `sudo` merely to complete the ledger; explain what evidence access would unlock.
- Inspect `/Library/Caches` and `/Library/Logs` only for a requested deep or system audit.
- Never inspect or modify `/System/Library`, swap, or broad system roots.
