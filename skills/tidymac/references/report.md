# Report

Generate the visual only from finalized finding records. It explains the audit; it never replaces investigation or invents dashboard values.

## Choose the surface

1. Use a supported in-conversation artifact.
2. For a requested standalone report, copy [the report template](../assets/report-template.html) to `/tmp`, replace its embedded JSON, and ask before opening another app.
3. Otherwise return the same records as concise text.

Do not require a renderer, server, browser library, package, remote asset, or downloaded code. Do not write reports into a project unless the user chooses that destination.

## Record shape

Use one canonical record per finding:

| Field | Meaning |
|---|---|
| `id` | Stable report and approval handle |
| `label` | Minimum useful owner or generic category |
| `allocated_bytes` | Observed local allocated-size estimate |
| `expected_host_recovery` | Estimate, range, or unknown; never copied blindly from allocation |
| `confidence` | Verified, likely, or unknown |
| `decision` | Clean up, optional, or keep |
| `action` | Keep, evict, relocate, native prune, remove derivative, redownload, reset, Trash, synced delete, or permanent delete |
| `scope` | This Mac, external volume, runtime, cloud, or synchronized devices |
| `consequence` | Regeneration, redownload, rebuild, reset, possible state loss, or non-regenerable loss |
| `recovery` | Undo, Trash, redownload, backup, Recently Deleted, or none |
| `preconditions` | Stopped owner, completed sync, attached destination, or other guard |
| `why` | Why the data exists |
| `evidence` | Concise local support |
| `recommendation` | Machine-specific route |

At report level, provide deduplicated `decision_totals` and reconciliation values. Store arithmetic in bytes. Omit unavailable optional data instead of guessing.

## Visual hierarchy

- Lead with **Clean up**, **Optional**, and **Keep** totals.
- Put coverage and reconciliation directly below the decision.
- Size findings by observed local allocation and label that encoding clearly.
- Encode proposed action separately from app category and consequence.
- On selection, show evidence, confidence, action, scope, consequence, recovery, preconditions, and expected host recovery.
- Keep valuable and unresolved context visible without turning it into cleanup.
- Keep potential, recommended, selected, staged, and observed totals distinct.

Do not create health scores, cleanliness grades, fear language, arbitrary thresholds, decorative metrics, or reassuring colors that hide uncertainty.

## Interaction

- Select by stable ID and keep alternatives mutually exclusive.
- Treat plan preparation as a request for exact previews, never approval.
- Never execute shell commands, Finder automation, or file operations from report JavaScript.
- Revalidate selected findings before asking for exact action approval.
- Use a conversational callback only to send selected IDs and request previews; otherwise expose a copyable request.

## Privacy and safety

Interactive output shows only identifiers needed to understand or approve a finding. Shareable output replaces usernames, hostnames, volume, project, container, and personal-content names with generic labels and IDs. Do not inspect more content to improve the visual.

For standalone HTML:

- preserve the template’s CSP, no-fetch boundary, text-only rendering, and lack of command bridge
- serialize valid JSON and encode `<`, `>`, and `&` as `\u003c`, `\u003e`, and `\u0026`; encode Unicode line or paragraph separators
- never interpolate finding strings into markup or executable JavaScript
- keep all data local and embedded

Make the first view useful without interaction. Support narrow screens, keyboard navigation, visible focus, readable contrast, light/dark appearance, and labels that do not rely on color. Mark synthetic data unmistakably.
