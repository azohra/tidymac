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
  <strong>Your Mac is hoarding. TidyMac finds out why.</strong>
  <br/><br/>
  Disk cleanup for people who do not want to become filesystem archaeologists.
  <br/><br/>
  <a href="https://github.com/azohra/tidymac/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/azohra/tidymac?style=flat-square"></a>
  <img alt="Runtime dependencies: none" src="https://img.shields.io/badge/runtime_dependencies-none-2ea44f?style=flat-square">
</p>

---

TidyMac is a judgment-driven macOS disk-space investigator for **Claude Code** and **Codex**.

It does the weird forensic work—APFS accounting, package-manager previews, app ownership, runtime inventories—and gives you the normal-person answer first:

| Decision | Meaning |
|---|---|
| **Clean up** | Verified disposable data. Here is what you get back and what may redownload. |
| **Optional** | Real savings with a noticeable tradeoff, such as a rebuild or sign-in. |
| **Keep** | Personal, active, unknown, or otherwise not worth gambling with. |

Nothing changes until you approve the exact action.

## The 30-second tour

Ask:

```text
$tidymac
```

Get something shaped like this:

```text
Clean up · 14.8 GB
  Package downloads       9.9 GB  Redownloaded only if needed
  Old diagnostic logs     4.6 GB  Old troubleshooting history
  Browser cache          0.3 GB  Regenerates silently

Optional · 11.2 GB
  Project build output    6.1 GB  Requires a rebuild
  Local model             5.1 GB  Requires a redownload

Keep
  Photos library                  Personal originals
  Active runtime volume           Stateful and currently in use
```

<sub>Synthetic example. Real findings come from the machine being audited.</sub>

Pick a group or individual finding. TidyMac rechecks it, shows the exact command or native action, asks for approval, runs only what you selected, and measures what actually changed.

## Install

The easiest route is the Skills installer:

```bash
npx skills add azohra/tidymac
```

Install for both supported hosts explicitly:

```bash
npx skills add azohra/tidymac -a claude-code -a codex
```

Then invoke it using your host’s syntax:

| Host | Invocation |
|---|---|
| Claude Code | `/tidymac` |
| Codex | `$tidymac` |

A bare invocation performs a read-only audit:

```text
/tidymac
$tidymac
```

Node.js is only used here to copy the skill into place. TidyMac itself has no Node.js, Python, daemon, compiled helper, package install, or service dependency.

<details>
<summary><strong>Install manually without npx</strong></summary>

Download this repository or a release archive, then copy the complete skill folder:

```bash
mkdir -p "$HOME/.claude/skills" "$HOME/.agents/skills"
cp -R /path/to/tidymac/skills/tidymac "$HOME/.claude/skills/tidymac"
cp -R /path/to/tidymac/skills/tidymac "$HOME/.agents/skills/tidymac"
```

Use the first destination for Claude Code, the second for Codex, or both. That nine-file folder is the whole runtime product.

</details>

## Why TidyMac exists

Finding a large directory is easy. Knowing whether it is disposable is not.

`8 GB cache` might mean a painless cleanup, a six-hour redownload, an active build accelerator, or a misleading label on something stateful. `Application Support` might be junk from an uninstalled app—or the only local copy of a workflow someone cares about.

TidyMac investigates the owner, activity, contents, timestamps, native cleanup interface, regeneration path, and actual consequence before making the recommendation. It treats free space as urgency context, not as a reason to keep verified junk forever.

In short: **size finds the suspect; evidence decides the action.**

## Where it looks

| Area | Examples |
|---|---|
| Apps and macOS | Caches, Application Support, containers, logs, saved state, Mail, Messages, Photos, browsers, Trash, device backups |
| Development | Xcode data, package-manager caches, old runtimes, `node_modules`, `target`, `.build`, `.next`, virtual environments |
| Containers and VMs | Docker Desktop, OrbStack, Podman, Colima, Parallels, VMware Fusion, UTM |
| Local AI | Ollama, Hugging Face, LM Studio, model revisions and download caches |
| Cloud storage | Local File Provider downloads that may be evicted without deleting the remote copy |
| Creative and large media | Generated media, optional sound libraries, game libraries, relocatable assets |
| Mystery space | Unclear app ownership, opaque runtime disks, inaccessible scope, APFS and OS-managed context |

The audit starts broad, then follows the evidence. It keeps lowering the scan floor until another pass no longer changes the explanation or recommendation—not until it has produced a scary list of every large thing you own.

