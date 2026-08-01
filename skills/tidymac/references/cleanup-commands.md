# Native cleanup and direct-path safety

Use only built-in macOS commands and tools already installed on the machine. Read the installed tool's current help and inspect or dry-run before proposing cleanup. A native command is not automatically low consequence.

## Package managers

| Tool | Inspect or preview | Candidate action | Consequence |
|---|---|---|---|
| Homebrew | `brew cleanup --dry-run`; optionally set `HOMEBREW_CLEANUP_MAX_AGE_DAYS` for an age-bounded preview; `brew cleanup --dry-run --prune=all` for the full cache | Recommend the material cache scope that matches the user's goal; keep `brew autoremove --dry-run` separate | Cache cleanup removes downloaded bottles, manifests, and cask installers, not installed formulae or applications; future operations redownload them. Autoremove uninstalls formulae. |
| npm | `npm cache verify`; `npm config get cache` | Version-supported cache clean | Redownload required. |
| Yarn | Resolve cache path and generation-specific help | Version-specific cache clean | Redownload; semantics differ by generation. |
| pnpm | `pnpm store path`; `pnpm store status` | `pnpm store prune` | Future installs may redownload. |
| pip | `pip cache info`; `pip cache list` | `pip cache purge` | Wheels and archives must be redownloaded or rebuilt. |
| uv | `uv cache dir`; `uv cache prune --help`; supported dry-run if present | Prefer `uv cache prune`; use broad clean only as a separate action | Prune targets unused entries; broad clean forces more redownload or rebuild work. |
| Conda | Supported dry-run for selected clean categories | Selected native clean | Caches can support reinstall or rollback workflows. |
| Cargo | Measure registry, Git, and project targets separately | No blanket default | Downloads and rebuilds differ. |
| Go | `go env GOCACHE GOMODCACHE` | Clean build and module caches separately | Rebuild versus redownload. |
| RubyGems | `gem cleanup --dry-run` | `gem cleanup` | Removes installed old gem versions, not just downloads. |

For any other installed manager, use its current local help. Never chain cleanup commands; preserve each result and partial failure independently.

Cache paths are evidence, not cleanup interfaces. Prefer a manager's supported verify, garbage-collection, prune, or clean operation over deleting its cache directory manually. When a manager documents its cache as self-healing, explain that cleanup is for reclaiming space rather than corruption repair; if the cache is fully redownloadable and material, recommend it without treating normal free space as a reason to keep it.

### Homebrew recommendation

Run the ordinary and `--prune=all` dry-runs when the Homebrew cache is material. Explain the result in plain language:

- The ordinary preview is Homebrew's conservative stale/age policy.
- `--prune=all` previews the full downloaded cache, including some current-version installers. These files are not active applications or formulae.
- Recommend the full prune when its recovery is meaningful and the user has no stated need for offline or bandwidth-saving reinstalls. Offer an age-bounded cleanup as the lower-redownload alternative, not as the automatic default.
- State that installed software remains installed and future Homebrew operations may download the artifacts again.

Keep `brew autoremove` out of the cache group because it uninstalls dependencies and has a different consequence.

## Version managers

List installed versions, active selections, and project references before proposing removal. Preserve versions referenced by `.tool-versions`, `.mise.toml`, `.python-version`, `.ruby-version`, `rust-toolchain.toml`, CI configuration, or equivalent manifests. Prefer the already-installed manager's own uninstall command.

## Containers

1. Inspect native disk usage, containers, images, build cache, networks, and volumes.
2. Prefer category-specific and age-filtered proposals.
3. Treat broad system prune as its own confirmation.
4. Treat all-unused-image pruning as more consequential.
5. Never add volumes to a general prune.
6. Compact a VM only after internal pruning and only with the installed runtime's documented command.

Keep these actions separate:

| Action | Consequence |
|---|---|
| Build-cache prune | Rebuild time; may remove recently referenced but currently unused cache. |
| Unused-image prune | Redownload or rebuild; may remove every image not referenced by a container. |
| Stopped-container removal | Workflow state and writable layer are lost. |
| Individual named-volume removal | Persistent application data may be permanently lost. |
| Runtime factory reset | All machines, containers, images, cache, networks, volumes, and runtime state are permanently lost. |
| Runtime uninstall | Application removal; data removal semantics must be established separately. |

For OrbStack, read `orbctl reset --help` from the installed version. If it confirms that reset deletes all Linux and Docker data while preserving the application and configuration, propose `orbctl reset --yes` only when the user explicitly requests that exact scope. Do not manually delete the backing disk. Measure Data-volume free space immediately before and after the reset; report the observed change separately from Docker's earlier internal estimate.

Put the exact command in the same prompt that asks for approval. Do not ask the user to approve a verbal scope and then reveal the irreversible command in a second round unless revalidation changed the action.

## Cloud and File Provider actions

