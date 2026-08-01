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
  <strong>Your Mac is hoarding. Let's find out why.</strong>
  <br/><br/>
  A judgment-driven macOS disk-space auditor for Claude Code and Codex.
</p>

---

TidyMac investigates disk usage across macOS, explains what it means on this particular machine, and cleans only what you approve.

It is a skill rather than a conventional cleaner app because the hard part is not finding large directories. The hard part is deciding whether an unfamiliar directory is disposable, expensive to regenerate, useful historical state, or the only remaining copy of something important.

## Install

Using the Skills installer is convenient:

```bash
npx skills add azohra/tidymac
```

The installer clones the GitHub repository, discovers `skills/tidymac`, and copies that complete directory into the selected host. TidyMac is entirely self-contained Markdown, host UI metadata, and one standalone report shell: there are no helper programs, runtime libraries, or later code downloads.

The installer can target Claude Code, Codex, or both. To select both explicitly:

```bash
npx skills add azohra/tidymac -a claude-code -a codex
```

Node.js is not a TidyMac runtime requirement; `npx` is only one way to copy the skill into place. Without it, download the repository or a release archive and copy the complete folder to the host's skill directory:

```bash
mkdir -p "$HOME/.claude/skills" "$HOME/.agents/skills"
cp -R /path/to/tidymac/skills/tidymac "$HOME/.claude/skills/tidymac"
cp -R /path/to/tidymac/skills/tidymac "$HOME/.agents/skills/tidymac"
```

Use the first destination for Claude Code, the second for Codex, or both. That nine-file skill folder is the whole runtime product.

Invoke the installed skill with the syntax used by your host:

| Host | Invocation |
|---|---|
| Claude Code | `/tidymac` |
| Codex | `$tidymac` |

For example:

```text
$tidymac Audit my Mac and present a cleanup plan.
```

A bare invocation runs a read-only audit. TidyMac presents a cleanup plan before making any changes.

## What it inspects

- macOS and XDG caches
- Application Support, containers, logs, saved state, and HTTP storage
- Xcode DerivedData, DeviceSupport, simulators, and archives
- Docker Desktop, OrbStack, Podman, and Colima
- Package-manager caches and developer toolchains
- Old runtime versions
- Local AI models and revisions from detected tools such as Ollama, Hugging Face, and LM Studio
- Locally downloaded cloud files from detected File Provider services
- Generated creative media and relocatable sound or media libraries
- Game libraries and virtual-machine storage
- Mail, Messages, Photos, browser, and Finder-managed backup storage through their native owners
- Regenerable project artifacts such as `node_modules`, `target`, `.build`, `.next`, and virtual environments
- Evidence of app data whose owner is no longer obvious
- iOS device backups, Trash, installers, and other large contextual storage

The audit starts with a fast user-space census, then lowers the scan floor and expands into contextual investigation. There is no fixed item-size definition of “important”: smaller findings are aggregated by owner and category, and another pass is required until the tail no longer changes the explanation or recommendations.

When a stopped container or VM runtime hides material storage behind an opaque disk image, TidyMac explains the gap and asks permission to start it temporarily for read-only native inventory. An approved inspection records the original state and restores it afterward, including when inventory fails.

## How decisions work

TidyMac keeps two questions separate:

1. **How certain are we about what this is?** Verified, likely, or unknown.
2. **What happens if it goes away?** Silent regeneration, redownload, rebuild, workflow reset, possible state loss, or non-regenerable loss.

That distinction prevents a common cleanup mistake: treating “cache” as synonymous with “free.” A dependency cache may be safe to remove but expensive to download again; an unmatched app directory may be an orphan, shared state, or a deliberately retained archive.

Findings are grouped by consequence so you can approve cheap cleanup without also agreeing to long rebuilds or loss of historical state.

TidyMac also distinguishes the right kind of action. Useful data may be better **evicted locally**, **relocated**, or **pruned by its owning tool** rather than deleted. Cloud deletion, workflow reset, Trash staging, and permanent deletion remain separate scopes.

## Generated opportunity map