## You do not need to know what to ask for

TidyMac’s job is to discover the suspects. You can describe the outcome you want—or simply invoke it with no instructions at all.

**No context needed:**

```text
$tidymac
```

**When you have no idea where the space went:**

```text
Why is my Mac full?
```

**When you want the shortest useful answer:**

```text
Make this easy: tell me what to clean, what is optional, and what to keep.
```

**When you need a specific amount of space:**

```text
I need 20 GB. Find the least painful way to get it.
```

**When you want a general tidy-up:**

```text
Free as much space as you reasonably can without disrupting my work.
```

You should not have to know what a simulator, package cache, File Provider, model revision, runtime volume, or mystery `Application Support` folder is. If one matters on this Mac, TidyMac finds it, explains it, and puts it in the right decision group.

## Opportunity map

On hosts with rich output, TidyMac can turn the completed audit into an interactive, machine-specific map.

The first view shows **Clean up**, **Optional**, and **Keep** totals. Underneath, finding size represents observed local allocation—not a promise of recovered space—and each item explains its owner, evidence, confidence, scope, consequence, recovery route, and expected host-space effect.

Selecting items builds a proposed plan. It cannot execute commands, silently broaden scope, or count as approval. A standalone report uses the bundled self-contained HTML shell with no external assets, runtime packages, or command bridge.

## Safety without the ceremony

TidyMac is cautious about your data, not timid about disposable caches.

- Auditing is read-only by default.
- Every mutation is tied to an exact approved finding or command.
- Unknown data stays out of cleanup groups.
- Personal content is measured as context, not casually enumerated.
- The current project and its ancestors are excluded from path cleanup.
- Direct-path cleanup uses a revalidated, recoverable move to Trash—not improvised recursive deletion.
- Trash is staged space, not reclaimed space, until it is reviewed and emptied.
- Cloud eviction stays separate from cloud deletion.
- Cache pruning, image removal, stateful-volume deletion, factory reset, and application uninstall remain different approval scopes.
- Xcode archives, device backups, container volumes, and other stateful data receive individual treatment.

That boundary is deliberate: understanding should be automatic; changing the machine should be explicit.

<details>
<summary><strong>How the investigation works</strong></summary>

```text
Native macOS census
        ↓
Contextual investigation
        ↓
Clean up / Optional / Keep
        ↓
Exact preview and approval
        ↓
Native action and measured result
```

Claude or Codex uses built-in macOS commands and relevant tools already installed on the machine. It gathers native inventories, dry-runs, manifests, application metadata, processes, receipts, timestamps, and project history until the important space is explained.

TidyMac keeps a coverage ledger and a separate storage-reconciliation ledger. Inaccessible, provider-managed, other-user, OS-managed, and residual space stays visible instead of being mislabeled as junk or forced into a fake total.

When a stopped container or VM runtime hides material storage behind an opaque disk image, TidyMac explains the gap and asks before temporarily starting it for read-only native inventory. An approved inspection records and restores the original state, including when inventory fails.

</details>

<details>
<summary><strong>How it classifies risk</strong></summary>

TidyMac keeps two questions separate:

1. **How certain are we about what this is?** Verified, likely, or unknown.
2. **What happens if it goes away?** Silent regeneration, redownload, rebuild, workflow reset, possible state loss, or non-regenerable loss.

That distinction is why a verified cache can be recommended while still warning about a large future download—and why an “orphan-looking” folder is protected until its ownership is actually established.

Useful data may be better **evicted locally**, **relocated**, or **pruned by its owning tool** rather than deleted. Synced deletion, workflow reset, Trash staging, and permanent deletion are never presented as interchangeable.

</details>

## Requirements

- macOS
- Claude Code or Codex

That is the full runtime requirement. Optional ecosystem commands such as `brew`, `docker`, or `xcrun` are used only when already installed and relevant to the machine.

A capable reasoning model is strongly recommended for a full-machine audit:

| Host | Guidance |
|---|---|
| Claude Code | Sonnet or Opus class; Haiku is not supported for full-machine audits |
| Codex | A frontier Codex model with medium or higher reasoning |

The host supplies the model. TidyMac does not call an API, transmit the audit to its own service, or bundle model credentials.

## Releases

TidyMac uses semantic Git tags and [GitHub releases](https://github.com/azohra/tidymac/releases): patches for fixes, minors for backward-compatible workflow or capability changes, and majors for incompatible contracts.

The skill itself does not need a runtime version field; installers record the repository source and content hash.
