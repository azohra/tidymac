# Classification and reporting

Classify evidence and consequences independently. Never turn “probably a cache” into permission to delete it.

## Evidence confidence

| Confidence | Meaning | Required next step |
|---|---|---|
| Verified | A native tool, manifest, bundle identifier, or documented path proves the identity. | Assess consequence. |
| Likely | Name, location, contents, and timestamps consistently suggest an identity. | Inspect before recommending. |
| Unknown | Evidence is missing, ambiguous, or contradictory. | Research; do not propose deletion yet. |

Treat failure to find a local owner as unknown. It is not equivalent to orphaned.

## Consequence

| Consequence | Examples | Default disposition |
|---|---|---|
| Silent regeneration | GPU shader cache, crash report, ephemeral web cache | Offer in a low-impact batch. |
| Redownload required | npm cache, browser binaries, Go module cache | Offer separately and mention network cost. |
| Rebuild required | DerivedData, `target`, `.next`, `node_modules` | Offer separately and mention time cost. |
| Workflow reset | Saved state, sessions, stopped containers, simulator state | Confirm individually or in a narrowly named group. |
| State loss possible | App support, Docker volumes, device backups, archives | Confirm individually after inspection. |
| Non-regenerable | User documents, Xcode archives, device backups | Recommend keeping unless the user identifies them as obsolete. |

Do not use an auto-clean tier. A bare skill invocation authorizes read-only auditing only. Treat a user's explicit approval of named action IDs as authorization for those actions and nothing else.

## Recommendation rules

- Recommend a low-impact batch only when evidence is verified and consequences are bounded.
- Split redownload, rebuild, workflow-reset, and state-loss findings into separate approval groups.
- Check whether the owning app or service is running before proposing removal of mutable app data.
- Inspect top-level contents and modification dates before proposing removal of application support or container data.
- Research unfamiliar findings with current primary sources. Report the source and the remaining uncertainty.
- Prefer a native tool's dry-run or inventory command before its cleanup command.
- Never characterize failure to find an owner as proof that data is orphaned.
- Call a container volume attached or referenced when that is what native metadata proves. Do not use “protected” or “active” as shorthand for a running workload.

## Reclaimable totals

- Show `potential`, `recommended`, `approved`, `staged in Trash`, and `observed reclaimed` separately. Zero is a valid value.
- Normalize source estimates to bytes before arithmetic, then display each equation in one unit. Preserve a native tool's decimal-GB figure beside the normalized value, not inside a mixed-unit sum.
- Show the included finding IDs or named aggregates beside each total and verify the arithmetic explicitly. Use a range rather than false precision when overlap or APFS behavior is uncertain.
- Do not add an ancestor finding and one of its descendants.
- Do not add inclusive alternatives. If an aggressive action contains a recommended action, show the aggressive inclusive total and its additional delta, not their sum.
- Do not count context-only findings, Time Machine local snapshots, opaque VM disk images, or non-regenerable data in the recommended total.
- Keep Trash out of the recommended total until its contents are reviewed and the user explicitly selects irreversible emptying. Moving additional items to Trash is staged, not reclaimed.
- Define `potential` as evidence-backed reclaimable space with a concrete action and known consequence. For every included ID, name the supported native cleanup command or the exact guarded Trash workflow, plus any required stopped-app or stopped-service precondition. A label such as “conditional,” “user decision,” “removable,” or “regenerable-looking” is not a concrete action. Exclude the ID until the action and preconditions are established. Also exclude non-regenerable history/content, context-only data, opaque runtime disks, and stores whose reclaimable fraction is wholly unknown.
- Describe measured sizes as allocated-size estimates. APFS clones, snapshots, sparse files, compression, and purgeable space can make apparent and physically recoverable sizes differ.
- Use before/after free-space measurements as the final authority, while noting that background activity can change them.
- For VM-backed runtimes, show native internal reclaimability, host-allocated backing-store size, and observed host recovery separately. Never substitute the sparse disk's logical capacity for any of them.

If the displayed candidate rows do not exactly sum to their stated total, fix the rows or the total before reporting. A prose range does not excuse arithmetic whose lower or upper bound cannot be reproduced.

## Report shape

For each actionable finding, show:

| Field | Purpose |
|---|---|
| ID | Stable selection handle from the scan output |
| Size | Allocated-size estimate |
| Evidence | Why the finding was identified |
| Confidence | Verified, likely, or unknown |
| Consequence | What the user pays or loses |
| Recommendation | Keep, clean, inspect, or research |

Lead with the best few opportunities. Put exhaustive low-value inventory behind a concise summary.

Also report investigation coverage: the share of ranked, non-overlapping measured bytes that reached a conclusion. A raw candidate, an unexplained `unknown`, or a generic “inspect later” does not count as contextualized coverage.

Write coverage as `contextualized allocated-size estimate / measured in-scope allocated-size estimate = percentage`, with separately measured root IDs. Do not call this whole-machine coverage when protected or inaccessible roots were not measured; disclose those roots and bytes separately.
