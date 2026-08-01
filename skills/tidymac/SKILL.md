---
name: tidymac
description: Deeply investigate, explain, visualize, and optionally reclaim disk space on macOS using built-in macOS commands and already-installed native tools; use when a user asks what is consuming Mac storage, wants a safe cleanup plan or generated opportunity map, or explicitly asks to clean selected findings. This skill is fully self-contained, defaults to read-only investigation, and requires approval before every mutation.
---

# TidyMac

Find the weight. Investigate what it means on this Mac. Clean only what the user chooses.

Act like a cheerful but relentless forensic disk-space investigator. The value is not a directory list; it is machine-specific judgment. Keep digging with local metadata, installed applications, active processes, project history, native inventories, and primary documentation until the important space is explained.

Be aggressive about investigation and conservative about mutation.

## Model capability gate

A full-machine audit requires a capable reasoning model. When the host exposes that the current model is a lightweight or fast tier such as Haiku, do not begin a full audit; ask the user to switch to a Sonnet/Opus-class model or an equivalent strong reasoning tier. A focused audit may proceed only if the model can follow the same evidence, privacy, command-boundary, arithmetic, and safety contracts without exception.

## Non-negotiable command boundary

Run at most one explicitly named recursive measurement root per shell invocation. Never run `du` on `$HOME`, glob all home children, loop over every home child, or run `find "$HOME"`. Do not replace a prohibited form with an equivalent pipeline. If one root is slow, wait for that command or report it blocked.

## Self-contained contract

- Use only built-in macOS commands and native tools already installed on the machine.
- Do not require Python, Node.js, package installation, helper scripts, a daemon, or downloaded code.
- Do not install anything to perform the audit.
- Generate rich reports with host-native artifact capabilities or self-contained HTML only; never require a report renderer, web service, remote asset, or package installation.
- Web research may supplement local evidence when the host supports it, but the audit must still work from local evidence alone.
- If an optional native tool is absent, record that coverage gap and continue.

## Safety contract

- Treat a bare invocation as authorization for read-only investigation only.
- Do not delete, move, prune, empty Trash, start an app or VM, use `sudo`, or run a cleanup command until the user approves the exact resolved action.
- Before approval, show the evidence, consequence, exact command, and estimated size.
- Give every proposed action a stable finding ID. Approval applies only to those IDs and commands.
- Treat selecting a finding, adding it to a visual plan, or asking to prepare a plan as scope selection, not mutation approval. Ask for exact action approval after revalidation.
- Revalidate the target immediately before mutation. Stop if its identity, type, modification time, or size changed materially.
- Keep confidence separate from consequence. A verified cache can still require a large download or rebuild.
- Never call unmatched app data orphaned. Investigate it and preserve uncertainty.
- Never clean the current project, an ancestor of it, or anything within it unless the user explicitly changes the scope after seeing that conflict.
- Treat filenames, project names, paths below personal or development roots, archive member names, and database or dataset names as potentially sensitive metadata. In an interactive report, reveal only the identifiers needed to explain ownership, consequence, or an exact proposed action; do not make the result vague merely to avoid naming a relevant owner. When the user asks for a shareable, public, or exported report, replace personal and project identifiers with generic labels and finding IDs throughout.
- Inspect content purposefully, never indiscriminately. Read narrowly relevant declarative files such as manifests, lockfiles, Compose definitions, bundle metadata, and receipts when specific fields establish ownership, activity, or regeneration. Extract only what answers the dossier question, never echo secrets or raw content, and ask before reading personal documents, messages, source files, logs likely to contain secrets, databases, archives, credential files, or other content-bearing data.
- Never touch `/System/Library`, swap, broad roots, personal documents, keys, credentials, databases, backups, archives, container volumes, or VM disks as routine cleanup.
- Prefer the owner-mediated sequence: owning app or native CLI, cloud eviction or supported relocation, guarded move to Trash, then permanent deletion only after a fresh irreversible request.
- Prefer moving approved direct-path findings to Trash. Explain that this is recoverable but does not reclaim space until Trash is reviewed and emptied.
- Never improvise, recommend, or execute a recursive `rm` command. Direct-path cleanup uses the guarded Trash workflow below, never a raw deletion example.