Use the installed provider's Finder integration or native application action. Confirm local presence, completed synchronization, expected scope, and current wording immediately before proposing it.

| Intent | Preferred action | Do not substitute |
|---|---|---|
| Keep remote, free local space | iCloud Remove Download, OneDrive Free up space, Dropbox/other provider Make online-only or equivalent | Deleting the file or provider database |
| Keep local permanently | Provider's Always keep/download/pin action | Copying into provider internals |
| Delete everywhere | Native deletion with propagation and retention warning | Calling it local cleanup |

Provider eviction may be asynchronous. Measure host free space after the provider finishes, and keep apparent file size, local allocation, and observed recovery separate.

## Local AI models

Read installed help before relying on these surfaces:

| Ecosystem | Inspect or preview | Candidate action | Guard |
|---|---|---|---|
| Ollama | `ollama list`; configured model location; local help | `ollama rm <exact-model>` | Remove through Ollama; never delete shared blobs or keys manually. |
| Hugging Face | `hf cache ls`; supported `hf cache rm --dry-run` or `hf cache prune --dry-run` | Exact native revision removal or prune | Review detached revisions, incomplete downloads, shared blobs, and expected recovery. |
| LM Studio | `lms ls`; app model directory; installed CLI help | Exact app or CLI model removal supported by the installed version | Preserve user-created models and confirm configured storage location. |

For any other model manager, establish its owner and native removal semantics. Treat a model removal as redownload, not silent regeneration. Fine-tunes, adapters, datasets, embeddings, exports, and custom models require individual data-value assessment.

## Creative media and libraries

- Use Final Cut's generated-media controls for render files, optimized media, and proxy media. Confirm originals remain and state regeneration cost.
- Use Premiere or the relevant Adobe application's media-cache controls; keep project files, originals, previews with unclear ownership, and shared team storage out of generic cache cleanup.
- Use Logic or MainStage's supported sound-library relocation or optional-content management. Confirm the destination and application dependency on the attached volume.
- Use an owning application's documented cache or generated-media action for other creative tools. Do not manipulate package or library internals directly.

## Games, VMs, and application-owned data

- Prefer a game launcher's uninstall or move-library operation. Keep saves, mods, workshop content, and cloud synchronization separate from the game payload.
- Prefer a VM application's reclaim, compact, move, snapshot-management, or delete workflow. Verify the VM power state and show host-allocated space separately from guest free space and maximum capacity.
- Prefer Finder's Manage Backups action for iPhone and iPad backups.
- Prefer Mail, Messages, Photos, and browser-native controls for their managed data. Explain synchronized deletion, Recently Deleted, sign-out, offline-data, and regeneration consequences as applicable.
- Prefer an application's bundled or vendor-provided uninstaller before related-file cleanup. Establish what the uninstaller preserves, including documents, shared libraries, licenses, and subscriptions.

Native UI actions still require an approval card. Name the exact menu or control, the item or category it affects, the scope, expected recovery, and any follow-up such as emptying Recently Deleted. Do not automate UI while the Mac is locked or the owning application cannot present confirmation.

## Direct paths

Direct-path cleanup defaults to a recoverable move to Trash and requires individual investigation.

Never put `rm -rf`, `rm -r`, `find -delete`, or a hand-written cache-deletion loop in an audit report or “next steps.” This remains prohibited even when the target looks like a cache. Use a supported owning-tool cleanup command, or prepare the exact guarded Trash move below after individual investigation.

Before asking for approval:

1. Resolve the exact absolute target and canonical current project.
2. Reject symlinks; nonexistent targets; `/`, `$HOME`, broad Library roots; system roots; personal-content roots; the current project; its ancestors; and anything inside it.
3. Record `stat -f 'device=%d inode=%i type=%HT modified=%m bytes=%z name=%N'` and `du -sk` output.
4. Choose a unique destination under `~/.Trash` that does not exist.
5. Show the resolved source, destination, measured size, consequence, exact `mv` command, and finding ID.

After approval, repeat the same `stat` and `du` measurements. Stop if device, inode, type, modification time, or size changed materially. Move only the exact quoted path to the exact unique Trash destination with a single `mv` command. Do not use a glob, loop, `xargs`, `find -delete`, chained command, or recursive `rm` for execution.

Verify the source no longer exists and the destination does. Report the amount as staged in Trash, not reclaimed.

Permanent deletion is a separate workflow requiring a fresh explicit request and irreversible-loss acknowledgment. Ordinary cleanup approval is not permanent-deletion approval.

For Finder-managed Trash emptying, establish that an interactive user session is available before invoking Finder automation. If the Mac is locked or the UI cannot receive the confirmation, leave Trash unchanged and report the block; do not replace the native operation with raw recursive deletion. Immediately before the irreversible action, confirm the reviewed Trash scope and observed size again.
