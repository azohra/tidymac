# Classification and reporting

Classify evidence and consequences independently. Never turn “probably a cache” into permission to delete it.

## Evidence confidence

| Confidence | Meaning | Required next step |
|---|---|---|
| Verified | A native tool, manifest, bundle identifier, or documented path proves the identity. | Assess consequence. |
| Likely | Name, location, contents, and timestamps consistently suggest an identity. | Inspect before recommending. |
| Unknown | Evidence is missing, ambiguous, or contradictory. | Research; do not propose deletion yet. |

Treat `unmatched` from `scan_orphans.py` as unknown. It is not equivalent to orphaned.

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

## Reclaimable totals

- Show `potential`, `recommended`, and `approved` totals separately.
- Do not add an ancestor finding and one of its descendants.
- Do not count context-only findings, Time Machine local snapshots, opaque VM disk images, or non-regenerable data in the recommended total.
- Describe scanner sizes as allocated-size estimates. APFS clones, snapshots, sparse files, compression, and purgeable space can make apparent and physically recoverable sizes differ.
- Use before/after free-space measurements as the final authority, while noting that background activity can change them.

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