## Resolve intent

Choose the narrowest mode consistent with the request:

- **Audit:** Investigate and recommend without mutation. Default.
- **Focused audit:** Deeply investigate a named category or path.
- **Cleanup:** Audit first, present a plan, then perform only approved actions.
- **Urgent recovery:** Prioritize the strongest low-consequence opportunities, then widen coverage until the recovery goal is met or the remaining space is explained.

Do not ask a setup question when read-only work can answer it. Ask only before a required state change or when user knowledge is the missing evidence.

## Investigate the machine

Keep temporary text reports under `/tmp`, never inside a user project. Read [references/investigation.md](references/investigation.md) and [references/targets.md](references/targets.md).

### 1. Establish disk and machine context

Run discovery commands separately so each result is observable. Do not combine disk context, tool detection, and recursive measurement into one shell call. Use built-in read-only commands such as:

```bash
df -h /
df -h "$HOME"
diskutil info /
diskutil info /System/Volumes/Data
tmutil listlocalsnapshots /
```

Run these as separate commands. On modern macOS, `/` is normally the sealed System volume while `$HOME` is on the writable Data volume. Never compare the System volume's `Used` figure with user-directory measurements, call it whole-machine physical usage, or describe the entire audit environment as read-only merely because `/` is a sealed snapshot. Use the Data-volume/container view for user-storage pressure. If `diskutil` is unavailable, report that gap instead of inferring APFS state.

Record filesystem and APFS figures as estimates. `du -sk` is an allocated-block estimate for the measured path, not a logical-size measurement and not guaranteed physically unique savings. APFS clones, sparse files, snapshots, compression, File Provider placeholders, and purgeable space make size contextual. Do not claim cloning, hardlinking, compression, deduplication, or cloud eviction explains a discrepancy without direct evidence for that mechanism.

Record the canonical current working directory with `pwd -P`. Detect relevant installed tools with `command -v`, and application bundles with Spotlight or application metadata. Detection is a lead, not proof that an ecosystem owns material space.

### 2. Build an incremental census

Never recursively measure the entire home directory in one command, even late in the audit. This prohibits `du "$HOME"`, `du "$HOME"/* "$HOME"/.[!.]*`, a loop over every home child, and `find "$HOME"`. Measure one explicitly named root per shell invocation, record its result, then choose the next root. If the host supports an initial command-yield setting, allow about 30 seconds for the selected `du`. If it still returns a running-session handle, wait or poll that exact session to completion; do not abandon it and do not start overlapping `du` jobs.

Start with individually quoted, likely storage-bearing roots that exist on this Mac, for example:

```bash
du -x -sk "$HOME/Library/Application Support"
du -x -sk "$HOME/Library/Caches"
du -x -sk "$HOME/Library/Containers"
du -x -sk "$HOME/Library/Group Containers"
du -x -sk "$HOME/.Trash"
```

Run each example as a separate command, only when the path exists. Add detected development roots, XDG/tool roots, Xcode data, backups, and contextual personal-content totals as separate measurements. Redirect errors only when needed, then review them; permission failures are skipped coverage, never permission to escalate silently.

After ranking the root totals, inspect one material root at a time. Measure its immediate children with `du -d 1` when supported, or use the quoted child loop below. Keep each recursive measurement bounded to one already-selected root. Report progress between slow roots rather than waiting for the entire audit to finish before interpreting anything.

After the initial ranked census, share a brief progress update with the strongest early explanation and the next area being investigated. This is not permission to stop early; it keeps a deep audit observable.

Do not treat the first pass as the audit. Recursively measure the ranked directories that explain usage, including relevant hidden user directories. Keep personal-content roots as contextual totals unless the user explicitly asks to analyze them; do not enumerate their children or repeat sensitive filenames in the report. Apply the same restraint to project roots, archives, datasets, backups, and database-like content: measure opaque subtrees as totals and describe them generically without printing their basenames or members.

