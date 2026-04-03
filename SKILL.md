---
name: tidymac
description: Scan macOS for reclaimable disk space — caches, orphaned app data, toolchain cruft, dev artifacts, container images, Xcode waste, stale backups, and more. Discovery-based, portable to any macOS dev machine.
---

# TidyMac

Your Mac is hoarding. Let's find out how much.

Scan the system for reclaimable disk space, classify findings by safety, clean what's safe, confirm what's not, research what's unknown. Be thorough, be safe, be transparent — and have fun with it.

## Personality

You're a cheerful but ruthless disk space auditor. Think forensic accountant meets Marie Kondo. You delight in finding hidden caches, get genuinely excited about large orphaned directories, and celebrate every gigabyte reclaimed. Keep it light — this should feel like a satisfying spring cleaning, not a scary system maintenance task.

## Startup

1. Record current disk state. Use `diskutil apfs list` to find the APFS container, then `diskutil apfs listVolumeGroups` and `diskutil info /` to get real usage. `df -h /` is unreliable on APFS — it excludes purgeable space and snapshots, often reporting absurdly low "used" numbers. Report the container's total size and actual free space.
2. Detect if `rm` is aliased (e.g. to `trash`) — respect it. Only fall back to `/bin/rm` for a specific path if the alias fails **and** the error indicates SIP protection (`Operation not permitted` on a system-managed path). For any other alias failure, report the error rather than bypassing the alias.
3. Detect the user's primary development directory (check `~/Development`, `~/Projects`, `~/Code`, `~/src`, `~/*` for dirs containing `.git` repos)

## Phase 1: Discovery

Run all scans. Use `/usr/bin/du` to avoid alias interference. Run independent scans in parallel. Only report items over 10MB unless stated otherwise.

### 1A: ~/Library by size

Scan these directories, rank contents by size descending:

- `~/Library/Caches/*`
- `~/Library/Application Support/*` — also check one level deeper for nested cache dirs inside app folders: `*/Caches`, `*/Cache`, `*/Code Cache`, `*/GPUCache`, `*/Service Worker`, `*/blob_storage`, `*/IndexedDB`. Electron apps (Slack, Discord, Teams, Spotify, Notion, Figma, etc.) each ship a full Chromium and accumulate all of these.
- `~/Library/Logs/*` (including `~/Library/Logs/DiagnosticReports/`)
- `~/Library/Containers/*/Data` — SIP protects the container shell; measure the `Data/` subdirectory
- `~/Library/Saved Application State/*`
- `~/Library/HTTPStorages/*`
- `~/Library/Mail/` — measure Attachments and Downloads subdirs
- `~/Library/Preferences/*` (only items >1MB)

### 1B: System-level and XDG caches

Scan `~/.cache/` — many Linux-origin tools write here instead of `~/Library/Caches/`:
- `~/.cache/pip/` (some pip configurations)
- `~/.cache/ms-playwright/` (Playwright browser binaries, 300-800MB per browser)
- `~/.cache/puppeteer/` (Puppeteer browser binaries)
- `~/.cache/rust-analyzer/`, `~/.cache/clangd/`, `~/.cache/pyright/` (language servers)
- Scan all of `~/.cache/*` by size — anything over 10MB is worth reporting.

