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
  <strong>Your Mac is hoarding. Let's fix that.</strong>
  <br/><br/>
  A Claude Code skill that hunts down reclaimable disk space<br/>
  with the tenacity of a Marie Kondo / forensic accountant hybrid.
</p>

---

## The Problem

Every macOS machine is quietly accumulating garbage:

- **Uninstalled apps leave their data behind.** Drag an app to Trash? Congrats, you deleted the 50MB binary. The 17GB of `~/Library/Application Support` data? Still there. Forever.
- **Package managers cache everything.** npm, brew, pip, cargo, pnpm, conda, composer — they all download, build, and cache aggressively. Nobody runs the cleanup commands.
- **Xcode is a black hole.** DerivedData, DeviceSupport, dead simulators, old runtimes — easily 50-100GB on an active iOS dev machine.
- **Electron apps are disk vampires.** Every Slack, Discord, Teams, Spotify, and Notion window is a full Chromium instance with its own Service Workers, IndexedDB, GPU shader cache, and crash dumps.
- **Container runtimes hoard images.** Docker, OrbStack, Podman — dangling images, stopped containers, and build cache pile up silently.
- **Build artifacts multiply.** That `node_modules` in a project you touched once six months ago? Still 1.2GB. The Rust `target/` dir? 6GB and growing.
- **Time Machine snapshots consume the boot drive.** Local snapshots can quietly eat 10-80GB without showing up in Finder.

macOS has no built-in mechanism to find or clean any of this.

## The Fix

```bash
npx skills add azohra/tidymac
```

Then in Claude Code:

```
/tidymac
```

That's it. TidyMac scans your machine, figures out what's reclaimable, and handles cleanup interactively — safe stuff gets cleaned automatically, sketchy stuff gets researched and presented for your approval.

## How It Works

TidyMac is **discovery-based, not list-based.** It doesn't maintain a hardcoded database of "known junk paths." Instead, it teaches Claude *how to find* reclaimable space on any Mac:

**1. Measure everything.** Scan `~/Library/*`, system caches, and rank by size. The biggest directories get attention first.

**2. Detect your tools.** Find every package manager, toolchain, version manager, and container runtime you have installed. Run their native cleanup commands. If it has a `cache clean`, TidyMac will find it.

**3. Scan developer tools.** Xcode DerivedData, DeviceSupport, dead simulators, old runtimes — the stuff that quietly grows to 50-100GB.

**4. Hunt orphans.** Systematically cross-reference every app data directory against what's actually installed. No match? It's dead weight from something you uninstalled.

**5. Find dev artifacts.** Locate `node_modules`, `.venv`, `target/`, `build/`, `.next/`, `Pods/`, and other regenerable directories across your projects (excluding the one you're currently working in).

**6. Check everything else.** Time Machine local snapshots, iOS backups, old macOS installers, GarageBand sound libraries, Trash — the stuff you forgot about.

## Safety Tiers

Not everything gets the same treatment:

| Tier | What happens | Examples |
|---|---|---|
| **Auto-clean** | Cleaned silently | Package manager caches, crash dumps, old logs |
| **Batch-confirm** | Presented as a group, single yes/no | Build artifacts, large app caches |
| **Research first** | Inspected + web-searched before recommending | Unknown large directories |
| **Individual-confirm** | Presented one at a time with context | Orphaned app data, SIP-protected containers |

If TidyMac doesn't know what something is, it looks it up. If it still can't tell, it asks you. It never guesses.

## What It Typically Finds

TidyMac routinely recovers **30-100+GB** depending on the machine. The biggest offenders, ranked by typical savings:

| Category | Typical Size | Example |
|---|---|---|
| Xcode DerivedData + DeviceSupport | 10-100GB | Build artifacts for every device you've ever connected |
| Container images & build cache | 5-60GB | Docker Desktop data after switching to OrbStack |
| Time Machine local snapshots | 10-80GB | Redundant on-disk copies of your TM backup |
| Dev artifacts across projects | 5-50GB | `node_modules`, `target/`, `.venv` in inactive repos |
| Orphaned app data | 5-50GB | ~/Library leftovers from uninstalled apps |
| Package manager caches | 5-50GB | npm, Homebrew, Cargo, pip, and friends |
| Electron app caches | 2-15GB | Slack, Discord, Teams, Spotify internals |
| Old toolchain versions | 2-20GB | Unused Node, Python, Ruby versions from nvm/pyenv/rbenv |
| Logs & crash reports | 1-5GB | Years of accumulated diagnostic data |

Most of it is from things the user has already stopped using.

## Requirements

- macOS
- [Claude Code](https://claude.ai/code)