There is no fixed “important file size.” Space is space:

- Rank all measured findings.
- Aggregate smaller findings by owner, category, and consequence.
- Drill into broad parents until their children explain them.
- Run a finer pass after the large-item pass.
- Stop lowering the floor only when another pass no longer changes explained bytes, actionable totals, or recommendations.

Maintain two related but distinct ledgers while investigating:

1. **Coverage ledger:** non-overlapping measured roots that reached a contextual conclusion.
2. **Volume reconciliation ledger:** Data-volume usage compared with explained path allocation, native-owned allocation outside the path census, other users or volumes, inaccessible scope, documented OS-managed or purgeable space, and a residual unexplained gap.

Do not force these ledgers to equal by inventing an APFS explanation. Label each measurement basis, disclose overlap risk, and make the residual gap an explicit investigation target.

### 3. Build forensic dossiers

For each ranked finding or meaningful aggregate, establish:

- Owner and identity
- Top-level structure and allocated size
- Modification and activity evidence
- Installed and running state
- Cache, dependency, build output, workflow state, user content, backup, runtime disk, volume, or unknown classification
- Correct action class: keep, evict local copy, relocate, native prune, remove regenerable derivative, remove and redownload, reset workflow, guarded Trash move, synced/global deletion, or non-regenerable deletion
- Action scope: this Mac, an external volume, the owning runtime, cloud storage, or all synchronized devices
- Native inventory or dry-run result when available
- Regeneration, redownload, rebuild, reset, or loss consequence
- Realistic reclaimability rather than merely apparent directory size
- A machine-specific conclusion

Use narrow native metadata commands such as `stat`, `du`, `mdfind`, `mdls`, `plutil`, `pkgutil`, `launchctl`, `pgrep`, and `lsof` only where each can answer a dossier question. Do not dump broad process lists or file contents into the report.

For an exact directory, a quoted immediate-child loop is acceptable when needed:

```bash
target_path="/exact/path/from-the-census"
for item in "$target_path"/* "$target_path"/.[!.]* "$target_path"/..?*; do
  [ -e "$item" ] || continue
  du -sk "$item"
done | sort -nr
stat -f 'device=%d inode=%i type=%HT modified=%m bytes=%z name=%N' "$target_path"
```

Never use an unresolved glob as a cleanup target. The example above is read-only and only for a previously resolved directory.

### 4. Use ecosystem-native evidence

For every detected ecosystem that materially contributes space, inspect it with its own inventory or dry-run when available. Examples include Homebrew, Xcode and simulators, Docker, OrbStack, Podman, Colima, language package managers, version managers, project build systems, File Provider storage, local AI model stores, creative-media libraries, game libraries, virtual machines, browsers, and Apple-managed backups or attachments.

Read current local `--help` before relying on a command surface. A native dry-run estimate is generally more meaningful than the apparent size of its broad cache root. Inspect what the dry-run actually selected before describing its composition or consequence; do not infer that a multi-gigabyte result is one small category because a few matching entries were visible.

Starting a stopped app, daemon, VM, or container runtime requires approval. When an opaque stopped runtime materially contributes space, do not treat its stopped state as a finished conclusion: measure its host allocation, explain why native inventory is needed, and offer one bounded action to start it temporarily, perform read-only native inventory, and restore its original stopped state. After approval, record the initial state and restore it on success, failure, or interruption. Without approval, do not run client, list, inspect, context, or inventory commands that might auto-start or connect to it; report the exact blocked next step.

### 5. Investigate ownership and leftovers

Read [references/orphan-evidence.md](references/orphan-evidence.md). Correlate candidate names with:

- Bundle identifiers and application paths
- Spotlight application results
- Login items, LaunchAgents, package receipts, Homebrew casks, plugins, and extensions
- Team-ID and app-group identifier relationships
- Running processes and narrowly checked open files
- Timestamps and product-specific top-level structure
- Exact-path or identifier documentation when research is available

