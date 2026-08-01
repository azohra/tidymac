# Contextual investigation protocol

Filesystem measurement locates allocated blocks. The audit is complete only after those blocks have machine-specific meaning.

## Build the investigation queue

1. Remove ancestor/descendant overlap from the ranked view.
2. Queue ranked findings without a fixed per-item cutoff.
3. Aggregate smaller findings by owner, ecosystem, and consequence.
4. Drill into broad parents until their important children are explained.
5. Continue until conclusions cover at least 80% of non-overlapping, in-scope measured usage; target 90% when access permits. Protected personal-content roots count at their aggregate total and must not be drilled into for the sake of coverage.
6. Run a finer second pass and continue while it changes explained bytes, actionable totals, or recommendations.
7. Track opaque, inaccessible, context-only, and possible-duplicate bytes separately.

A measurement floor is only a way to get fast bearings. It is never a claim that smaller space does not matter. Do not force a recursive entire-home measurement to manufacture a coverage percentage; derive coverage from separately measured roots and disclose the unmeasured gap.

Alongside coverage, maintain a volume reconciliation ledger. Record Data-volume usage, the non-overlapping path census, native-owned allocations that sit outside or overlap the census, other users or mounted volumes, inaccessible scope, documented purgeable or OS-managed context, and residual unexplained storage. Preserve the source and measurement basis for each figure. The purpose is to expose gaps and direct more investigation, not force `du`, `df`, APFS, and native-tool figures into a false equality.

## Forensic dossier

For each queued finding or meaningful aggregate, seek:

| Field | Evidence |
|---|---|
| Identity and owner | Bundle identifier, app metadata, package receipt, CLI path, launch item, process, manifest, or primary documentation |
| Contents | Safe top-level categories, types, allocated-size estimates, metadata, and narrowly selected manifest fields without opening personal content |
| Activity | Directory and child modification times, project history, running state, or native last-used metadata |
| Installed state | Application bundle, cask/formula, package-manager record, version-manager inventory, plugin, extension, or service |
| Data class | Cache, dependency, build output, workflow state, user-created content, backup, runtime disk, volume, or unknown |
| Correct action | Keep, local eviction, relocation, native prune, regenerable-derivative removal, redownload, reset, guarded Trash, synced delete, or permanent delete |
| Scope and recovery | This Mac, external volume, owning runtime, cloud, or synchronized devices; undo, Trash, retention, redownload, backup, or none |
| Native view | Inventory, status, or dry-run from the owning tool |
| Regeneration cost | Silent, network redownload, local rebuild, workflow reset, state loss possible, or non-regenerable |
| Real reclaimability | Native estimate, allocated size, sparse/clone risk, overlap, and whether Trash delays recovery |
| Conclusion | Keep, cleanup candidate, user decision, blocked on state change, or unresolved with exact missing evidence |

## Local evidence order

Prefer evidence in this order:

1. Owning tool's inventory, status, or dry-run
2. Installed app metadata, bundle identifiers, manifests, receipts, and version-manager state
3. Running process and narrowly scoped open-file ownership
4. Immediate-child structure, allocated size, and timestamps
5. Exact-path or identifier research from current primary sources when available
6. User recognition when machine evidence cannot establish intent or data value

Use built-in `stat`, `du`, `mdfind`, `mdls`, `plutil`, `pkgutil`, `launchctl`, `pgrep`, and `lsof` narrowly. Read known declarative files only when selected fields answer a specific ownership, activity, or regeneration question. Do not dump files, echo secrets, recursively print personal filenames, list archive members, or query content databases merely to classify storage. Ask before content-level inspection of personal documents, messages, source files, secret-bearing logs or configuration, databases, archives, and credentials.

In the live interactive report, include a relevant app, package, container, volume, or project identifier when the user needs it to understand the finding or approve an action. Avoid unnecessary paths and structure. If the user asks for output that will be shared, published, filed as an issue, or committed to a public repository, sanitize personal and project identifiers throughout.

The absence of a process does not prove abandonment. Directory modification time is a clue, not proof of last use.

## Native inspection

When an ecosystem materially contributes space, use the installed tool's current help and read-only surface. Typical examples:

- Homebrew: installed formulae/casks, `brew cleanup --dry-run`, an age-bounded dry-run when useful, and `brew cleanup --dry-run --prune=all` so the report distinguishes ordinary cleanup from the full redownloadable download cache
- Docker: `docker system df -v`, container/image lists, and volume inventory if the daemon is already running
- OrbStack, Podman, and Colima: runtime status and supported native inventory
- Xcode: `xcrun simctl` device/runtime inventories
- Package managers: cache location, installed versions, and supported verify, info, list, or dry-run commands
- Version managers: installed versions plus project version files
- File Providers: local/online/pinned/synchronization state and supported eviction controls
- Local AI tools: model/revision inventory, configured stores, shared blobs, and native expected recovery
- Creative tools: generated-media, cache, optional-library, and supported relocation views
- Game launchers and VM applications: installed payloads, saves or state, snapshots, compact/reclaim, and move-library controls
- Apple apps and browsers: native management surfaces for backups, attachments, synchronized data, profiles, and caches

A dry-run estimate supersedes the apparent size of a broad cache root when estimating likely recovery. Describe only categories demonstrated by the dry-run output; a few visible entries do not explain the entire total. Starting an app, daemon, VM, or runtime is a state change. When a stopped runtime is material, offer a bounded temporary start for read-only inventory and restoration to the recorded prior state; otherwise report the blocked native evidence instead of stopping at an opaque disk image.

## Development context

For each meaningful artifact, identify the project root and manifest or lockfile that can rebuild it. Check:

- Recent Git history and working-tree activity
- Active checkout, linked worktree, archived clone, or agent-generated worktree status
- Repeated artifact sizes and possible APFS clone or duplicate-counting risk
- Network and rebuild cost, including native modules and downloaded toolchains
- Whether generated-looking output contains local-only work

Never sum suspected duplicate groups as guaranteed physical savings. Report a range unless physical uniqueness is established. Do not print exact project roots or content-bearing child names. In an interactive report, a project basename may be used when it is necessary to explain ownership or an action; otherwise use generic labels such as “active development project A” and stable finding IDs. Always use generic labels in shareable output.

## macOS volume interpretation

Modern macOS normally mounts a sealed, read-only System volume at `/` and the writable Data volume for `$HOME`. `df` for `/` can therefore show a small System-volume `Used` value alongside container-wide available space. It is not the physical usage of the whole Mac and must not be reconciled against user-directory `du` results.

Use `df` for the filesystem containing `$HOME`, or `/System/Volumes/Data` when accessible, plus APFS container information from `diskutil`. `diskutil info "$HOME"` is not a portable way to address the Data mount. `du -sk` reports allocated blocks charged to a path; call it an allocated-size estimate, not logical size. Do not attribute differences to clones, hardlinks, sparse allocation, compression, snapshots, or purgeable data without direct supporting evidence.

## Research discipline

Research only to answer a dossier question. Prefer vendor documentation, source repositories, native manuals, and Apple documentation. Distinguish documented general behavior from an inference about this Mac. Avoid generic cleanup listicles and do not let web claims override local evidence.

## Completion

The final report answers: what is using space here, why, and what is worth doing? It includes coverage, conclusions, meaningful smaller aggregates, consequence-aware opportunities, valuable context, and precisely blocked or unresolved dossiers. It does not substitute raw command output for analysis.

When a generated report is available, build it only after these conclusions exist. A polished opportunity map is not evidence that the audit reached adequate coverage.
