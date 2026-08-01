# Decisions and reporting

Classify identity, consequence, action, and recommendation independently. “Probably a cache” is neither proof nor permission.

## Evidence

| Confidence | Meaning | Next step |
|---|---|---|
| Verified | Native inventory, manifest, bundle, receipt, or documented path proves identity | Assess action and consequence |
| Likely | Location, structure, timestamps, and local signals agree | Inspect further before recommending cleanup |
| Unknown | Evidence is missing, ambiguous, or contradictory | Research or keep |

No local owner match means unknown, not orphaned.

## Consequence

| Consequence | Typical cost |
|---|---|
| Silent regeneration | Ephemeral cache or diagnostics reappear automatically |
| Redownload | Network, time, version, or future-availability cost |
| Rebuild | Local compute, toolchain, or native compilation cost |
| Workflow reset | Sessions, saved state, writable layers, or simulator state disappear |
| State loss possible | App support, volume, backup, archive, or unclear history may matter |
| Non-regenerable | No established reconstruction path |

## Action

| Action | Boundary |
|---|---|
| Keep | Active, valuable, OS-managed, or insufficiently understood |
| Evict | Remove the local copy only after proving remote synchronization |
| Relocate | Move valid data through an owner-supported workflow |
| Native prune | Let the owner select unused cache or generated data |
| Remove derivative | Preserve originals; state regeneration time and space |
| Remove and redownload | Preserve an exact known source and variant |
| Reset | Name the exact workflow state lost |
| Trash | Stage one verified direct path; no space is reclaimed yet |
| Synced delete | State propagation and retention or Recently Deleted behavior |
| Permanent delete | Fresh irreversible approval after other routes |

Record whether scope is this Mac, an external volume, one runtime, a cloud account, or synchronized devices.

## Recommendation

- **Clean up:** verified, material, disposable data with a concrete action and bounded consequence.
- **Optional:** valid recovery with rebuild, sign-in, reset, useful-history, or similar friction.
- **Keep:** non-regenerable, active, unknown, protected, or lacking a supported recovery route.

Free space changes urgency, not evidence. Recommend verified material cache even on a healthy disk. Do not weaken a recommendation merely because data is redownloadable; state the cost plainly.

Prefer the owner-native action that matches the user’s goal. For material package caches, compare ordinary and full supported previews where available. Recommend the broader redownloadable cache when recovery is meaningful and the user has not prioritized offline reinstalls or bandwidth; offer the narrower action as the lower-cost alternative.

Put rebuilds, sign-outs, resets, and useful-history loss in **Optional**. Keep state loss, synchronized deletion, and non-regenerable data individually scoped. Unknown findings never enter cleanup groups.

## Totals

Keep these values separate:

- **Potential:** evidence-backed, deduplicated upper bound with a concrete action and known consequence
- **Recommended:** findings in **Clean up**
- **Approved:** exact IDs and actions the user authorized
- **Staged:** data moved to Trash but still occupying space
- **Observed:** before/after host free-space change

Normalize inputs to bytes, then format each equation in one unit. List included IDs. Do not add ancestors and descendants, overlapping stores, inclusive alternatives, snapshots, opaque VM disks, context-only parents, non-regenerable data, or unknown reclaimable fractions.

For alternatives, show the inclusive total and additional delta. Use a range when physical uniqueness is uncertain. Keep logical size, allocated size, native reclaimability, and expected or observed host recovery distinct.

File Provider eviction counts only after local presence and completed synchronization are established. Relocation counts only when the owner supports it, the destination is eligible, and the source will not remain duplicated.

## Output

Lead with the decision, not the audit machinery:

```text
Clean up · <total> · <plain consequence> · <IDs>
Optional · <total> · <plain tradeoff> · <IDs>
Keep · <why the important context stays>
```

Then provide only the evidence needed to understand or approve the result. Each actionable finding carries:

- ID, allocated size, and expected host recovery
- owner evidence and confidence
- action, scope, consequence, recovery, and preconditions
- exact native or guarded route

Also disclose in-scope coverage, access gaps, valuable context, unresolved dossiers, and their exact next evidence. Put exhaustive low-value inventory and raw command output out of the primary report.

## Preflight

Before reporting, verify silently:

1. **Volume:** System and Data usage are not confused; APFS explanations have evidence.
2. **Privacy:** No secrets, raw content, or unnecessary identifiers; shareable output is sanitized.
3. **Evidence:** Local claims and consequences are observed or labeled inference; native previews are not guessed.
4. **Arithmetic:** IDs, units, overlaps, alternatives, and totals reconcile exactly.
5. **Safety:** The audit made no unapproved changes; proposed actions are clearly future tense.
6. **Restraint:** Unknown, opaque, stateful, non-regenerable, and possible-duplicate data is not called safe.
7. **Presentation:** Text and visual views use the same records and uncertainty; size is not presented as guaranteed recovery.

If evidence is insufficient, return a shorter accurate answer with explicit gaps. Never fill a field with a guess for completeness.
