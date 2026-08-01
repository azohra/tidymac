# Generated opportunity reports

Generate a report from finalized finding records only. The visual explains evidence and tradeoffs; it never substitutes for investigation or invents values to make a complete-looking dashboard.

## Host adaptation

Use the richest surface already supported by the host:

1. Render an in-conversation interactive artifact when available.
2. If the user asks for a standalone report, copy [the bundled report shell](../assets/opportunity-report.html) to one self-contained HTML file under `/tmp`, replace only its embedded JSON with sanitized finding records, and ask before opening another app to display it.
3. Otherwise produce the same information as structured text.

Do not require Python, Node.js, a package manager, a local server, a browser library, or downloaded assets. Do not write generated reports into a project unless the user explicitly chooses that destination. Keep the shell's content-security policy, no-fetch boundary, text-only field rendering, and no-command-execution boundary intact.

Serialize embedded data as valid JSON and make it safe inside an HTML script element: encode `<`, `>`, and `&` as `\u003c`, `\u003e`, and `\u0026`, and encode Unicode line or paragraph separators when present. Never interpolate a finding string into markup or executable JavaScript.

## Finding record

Give every displayed opportunity one canonical record:

| Field | Meaning |
|---|---|
| `id` | Stable finding ID used by reports and approvals |
| `label` | Minimum useful owner or generic category label |
| `allocated_bytes` | Observed local allocated-size estimate |
| `native_reclaimable_bytes` | Owning tool's estimate, if available |
| `expected_host_recovery` | Range or unknown; never copied blindly from another size |
| `confidence` | Verified, likely, or unknown |
| `data_class` | Cache, generated media, model, backup, workflow state, content, runtime, or unknown |
| `decision` | Clean up, optional, or keep |
| `action` | Keep, evict, relocate, native prune, remove regenerable derivative, redownload, reset, Trash, synced delete, or permanent delete |
| `scope` | This Mac, external volume, owning runtime, cloud, or synchronized devices |
| `consequence` | Regeneration, redownload, rebuild, reset, possible state loss, or non-regenerable loss |
| `recovery` | Undo route, Trash staging, redownload source, backup, Recently Deleted, or none |
| `preconditions` | Required stopped owner, synchronization state, attached destination, or other guard |
| `evidence` | Concise local evidence supporting identity and action |
| `recommendation` | Machine-specific conclusion |

Omit unavailable optional values rather than guessing. Store all arithmetic in bytes and format values only for display.

At report level, provide deduplicated `decision_totals` for `clean_up_bytes`, `optional_bytes`, and `keep_bytes`. Do not derive these totals by blindly summing overlapping findings or inclusive alternatives.

## Opportunity map

Default to one compact generated view rather than a generic dashboard:

- Lead with the **Clean up**, **Optional**, and **Keep** decision groups plus their deduplicated totals. Put contextualized coverage and reconciliation immediately below rather than making them the primary decision surface.
- Show a storage-accounting bar with explained measured storage, inaccessible scope, documented OS-managed context, and residual unexplained storage. Do not imply that unrelated measurement bases add exactly.
- Size finding marks by observed local allocation, clearly labeled as allocated size rather than promised savings.
- Encode the proposed action—not the application category or consequence—with stable labels such as evict, native prune, remove generated copy, relocate, Trash, and delete.
- On selection, show why the data exists, evidence, confidence, native action, scope, consequence, recovery, preconditions, and expected host recovery.
- Show valuable “keep” context and unresolved findings without turning them into cleanup opportunities.
- Show potential, recommended, selected, staged, and observed-recovery totals separately.

Do not create health scores, cleanliness grades, fear language, arbitrary thresholds, or decorative metrics. Do not hide uncertainty behind a reassuring color.

## Interaction contract

- Let the user select findings by stable ID and build a proposed plan.
- Keep mutually exclusive alternatives mutually exclusive and show only their delta.
- Treat `Prepare plan` as a request to generate exact previews and approval cards.
- Never execute shell commands, cleanup commands, Finder automation, or file operations from report JavaScript.
- Never translate a click, checkbox, visual selection, or host follow-up into cleanup approval.
- After selection, revalidate each finding and ask for approval with the exact resolved command or native UI route.

When the host offers a conversational callback, the report may send a follow-up containing only selected IDs and the request to prepare previews. Otherwise expose the selected IDs for the user to quote. Do not embed command execution bridges.

## Privacy modes

**Interactive:** Show the minimum owner or project identifier needed to understand a finding. Avoid unnecessary exact paths and content-bearing names.

**Shareable:** Replace usernames, hostnames, volume names, project and container names, personal filenames, paths, archive members, model prompts, dataset names, and database names with generic labels and finding IDs. Preserve sizes only when the user wants them shared.

Never inspect additional personal content merely to improve the visual. Use already-approved evidence and aggregate personal roots by default.

## Presentation quality

- Make the first view useful without interaction and responsive to narrow screens.
- Use semantic controls, keyboard access, visible focus, readable contrast, and labels that do not rely on color alone.
- Support light and dark appearance when the surface permits it.
- Keep all data embedded and local. Do not fetch analytics, fonts, scripts, images, or application data.
- Label example or synthetic data unmistakably; never mix it with a real scan.
- Keep raw command logs out of the visual. Preserve them only as local evidence when necessary.

The report should feel generated for this Mac because its groupings, labels, action choices, and explanations come from this audit—not because it exposes more personal information.