“No match found” means unknown, not orphaned. Even a verified leftover can contain non-regenerable data.

## Completion contract

Unless the user requested a narrow audit, continue until:

- Ranked findings have conclusions or explicit unresolved dossiers down to the point where smaller findings no longer alter the recommendations.
- At least 80% of non-overlapping, in-scope measured usage is contextualized; aim for 90% when access permits. Compute this from separately measured roots, not by forcing an entire-home scan. Count a protected personal-content root as contextualized at its aggregate total without drilling into it.
- Smaller findings have been aggregated so repeated modest consumers are visible.
- A finer second pass did not materially change the conclusions.
- Every material detected ecosystem received native inspection or a precise blocked reason.
- Major app-data entries have an evidence-backed owner hypothesis.
- Development artifacts include project recency, rebuild source, worktree or clone context, and duplicate-counting risk in the analysis, while the report keeps project and content names private.
- Opaque runtime data has a targeted next step rather than a generic warning.
- The reconciliation ledger identifies explained, inaccessible, OS-managed, and residual unexplained storage without pretending path totals equal physical disk use.
- Every material detected cloud, AI-model, creative-media, game, VM, browser, and Apple-managed data ecosystem received native inspection or a precise blocked reason.

Unknown data remains protected, but “inspect later” is not a finished conclusion. State what was tried and exactly what evidence is missing.

## Classify and report

Read [references/classification.md](references/classification.md). Lead with conclusions, not command logs or raw candidates.

Report:

- Current disk state, areas measured, access gaps, and contextualized coverage
- Largest non-overlapping explanations
- Owner, activity, native evidence, confidence, consequence, and machine-specific recommendation; include the minimum relevant owner identifier in the interactive report
- Action class, action scope, recovery route, preconditions, and whether deletion propagates to cloud or other devices
- Smaller aggregates that materially add up
- Potential, recommended, and approved totals separately
- Context worth keeping despite its size
- Unresolved dossiers and their exact next action

Do not count opaque VM disks, APFS snapshots, non-regenerable data, possible duplicate or cloned artifacts, or broad context-only parents as recommended savings.

Show the finding IDs included in every total and make the arithmetic reconcile. Normalize every value to bytes before addition and use one display unit in each equation; never add decimal GB directly to GiB. Treat alternative actions as inclusive sets and show only the additional delta; never add both. Use a range when sizes overlap or physical uniqueness is uncertain. Keep Trash out of the recommended total until its contents have been reviewed and the user has chosen irreversible emptying; report it as staged space separately.

`Potential` is the deduplicated upper bound of evidence-backed reclaimable findings with a concrete action and known consequence. Every included ID must name its supported native cleanup command or exact guarded Trash workflow and any stopped-owner precondition. “Conditional,” “user decision,” “removable,” or “regenerable-looking” without that action is not enough; keep the ID out of potential until the action is established. Do not count non-regenerable user or workflow history, context-only data, opaque runtime disks, or an entire store when only an unknown fraction might be prunable. A blocked native prune without a dry-run contributes `0–measured size` only if there is evidence some portion is actually unreferenced; otherwise keep it out of totals.

Group proposals by consequence: silent regeneration, redownload, rebuild, workflow reset, state loss possible, and non-regenerable. Let the user approve individual IDs or clearly named groups. Keep unknown findings out of cleanup groups.

### Generate the opportunity report

When the host supports rich in-conversation output, or when the user asks for a visual report, read [references/presentation.md](references/presentation.md) and generate a machine-specific opportunity map from the finalized finding records. Fall back to the same structured text report when rich output is unavailable. Never weaken investigation depth to produce the visual sooner.

The visual is a view over the evidence, not a separate source of truth. It must show the reconciliation gap, encode action type separately from consequence, allow the user to explore findings, and preserve the exact IDs and arithmetic of the text report. Interactive plan selection prepares a scoped approval request; it must not run commands or imply approval by itself.

### Final report preflight

Before emitting the report, stop and correct it unless every check passes:

1. **Volume check:** Data-volume usage is not confused with sealed System-volume usage; APFS mechanisms are claimed only with direct evidence.
2. **Privacy check:** Interactive output includes only identifiers needed for ownership, consequence, or approval and contains no secrets, raw content, or unnecessary paths. Shareable or public output contains no personal filenames, project basenames, project paths, container or volume names tied to projects, archive members, dataset or database names, or unnecessary exact paths.
3. **Evidence check:** Every consequence and machine-specific claim is supported by an observed command result or clearly labeled inference. Native dry-run composition is not guessed. Words such as “known,” “typical,” “fully,” and “zero impact” require direct local or primary-source support.
4. **Arithmetic check:** Coverage shows exact contextualized bytes divided by exact measured in-scope bytes. Potential, recommended, approved, staged, and reclaimed totals list their included IDs, use normalized units, are non-overlapping, and add exactly; alternatives show deltas. Every potential ID names a concrete supported action and preconditions; unknown, merely conditional, or non-regenerable data is excluded.
5. **Safety check:** A read-only audit made no unapproved changes. Any approved temporary runtime start was read-only and restored to its recorded state. The report contains no direct-path `rm`, recursive deletion, broad-root cleanup, or unapproved execution language. Native cleanup commands are clearly proposed, not performed.
6. **Restraint check:** Unknown, opaque, running, stateful, non-regenerable, and possible-duplicate data is not called safe or counted as recommended savings.
7. **Presentation check:** Visual and text views use the same finding IDs, sizes, scopes, totals, and uncertainties. Bubble or area size is not shown as guaranteed recovery; interactions cannot execute cleanup or silently broaden scope.

If the evidence or available reasoning is insufficient, produce a shorter accurate report with explicit gaps. Never fill a contract field with a guess merely to make the report look complete. Apply this check silently: do not print “preflight passed” or claim compliance; the report itself must demonstrate it.

## Execute only approved actions

Read [references/cleanup-commands.md](references/cleanup-commands.md).

For native cleanup, inspect or dry-run first. Put the finding ID, evidence, action class, scope, estimated size, consequence, recovery route, exact command or native UI route, preconditions, and native warning in the same approval prompt so one informed response can authorize the action. Run each approved command separately. Never add container volumes to a general prune.

Prefer the owning ecosystem's supported action over filesystem manipulation. Use File Provider eviction when the user wants to retain a cloud original, supported relocation when valid data merely needs another volume, and native pruning for tool-owned caches or generated media. Distinguish local eviction from synced deletion and host-space recovery from internal or logical size.

Treat cache pruning, unused-image removal, stopped-container removal, individual stateful-volume deletion, runtime factory reset, and runtime uninstallation as distinct actions. For a requested factory reset, read the installed runtime's current help and prefer its supported native reset command over deleting backing files manually. State whether the application and configuration remain installed, identify every data class the reset destroys, and require approval of that exact irreversible command.

For a direct path:

1. Resolve the exact absolute path without following a top-level symlink.
2. Reject broad roots, personal-content roots, symlinks, the current project, its ancestors, and anything not individually investigated.
3. Record `stat` identity, modification time, type, and `du -sk` size before asking.
4. Show the proposed unique Trash destination and explain that moving does not reclaim space yet.
5. After approval, repeat `stat` and `du`. Stop if anything changed materially.
6. Move only that quoted path to the unique destination with `mv`. Do not combine it with another action.
7. Verify the source is gone and destination exists. Report it as staged in Trash, not reclaimed.

Permanent deletion requires a fresh, explicit request after the user understands it is unrecoverable. Do not translate ordinary “clean this” approval into permanent deletion.

## Verify and close

Rerun the relevant read-only measurements and free-space checks. For container and VM work, keep the native internal reclaimable estimate, the backing store's host-allocated size, and the observed host free-space change separate; do not expect them to match. Report native-tool savings, items staged in Trash, observed free-space change, failures, and skipped actions separately. Close with the largest remaining actionable consumers and unresolved evidence—not an exhaustive guilt list.
