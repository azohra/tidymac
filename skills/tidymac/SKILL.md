---
name: tidymac
description: Investigate, explain, visualize, and optionally reclaim disk space on macOS with built-in commands and already-installed native tools. Use when a user asks what is consuming Mac storage, wants a decisive cleanup recommendation or opportunity map, or asks to clean selected findings. Self-contained; defaults to a read-only audit and requires exact approval before every mutation.
---

# TidyMac

Explain what occupies this Mac, recommend what to do, and change only what the user approves.

Investigate aggressively. Mutate conservatively. Raw sizes find suspects; machine-specific evidence decides the action.

## Operating contract

- Treat a bare invocation as a read-only audit.
- Use built-in macOS commands and relevant tools already installed. Do not install or require a runtime, package, helper, daemon, service, or downloaded code.
- Run at most one explicitly named recursive measurement root per shell invocation. Never scan `$HOME` recursively, enumerate all of its children in one command, or replace either form with an equivalent pipeline.
- Wait for each recursive measurement to finish before starting another. Keep slow work observable with brief progress updates.
- Do not use `sudo`, start an app or runtime, move data, prune, empty Trash, or run any cleanup action without exact approval.
- Treat visual selection as plan scope, not cleanup approval.
- Revalidate identity, type, modification time, and size immediately before mutation. Stop on material change.
- Exclude the current project, its ancestors, and its contents unless the user explicitly changes that scope after seeing the conflict.
- Inspect narrow ownership metadata and declarative manifests when needed. Ask before reading personal documents, messages, source, databases, archives, credentials, or secret-bearing logs.
- Show only identifiers needed to explain or approve a finding. Sanitize all personal and project identifiers in shareable output.
- Prefer the owner’s native action, then supported eviction or relocation, then a guarded Trash move. Permanent deletion requires a fresh irreversible request.
- Never propose or execute recursive `rm` for direct-path cleanup.

For a full-machine audit, require a strong reasoning model. If the host identifies the current model as a lightweight tier that cannot honor the evidence, privacy, arithmetic, and safety contracts, ask the user to switch models. A focused audit may proceed only under the same contracts.

## Choose the mode

- **Audit:** Investigate and recommend. Default.
- **Focused audit:** Investigate one path or ecosystem deeply.
- **Cleanup:** Audit first; execute only approved findings.
- **Urgent recovery:** Rank the least disruptive path to the requested recovery, then widen coverage as needed.

Do not ask setup questions that read-only evidence can answer. Ask only before a state change or when user knowledge is the missing evidence.

## 1. Build the census

Read [references/investigation.md](references/investigation.md) before a full audit.

Establish sealed System-volume, writable Data-volume, APFS, snapshot, free-space, and current-project context with separate commands. Treat `du -sk` as an allocated-size estimate, not logical size or guaranteed physical recovery. Never invent clone, hard-link, sparse-file, compression, snapshot, File Provider, or purgeable-space explanations.

Measure likely storage-bearing roots one at a time. Rank non-overlapping results, drill into material parents, aggregate smaller peers, and run a finer pass. There is no fixed important size: stop lowering the scan floor only when another pass no longer changes explained bytes, actionable totals, or recommendations.

Keep personal-content roots as aggregate context unless the user explicitly requests content review. Keep temporary evidence under `/tmp`, never in a user project.

Maintain two ledgers:

- **Coverage:** non-overlapping measured bytes that reached a conclusion.
- **Reconciliation:** Data-volume use compared with explained allocation, inaccessible scope, other users or volumes, OS-managed context, and the residual gap.

Do not force unrelated measurement bases to equal.

## 2. Explain the findings

Read [references/ecosystems.md](references/ecosystems.md) for every detected ecosystem that materially contributes space. Skip absent or immaterial ecosystems.

For each ranked finding or useful aggregate, establish:

- owner, identity, structure, allocated size, and activity
- installed and running state
- data class and native inventory or dry-run
- action, scope, consequence, recovery route, and preconditions
- realistic host recovery, overlap risk, and machine-specific conclusion

Prefer evidence in this order: owning tool, installed metadata, process ownership, immediate-child structure and timestamps, current primary documentation, then user recognition.

Starting a stopped app, daemon, VM, or runtime is a mutation. If native inventory is necessary, explain why and ask for one bounded temporary start that records and restores the original state even on failure. Otherwise report the exact blocked evidence.

Treat “no owner found” as unknown, never orphaned. Even a verified leftover may contain non-regenerable data.

## 3. Finish the investigation

Unless the scope is narrow, continue until:

- conclusions cover at least 80% of non-overlapping in-scope measured bytes; aim for 90% when access permits
- a finer pass no longer changes conclusions or recommendations
- smaller repeated consumers are aggregated
- every material detected ecosystem has native evidence or a precise blocked reason
- app-data ownership hypotheses are evidence-backed
- opaque runtime storage has a targeted next step
- the reconciliation ledger exposes inaccessible, OS-managed, and residual space without calling it junk

Protected personal roots count as contextualized at their aggregate total. Do not drill into them merely to improve coverage. Unknown findings remain protected, but “inspect later” is incomplete—state what was tried and what evidence is missing.

## 4. Make the decision easy

Read [references/decisions.md](references/decisions.md).

Lead with at most three groups:

1. **Clean up:** verified disposable data with a concrete action and bounded cost
2. **Optional:** real recovery with a noticeable rebuild, sign-in, reset, or history tradeoff
3. **Keep:** active, personal, non-regenerable, unknown, or unsupported data

Give each group a deduplicated total, one plain-language consequence, and finding IDs. Put evidence, paths, commands, coverage, and arithmetic after the decision summary or reveal them when the user prepares cleanup.

When rich output is supported or requested, read [references/report.md](references/report.md). The visual and text reports must share one finding record, one set of totals, and the same uncertainty. Fall back to text without reducing investigation depth.

## 5. Approve and execute

Read [references/cleanup.md](references/cleanup.md) only when preparing or executing cleanup.

An approval card must include the finding ID, evidence, action, scope, size estimate, expected host recovery, consequence, recovery route, preconditions, and exact command or native UI route. One concise card may cover a clearly named same-consequence group. Run each approved action separately.

Keep cache pruning, image removal, stopped-container removal, stateful-volume deletion, factory reset, uninstall, cloud eviction, synced deletion, Trash staging, and permanent deletion as distinct scopes.

## 6. Verify and close

Rerun the relevant measurements and free-space checks. Report native-tool savings, staged Trash, observed host recovery, failures, and skipped actions separately. For VM-backed storage, keep internal reclaimability, host allocation, and observed recovery distinct.

Close with the largest remaining actionable findings and unresolved evidence—not an exhaustive guilt list.
