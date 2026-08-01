# Cleanup

Read installed help and preview the exact scope before proposing any action. A native command is not automatically low consequence.

## Approval

Put the finding ID, evidence, action, scope, estimated allocation and host recovery, consequence, recovery route, preconditions, and exact command or UI route in one approval card. Approval covers only those IDs and actions.

Run approved actions separately. Preserve each result and partial failure. Never reveal an irreversible command only after receiving vague verbal approval.

## Package and version managers

| Tool | Inspect or preview | Distinction |
|---|---|---|
| Homebrew | `brew cleanup --dry-run`; age-bounded preview when useful; `brew cleanup --dry-run --prune=all` | Cache cleanup redownloads; keep `brew autoremove --dry-run` separate because it uninstalls |
| npm | `npm cache verify`; `npm config get cache`; installed help | Self-healing cache; cleanup is for space, not repair |
| Yarn | Configured path and generation-specific help | Semantics differ by generation |
| pnpm | `pnpm store path`; `pnpm store status`; installed prune help | Shared store may redownload |
| pip | `pip cache info`; `pip cache list`; installed purge help | Wheels may redownload or rebuild |
| uv | `uv cache dir`; installed prune help and dry-run if supported | Prefer prune; broad clean is a separate action |
| Conda | Supported dry-run by selected category | Cleanup may affect reinstall or rollback |
| Cargo | Registry, Git, and project targets separately | Redownload and rebuild are different |
| Go | `go env GOCACHE GOMODCACHE` | Build and module caches have different costs |
| RubyGems | `gem cleanup --dry-run` | Removes installed old versions, not downloads |

For material Homebrew cache, compare ordinary and `--prune=all` previews. Explain that the full preview may include current-version downloaded installers but not installed software. Recommend the scope matching the user’s recovery goal; state future redownload cost. Never group `brew autoremove` with cache cleanup.

Before removing a runtime version, check active selections and project/CI references. Use the installed manager’s uninstall command.

## Containers and VMs

Inspect native disk use, containers, images, cache, networks, volumes, and VM state first. Keep these approvals separate:

| Action | Consequence |
|---|---|
| Build-cache prune | Rebuild time |
| Unused-image prune | Redownload or rebuild |
| Stopped-container removal | Writable layer and workflow state loss |
| Named-volume removal | Persistent data loss |
| Factory reset | All runtime machines, containers, images, cache, networks, volumes, and state lost |
| Runtime uninstall | Application removal; data semantics established separately |
| Compact or reclaim | Host allocation changes after internal pruning; result may differ from native estimate |

Prefer category-specific and age-filtered actions. Never add volumes to a general prune.

For OrbStack reset, read installed `orbctl reset --help`. Propose `orbctl reset --yes` only when the user requests the exact confirmed all-data scope. Do not delete its backing disk manually. Measure Data-volume free space immediately before and after.

## Cloud, AI, and owner-managed apps

- Use File Provider eviction only after confirming local presence and completed sync. Keep it separate from cloud deletion.
- Use native model inventory and exact removal. For Ollama, prefer installed `ollama list` and `ollama rm` help; for Hugging Face, use installed cache list and supported dry-run removal or prune; for LM Studio, use its configured store and installed app/CLI controls. Never remove shared blobs or keys manually.
- Use Final Cut generated-media, Adobe media-cache, Logic/MainStage relocation, game-launcher, VM, Finder backup, Mail, Messages, Photos, and browser controls through the owning app.
- Prefer a bundled or vendor uninstaller. Establish what it preserves: documents, shared libraries, licenses, subscriptions, and integrations.

For a native UI action, name the exact item or category, control, scope, consequence, expected recovery, and follow-up retention area. Do not automate UI while the Mac is locked or unable to present confirmation.

## Direct paths

Use this only when no supported owner action exists. Default to a recoverable Trash move.

Before approval:

1. Resolve one exact absolute path without following a top-level symlink.
2. Reject nonexistent targets, symlinks, `/`, `$HOME`, broad Library or system roots, personal-content roots, the current project, its ancestors, and anything inside it.
3. Record `stat -f 'device=%d inode=%i type=%HT modified=%m bytes=%z name=%N'` and `du -sk`.
4. Choose a unique, nonexistent destination under `~/.Trash`.
5. Show source, destination, size, consequence, finding ID, and exact quoted `mv` command.

After approval, repeat the same `stat` and `du`. Stop if identity, type, modification time, or size changed materially. Move only the quoted target to the quoted destination with one `mv`; never use a glob, loop, `xargs`, `find -delete`, or recursive `rm`.

Verify source absence and destination presence. Report the amount as staged, not reclaimed.

Permanent deletion requires a new irreversible request. Ordinary cleanup approval is insufficient.

Before Finder-managed Trash emptying, confirm the reviewed scope and size again and ensure an interactive unlocked session can receive confirmation. If not, leave Trash unchanged; never substitute raw deletion.