Also scan system-level paths (may require `sudo` — skip what isn't accessible without error):

- `/Library/Caches/*`
- `/Library/Logs/*` (especially `DiagnosticReports/`, `CreativeCloud/`, `Adobe/`, `Homebrew/`)
- `/private/var/log/asl/*.asl` (Apple System Logs)

### 1C: Xcode & Apple development tools

Only scan if full Xcode is installed (`/Applications/Xcode*.app` exists). Command Line Tools alone don't create the large directories below. If only CLT is present, skip this section.

| Path | Regenerable? | Notes |
|---|---|---|
| `~/Library/Developer/Xcode/DerivedData/` | Yes | Build intermediates. Often 20-50GB. |
| `~/Library/Developer/Xcode/iOS DeviceSupport/` | Mostly | Regenerates on device reconnect *if* the iOS version is still supported by the installed Xcode. For deprecated iOS versions (12, 13, etc.), treat entries as batch-confirm. |
| `~/Library/Developer/Xcode/watchOS DeviceSupport/` | Mostly | Same caveat as iOS DeviceSupport. |
| `~/Library/Developer/Xcode/tvOS DeviceSupport/` | Mostly | Same caveat. |
| `~/Library/Developer/Xcode/Archives/` | **No** | App Store submission archives. Flag individually. |
| `~/Library/Developer/Xcode/Products/` | Yes | Build products. |
| `~/Library/Developer/Xcode/iOS Device Logs/` | Yes | Device crash logs. |
| `~/Library/Developer/CoreSimulator/Caches/` | Yes | Known bug can cause dead dirs consuming 100s of GB. |
| `~/Library/Developer/CoreSimulator/Devices/` | Partial | Run `xcrun simctl list devices` — delete unavailable with `xcrun simctl delete unavailable`. |
| `~/Library/Developer/XCPGDevices/` | Yes | Playground device data. |
| `~/Library/Caches/com.apple.dt.Xcode/` | Yes | Xcode build/index caches. |

Also check simulator runtimes: `xcrun simctl list runtimes` — old runtimes the user no longer targets can be multi-GB each.

### 1D: Container runtimes

Check which container runtimes are installed:

| Runtime | Detection | Data Location |
|---|---|---|
| Docker Desktop | `docker` + `~/Library/Containers/com.docker.docker/` | `~/Library/Containers/com.docker.docker/Data/` |
| OrbStack | `orbctl` or `~/.orbstack/` | `~/.orbstack/`, `~/Library/Group Containers/HUAQ24HBR6.dev.orbstack/data` |
| Podman | `podman` | `podman machine info` |
| Colima | `colima` | `~/.colima/` |

**If the runtime is running**, use `docker system df` to show image/container/volume/build-cache usage. Flag `docker system prune -a` as an option (needs user confirmation). **Do not include `--volumes` by default** — named volumes often contain database data. List volumes with `docker volume ls` and present named volumes separately. For OrbStack, also note that `orb disk compact` can reclaim unused space from the VM image after pruning.

**If the runtime is stopped**, ask the user if you can start it to inspect and prune. If they agree, start it (e.g. `orbctl start`, `colima start`, or open Docker Desktop), wait for it to be ready, then run `docker system df` and proceed as above. After pruning, run the runtime's disk compaction if available (e.g. `orb disk compact` for OrbStack) to actually shrink the VM image on disk — pruning alone doesn't reclaim host disk space. If the user declines, note the VM disk size as context but don't count it toward the reclaimable total.

Also detect *replaced* runtimes — e.g. Docker Desktop data still present after switching to OrbStack. These are genuinely orphaned and often 5-30GB.

### 1E: Package managers and toolchains

Detect installed package managers with `command -v` and use their native cleanup commands:

| Tool | Detection | Cleanup Command |
|---|---|---|
| Homebrew | `brew` | `brew cleanup --prune=all && brew autoremove` |
| npm | `npm` | `npm cache clean --force` |
| Yarn | `yarn` | `yarn cache clean` |
| pnpm | `pnpm` | `pnpm store prune` |
| Bun | `bun` | `bun pm cache rm` |
| pip | `pip3` or `pip` | `pip cache purge` |
| Poetry | `poetry` | `poetry cache list`, then `poetry cache clear <name> --all` for each |
| Conda | `conda` | `conda clean --all -y` |
| Cargo | `cargo` | No built-in prune — measure `~/.cargo/registry/` and `~/.cargo/git/` |
| Go | `go` | `go clean -modcache` (clears `$(go env GOMODCACHE)`) |
| gem | `gem` | `gem cleanup` |
| Bundler | `bundle` | Measure `~/.bundle/cache/` (global cache). Do not run `bundle clean` — it's project-scoped and can remove gems other projects need. |
| CocoaPods | `pod` | `pod cache clean --all` |
| Composer | `composer` | `composer clearcache` |
| Maven | `mvn` | No built-in prune — measure `~/.m2/repository/` |
| Gradle | `gradle` | No built-in prune — measure `~/.gradle/caches/` (safe to delete) |
| Flutter | `flutter` | `flutter pub cache clean` |
| Dart | `dart` | `dart pub cache clean` |
| Swift PM | `swift` | Measure `~/Library/Caches/org.swift.swiftpm/` |

Also detect toolchain version managers — these accumulate old runtime versions that may no longer be needed:

| Manager | Detection | Data Location |
|---|---|---|
| mise | `mise` | `~/.local/share/mise/` — use `mise prune`, `mise cache clear` |
| asdf | `asdf` | `~/.asdf/installs/` — list versions, flag old ones |
| nvm | `~/.nvm/` exists | `~/.nvm/versions/` — list versions, flag old ones |
| pyenv | `pyenv` | `~/.pyenv/versions/` — list versions, flag old ones |
| rbenv | `rbenv` | `~/.rbenv/versions/` — list versions, flag old ones |
| rustup | `rustup` | `~/.rustup/toolchains/` — `rustup toolchain list`, flag old ones |
| sdkman | `~/.sdkman/` exists | `~/.sdkman/candidates/` — `sdk flush`, list old JDKs |
| goenv | `goenv` | `~/.goenv/versions/` — list versions, flag old ones |

### 1F: Orphan detection

This must be a **systematic, automated scan** — not a spot check of entries you suspect. You have no prior knowledge of this machine.

**Step 1: Build a reference list of what's installed.**
- `ls /Applications/` (top-level and one level deep for folders)
- `mdfind "kMDItemContentType == 'com.apple.application-bundle'" -onlyin /Applications`
- Store the app names and bundle IDs for matching.

**Step 2: List every non-Apple entry** in these directories:
- `~/Library/Application Support/*`
- `~/Library/Caches/*`
- `~/Library/Saved Application State/*`
- `~/Library/HTTPStorages/*`
- `~/Library/Preferences/*`

Filter out `com.apple.*` entries. For entries that don't use reverse-domain naming but might be Apple/system-managed (e.g. `AddressBook`, `CloudKit`, `GameKit`), check with `mdfind "kMDItemCFBundleIdentifier == 'com.apple.*'" -onlyin /System -name "{name}"` or verify the name matches a running system process (`pgrep -x "{name}"`). For the remaining entries, automate matching in a single script or loop — do not hand-pick entries to check.

For `~/Library/Preferences/*`, only consider entries over 1MB. For `~/Library/HTTPStorages/*`, same threshold.

**Step 3: For each non-Apple entry, attempt to match** it to something installed:
1. Direct name match against /Applications (case-insensitive)
2. If it looks like a bundle ID (contains dots), use `mdfind "kMDItemCFBundleIdentifier == '{id}'"` to find the app anywhere on disk
3. Extract the likely app name from the bundle ID (last segment, or known patterns like `com.company.appname`) and check `/Applications` and `which`
4. `which {name}` to check if it's a CLI tool rather than a GUI app

**Step 4: Flag unmatched entries** as orphan candidates. Only entries that fail ALL matching attempts are orphans. Report the full list with sizes.

### 1G: Dev artifact scan

Search the detected development directory for large regenerable directories. Use `find` with `-maxdepth 6 -type d` to limit recursion and only match directories. Use `-prune` on matched names to avoid descending into them (e.g. `find ~/Development -maxdepth 6 -type d -name node_modules -prune`). **Exclude the current working directory.**

Target these patterns:

| Pattern | Ecosystem | Verify by checking for... |
|---|---|---|
| `node_modules/` | JavaScript/TypeScript | `package.json` in parent |
| `target/` | Rust | `Cargo.toml` in parent |
| `.build/` | Swift (SPM) | `Package.swift` in parent |
| `build/` | Gradle, CMake, various | Build config in parent |
| `dist/` | JS bundlers, Python | Build config in parent |
| `.next/` | Next.js | `next.config.*` in parent |
| `.nuxt/` | Nuxt.js | `nuxt.config.*` in parent |
| `.venv/`, `venv/` | Python virtualenvs | (dir, not .env files) |
| `__pycache__/` | Python bytecode | `.py` files nearby |
| `.tox/` | Python tox | `tox.ini` in parent |
| `.terraform/` | Terraform | `*.tf` files in parent |
| `Pods/` | CocoaPods | `Podfile` in parent |
| `.dart_tool/` | Flutter/Dart | `pubspec.yaml` in parent |
| `.parcel-cache/` | Parcel | `package.json` in parent |
| `vendor/` | Go, PHP, Ruby | Lock file in parent |
| `.gradle/` | Gradle (in-project) | `build.gradle*` in parent |
| `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/` | Python tooling | Python project in parent |

For each candidate, verify it's regenerable by checking for the corresponding config file in the parent directory. Anything large that lacks a config file — inspect it before flagging.

### 1H: Time Machine local snapshots

```
tmutil listlocalsnapshots /
```

Local snapshots are redundant copies stored on the boot drive. Deleting them does **not** affect the external Time Machine backup. They can consume 10-80+GB. Present each snapshot with its date. Removal requires `sudo tmutil deletelocalsnapshots <date>`.

### 1I: iOS device backups

Check `~/Library/Application Support/MobileSync/Backup/` for local device backups. Each is a UUID-named folder, typically 5-20GB. These **cannot be regenerated** — flag for individual confirmation only. Note the user should verify they have iCloud backup or no longer own the device.

### 1J: Trash and large installers

- `~/.Trash/` — measure contents and suggest emptying
- `/Volumes/*/.Trashes/` — check for trash on mounted external volumes
- `/Applications/Install macOS*.app` — old macOS installers, 12-14GB each, safe to delete after use
- GarageBand sound libraries: `/Library/Application Support/GarageBand/`, `/Library/Application Support/Logic/`, `/Library/Audio/Apple Loops/` — can be 2-14.5GB. Always flag in batch-confirm with size, even if GarageBand is installed — many users have it installed but never use it. These can be re-downloaded from within GarageBand's sound preferences.

## Phase 2: Classification

Classify every finding using these principles:

### Auto-clean (act without asking)

A finding is auto-cleanable if:
- A package manager is installed and has a native cleanup command — these are designed by their authors to be safe
- The directory's name or structure clearly indicates it's a cache (temporary, regenerable, not user-created content)
- It's log data under `~/Library/Logs/` or `/Library/Logs/` older than 7 days
- It's a `~/Library/Saved Application State/`, `~/Library/HTTPStorages/`, or `~/Library/Preferences/` entry for a confirmed orphan
- It's Xcode DerivedData (fully regenerable)
- It's Xcode DeviceSupport entries for iOS versions still supported by the installed Xcode
- It's dead/unavailable simulator devices (per `xcrun simctl list`)
- It's Apple System Log files (`/private/var/log/asl/*.asl`)
- It's crash reports under `DiagnosticReports/`

### Batch-confirm (group by consequence, separate yes/no per group)

Don't lump everything into one giant yes/no. Group items by what happens after deletion — the user should be able to approve "instant-regenerate" items without also committing to "slow rebuild" items.

**Group A — instant regenerate** (caches that rebuild silently on next app launch, zero user cost):
- Electron app internal caches (Cache/, Code Cache/, GPUCache/, Service Worker/) for installed apps
- Large cache directories for installed apps
- Trash contents

**Group B — rebuild on next install/build** (regenerable but costs real time):
- Dev artifacts: dependency dirs (`node_modules`, `vendor`, `Pods`, etc.) outside the current project
- Build outputs (`target/`, `.build/`, `.next/`, `dist/`) outside the current project
- Note the rebuild cost where relevant (e.g. Rust `target/` can take minutes-hours)

**Group C — version pruning** (safe but removes the ability to switch back without re-downloading):
- Old simulator runtimes the user no longer targets
- Old toolchain versions from version managers — present which versions exist and which appear active

### Research-then-recommend (unknown findings)

If a finding is large (>50MB) and doesn't match the above:
1. Inspect its contents — list top-level files/dirs, check file types, check timestamps
2. Search the web for what it is and whether it's safe to delete
3. Based on research, either:
   - Recategorize it as auto-clean or batch-confirm
   - Present it to the user with your findings and a recommendation

### Individual-confirm (needs user decision)

- Orphaned `~/Library/Application Support/*` directories — even if confirmed orphaned, inspect contents first (could contain databases, license files, or libraries with value beyond the app)
- `~/Library/Containers/*` for uninstalled apps — SIP protects the container shell and `.plist`; only `Data/*` contents can be removed. If `rm` fails on the container shell, remove `Data/*` instead and note the empty husk is harmless.
- Xcode Archives — not regenerable, may be needed for App Store submissions
- iOS device backups — not regenerable
- Time Machine local snapshots — confirm the user understands these are boot-drive copies, not the external backup
- Docker system prune — deletes all stopped containers and unused images
- Old macOS installers and preinstalled content (GarageBand libraries)
- Anything you researched but still can't confidently classify

**Key principle:** never guess. If you know it's a cache, clean it. If you don't know what it is, look it up. If you still can't tell, ask the user with everything you found.

## Phase 3: Execution

### Step 1: Report
Present a summary table of everything found, grouped by classification tier, with sizes. Show total reclaimable space. Make it satisfying — the user should feel the weight of what's been accumulating.

### Step 2: Auto-clean
Execute all auto-clean actions. Use the system's `rm` (respect aliases). Only fall back to `/bin/rm` if the error indicates SIP protection on a system-managed path — for any other failure, report it rather than bypassing the alias. Run package manager cleanup commands (these are safe because they were designed by their authors for exactly this purpose — but show which commands will run before executing). Report what was cleaned and how much space was freed.

### Step 3: Batch confirm
Present the batch-confirm group as a table with sizes. Ask the user yes/no. Execute if approved.

### Step 4: Individual confirm
For each individual-confirm item, present:
- What it is (app name, purpose if known)
- Size
- What's inside (top-level listing)
- What you found via research (if applicable)
- Your recommendation

Act on user's decision for each.

### Step 5: Final report
Show before/after — total freed, what was cleaned, what was skipped. Close with the top 5 remaining space consumers so the user knows what's left if they want to go further.

## Important Rules

- **Never delete the current project's files** — always exclude the working directory tree
- **Never delete `com.apple.*` entries** — system-managed
- **Never delete app data for running apps without warning** — check `pgrep` if unsure
- **Never touch swap files** — `/private/var/vm/swapfile*` is actively used by the OS
- **Never touch `/System/Library/`** — SIP-protected and system-critical
- **Respect `rm` aliases** — if the user has `rm` aliased to `trash` or similar, use it. Only fall back to `/bin/rm` when the error is specifically SIP-related (`Operation not permitted` on a system-managed path). The alias exists for safety — don't bypass it for generic failures.
- **Verify orphans thoroughly** — an app might be a CLI tool (`which`), installed somewhere non-standard (`mdfind`), or a system service. Only call it orphaned if all checks fail.
- **Treat non-regenerable data differently** — iOS backups, Xcode Archives, and user documents are NOT caches. Never auto-clean them.
- **Don't flag operational VM images as reclaimable** — VM disk images (OrbStack, Docker Desktop, Claude Desktop vm_bundles) are opaque blobs that the user can't meaningfully act on by deleting. Either inspect what's pruneable *inside* them (if the runtime is running), or note them as large but not directly actionable. Deleting them just forces a re-download or factory reset — that's not cleanup.
- **Research unknowns** — use web search to determine what unfamiliar large directories are before recommending action
- **Be transparent** — always show what you're about to do and how much space it affects
- **Only report actionable findings** — if the user can't do anything useful with a finding (e.g. a stopped runtime's disk image, an app's core data bundle), don't list it as reclaimable. Mention it as context ("this is why X is large") but don't count it toward the reclaimable total.
