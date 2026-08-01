# Native cleanup commands

Detect the installed version, read its current `--help`, and inspect or dry-run before proposing cleanup. A native command is not automatically low consequence.

## Package managers

| Tool | Inspect or preview | Candidate action | Consequence |
|---|---|---|---|
| Homebrew | `brew cleanup --dry-run`; `brew autoremove --dry-run` | Offer `brew cleanup`; offer `brew autoremove` separately | Cleanup drops cached downloads/old versions; autoremove uninstalls formulae. |
| npm | `npm cache verify`; `npm config get cache` | `npm cache clean --force` | Entire cache must be redownloaded. |
| Yarn | Resolve cache location; use version-specific help | Version-specific cache clean | Redownload required; semantics differ between Yarn generations. |
| pnpm | `pnpm store path`; `pnpm store status` | `pnpm store prune` | Removes unreferenced packages; future installs may download again. |
| Bun | `bun pm cache` help and cache path | Version-specific cache removal | Redownload required. |
| pip | `pip cache info`; `pip cache list` | `pip cache purge` | Wheels and archives must be downloaded or rebuilt. |
| Poetry | `poetry cache list` | Clear a named cache, one at a time | Redownload required. |
| Conda | `conda clean --all --dry-run` when supported | `conda clean` with selected categories | Package caches may support environment rollback/reinstall workflows. |
| Cargo | Measure registry, git, and target data separately | No blanket default | Registry/git removal causes downloads; target removal causes rebuilds. |
| Go | `go env GOCACHE GOMODCACHE` and measure both | `go clean -cache` or `go clean -modcache` separately | Build cache requires rebuild; module cache requires redownload. |
| RubyGems | `gem cleanup --dry-run` | `gem cleanup` | Removes old installed gem versions, not just downloads. |
| Bundler | Resolve configured paths | No global `bundle clean` default | Project and shared installation layouts differ. |
| CocoaPods | `pod cache list` | Selective cache clean; `--all` only as its own batch | Redownload required. |
| Composer | `composer clear-cache --dry-run` if supported by the installed version | `composer clear-cache` | Redownload required. |
| Maven | Measure the local repository | No blanket default | Dependencies and locally published snapshots may be hard to reproduce. |
| Gradle | Inspect configured `GRADLE_USER_HOME` and cache contents | No blanket default | Rebuild/redownload required; active daemons may hold files. |
| Dart/Flutter | Inspect pub-cache location and current help | Pub cache clean as a separate batch | Redownload required. |

Never chain cleanup commands. Present and record each action independently so a partial failure is visible.

## Version managers

List installed versions, active global/local selections, and project references before proposing removal. Treat old versions as a version-pruning batch, not cache cleanup.

- Prefer native prune or uninstall commands from mise, asdf, pyenv, rbenv, rustup, sdkman, or goenv.
- Preserve versions referenced by project files such as `.tool-versions`, `.mise.toml`, `.python-version`, `.ruby-version`, `rust-toolchain.toml`, and CI configuration.
- State that removal sacrifices offline switching and may require a future download.

## Containers

Use increasingly broad options and show the native warning before execution:

1. Inspect with `docker system df -v`, `docker ps -a`, `docker image ls`, and `docker volume ls`.
2. Prefer category-specific, age-filtered prune commands when they meet the user's goal.
3. Treat `docker system prune` as individual confirmation because it removes all stopped containers plus unused networks, dangling images, and build cache.
4. Treat `docker system prune -a` as more consequential because it removes every image unused by a container.
5. Never add `--volumes` to a general cleanup. Inspect volumes individually.
6. Compact a runtime VM only after internal pruning and only with the installed runtime's documented command.

## Filesystem paths

Use `scripts/tidy_paths.py` for direct path removal. Default to Trash so the action remains recoverable; explain that this does not free host space until Trash is emptied.

Prepare a plan:

```bash
python3 <skill-dir>/scripts/tidy_paths.py prepare PATH... \
  --plan /tmp/tidymac-plan.json \
  --home "$HOME" \
  --cwd "$PWD" \
  --mode trash
```

Show the user every plan item, mode, total estimate, and approval token. Apply only after the user approves those exact items:

```bash
python3 <skill-dir>/scripts/tidy_paths.py apply \
  --plan /tmp/tidymac-plan.json \
  --approval-token TOKEN
```

The executor rechecks device, inode, type, modification time, and allocated size. If anything changed, stop and rescan. Use `--allow-unrecognized` only for an individually researched path. Use permanent mode only when the user explicitly requests permanent deletion; it additionally requires `--acknowledge-permanent` during plan preparation.
