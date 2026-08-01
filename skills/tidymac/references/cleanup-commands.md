# Native cleanup and direct-path safety

Use only built-in macOS commands and tools already installed on the machine. Read the installed tool's current help and inspect or dry-run before proposing cleanup. A native command is not automatically low consequence.

## Package managers

| Tool | Inspect or preview | Candidate action | Consequence |
|---|---|---|---|
| Homebrew | `brew cleanup --dry-run`; `brew autoremove --dry-run` | Offer cleanup and autoremove separately | Cleanup removes downloads/old versions; autoremove uninstalls formulae. |
| npm | `npm cache verify`; `npm config get cache` | Version-supported cache clean | Redownload required. |
| Yarn | Resolve cache path and generation-specific help | Version-specific cache clean | Redownload; semantics differ by generation. |
| pnpm | `pnpm store path`; `pnpm store status` | `pnpm store prune` | Future installs may redownload. |
| pip | `pip cache info`; `pip cache list` | `pip cache purge` | Wheels and archives must be redownloaded or rebuilt. |
| Conda | Supported dry-run for selected clean categories | Selected native clean | Caches can support reinstall or rollback workflows. |
| Cargo | Measure registry, Git, and project targets separately | No blanket default | Downloads and rebuilds differ. |
| Go | `go env GOCACHE GOMODCACHE` | Clean build and module caches separately | Rebuild versus redownload. |
| RubyGems | `gem cleanup --dry-run` | `gem cleanup` | Removes installed old gem versions, not just downloads. |

For any other installed manager, use its current local help. Never chain cleanup commands; preserve each result and partial failure independently.

## Version managers

List installed versions, active selections, and project references before proposing removal. Preserve versions referenced by `.tool-versions`, `.mise.toml`, `.python-version`, `.ruby-version`, `rust-toolchain.toml`, CI configuration, or equivalent manifests. Prefer the already-installed manager's own uninstall command.

## Containers

1. Inspect native disk usage, containers, images, build cache, networks, and volumes.
2. Prefer category-specific and age-filtered proposals.
3. Treat broad system prune as its own confirmation.
4. Treat all-unused-image pruning as more consequential.
5. Never add volumes to a general prune.
6. Compact a VM only after internal pruning and only with the installed runtime's documented command.

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