When the host supports rich output, TidyMac can turn a completed investigation into a machine-specific interactive opportunity map. Space is sized by observed local allocation and grouped by the correct action—evict, native prune, remove generated media, relocate, Trash, or delete.

Selecting a finding explains why it exists, the evidence, confidence, scope, consequence, recovery route, and expected host-space effect. Users can assemble a proposed plan, but the visual never executes cleanup or replaces the exact approval prompt.

The map is generated from the same finding records and reconciled arithmetic as the text report. It is optional: hosts without an artifact surface receive the complete structured report, and a requested standalone report uses the bundled self-contained HTML shell with no external assets or runtime dependencies.

## Safety model

- Auditing is the default. Nothing is silently cleaned.
- Every mutation is tied to an approved finding or command.
- Unknown findings are researched rather than guessed at.
- Interactive reports reveal the minimum relevant owner identifiers needed to explain a finding or approve an action; shareable and public reports redact personal and project identifiers throughout.
- Visual selections prepare a scoped plan but never count as cleanup approval.
- Narrow manifests and configuration fields may be inspected when they establish ownership or regeneration. Personal content, credentials, secret-bearing logs, databases, and archives require explicit content-level permission.
- “Unmatched” app data is never automatically called orphaned.
- The current project and its ancestors are excluded from path cleanup.
- Broad roots, symlinks, system directories, and changed-since-scan paths are rejected.
- Direct path cleanup defaults to moving data to Trash.
- Trash is never presented as reclaimed disk space until it is reviewed and emptied.
- Container volumes, Xcode archives, iOS backups, and other stateful data receive individual treatment.
- Container cache pruning, image removal, stateful-volume deletion, factory reset, and application uninstall are separate approval scopes.
- Time Machine local snapshots are shown as context, not added to routine reclaimable totals; macOS normally manages their space automatically.

## Architecture

TidyMac is deliberately judgment-first:

```text
Native macOS census → contextual investigation → model conclusions → approval → exact native action
```

Claude or Codex uses built-in macOS commands and tools already installed on the machine to gather evidence. It keeps digging with native inventories, dry-runs, manifests, application metadata, processes, receipts, timestamps, project history, and current primary sources until the important space is explained. Raw directory sizes are intermediate evidence, not the report.

The cleanup contract requires an exact plan and explicit approval. Direct-path actions are revalidated immediately before a recoverable move to Trash. Native cleanup commands are previewed when possible and approved individually.

TidyMac maintains a coverage ledger and a separate storage-reconciliation ledger. Unexplained, inaccessible, provider-managed, other-user, and OS-managed space remains visible rather than being mislabeled as junk or forced into a false total.

## Example requests

```text
/tidymac
$tidymac
Audit my Mac, but don't clean anything.
Focus on Xcode and old simulators.
Show me an interactive opportunity map after the audit.
Find local AI models I no longer need, but don't remove anything.
Show cloud files I can evict locally without deleting remotely.
Find stale build artifacts outside this project.
Investigate whether these large Application Support folders are leftovers.
Clean only the low-impact items I approve.
I need 20 GB quickly; prioritize things that won't require a rebuild.
```

## Requirements

- macOS
- Claude Code or Codex

That is the full runtime requirement. TidyMac does not require Python, Node.js, npm packages, compiled helpers, a daemon, or a service. Optional ecosystem commands such as `brew`, `docker`, or `xcrun` are used only when they are already installed and relevant to the machine.

A capable reasoning model is strongly recommended for a full audit. TidyMac contains explicit evidence, privacy, arithmetic, and safety preflight checks so a weaker model should fail closed with coverage gaps instead of inventing a complete-looking answer.

Tested guidance:

| Host | Full audit recommendation |
|---|---|
| Claude Code | Sonnet or Opus class; Haiku is not supported for full-machine audits |
| Codex | A frontier Codex model with medium or higher reasoning |

The host chooses and provides the model; TidyMac does not call an API or bundle model credentials.

## Versioning

TidyMac releases are Git tags and GitHub releases. The skill format does not need a runtime version field: the installer records the repository source and content hash. Use semantic versions for human-facing changes—patch for fixes, minor for backward-compatible workflow or capability changes, and major for a new contract or incompatible behavior.
